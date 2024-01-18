from edge.entities.Entity import Entity, get_entity_by_id, get_base_stations, map_user_id_to_entity, get_sim
from edge.network.NetworkTopology import get_topology
from edge.util.Util import closest_node
from networkx import shortest_path_length
from numpy import random, argmin, ceil

AVERAGING_COEFFICIENT = 0.5


class EdgeOrchestrator(Entity):

    def __init__(self, name="default_orchestrator"):
        super(EdgeOrchestrator, self).__init__(name=name)
        self.nodes_managed = []
        self.connected_devices = []
        self.average_user_radio_latency = {}
        self.deployment_requests = []
        self.assignment_requests = []
        self.deployed_service_info = []
        self.service_map = {}
        self.service_assignment_map = {}
        self.analytic_packets = []

    def add_server(self, server):
        self.nodes_managed.append(server)

    def add_assignment(self, assigned_service, user):
        if assigned_service.name not in self.service_assignment_map:
            self.service_assignment_map[assigned_service.name] = {}
        self.service_assignment_map[assigned_service.name][user] = assigned_service
        map_user_id_to_entity(user).add_to_assigned_services(assigned_service)

    def update_service_map(self):
        def add_service_to_service_map(service):
            if service.app not in self.service_map:
                self.service_map[service.app] = {}
            if service.name not in self.service_map[service.app]:
                self.service_map[service.app][service.name] = {}
            if service.user not in self.service_map[service.app][service.name]:
                self.service_map[service.app][service.name][service.user] = []

            if service in self.service_map[service.app][service.name][service.user]:
                return
            else:
                self.service_map[service.app][service.name][service.user].append(service)

        def update_node_services(node):
            for app in node.hosted_services.keys():
                for service in node.hosted_services[app]:
                    for user in node.hosted_services[app][service]:
                        for service_instance in node.hosted_services[app][service][user]:
                            add_service_to_service_map(service_instance)

        self.service_map = {}
        for node in self.nodes_managed:
            update_node_services(node)

        for device in self.connected_devices:
            update_node_services(device)

    def get_service_map(self, requesting_entity):
        def add_service_entry_to_filtered_map(service_list):
            for entry in service_list:
                if entry.app.name not in filtered_map:
                    filtered_map[entry.app.name] = {}
                if entry.name not in filtered_map[entry.app.name]:
                    filtered_map[entry.app.name][entry.name] = {}
                if entry.user not in filtered_map[entry.app.name][entry.name]:
                    filtered_map[entry.app.name][entry.name][entry.user] = []

                filtered_map[entry.app.name][entry.name][entry.user].append(entry)

        self.update_service_map()
        filtered_map = {}
        for app in self.service_map:
            for service in self.service_map[app]:
                for user in self.service_map[app][service]:
                    if requesting_entity.__class__.__name__ == "EdgeServer":
                        add_service_entry_to_filtered_map(self.service_map[app][service][user])
                    elif user == requesting_entity.user_id:
                        add_service_entry_to_filtered_map(self.service_map[app][service][user])
                    elif user == "public":
                        add_service_entry_to_filtered_map(self.service_map[app][service][user])
                    else:
                        pass

        return filtered_map

    def search_for_the_service(self, service):
        suitable_services = []
        for server in self.nodes_managed:
            if service.app_name in server.hosted_services:
                if service.name in server.hosted_services[service.app_name]:
                    if service.user in server.hosted_services[service.app_name][service.name]:
                        for service in server.hosted_services[service.app_name][service.name][service.user]:
                            suitable_services.append(service)

        return suitable_services

    def find_suitable_server(self, service):
        for node in self.nodes_managed:
            if node.has_enough_capacity_for_the_service(service):
                return node

        print('Orchestrator : %s, Cant find a suitable server!' % self.name)
        return None

    def request_deployment(self, request):
        self.deployment_requests.append(request)

    def request_assignment(self, request):
        self.assignment_requests.append(request)

    def deploy_service(self, service):
        suitable_server = self.find_suitable_server(service)
        suitable_server.deploy_service(service)

    def filter_suitable_nodes(self, service):
        filtered_nodes = []
        for node in self.nodes_managed:
            if node.has_enough_capacity_for_the_service(service):
                filtered_nodes.append(node)
        return filtered_nodes

    def collect_message_for_analytics(self, message):
        self.analytic_packets.append(message)

    def perform_analytics(self):
        num_of_packets_per_user = {}
        self.average_user_radio_latency = {}
        for message in self.analytic_packets:
            if message.user_id in self.average_user_radio_latency:
                self.average_user_radio_latency[message.user_id] += get_sim().env.now - message.timestamp
            else:
                self.average_user_radio_latency[message.user_id] = get_sim().env.now - message.timestamp

            if message.user_id in num_of_packets_per_user:
                num_of_packets_per_user[message.user_id] += 1
            else:
                num_of_packets_per_user[message.user_id] = 1

        for user in self.average_user_radio_latency.keys():
            self.average_user_radio_latency[user] /= num_of_packets_per_user[user]

        self.analytic_packets = []

    def share_analytic_with_services(self):
        """
        Shares average latency statistic in a predefined time period
        """
        self.update_service_map()
        for app in self.service_map:
            for service in self.service_map[app]:
                for owner in self.service_map[app][service]:
                    for service_instance in self.service_map[app][service][owner]:
                        shared_information_with_service = {}
                        for user in service_instance.user_list:
                            shared_information_with_service[user] = {}
                            if user in self.average_user_radio_latency:
                                shared_information_with_service[user]["average_radio_latency"] = \
                                    self.average_user_radio_latency[user]
                            else:
                                self.average_user_radio_latency[user] = 0

                        service_instance.update_user_information_from_orchestrator(shared_information_with_service)

    def place_services(self, algorithm=None):
        """
        Deploys hosted_services or assigns users to hosted_services according to Round Robin, Random
        and LatencyAware algorithms.
        """
        if algorithm == "Round_Robin":
            rr_deployment_cnt = 0
            rr_assignment_cnt = 0

            for request in self.deployment_requests:
                suitable_nodes = self.filter_suitable_nodes(request["service"])
                deployed_node = self.nodes_managed[rr_deployment_cnt % len(suitable_nodes)]
                service_instance = request["service"]()
                deployed_node.deploy_service({"service": service_instance, "user": request["user"]})
                self.add_assignment(service_instance, request["user"])
                rr_deployment_cnt += 1
                self.deployed_service_info.append(
                    {"user": request["user"], "service": request["service"], "deployed_node": deployed_node})

            for request in self.assignment_requests:
                print("service")
                print(request["service"])
                services = self.search_for_the_service(request["service"])
                print("services")
                print(services)
                assigned_service = services[rr_assignment_cnt % len(services)]
                assigned_service.register_user(request["user"])
                self.add_assignment(assigned_service, request["user"])
                rr_assignment_cnt += 1

        if algorithm == "Random" or None:
            for request in self.deployment_requests:
                suitable_nodes = self.filter_suitable_nodes(request["service"])
                deployed_node = random.choice(suitable_nodes)
                deployed_node.deploy_service(request)
                self.deployed_service_info.append(
                    {"user": request["user"], "service": request["service"], "deployed_node": deployed_node})

            for request in self.assignment_requests:
                services = self.search_for_the_service(request["service"])
                assigned_service = random.choice(services)
                assigned_service.register_user(request["user"])
                self.add_assignment(assigned_service, request["user"])
                map_user_id_to_entity(request["user"]).add_to_hosted_services(assigned_service)

        if algorithm == "LatencyAware":
            for request in self.deployment_requests:
                suitable_nodes = self.filter_suitable_nodes(request["service"])
                latencies = []
                for node in suitable_nodes:
                    if request["user"].my_gnb is None:
                        closest_bs = closest_node(get_base_stations(), request["user"])
                        latency = shortest_path_length(G=get_topology(), source=closest_bs, target=node,
                                                       weight="latency")
                    else:
                        latency = shortest_path_length(G=get_topology(), source=request["user"].my_gnb, target=node,
                                                       weight="latency")
                    latencies.append(latency)

                min_latency_node_index = argmin(latencies)
                deployed_node = suitable_nodes[min_latency_node_index]
                deployed_node.deploy_service(request["service"])
                self.deployed_service_info.append(
                    {"user": request["user"], "service": request["service"], "deployed_node": deployed_node})

            for request in self.assignment_requests:
                services = self.search_for_the_service(request["service"])
                hosts = []
                for service in services:
                    hosts.append(service.host_entity)
                latencies = []
                for host in hosts:
                    if request["user"].my_gnb is None:
                        closest_bs = closest_node(get_base_stations(), request["user"])
                        latency = shortest_path_length(G=get_topology(), source=closest_bs, target=host,
                                                       weight="latency")
                    else:
                        latency = shortest_path_length(G=get_topology(), source=request["user"].my_gnb, target=host,
                                                       weight="latency")
                    latencies.append(latency)

                min_latency_node_index = argmin(latencies)
                assigned_service = services[min_latency_node_index]
                assigned_service.register_user(request["user"])
                self.add_assignment(assigned_service, request["user"])

    def expose_public_services(self):
        for node in self.nodes_managed:
            public_services = node.get_public_services()
            public_load_balancers = node.get_public_load_balancers()
            for device in self.connected_devices:
                device.add_public_services(public_services)
                device.add_public_services(public_load_balancers)

    def replace_services(self, algorithm=None):
        if algorithm == "autoscaling":
            self.update_service_map()
            for app in self.service_map:
                for service_name in self.service_map[app]:
                    sum_latencies = 0
                    sum_queue_length = 0
                    for service in self.service_map[app][service_name]["public"]:
                        sum_latencies += service.avg_processing_time
                        sum_queue_length += len(service.processing_queue)
                    desired_latency = get_service(service_name).desired_latency
                    num_replicas = len(self.service_map[app][service_name]["public"])
                    avg_latency = sum_latencies / num_replicas
                    desired_replicas = int((num_replicas * ((avg_latency / desired_latency) + 1) / 2))
                    service = get_service(service_name)
                    if desired_replicas > num_replicas:
                        for _ in range(desired_replicas - num_replicas):
                            deployed_service = service()
                            server = self.find_suitable_server(deployed_service)
                            if server is not None:
                                server.deploy_service({"service": deployed_service, "user": "public"})
                            else:
                                break

                    elif desired_replicas < num_replicas:
                        for _ in range(num_replicas - desired_replicas):
                            replicas = self.search_for_the_service(service)
                            deleted_replica = random.choice(replicas)
                            deleted_replica.host_entity.undeploy_service(deleted_replica)
                    else:
                        break

                    services = self.search_for_the_service(service)
                    rr_count = 0
                    for user in self.service_assignment_map[service.name]:
                        user_device = map_user_id_to_entity(user)
                        prev_service = user_device.get_assigned_service(service)
                        if prev_service is None:
                            pass
                        else:
                            prev_service.deregister_user(user)
                        assigned_service = services[rr_count % len(services)]
                        user_device.change_assigned_service(assigned_service)
                        assigned_service.register_user(user)
                        rr_count += 1
                    # print('SERVICE ASSIGNMENT MAP')
                    # print(self.service_assignment_map)
