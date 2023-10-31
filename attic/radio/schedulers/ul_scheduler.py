from attic.radio.schedulers.schedulers_config import TIME_GRANULARITY, NUM_OF_RB_UL, RB_THROUGHPUT_UL, USE_RAN_SIMULATOR
from edge.util.Util import random_list_w_sum_1, random_list_w_fixed_sum


class UplinkScheduler:

    def __init__(self, bs_served, name="ul_scheduler", period=10, env=None):
        self.bs_served = bs_served
        self.name = name  # name of the scheduler
        self.period = TIME_GRANULARITY  # period in ms
        self.next_scheduling_time = TIME_GRANULARITY
        self.is_active = True
        self.env = env  # environment scheduler is running
        self.num_of_rb = NUM_OF_RB_UL
        self.rb_throughput = RB_THROUGHPUT_UL  # In bits
        self.total_throughput = self.num_of_rb * self.rb_throughput  # Total throughput of the base station in bits
        self.user_scheduling_requests = {}

    def set_env(self, env):
        self.env = env

    def schedule(self):
        while self.is_active:
            users_to_be_served = len(self.user_scheduling_requests.keys())
            messages_to_be_served = False

            for user in self.user_scheduling_requests.keys():
                for message_of_user in self.user_scheduling_requests[user]:
                    if message_of_user.remaining_bytes_to_send > 0:
                        messages_to_be_served = True
                        break

            if messages_to_be_served:
                counter = 0
                if USE_RAN_SIMULATOR:
                    rb_scheduling = random_list_w_fixed_sum(users_to_be_served, self.num_of_rb)
                    for user_being_served in self.user_scheduling_requests.keys():
                        if counter == users_to_be_served:
                            break

                        task_upload_shares = random_list_w_sum_1(len(self.user_scheduling_requests[user_being_served]))
                        j = 0
                        i = 0
                        while i < len(self.user_scheduling_requests[user_being_served]):
                            self.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send = \
                                max(self.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send -
                                    rb_scheduling[counter] * task_upload_shares[j], 0)

                            if self.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send == 0:
                                del self.user_scheduling_requests[user_being_served][i]
                                i -= 1

                            i += 1
                            j += 1
                        counter += 1

                else:
                    rb_scheduling = random_list_w_fixed_sum(users_to_be_served, self.num_of_rb)

                    for user_being_served in self.user_scheduling_requests.keys():
                        if counter == users_to_be_served:
                            break

                        task_upload_shares = random_list_w_sum_1(len(self.user_scheduling_requests[user_being_served]))
                        j = 0
                        i = 0
                        while i < len(self.user_scheduling_requests[user_being_served]):
                            self.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send = \
                                max(self.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send -
                                    rb_scheduling[counter] * self.rb_throughput * task_upload_shares[j], 0)

                            if self.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send == 0:
                                del self.user_scheduling_requests[user_being_served][i]
                                i -= 1

                            i += 1
                            j += 1
                        counter += 1

            self.next_scheduling_time += TIME_GRANULARITY
            yield self.env.timeout(self.period)

    def start_scheduler(self):
        self.env.process(self.schedule())


# class UplinkScheduler:
# 
#     def __init__(mec_simulation, bs_served, name="ul_scheduler", period=10, env=None):
#         mec_simulation.bs_served = bs_served
#         mec_simulation.name = name  # name of the scheduler
#         mec_simulation.period = TIME_GRANULARITY  # period in ms
#         mec_simulation.next_scheduling_time = TIME_GRANULARITY
#         mec_simulation.is_active = True
#         mec_simulation.env = env  # environment scheduler is running
#         mec_simulation.num_of_rb = NUM_OF_RB_UL
#         mec_simulation.rb_throughput = RB_THROUGHPUT_UL  # In bits
#         mec_simulation.total_throughput = mec_simulation.num_of_rb * mec_simulation.rb_throughput  # Total throughput of the base station in bits
#         mec_simulation.user_scheduling_requests = {}
#         mec_simulation.scheduling_dist = DeterministicDistribution(name='UL_Scheduling_Dist',time=TIME_GRANULARITY)
# 
#     def set_env(mec_simulation, env):
#         mec_simulation.env = env
# 
#     def schedule(mec_simulation):
#         while mec_simulation.is_active:
#             next_scheduling_time = mec_simulation.scheduling_dist.next()
#             yield mec_simulation.env.timeout(next_scheduling_time)
#             users_to_be_served = len(mec_simulation.user_scheduling_requests.keys())
#             messages_to_be_served = False
# 
#             for device in mec_simulation.user_scheduling_requests.keys():
#                 for message_of_user in mec_simulation.user_scheduling_requests[device]:
#                     if message_of_user.remaining_bytes_to_send > 0:
#                         messages_to_be_served = True
#                         break
# 
#             if messages_to_be_served:
#                 counter = 0
#                 if USE_RAN_SIMULATOR:
#                     rb_scheduling = random_list_w_fixed_sum(users_to_be_served, mec_simulation.num_of_rb)
#                     for user_being_served in mec_simulation.user_scheduling_requests.keys():
#                         if counter == users_to_be_served:
#                             break
# 
#                         task_upload_shares = random_list_w_sum_1(len(mec_simulation.user_scheduling_requests[user_being_served]))
#                         j = 0
#                         i = 0
#                         while i < len(mec_simulation.user_scheduling_requests[user_being_served]):
#                             mec_simulation.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send = \
#                                 max(mec_simulation.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send -
#                                     rb_scheduling[counter] * task_upload_shares[j], 0)
# 
#                             if mec_simulation.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send == 0:
#                                 del mec_simulation.user_scheduling_requests[user_being_served][i]
#                                 i -= 1
# 
#                             i += 1
#                             j += 1
#                         counter += 1
# 
#                 else:
#                     rb_scheduling = random_list_w_fixed_sum(users_to_be_served, mec_simulation.num_of_rb)
# 
#                     for user_being_served in mec_simulation.user_scheduling_requests.keys():
#                         if counter == users_to_be_served:
#                             break
# 
#                         task_upload_shares = random_list_w_sum_1(len(mec_simulation.user_scheduling_requests[user_being_served]))
#                         j = 0
#                         i = 0
#                         while i < len(mec_simulation.user_scheduling_requests[user_being_served]):
#                             mec_simulation.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send = \
#                                 max(mec_simulation.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send -
#                                     rb_scheduling[counter] * mec_simulation.rb_throughput * task_upload_shares[j], 0)
# 
#                             if mec_simulation.user_scheduling_requests[user_being_served][i].remaining_bytes_to_send == 0:
#                                 del mec_simulation.user_scheduling_requests[user_being_served][i]
#                                 i -= 1
# 
#                             i += 1
#                             j += 1
#                         counter += 1
# 
#             mec_simulation.next_scheduling_time += TIME_GRANULARITY
# 
#     def start_scheduler(mec_simulation):
#         mec_simulation.env.process(mec_simulation.schedule())
        
        

