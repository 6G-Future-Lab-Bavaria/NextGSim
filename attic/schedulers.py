from util.util import random_list_w_sum_1, random_list_w_fixed_sum

TIME_GRANULARITY = 4
USERS_PER_BS = 1
NUM_OF_RB_DL = 10
RB_THROUGHPUT_DL = 100000
NUM_OF_RB_UL = 20
RB_THROUGHPUT_UL = 100000
USE_RAN_SIMULATOR = False


class DownlinkScheduler:

    def __init__(self, bs_served, name="dl_scheduler", env=None, bs_id=None):
        self.bs_served = bs_served
        self.name = name  # name of the scheduler
        self.bs_id = bs_id
        self.period = TIME_GRANULARITY  # period in ms
        self.next_scheduling_time = TIME_GRANULARITY
        self.is_active = True
        self.env = env  # environment scheduler is running
        self.num_of_rb = NUM_OF_RB_DL
        self.rb_throughput = RB_THROUGHPUT_DL  # In num_of_bytes
        self.total_throughput = self.num_of_rb * self.rb_throughput  # Total throughput of the base station in num_of_bytes
        self.user_scheduling_requests = {}

    def set_env(self, env):
        self.env = env

    def schedule(self):
        while self.is_active:
            yield self.env.timeout(self.period)
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
                    print('None')
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

    def start_scheduler(self):
        self.env.process(self.schedule())


class UplinkScheduler:

    def __init__(self, bs_served, name="ul_scheduler", period=10, env=None):
        self.bs_served = bs_served
        self.name = name  # name of the scheduler
        self.period = TIME_GRANULARITY  # period in ms
        self.next_scheduling_time = TIME_GRANULARITY
        self.is_active = True
        self.env = env  # environment scheduler is running
        self.num_of_rb = NUM_OF_RB_UL
        self.rb_throughput = RB_THROUGHPUT_UL  # In num_of_bytes
        self.total_throughput = self.num_of_rb * self.rb_throughput  # Total throughput of the base station in num_of_bytes
        self.user_scheduling_requests = {}

    def set_env(self, env):
        self.env = env

    def schedule(self):
        while self.is_active:
            yield self.env.timeout(self.period)
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

    def start_scheduler(self):
        self.env.process(self.schedule())


class ProcessingScheduler:

    def __init__(self, name="processing_scheduler", period=10, env=None):
        self.name = name  # name of the scheduler
        self.period = TIME_GRANULARITY  # period in ms
        self.is_active = True
        self.env = env  # environment scheduler is running

    def blink(self):
        while self.is_active:
            yield self.env.timeout(TIME_GRANULARITY)
            print("Processing Scheduler is active at (T: %d)" % self.env.now)

    def start_scheduler(self):
        self.env.process(self.blink())
