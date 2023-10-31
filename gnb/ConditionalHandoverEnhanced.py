import sys
import numpy as np
import heapq
from gnb.ConditionalHandover import ConditionalHandover
from runtime.data_classes import MeasurementParams, ECHOVersions, ConditionalHandoverParameters, HandoverAlgorithms


class ConditionalHandoverEnhanced(ConditionalHandover):
    def __init__(self, simulation):
        super().__init__(simulation)
        # self.required_time_handover = self._calc_time_required_for_handover()  # ms
        self.delay_predicted_gnb_preparation = False  # till next update_ue_position_gap  # fixme
        self.version = ECHOVersions.distance_based_one_macro
        self.known_trajectory = None
        self.X_mobility = None
        self.Y_mobility = None
        self.next_distances = None
        self.look_ahead_cur = None
        self.current_time_for_pos = 0
        self.x_next = {}
        self.y_next = {}
        if ConditionalHandoverParameters.with_ttt_exec:
            self.version += '_TTT'

    def check_if_prepare_condition_is_satisfied(self, user, channel_matrix):
        if not self.check_user_can_rx_tx(user):
            # gNB received no measurement report from the UE
            return
        user.best_next_gnb_ids = self.find_best_next_gnbs(user)
        for gnb_id in user.best_next_gnb_ids:
            if gnb_id == user.my_gnb.ID:
                continue
            target_gnb = self.simulation.gNBs_per_scenario[gnb_id]
            if target_gnb in user.prepared_gnbs or target_gnb in user.currently_being_prep_cells_finish_time:
                # this gNB is already prepared or being prepared
                continue
            else:
                if self.delay_predicted_gnb_preparation:
                    current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
                    handover_must_start_at = self.simulation.TTI + MeasurementParams.update_ue_position_gap
                    ho_prep_time = self.handover_interruption.calc_handover_preparation_time(None)[1]
                    # hit_prep = self.handover_interruption.calc_handover_interruption(None)
                    prep_time_offset = handover_must_start_at - current_time - ho_prep_time
                    raise NotImplemented("Delayed gNB preparation must be passed to the next function")
                else:
                    prep_time_offset = 0

                # if self.get_num_are_and_being_prepared_gnbs(device) < self.num_top_gnbs + 1:
                #     self.prepare_cho_handover(device, target_gnb)
                # else:
                #     self.replace_gnb(channel_matrix, device, target_gnb)
                self.decide_to_replace_or_prepare(user, target_gnb, channel_matrix)
        assert self.get_num_are_and_being_prepared_gnbs(user) != self.num_top_gnbs, \
            f"prepared gNBs: {len(user.prepared_gnbs)}, being prepared: {len(user.currently_being_prep_cells_finish_time)}"

    def set_next_predicted_position(self, user):
        if self.simulation.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_look_ahead:
            return self.set_next_predicted_position_look_ahead()
        if self.simulation.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_current_pos:
            user.x_next = user.x
            user.y_next = user.y
        else:
            user.x_next, user.y_next = self._make_prediciton(user)
            # # fixme: added an error to the predicted position
            # device.x_next += np.random.choice([-2, 2])
            # device.y_next += np.random.choice([-2, 2])

        _, self.next_distances, = self.simulation.channel.calc_distance_btw_users_gnbs(True)
        self.sanity_check_current_and_next_positions_are_different(user)

    def set_next_predicted_position_look_ahead(self):
        if self.simulation.sim_params.handover_algorithm in \
                [HandoverAlgorithms.echo_with_look_ahead, HandoverAlgorithms.echo_with_current_look_ahead] \
                and self.simulation.TTI % MeasurementParams.update_ue_position_gap == 0:
            pass
        else:
            return
        if self.look_ahead_cur is None or self.look_ahead_cur == self.simulation.sim_params.look_ahead:
            self._make_prediciton_look_ahead()
            self.look_ahead_cur = 0
        for user in self.simulation.devices_per_scenario:
            user.x_next = self.x_next[user.ID][self.look_ahead_cur]
            user.y_next = self.y_next[user.ID][self.look_ahead_cur]

            # if self.ran_simulation.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_look_ahead:
            #     self.positions_look_ahead.append((device.x_next, device.y_next))
            # elif self.ran_simulation.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_current_look_ahead:
            #     self.positions_current.append((device.x_next, device.y_next))

        _, self.next_distances, = self.simulation.channel.calc_distance_btw_users_gnbs(True)
        self.look_ahead_cur += 1

    def find_best_next_gnbs(self, user):
        if ECHOVersions.distance_based in self.version:
            assert 0  # many RLFs because often only macro gNBs are prepared, thus. device gets out of coverage
            return self.find_closest_next_gnbs(user)
        elif ECHOVersions.distance_based_one_macro in self.version:
            # return self.find_closest_next_gnbs_one_macro(device)
            # return self.find_closest_next_gnbs(device)  # fixme:
            return self.find_gnbs_that_cover_ue(user)
        else:
            raise NotImplemented(f"Not implemented how to find best gNBs for this ECHO version {self.version}")

    def find_gnbs_that_cover_ue(self, user):
        # first find gNBs that could serve the device, namely, ue is in their coverage area
        # next, select the closest gNB among gnbs that could serve device
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        coverage = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        good_gnbs = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        macro_r = 530
        micro_r = 110
        coverage[:num_macro_gnbs] = macro_r
        coverage[num_macro_gnbs:] = micro_r
        mask = self.next_distances[user.ID] < coverage
        good_gnbs[mask] = 1
        # print(self.next_distances[device.ID])
        # print(good_gnbs)
        coverage_gnb_ids = np.where(good_gnbs == 1)[1]
        # print(coverage_gnb_ids)
        # print(self.next_distances[device.ID])
        # print("****")
        distances = self.next_distances[user.ID].take(coverage_gnb_ids, axis=0)
        # sort coverage_gnb_ids based on proximity to the device
        distances, best_gnb_ids = zip(*sorted(zip(list(distances),list(coverage_gnb_ids))))
        # print(distances)
        # print(best_gnb_ids)
        return best_gnb_ids[:self.num_top_gnbs + 1]  # select top gNBs

    def find_closest_next_gnbs(self, user):
        best_gnb_ids = heapq.nsmallest(self.num_top_gnbs+1, range(len(self.next_distances[user.ID])),
                                       self.next_distances[user.ID].take)
        return best_gnb_ids

    def find_closest_next_gnbs_one_macro(self, user):
        macro = self.find_closed_macro_gnb(user)
        micros = self.find_closed_micro_gnbs(user, self.num_top_gnbs + 1)
        if macro in micros:
            return micros
        else:
            best_gnbs_ids = [macro]
            best_gnbs_ids.extend(micros)
            return best_gnbs_ids

    def _make_prediciton(self, user):
        positon_index = int(self.simulation.TTI / MeasurementParams.update_ue_position_gap)  #+ 1  # alredy the next position
        if positon_index >= len(self.simulation.X_mobility[user.ID]):  # last position
            return user.x_next, user.y_next
        if self.known_trajectory:
            x_next = self.simulation.X_mobility[user.ID][positon_index]
            y_next = self.simulation.Y_mobility[user.ID][positon_index]
        else:
            x_next = self.X_mobility[user.ID][positon_index]
            y_next = self.Y_mobility[user.ID][positon_index]
            # assert x_next != self.ran_simulation.X_mobility[device.ID][positon_index]
            # assert y_next != self.ran_simulation.Y_mobility[device.ID][positon_index]
            diff_x = abs(x_next - self.X_mobility[user.ID][positon_index-1])
            diff_y = abs(y_next - self.Y_mobility[user.ID][positon_index-1])
            # predictions, hence, the difference can be large due to the error
            # if diff_x > 10 or diff_y > 10:
            #     print(f"Predicted position: device moved {diff_x} m along X, {diff_y} along Y", file=sys.stderr)
        return x_next, y_next

    def _make_prediciton_look_ahead(self):
        position_index = int(self.simulation.TTI / MeasurementParams.update_ue_position_gap)  # already the next pos
        for user in self.simulation.devices_per_scenario:
            if self.known_trajectory:
                self.x_next[user.ID] = self.simulation.X_mobility[user.ID][position_index]
                self.y_next[user.ID] = self.simulation.Y_mobility[user.ID][position_index]
            elif self.simulation.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_current_look_ahead:
                self.x_next[user.ID] = [user.x] * self.simulation.sim_params.look_ahead
                self.y_next[user.ID] = [user.y] * self.simulation.sim_params.look_ahead
            else:
                self.x_next[user.ID] = self.X_mobility[user.ID][position_index]
                self.y_next[user.ID] = self.Y_mobility[user.ID][position_index]

    def condition_to_execute_handover(self, user, prep_cell, channel_matrix):
        if self.version == ECHOVersions.force_closed_micro:
            serving_rsrp = channel_matrix[user.ID, user.my_gnb.ID]
            prep_rsrp = channel_matrix[user.ID, prep_cell.ID]
            offset = 15
            if prep_cell.type == 'micro':
                prep_rsrp += offset
            elif user.my_gnb.type == 'micro':
                serving_rsrp += offset
            assert 0
            return prep_rsrp > serving_rsrp + ConditionalHandoverParameters.exec_offset
        else:
            return super().condition_to_execute_handover(user, prep_cell, channel_matrix)

    def check_if_remove_prep_cell_at_ue(self, user, channel_matrix):
        pass

    def condition_to_remove_gnb_satisfied(self, user, prep_cell, channel_matrix):
        # return prep_cell.ID not in device.best_next_gnb_ids and prep_cell.ID != device.my_gnb.ID and prep_cell != device.next_gnb
        return False  # fixme

    # def _calc_time_required_for_handover(self):
    #     ho_prep_time = self.handover_interruption.calc_handover_preparation_time(None)[1]
    #     hit_prep = self.handover_interruption.calc_handover_interruption(None)
    #     return ho_prep_time + hit_prep

    def find_closed_macro_gnb(self, user):
        total_num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        distances = self.next_distances[user.ID][:total_num_macro_gnbs]
        closed_macro_gnb = np.argmin(distances)
        return closed_macro_gnb

    def find_closed_micro_gnbs(self, user, num):
        total_num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        distances = self.next_distances[user.ID][total_num_macro_gnbs:]
        res = heapq.nsmallest(num, range(len(distances)), distances.take)
        closed_macro_gnb = [val + total_num_macro_gnbs for val in res]
        return closed_macro_gnb

    def sanity_check_current_and_next_positions_are_different(self, user):
        if self.simulation.sim_params.with_sanity_checks:
            if len(self.simulation.devices_per_scenario) > 5 and self.simulation.TTI > 10**4:
                # if there are many users, at least some of them, must have moved, thus, the positions must be different.
                try:
                    assert not np.array_equal(self.next_distances, self.simulation.channel.distance_users_gnbs_3d)
                    assert (self.next_distances != self.simulation.channel.distance_users_gnbs_3d).any()
                except:
                    print(self.next_distances is self.simulation.channel.distance_users_gnbs_3d, file=sys.stderr)
                    print(self.next_distances, file=sys.stderr)
                    print("\n")
                    print(self.simulation.channel.distance_users_gnbs_3d, file=sys.stderr)
