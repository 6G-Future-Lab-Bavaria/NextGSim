import numpy as np
import sys
from collections import defaultdict
from termcolor import colored
from runtime.data_classes import States, HandoverParameters, ConditionalHandoverParameters


# todo: Fast recovery from RLF if the cell is already prepared (in case of CHO)


class MonitorRLF:
    def __init__(self, simulation):
        self.simulation = simulation
        self.rlf_dict = defaultdict(list)
        self.num_rlf = 0
        self.rlf_at_position = []
        self.rlf_per_user = defaultdict(int)
        self.not_connected_users_due_to_rlf_till = {}

    def check_if_rlf(self, user):
        # Radio Link Failure timer (T310) is started when DL SINR < Qout. RLF is detected when the timer expires.
        # If during this timer, the UE's SINR > Qin, the timer stops.
        if user.state == States.rrc_connected:
            snr = self.simulation.channel.average_SINR[user.ID, user.my_gnb.ID]  # average or measured? fixme
            current_time = self.simulation.TTI  # * self.ran_simulation.sim_params
            if user.rlf_finish_timer is None and snr <= HandoverParameters.Qout:
                user.rlf_finish_timer = current_time + HandoverParameters.Qin_duration
                msg = f"\nStart RLF timer for UE {user.ID} with gNB {user.my_gnb.ID} snr = {snr} at TTI {current_time}, " \
                      f"RLF Timer Finish Time = {user.rlf_finish_timer}"
                self.print_msg(user, msg, 'white')

            elif snr > HandoverParameters.Qin:
                user.rlf_finish_timer = None

            # time left till connect must be divisible by TTI_duration, otherwise UE stays longer non-connected.
            elif user.rlf_finish_timer and user.rlf_finish_timer <= current_time:
                msg = f"User {user.ID}: RLF with gNB {user.my_gnb.ID} snr = {snr} at TTI {current_time}, " \
                      f"HO prep {user.handover_prep_time_finish}, HIT {user.hit_finish}\n"
                self.print_msg(user, msg, 'red')

                self.sanity_check_user_connected_to_best_cell(user)

                try:
                    user.my_gnb.connected_devices.remove(user)
                    self.rlf_dict[self.simulation.TTI].append(user.ID)
                    self.num_rlf += 1
                    self.rlf_per_user[user.ID] += 2
                    self.simulation.save_results.add_to_current_num_rlfs()
                except ValueError as e:
                    print(f"UE {user.handover_t304_finish}, {user.hit_finish}, {user.next_gnb}", file=sys.stderr)
                    self.simulation.handover.check_if_hof(user)
                    self.simulation.handover.log_hof(user)  # ToDo: HOF
                    print(e, file=sys.stderr)
                    assert 0, "HOF???"
                # Do not remove the gNB if RLF, network might not know about it,
                # and the UE might do fast RLF recovery to one of the prepared gNBs
                # self.ran_simulation.handover.remove_user_from_gnb(device, device.my_gnb)
                user.state = States.rrc_idle
                time_left_till_connect = \
                    self.simulation.handover.handover_interruption.calc_time_to_reconnect_after_failure()
                self.not_connected_users_due_to_rlf_till[user] = current_time + time_left_till_connect
                user.my_gnb = None
            # elif device.rlf_finish_timer:
            #     enable_print()
            #     self.print_msg(device, f"RLF Timer is running {device.rlf_finish_timer} > {current_time}", 'white')
            #     block_print(True)
            #     self.ran_simulation.handover.print_prep_stats(device)

    def reconnect_in_case_failure(self):
        # It has to run every TTI (TTI does not have to be 1 ms, but has to be small)
        for user in list(self.not_connected_users_due_to_rlf_till.keys()):
            if user.state != States.rrc_connected and ~self.simulation.sim_params.traffic_model:
                # all users must be connected
                time_to_reconnect = self.not_connected_users_due_to_rlf_till[user]
                current_time = self.simulation.TTI  # *self.ran_simulation.sim_params.TTI_duration
                if time_to_reconnect <= current_time:
                    user.state = States.rrc_connected
                    del self.not_connected_users_due_to_rlf_till[user]
                    self.simulation.handover.set_handover_params_to_default(user)
                    self.select_cell_after_rlf(user)
                    msg = f"Reconnected device after RLF to {user.my_gnb.ID} at {self.simulation.TTI}"
                    self.print_msg(user, msg, 'white')
                    # for CHO only
                    user.prepared_gnbs[user.my_gnb] = True
                    user.my_gnb.prepared_CHO_for_users.append(user)
                    self.rlf_at_position.append([user.x, user.y])
            elif user.state != States.rrc_connected and self.simulation.sim_params.traffic_model:
                raise NotImplementedError("Check if device has something to Tx, if so, connect this device")

    def select_cell_after_rlf(self, user):
        # try fast re-connection to a prepared gNB (device does not know about being prepared gNBs)
        best_gnb_id = np.argmax(user.prepared_gnbs, axis=0)
        snr = self.simulation.channel.average_SINR[user.ID, best_gnb_id]
        if snr > HandoverParameters.Qin:
            # good, fast RLF recovery is possible
            # todo: add shorter latency here, can reconnect faster
            pass
        else:
            # if no good prepared gNBs, select any
            best_gnb_id = np.argmax(self.simulation.channel.measured_SINR[user.ID, :], axis=0)
        user.my_gnb = self.simulation.gNBs_per_scenario[best_gnb_id]
        if user is not user.my_gnb.connected_devices:
            user.my_gnb.connected_devices.append(user)
        if 'CHO' in self.simulation.sim_params.handover_algorithm:
            if user.my_gnb not in user.prepared_gnbs and self.simulation.handover.get_num_are_and_being_prepared_gnbs(
                    user) \
                    >= self.simulation.sim_params.num_top_gnbs + 1:
                self.simulation.handover.remove_worst_gnb_from_prepared(user, self.simulation.channel.average_RSRP)
                self.print_error(user, f"Reconnecting after RLF: removed one gNB from prepared cells")
                # self.print_error(device, f"Number of prepared cells is {self.ran_simulation.handover.get_num_are_and_being_prepared_gnbs(device)}")

    def sanity_check_user_connected_to_best_cell(self, user):
        # Must be called after handovers are performed.
        if self.simulation.sim_params.with_sanity_checks:
            self.assert_there_is_no_better_prepared_gnb_for_ue(user)
            # self.assert_there_is_no_better_gnb_at_all_for_ue(device)

    def assert_there_is_no_better_prepared_gnb_for_ue(self, user):
        if user.state != States.rrc_connected:
            return
        prepared_gnbs, prep_gnbs_sinr = \
            self.simulation.handover.get_prepared_gnbs_and_their_channel(user, self.simulation.channel.average_SINR)
        if len(prepared_gnbs) != self.simulation.handover.num_top_gnbs + 1:
            assert 'RLF and not enough cells are prepared'
        # Check that there is no better prepared gNB for the device (RSRP-based).
        sinr_serving = self.simulation.channel.average_SINR[user.ID, user.my_gnb.ID]
        rsrp_serving = self.simulation.channel.average_RSRP[user.ID, user.my_gnb.ID]
        for gnb, sinr in zip(prepared_gnbs, prep_gnbs_sinr):
            rsrp = self.simulation.channel.average_RSRP[user.ID, gnb.ID]
            if rsrp > rsrp_serving + ConditionalHandoverParameters.exec_offset:
                msg = f"RSRP sgNB = {rsrp_serving} and target {rsrp}"
                current_time = self.simulation.TTI  # * self.ran_simulation.sim_params.TTI_duration
                if user.hit_finish and user.hit_finish > current_time:  # a handover to a better cell is ongoing
                    return

                # check if device has just finished a handover (HIT = 15 ms)
                # although why a device started making a handover to a worse cell? Channel might have been updated.
                # todo: check why device makes a handover to a gNB with worse SINR?
                hit = self.simulation.handover.handover_interruption.calc_handover_interruption(user.next_gnb)
                hit = np.ceil(hit)
                handover_time = current_time - hit
                if handover_time in self.simulation.handover.who_made_handovers:
                    users = self.simulation.handover.who_made_handovers[handover_time]
                    if user.ID in users:
                        return
                self.print_error(user, msg)
                assert 0, f"gNB {gnb.ID}'s SINR = {sinr} dB. My gNB is {user.my_gnb.ID} and has sinr {sinr_serving} dB"
                # If hit here, why did not make a handover before?

    def assert_there_is_no_better_gnb_at_all_for_ue(self, user):
        if user.state != States.rrc_connected:
            return
        rsrp_serving = self.simulation.channel.average_RSRP[user.ID, user.my_gnb.ID]
        # Check that there is no better gNB for the device at all.
        for gnb in self.simulation.gNBs_per_scenario:
            if gnb in user.prepared_gnbs:
                continue
            rsrp = self.simulation.channel.average_RSRP[user.ID, gnb.ID]
            if rsrp > rsrp_serving + ConditionalHandoverParameters.exec_offset + 0.1:
                msg = f"RSRP sgNB = {rsrp_serving} and target {rsrp}"
                self.print_msg(user, msg, 'white')
                # self.ran_simulation.handover.print_prep_stats(device)
                for currently_being_prepared in user.currently_being_prep_cells_finish_time:
                    rsrp_curr_prepared = self.simulation.channel.average_RSRP[user.ID, currently_being_prepared.ID]
                    if rsrp_serving > rsrp_curr_prepared + ConditionalHandoverParameters.exec_offset:
                        return
                    assert 0, f"Prepared gNb {currently_being_prepared.ID}: {rsrp_curr_prepared} vs. serving gNb {user.my_gnb.ID}: {rsrp_serving}"
                    # if hit here, why did not prepare a better gNB at this TTI before calling RLF functions?

    def handover_recovery_procedure(self, user):
        # device performs a cell selection and attempts an RRC connection reestablishment procedure
        # Paper: Faster Recovery From RLF During Handover, 2020
        pass

    def print_msg(self, user, msg, color):
        print(colored(msg, color))

    def print_error(self, user, msg):
        print(msg, file=sys.stderr)
