import copy

from edge.entities.ComputeNode import ComputeNode
from edge.entities.cpu.Cpu import Cpu
from edge.application.ApplicationRepository import get_app
from edge.application.LoadBalancerService import LoadBalancerService


class EdgeServer(ComputeNode):
    # Default CPU : Intel Core i9-9900K
    def __init__(self, cpu_clock_speed=4.12*10**5, num_of_cpus=50, memory=32, location=None):
        self.memory = memory  # In GB
        self.orchestrator = None
        self.service_map = {}
        self.services = {}
        self.hosted_vms = []
        super().__init__(cpu_clock_speed=cpu_clock_speed, num_of_cpus=num_of_cpus, memory=memory, location=location)

    def bind_to_orchestrator(self, orchestrator):
        self.orchestrator = orchestrator
        orchestrator.add_server(self)

    def deploy_load_balancer(self, app_name, service_name, balanced_servers):
        load_balancer_service = LoadBalancerService(app_name=app_name, balanced_service=service_name,
                                                    balanced_servers=balanced_servers)
        load_balancer_service.deploy(self, "public")
        self.add_to_load_balancer_list(load_balancer_service)

    def add_to_load_balancer_list(self, load_balancer):
        if load_balancer.app_name not in self.load_balancers:
            self.load_balancers[load_balancer.app_name] = {}
        if load_balancer.name not in self.load_balancers[load_balancer.app_name]:
            self.load_balancers[load_balancer.app_name][load_balancer.name] = {}
        if load_balancer.user in self.load_balancers[load_balancer.app_name][load_balancer.name]:
            self.load_balancers[load_balancer.app_name][load_balancer.name][load_balancer.user].append(load_balancer)
        else:
            self.load_balancers[load_balancer.app_name][load_balancer.name][load_balancer.user] = [load_balancer]

    def deploy_app(self, app_name, num_of_instances=None):
        app = get_app(app_name)
        for service in app.services:
            if service.is_deployed_at_edge:
                if num_of_instances is not None:
                    num_of_deployed_instances = num_of_instances
                else:
                    num_of_deployed_instances = app.number_of_service_instances[service.name]
                for _ in range(num_of_deployed_instances):
                    service_instance = service()
                    service_instance.app_name = app_name
                    if service.is_shared:
                        self.deploy_service({"service": service_instance, "user": "public"})
                    else:
                        self.deploy_service({"service": service_instance, "user": None})






