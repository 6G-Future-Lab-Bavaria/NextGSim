from entities.entity import get_entity_by_id, get_entity_list
from entities.edge_server import get_edge_servers
import csv


def report_backhaul_status(sim):
    """
        Reports information about the messages in backhaul such as : process entity_id of the process they belong, ID of the device they serve, ID of the entity_id that the output_message is being or going to be processed,
        completion percentage of the processing, latency experienced by the app_name in the backhaul, and a boolean value indicating if the output_message is waiting to be scheduled by a base station or not ( if this value is None, the output_message is not meant
        to be sent by a base station ).

        It can report them as a log, or if enabled, it can output them as a .csv file to be used by the RAN.csv simulator.

        e.g :

            Messages in the Backhaul at time : 879

            Sensor_1_Data_APP4

            Percentage : 53.54330708661415

            Location : 12 - server

            Processed_Sensor_Data_APP4

            Percentage : 0

            Location : 8 - base_station

            Processed_Sensor_Data_APP4

            Percentage : 0

            Location : 3 - base_station

            ['Process ID', 21, 31, 25]

            ['User ID', 21, 30, 24]

            ['Server ID', 12, 30, 24]

            ['Processing Percentage', 53.54330708661415, 0, 0]

            ['Latency', None, 12.800000004062326, 12.800000008062284]

            ['Waiting to be Scheduled', False, True, True]

        """
    while not sim.stop:
        next_report_time = sim.reporting_distribution.next()
        yield sim.env.timeout(next_report_time)
        messages_to_remove = []
        process_ids = ["Process ID"]
        process_names = ["Process Name"]
        user_ids = ["User ID"]
        server_ids = ["Computing Node ID"]
        processing_percentages = ["Processing Percentage"]
        latencies = ["Latency(ms)"]
        scheduling_status = ["Is Scheduled?"]
        packet_data_sizes = ["Packet Data Sizes(bits)"]
        reporting_time = ["Reporting Time(ms)", round(sim.env.now, 2)]
        data_to_csv = []
        edge_server_list = ["Edge Server IDs"]
        edge_servers_available_cpu_shares = ["Available CPU Shares"]
        edge_servers_available_gpus = ["Available GPU Cores"]
        edge_servers_available_storage = ["Available Storage"]

        edge_servers = get_edge_servers()
        print('edge servers')
        print(edge_servers)
        print(get_entity_list())

        for message in sim.messages_in_the_backhaul:
            if message.remaining_instructions_to_compute == 0:
                messages_to_remove.append(message)
                continue
            else:
                app = get[message.app_name]
                server_id = message.destination_id
                location_entity = get_entity_by_id(message.location)
                if location_entity.model != "server" and location_entity.model != "base_station" and \
                        location_entity.model != "gateway" and \
                        location_entity.model != 'vm' and location_entity.model != "edge_server":
                    print("removing message")
                    print('location entity')
                    print(location_entity.model)
                    messages_to_remove.append(message)
                    continue
                else:
                    user_id = sim.processId_to_nodeId[message.destination_service_id]
                    process_ids.append(message.destination_service_id)
                    process_names.append(get_entity_by_id(server_id).services[message.destination_service_id].name)
                    user_ids.append(user_id)
                    server_ids.append(server_id)

                    if location_entity.model == "base_station":
                        processing_percentages.append("N/A")
                        scheduling_status.append(message.is_scheduled_by_ran)
                        packet_data_sizes.append(message.bits * 8)
                    else:
                        tmp_processing_percentage = \
                            round((message.instructions - message.remaining_instructions_to_compute)
                                  / message.instructions * 100, 2)
                        processing_percentages.append(tmp_processing_percentage)
                        scheduling_status.append("N/A")
                        packet_data_sizes.append("N/A")
                    if (app.exit_time_from_backhaul - app.entry_time_to_backhaul) > 0:
                        latency = round(app.exit_time_from_backhaul - app.entry_time_to_backhaul, 2)
                        latencies.append(latency)
                    else:
                        # latencies.append(mec_simulation.app_latencies[app_name.name] + mec_simulation.env.now - app_name.entry_time_to_backhaul)
                        latencies.append(round(app.ul_latency + sim.env.now - app.entry_time_to_backhaul, 2))

        for msg in messages_to_remove:
            sim.messages_in_the_backhaul.remove(msg)

        for server in edge_servers:
            edge_server_list.append(server.entity_id)
            tmp_share = server.available_cpu_share
            edge_servers_available_cpu_shares.append(tmp_share)
            edge_servers_available_storage.append(server.memory)

        if sim.sim_params.SHOW_CSV:
            sim.logger.debug(edge_server_list)
            sim.logger.debug(edge_servers_available_cpu_shares)
            sim.logger.debug(edge_servers_available_storage)
            sim.logger.debug(process_ids)
            sim.logger.debug(process_names)
            sim.logger.debug(user_ids)
            sim.logger.debug(server_ids)
            sim.logger.debug(processing_percentages)
            sim.logger.debug(latencies)
            sim.logger.debug(scheduling_status)
            sim.logger.debug(packet_data_sizes)
            sim.logger.debug(reporting_time)
            print("\n")

        if len(edge_server_list) < len(process_ids):
            for i in range(len(process_ids) - len(edge_server_list)):
                edge_server_list.append(None)
                edge_servers_available_cpu_shares.append(None)
                edge_servers_available_gpus.append(None)
                edge_servers_available_storage.append(None)

        if sim.sim_params.OUTPUT_CSV:
            data_to_csv.append(edge_server_list)
            data_to_csv.append(edge_servers_available_cpu_shares)
            data_to_csv.append(edge_servers_available_gpus)
            data_to_csv.append(edge_servers_available_storage)
            data_to_csv.append(process_ids)
            data_to_csv.append(process_names)
            data_to_csv.append(user_ids)
            data_to_csv.append(server_ids)
            data_to_csv.append(processing_percentages)
            data_to_csv.append(latencies)
            data_to_csv.append(scheduling_status)
            data_to_csv.append(packet_data_sizes)
            data_to_csv.append(reporting_time)
            data_to_csv = zip(*data_to_csv)

            with open(sim.sim_params.MEC_CSV_DIR, 'w') as file:
                writer = csv.writer(file)
                writer.writerows(data_to_csv)
