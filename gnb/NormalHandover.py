import numpy as np
from tabulate import tabulate
from runtime.data_classes import States, HandoverParameters
from gnb.Handover import Handover


# This is a 5G handover: make before break, so the device is scheduled during handover preparation time.
# User is not scheduled during handover interruption time because device has to detach and perform RACH to the target cell
class NormalHandover(Handover):
    def __init__(self, simulation):
        super().__init__(simulation)
        self.version = ''

    def main_handover_function(self, user):
        if user.state != States.rrc_connected:
            return
        super().main_handover_function(user)
        channel_matrix = self.select_channel_metric_to_use(self.simulation.channel.average_SINR,
                                                           self.simulation.channel.average_RSRP)
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        if user.handover_prep_time_finish and user.handover_prep_time_finish > current_time:
            # print(f"User {device.ID} is waiting for the SBS to prepare a handover to {device.next_gnb.ID} "
            #       f"at TTI = {current_time}")
            return  # without return? can still request a new handover, maybe too complicated
        if user.hit_finish and user.hit_finish > current_time:
            # print(f"User {device.ID} is making a HO to {device.next_gnb.ID} at {device.hit_finish}, TTI = {current_time}")
            return
        if user.handover_prep_is_ongoing and user.handover_prep_time_finish <= current_time:
            print(f"3. User {user.ID} is executing a handover to gNB {user.next_gnb.ID} at TTI={current_time}. "
                  f"Prep waiting has expired")
            self.execute_handover(user)
            return
        if user.hit_finish and user.hit_finish <= current_time:
            # UE completed handover (reset parameters)
            print(f"4. UE {user.ID} completed a handover at {current_time}")
            self.complete_handover(user)
            return

        # determine the target gNB
        mean_channel_per_gnb = channel_matrix[user.ID, :]
        best_gnb_id = np.argmax(mean_channel_per_gnb)
        best_channel = mean_channel_per_gnb[best_gnb_id]
        if user.my_gnb.ID != best_gnb_id and best_channel > channel_matrix[user.ID, user.my_gnb.ID] \
                + HandoverParameters.a3_offset:
            # if there is a BS with a larger SINR/RSRP by an offset
            # start handover counter TTT
            if user.next_gnb is None or user.next_gnb.ID != best_gnb_id:
                user.next_gnb = self.simulation.gNBs_per_scenario[best_gnb_id]
                user.ttt_finish = current_time + HandoverParameters.ttt_exec
                print(f"\n1. Start TTT timer for user {user.ID} at TTI = {current_time}")
            # elif device.next_gnb.ID == best_gnb_id:
                # self.log(f"Continue: For device {device.ID} gnb {best_gnb_id} is better than gnb {device.my_gnb.ID}")
            elif user.ttt_finish and current_time >= user.ttt_finish:
                self.prepare_handover(user, user.next_gnb)
                print(f"2. TTT timer has expired for user {user.ID} at TTI = {current_time}. "
                      f"Prep waiting is till {user.handover_prep_time_finish}")
                # elif device.ttt_handover_timer < current_time:
                #     assert 0, "Should have made a handover at the previous TTI or" \
                #               "maybe was rejected by the taregt gNB"
        else:
            if user.next_gnb:
                print(f"Setting next_gnb to None  at TTI = {current_time} \n")
            user.next_gnb = None
            user.ttt_finish = None

    def execute_handover(self, user):
        super().execute_handover(user)
        self.start_ttt(user)
        print(f"HIT till {user.hit_finish} at TTI= {self.simulation.TTI}")

    def print_handover_parameters(self):
        super().print_handover_parameters()
        print(tabulate([['TTT handover timer', HandoverParameters.ttt_exec],
                        ['A3 offset', HandoverParameters.a3_offset],
                        ['Qout', HandoverParameters.Qout],
                        ['Qin duration', HandoverParameters.Qin_duration],
                        ['Qin', HandoverParameters.Qin],
                        ['HOF T304 timer', HandoverParameters.handover_hof_t304_timer]
                        ],
                       headers=['NHO Parameter', 'Value']))

