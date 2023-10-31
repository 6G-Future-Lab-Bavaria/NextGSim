import numpy as np
from collections import defaultdict
import sys
import heapq
from tabulate import tabulate
from gnb.Handover import Handover
from runtime.data_classes import ConditionalHandoverParameters, States, CHOVersions, HandoverParameters


# todo: First prepare a new gNB and then remove; During the preparation of a new one,
#  there are no prepared gNBs (in case top_num_gnbs = 1), which causes RLFs.


class ConditionalHandover(Handover):
    def __init__(self, simulation):
        super().__init__(simulation)
        self.num_top_gnbs = self.simulation.sim_params.num_top_gnbs
        self.count_prepared_cells = 1  # count the initial gNB
        self.count_released_cells = 0
        self.count_prepared_but_not_used_cells = 0
        self.count_wasted_ttis_per_gnb = defaultdict(int)
        self.version = CHOVersions.up_to_top_gnbs_prepared
        if ConditionalHandoverParameters.with_ttt_exec:
            self.version += '_TTT'
        self.prepared_cells_dict = defaultdict(list)
        self.handover_events_stats = {'a3 only': 0, 'a5 only': 0, 'both':0}

    def main_handover_function(self, user):
        if user.state != States.rrc_connected:
            return
        super().main_handover_function(user)
        channel_matrix = self.select_channel_metric_to_use(self.simulation.channel.average_SINR,
                                                           self.simulation.channel.average_RSRP)
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        if user.hit_finish and user.hit_finish >= current_time:
            # print(f"User {device.ID} is making a HO to {device.next_gnb.ID} at {device.hit_finish}, TTI = {current_time}")
            return
        if self.check_if_execution_has_completed(user):
            return

        self.add_serving_cell_to_prep_cells(user)
        self.check_if_preparation_finished(user)
        self.check_if_prepare_condition_is_satisfied(user, channel_matrix)
        if self.check_if_execution_condition_is_satisfied(user, channel_matrix):
            # UE starts handover execution
            return

        self.check_if_remove_prep_cell_at_ue(user, channel_matrix)
        self.check_if_any_user_to_be_removed_from_prep_cell_list(user)

        if self.version == CHOVersions.max_top_gnbs_always_preped:
            self.ensure_num_top_gnbs_are_prepared(user, channel_matrix)

        self.sanity_checks(user)

    def get_num_are_and_being_prepared_gnbs(self, user):
        return len(user.prepared_gnbs) + len(user.currently_being_prep_cells_finish_time)

    def add_serving_cell_to_prep_cells(self, user):
        if self.simulation.TTI == 0:
            if user.my_gnb not in user.prepared_gnbs:
                user.prepared_gnbs[user.my_gnb] = True
                self.log_prepared_cells(user.my_gnb.ID)
            if user not in user.my_gnb.prepared_CHO_for_users:
                user.my_gnb.prepared_CHO_for_users.append(user)
        else:
            if user.my_gnb not in user.prepared_gnbs or user not in user.my_gnb.prepared_CHO_for_users:
                self.print_prep_stats(user)
                # if using traffic models, the device might be inactive
                assert 0, f"How come my gNB {user.my_gnb.ID} is not in prepared ones at TTI = {self.simulation.TTI}?"

    def check_if_prepare_condition_is_satisfied(self, user, channel_matrix):
        if not self.check_user_can_rx_tx(user):
            # gNB received no measurement report from the UE
            return
            # target cell > serving cell + prep_offset; only for non prepared cells; prep_offset can be negative
        if self.get_num_are_and_being_prepared_gnbs(user) < self.num_top_gnbs + 1 or \
                len(user.currently_being_prep_cells_finish_time) == 0:
            # still can prepare some gNBs or no preparations are ongoing (hence, a gNB can be replaced).
            serving_rsrp = channel_matrix[user.ID, user.my_gnb.ID]
            for target_gnb in self.simulation.gNBs_per_scenario:
                if target_gnb not in user.prepared_gnbs and target_gnb not in user.currently_being_prep_cells_finish_time \
                        and target_gnb.ID != user.my_gnb.ID:
                    target_rsrp = channel_matrix[user.ID, target_gnb.ID]

                    if self.a3_prep_condition(serving_rsrp, target_rsrp) and not self.a5_prep_condition(serving_rsrp, target_rsrp):
                        # self.print_error(device, f"A33333 and not A5 s: {serving_rsrp}, t: {target_rsrp}")
                        self.handover_events_stats['a3 only'] += 1
                    elif self.a5_prep_condition(serving_rsrp, target_rsrp) and not self.a3_prep_condition(serving_rsrp, target_rsrp):
                        # self.print_error(device, f"A55555 and not A3 s: {serving_rsrp}, t: {target_rsrp}")
                        self.handover_events_stats['a5 only'] += 1
                    elif self.a3_prep_condition(serving_rsrp, target_rsrp) and self.a5_prep_condition(serving_rsrp, target_rsrp):
                        self.handover_events_stats['both'] += 1

                    if self.prep_condition(serving_rsrp, target_rsrp):
                        # admission, prep_time = self.handover_interruption.calc_handover_preparation_time(target_gnb)
                        if ConditionalHandoverParameters.with_ttt_prep:
                            # TTT in handover preparation
                            self.start_prep_ttt(user, target_gnb, channel_matrix)
                        else:
                            self.decide_to_replace_or_prepare(user, target_gnb, channel_matrix)
                    else:
                        if ConditionalHandoverParameters.with_ttt_prep:
                            self.remove_prep_ttt(user, target_gnb,)

    def start_prep_ttt(self, user, target_gnb, channel_matrix):
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        if target_gnb.ID in user.ttt_MR_finish and user.ttt_MR_finish[target_gnb.ID] <= current_time:
            del user.ttt_MR_finish[target_gnb.ID]
            self.decide_to_replace_or_prepare(user, target_gnb, channel_matrix)
        elif target_gnb.ID in user.ttt_MR_finish:
            user.ttt_MR_finish[target_gnb.ID] -= self.simulation.sim_params.TTI_duration
        elif target_gnb.ID not in user.ttt_MR_finish:
            user.ttt_MR_finish[target_gnb.ID] = current_time + HandoverParameters.ttt_prep

    def remove_prep_ttt(self, user, target_gnb,):
        if target_gnb.ID in user.ttt_MR_finish:
            del user.ttt_MR_finish[target_gnb.ID]

    def prep_condition(self, serving_rsrp, target_rsrp):
        if ConditionalHandoverParameters.event == 3:
            return self.a3_prep_condition(serving_rsrp, target_rsrp)
        elif ConditionalHandoverParameters.event == 5:
            return self.a5_prep_condition(serving_rsrp, target_rsrp)
        else:
            raise NotImplemented

    def a3_prep_condition(self, serving_rsrp, target_rsrp):
        if target_rsrp > serving_rsrp + ConditionalHandoverParameters.prep_offset:
            return True
        else:
            return False

    def a5_prep_condition(self, serving_rsrp, target_rsrp):
        if self.a2_condition(serving_rsrp) and self.a4_condition(target_rsrp):
            return True
        else:
            return False

    def a2_condition(self, serving_rsrp):
        # serving cell's signal becomes weaker than the threshold
        if serving_rsrp < ConditionalHandoverParameters.a2_rsrp_threshold:
            return True
        else:
            return False

    def a4_condition(self, target_rsrp):
        # Neighbor cell's signal becomes stronger than the threshold
        if target_rsrp > ConditionalHandoverParameters.a4_rsrp_threshold:
            return True
        else:
            return False

    def decide_to_replace_or_prepare(self, user, target_gnb, channel_matrix):
        if self.get_num_are_and_being_prepared_gnbs(user) < self.num_top_gnbs + 1:
            self.prepare_cho_handover(user, target_gnb)
        elif len(user.currently_being_prep_cells_finish_time) > 0:
            # one preparation is already ongoing and the num_top_gnbs is already reached
            return
        elif len(user.prepared_gnbs) == self.num_top_gnbs + 1:
            self.replace_gnb(channel_matrix, user, target_gnb)
        elif self.get_num_are_and_being_prepared_gnbs(user) == self.num_top_gnbs + 2:
            self.remove_worst_gnb_from_prepared(user, channel_matrix)
        else:
            assert 0, f"prepared gNBs: {len(user.prepared_gnbs)}, being prepared: {len(user.currently_being_prep_cells_finish_time)}"

    def remove_worst_gnb_from_prepared(self, user, channel_matrix):
        prepared_gnbs, prep_gnbs_channel = self.get_prepared_gnbs_and_their_channel(user, channel_matrix)
        position_of_min_channel_gnb = np.argmin(prep_gnbs_channel)  # not gNB's id
        remove_gnb = prepared_gnbs[position_of_min_channel_gnb]
        remove_gnb_channel = prep_gnbs_channel[position_of_min_channel_gnb]
        assert remove_gnb_channel == channel_matrix[user.ID, remove_gnb.ID]
        self.remove_user_from_gnb(user, self.simulation.gNBs_per_scenario[remove_gnb.ID])

    def replace_gnb(self, channel_matrix, user, target_gnb):
        prepared_gnbs, prep_gnbs_channel = self.get_prepared_gnbs_and_their_channel(user, channel_matrix)
        position_of_min_channel_gnb = np.argmin(prep_gnbs_channel)  # not gNB's id
        remove_gnb = prepared_gnbs[position_of_min_channel_gnb]
        remove_gnb_channel = prep_gnbs_channel[position_of_min_channel_gnb]

        channel_target = channel_matrix[user.ID, target_gnb.ID]
        assert remove_gnb_channel == channel_matrix[user.ID, remove_gnb.ID]
        if channel_target > remove_gnb_channel + ConditionalHandoverParameters.replace_offset:
            if user.my_gnb.ID != remove_gnb.ID and target_gnb.ID != remove_gnb.ID:
                assert remove_gnb.ID != user.my_gnb.ID and len(prepared_gnbs) > 1,\
                    f"Want to remove s-gNB {user.my_gnb.ID}, remove gNB {remove_gnb.ID}"

                self.remove_user_from_gnb(user, self.simulation.gNBs_per_scenario[remove_gnb.ID])
                self.prepare_cho_handover(user, target_gnb)
                msg = f"5. Replaced gNB {remove_gnb.ID} by {target_gnb.ID}: {remove_gnb_channel} --> {channel_target}. My gNB is {user.my_gnb.ID}"
                self.print_msg(user, msg, 'red')
                # self.print_prep_stats(device)

    def get_prepared_gnbs_and_their_channel(self, user, channel_matrix):
        prepared_gnbs = list(user.prepared_gnbs.keys())
        prep_gnbs_channel = [channel_matrix[user.ID, gnb.ID] for gnb in prepared_gnbs]
        return prepared_gnbs, prep_gnbs_channel

    def ensure_num_top_gnbs_are_prepared(self, user, channel_matrix):
        if self.get_num_are_and_being_prepared_gnbs(user) < self.num_top_gnbs + 1:
            best_gnb_ids_sorted = heapq.nlargest(self.num_top_gnbs+1, range(len(channel_matrix[user.ID, :])),
                                                 channel_matrix[user.ID, :].take)
            for gnb_id in best_gnb_ids_sorted:
                gnb = self.simulation.gNBs_per_scenario[gnb_id]
                if gnb not in user.prepared_gnbs and gnb not in user.currently_being_prep_cells_finish_time and gnb_id != user.my_gnb.ID:
                    self.prepare_cho_handover(user, gnb)
                    self.print_msg(user, f"Forced prep of gNB {gnb_id}", 'white')
                    # executed in the beginning or after a RLF
                    if self.get_num_are_and_being_prepared_gnbs(user) == self.num_top_gnbs + 1:
                        return 0
        assert self.get_num_are_and_being_prepared_gnbs(user) == self.num_top_gnbs + 1, self.get_num_are_and_being_prepared_gnbs(user)

    def prepare_cho_handover(self, user, target_gnb, prep_time_offset=0):
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        msg = f"\n1. Start gNB {target_gnb.ID} preparation for user {user.ID} at TTI={current_time}. Prep till {user.handover_prep_time_finish}. My gNB is {user.my_gnb.ID}."
        self.print_msg(user, msg, 'green')
        self.prepare_handover(user, target_gnb, prep_time_offset)
        assert target_gnb.ID != user.my_gnb.ID, "Preparing serving cell. Wrong"
        if target_gnb.ID == user.my_gnb.ID:
            assert 0
        user.currently_being_prep_cells_finish_time[target_gnb] = user.handover_prep_time_finish
        self.log_prepared_cells(target_gnb.ID)

    def check_if_preparation_finished(self, user):
        if not self.check_user_can_rx_tx(user):
            # s-gNB cannot let the device know that a target cell is prepared
            return
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        for gnb in list(user.currently_being_prep_cells_finish_time):
            if user.currently_being_prep_cells_finish_time[gnb] <= current_time:
                print(user.currently_being_prep_cells_finish_time)
                print(user.currently_being_prep_cells_finish_time[gnb])
                user.prepared_gnbs[gnb] = False
                del user.currently_being_prep_cells_finish_time[gnb]
                gnb.prepared_CHO_for_users.append(user)
                self.count_prepared_cells += 1

                msg = f"2. Finished preparation of gNB {gnb.ID} for user {user.ID} at TTI={current_time}. My gNB is {user.my_gnb.ID}"
                self.print_msg(user, msg, 'white')
                if gnb.ID == user.my_gnb.ID:
                    msg = "Prepared serving cell. WRONG."
                    self.print_error(user, msg)
                    self.print_prep_stats(user)
                    # assert 0
                    # might happen after RLF

    def check_if_execution_condition_is_satisfied(self, user, channel_matrix):
        # target cell > serving cell + execution offset; only for prepared cells
        for prep_cell in user.prepared_gnbs:
            if prep_cell.ID == user.my_gnb.ID:
                continue
            if self.condition_to_execute_handover(user, prep_cell, channel_matrix):
                current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
                if not ConditionalHandoverParameters.with_ttt_exec or \
                        (user.next_gnb and user.ttt_finish and user.ttt_finish <= current_time): # no TTT or TTT expired
                    msg = f"3. Executing handover to prepared gNB {prep_cell.ID} for user {user.ID} at TTI={current_time}. My gNB is {user.my_gnb.ID}"
                    self.print_msg(user, msg, 'magenta')
                    user.prepared_gnbs[prep_cell] = True
                    user.next_gnb = prep_cell
                    self.execute_handover(user)
                    return True
                elif user.ttt_finish and user.ttt_finish > current_time:
                    if user.next_gnb and user.next_gnb == prep_cell:
                        # same gNB is still good, so continue waiting for the TTT to expire
                        # return
                        pass
                    else:
                        user.next_gnb = prep_cell  # another gNB became better in the meanwhile
                        user.ttt_finish = None
                        msg = f"Restarted TTT for user {user.ID} and gNB {prep_cell.ID} at TTI = {self.simulation.TTI}"
                        self.print_msg(user, msg, 'red')
                        self.print_error(user, msg)
                elif not user.next_gnb:
                    user.next_gnb = prep_cell
                    self.start_ttt(user)
                    return

        return False

    def condition_to_execute_handover(self, user, prep_cell, channel_matrix):
        serving_rsrp = channel_matrix[user.ID, user.my_gnb.ID]
        prep_rsrp = channel_matrix[user.ID, prep_cell.ID]
        res = prep_rsrp > serving_rsrp + ConditionalHandoverParameters.exec_offset
        # msg = f"HO EXEC? RSRP {serving_rsrp} --> {prep_rsrp}. Res: {res}"
        # self.print_msg(device, msg, 'cyan')
        # src_sinr = self.ran_simulation.channel.average_SINR[device.ID, device.my_gnb.ID]
        # target_sinr = self.ran_simulation.channel.average_SINR[device.ID, prep_cell.ID]
        # msg = f"HO EXEC? SINR {src_sinr} --> {target_sinr}"
        # self.print_msg(device, msg, 'cyan')
        return res

    def check_if_execution_has_completed(self, user):
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        if user.hit_finish and user.hit_finish <= current_time:
            snr = self.simulation.channel.average_SINR[user.ID, user.my_gnb.ID]
            self.print_msg(user, f"Previous gNB's average SNR is {snr}", 'white')
            self.complete_handover(user)
            snr = self.simulation.channel.average_SINR[user.ID, user.my_gnb.ID]
            msg = f"4. UE {user.ID} completed a handover at TTI={current_time}. " \
                  f"My gNB is {user.my_gnb.ID} with average SINR = {snr} dB \n"
            self.print_msg(user, msg, 'white')
            return True
        return False

    def check_if_remove_prep_cell_at_ue(self, user, channel_matrix):
        if not self.check_user_can_rx_tx(user):
            # UE cannot send its measurement report to gNB
            return
        # only for target cells that have already been prepared
        for prep_cell in list(user.prepared_gnbs.keys()):
            if prep_cell.ID == user.my_gnb.ID:
                continue
            if self.condition_to_remove_gnb_satisfied(user, prep_cell, channel_matrix):
                if self.version == CHOVersions.max_top_gnbs_always_preped and \
                        self.get_num_are_and_being_prepared_gnbs(user) <= self.num_top_gnbs + 1:
                    return
                self.remove_user_from_gnb(user, prep_cell)

    def condition_to_remove_gnb_satisfied(self, user, prep_cell, channel_matrix):
        if user.my_gnb.ID == prep_cell.ID:
            assert 0, f"Removing serving gNB {user.my_gnb.ID} from the prepared cells"
        serving_rsrp = channel_matrix[user.ID, user.my_gnb.ID]
        rsrp_prep_cell = channel_matrix[user.ID, prep_cell.ID]
        return rsrp_prep_cell < serving_rsrp + ConditionalHandoverParameters.remove_offset

    def remove_user_from_gnb(self, user, prep_cell):
        used_prep_gnb_flag = user.prepared_gnbs[prep_cell]
        self.count_released_cells += 1
        if not used_prep_gnb_flag:
            self.count_prepared_but_not_used_cells += 1
        del user.prepared_gnbs[prep_cell]
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        free_resources_at_time = current_time + self.handover_interruption.calc_remove_prep_cell_at_gnb_latency()
        prep_cell.remove_prep_cells_at[user] = free_resources_at_time

        total_prep = self.get_num_are_and_being_prepared_gnbs(user)
        msg = f"Removing user {user.ID} from gNB {prep_cell.ID} at {free_resources_at_time}. " \
              f"My gNB is {user.my_gnb.ID}. Now={current_time}. Total prep {total_prep}"
        self.print_msg(user, msg, 'blue')

    def check_if_any_user_to_be_removed_from_prep_cell_list(self, user):
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        for gnb in self.simulation.gNBs_per_scenario:
            if user in list(gnb.remove_prep_cells_at):
                if current_time >= gnb.remove_prep_cells_at[user]:
                    gnb.prepared_CHO_for_users.remove(user)
                    del gnb.remove_prep_cells_at[user]
                    self.print_msg(user, f"Removed user {user.ID} from prep cell {gnb.ID}", 'white')

    def count_resource_reservation_duration(self, gnb):
        # called in scheduler coz there is a loop over gNBs
        for user in gnb.prepared_CHO_for_users:
            if user not in gnb.connected_devices:
                self.count_wasted_ttis_per_gnb[gnb.ID] += 1

    def print_handover_parameters(self):
        super().print_handover_parameters()
        print(tabulate([['prep_offset', ConditionalHandoverParameters.prep_offset],
                        ['exec_offset', ConditionalHandoverParameters.exec_offset],
                        ['remove_offset', ConditionalHandoverParameters.remove_offset],
                        ['replace_offset', ConditionalHandoverParameters.replace_offset],
                        # ['top gnb to prepare', self.num_top_gnbs],
                        ['with TTT Exec', ConditionalHandoverParameters.with_ttt_exec],
                        ['with TTT Prep', ConditionalHandoverParameters.with_ttt_prep],
                        ['TTT Exec', HandoverParameters.ttt_exec],
                        ['TTT Prep', HandoverParameters.ttt_prep],
                        ['Event', f"A{ConditionalHandoverParameters.event}"]
                        ],
                       headers=['CHO parameter', 'Value']))

        if "ECHO" in self.simulation.sim_params.handover_algorithm:
            print(tabulate([['top gnb to prepare', self.num_top_gnbs]]))

        if ConditionalHandoverParameters.with_ttt_prep:
            print(tabulate([['TTT Prep', HandoverParameters.ttt_prep]]))

        if ConditionalHandoverParameters.with_ttt_exec:
            print(tabulate([['TTT Exec', HandoverParameters.ttt_exec]]))


    def log_prepared_cells(self, gnb_id):
        if gnb_id not in self.simulation.save_results.prepared_cells_count_dict:
            self.simulation.save_results.prepared_cells_count_dict[gnb_id] = 1
        else:
            self.simulation.save_results.prepared_cells_count_dict[gnb_id] += 1
        self.prepared_cells_dict[self.simulation.TTI].append(gnb_id)

    def print_prep_stats(self, user):
        already_prepared = [gnb.ID for gnb in user.prepared_gnbs]
        being_prepared = [gnb.ID for gnb in user.currently_being_prep_cells_finish_time]
        print(f"Prepared:{already_prepared}, Preparing: {being_prepared}, my gNB {user.my_gnb.ID}", file=sys.stderr)
        for gnb in user.prepared_gnbs:
            print(f"RSRP {self.simulation.channel.average_RSRP[user.ID, gnb.ID]} dB (gNB {gnb.ID}, UE {user.ID})", file=sys.stderr)

    def sanity_checks(self, user):
        assert 0 < self.num_top_gnbs < len(self.simulation.gNBs_per_scenario), self.num_top_gnbs
        prepared = self.get_num_are_and_being_prepared_gnbs(user)
        assert prepared <= self.num_top_gnbs + 1, prepared
        if self.num_top_gnbs and prepared > self.num_top_gnbs + 1:
            self.print_prep_stats(user)
            assert 0

        elif self.num_top_gnbs and self.get_num_are_and_being_prepared_gnbs(user) < self.num_top_gnbs + 1:
            if self.version == CHOVersions.max_top_gnbs_always_preped:
                self.print_prep_stats(user)
                assert 0, f"Fewer gNBs are prepared than required: {user.prepared_gnbs}, {user.currently_being_prep_cells_finish_time}"
        assert self.get_num_are_and_being_prepared_gnbs(
            user) <= self.num_top_gnbs + 1, f"prepared gNBs: {len(user.prepared_gnbs)}, being prepared: {len(user.currently_being_prep_cells_finish_time)}"

        # if 'CHO' in self.ran_simulation.sim_params.handover_algorithm and self.ran_simulation.TTI > 60*10**3:
        #     prepared_gnbs = len(device.prepared_gnbs) + len(device.currently_being_prep_cells_finish_time)
        #     if prepared_gnbs != self.num_top_gnbs + 1 and CHOVersions.up_to_top_gnbs_prepared not in self.version:
        #         enable_print()
        #         print(f"Prepared {prepared_gnbs} != {self.num_top_gnbs+1} for device {device.ID}")
        #         self.print_prep_stats(device)
        #         assert 0  # fixme
