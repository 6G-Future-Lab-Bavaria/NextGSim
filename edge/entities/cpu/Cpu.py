import copy
import csv
import math
from edge.entities.Entity import Entity
from runtime.utilities import utility
from definitions import RESULTS_DIR

CPU_LIST = []


class Cpu(Entity):
    def __init__(self, num_of_cores=1, model="cpu", clock_speed=3.1 * 10 ** 6, host_entity=None):
        super().__init__(model)
        self.clock_speed = clock_speed
        self.running_processes = []
        # self.reserved_cpu_time_per_process = {}
        self.num_of_cores = num_of_cores
        self.available_share = num_of_cores
        self.host_entity = host_entity
        CPU_LIST.append(self)

    def deploy_service(self, service):
        self.available_share -= service.request_cpu_share
        # self.reserved_cpu_time_per_process[service.process_id] = service.request_cpu_share
        self.running_processes.append(service)

    def release_service(self, service):
        self.available_share += service.request_cpu_share
        # del self.reserved_cpu_time_per_process[service.process_id]
        self.running_processes.remove(service)

    def start_processing(self, mec_simulation):
        mec_simulation.env.process(self.__start_processing(mec_simulation))

    def __start_processing(self, mec_simulation):
        main_simulation = mec_simulation.main_simulation
        computing_period = main_simulation.sim_params.computing_period
        while not mec_simulation.stop:
            yield mec_simulation.env.timeout(computing_period)
            processed_messages = []
            # cpu_utilization = 1 - (self.available_share / self.num_of_cores)
            for process in self.running_processes:
                for thread_queue in process.processing_queue:
                    cpu_time = process.request_cpu_share * computing_period
                    if process.radio_aware:
                        average_radio_latencies_of_users = process.get_average_radio_latency()
                        print("PROCESS NAME")
                        print(process.name)
                        print("THREAD QUEUE")
                        print(thread_queue)
                        thread_queue = sorted(thread_queue,
                                              key=lambda message: message.sequence_number,
                                              reverse=False)

                        thread_queue = sorted(thread_queue,
                                              key=lambda message: (
                                                  average_radio_latencies_of_users[message.user_id] if
                                                  message.user_id in average_radio_latencies_of_users else 0),
                                              reverse=True)

                        # while latency_aware_thread_queue:
                        #     message = latency_aware_thread_queue.pop(0)
                        #     time_to_complete_task = round(
                        #         message.remaining_instructions_to_compute / (
                        #                 process.request_cpu_share * self.clock_speed),
                        #         2)
                        #
                        #     if time_to_complete_task <= cpu_time:
                        #         message.remaining_instructions_to_compute = 0
                        #         cpu_time -= time_to_complete_task
                        #         message.processing_time_of_message = mec_simulation.env.now - message.start_of_processing + computing_period - cpu_time
                        #         message.latency_experienced = mec_simulation.env.now - message.entry_time_to_backhaul + message.ul_latency + \
                        #                                       (computing_period - cpu_time)
                        #         process.update_average_processing_latency(message.processing_time_of_message)
                        #         thread_queue.remove(message)
                        #         processed_messages.append(message)
                        #         if process.output_messages:
                        #             for tmp_msg in process.output_messages:
                        #                 output_message = copy.copy(tmp_msg)
                        #                 output_message.sequence_number = message.sequence_number
                        #                 output_message.user_id = message.user_id
                        #                 process.message_send_queue.put(output_message)
                        #
                        #         mec_simulation.messages_in_the_backhaul.remove(message)
                        #
                        #     else:
                        #         message.remaining_instructions_to_compute -= cpu_time * self.clock_speed
                        #         message.latency_experienced = mec_simulation.env.now - message.entry_time_to_backhaul + message.ul_latency + \
                        #                                       (computing_period - cpu_time)
                        #         break
                        #
                        # for message in thread_queue:
                        #     message.processing_time_of_message += computing_period

                    # else:
                    while thread_queue:
                        message = thread_queue.pop(0)
                        time_to_complete_task = round(message.remaining_instructions_to_compute / (
                                process.request_cpu_share * self.clock_speed), 2)
                        if time_to_complete_task <= cpu_time:
                            message.remaining_instructions_to_compute = 0
                            cpu_time -= time_to_complete_task
                            message.processing_time_of_message = mec_simulation.env.now - message.start_of_processing + computing_period - cpu_time
                            message.latency_experienced = mec_simulation.env.now - message.entry_time_to_backhaul + message.ul_latency + \
                                                          (computing_period - cpu_time)
                            process.update_average_processing_latency(message.processing_time_of_message, message.user_id)
                            processed_messages.append(message)
                            if process.output_messages:
                                print("OUTPUT MESSAGES")
                                print(process.output_messages)
                                for tmp_msg in process.output_messages:
                                    output_message = copy.copy(tmp_msg)
                                    output_message.sequence_number = message.sequence_number
                                    output_message.user_id = message.user_id
                                    process.message_send_queue.put(output_message)

                            # mec_simulation.messages_in_the_backhaul.remove(message)

                        else:
                            message.remaining_instructions_to_compute -= cpu_time * self.clock_speed
                            message.latency_experienced = mec_simulation.env.now - message.entry_time_to_backhaul + message.ul_latency + \
                                                          (computing_period - cpu_time)
                            thread_queue.insert(0, message)
                            break

                    for message in thread_queue:
                        message.processing_time_of_message += computing_period

            with open(main_simulation.results_folder, 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                for message in processed_messages:
                    data = [str(message.name),
                            str(message.user_id),
                            str(message.sequence_number),
                            str(message.ul_latency),
                            str(message.processing_time_of_message),
                            str(message.latency_experienced),
                            str(message.delay_budget)]

                    writer.writerow(data)
                f.close()


def get_cpu_list():
    return CPU_LIST
