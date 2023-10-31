from attic.placement.ServicePlacement import ServicePlacement

rr_counter = 0
placed_services = {}


class SimpleServicePlacementRoundRobin(ServicePlacement):
    def __init__(self, name=None, activation_distribution=None, logger=None):
        super().__init__(name, activation_distribution, logger)

    def initial_allocation(self, orchestrator):
        rr_deployment_cnt = 0
        rr_assignment_cnt = 0
        for request in self.deployment_requests:
            suitable_nodes = self.filter_suitable_nodes(request["service"])
            deployed_node = self.nodes_managed[rr_deployment_cnt % len(suitable_nodes)]
            deployed_node.deploy_service(request)
            rr_deployment_cnt += 1
            self.deployed_service_info.append(
                {"user": request["user"], "service": request["service"], "deployed_node": deployed_node})

        for request in self.assignment_requests:
            services = self.search_for_the_service(request["service"])
            assigned_service = services[rr_assignment_cnt % len(services)]
            assigned_service.register_user(request["user"])
            self.add_assignment(assigned_service, request["user"])
            rr_assignment_cnt += 1

