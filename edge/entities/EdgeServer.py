import copy

from edge.entities.ComputeNode import ComputeNode
from edge.entities.cpu.Cpu import Cpu
from edge.application.ApplicationRepository import get_app


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

    def deploy_app(self, app_name, num_of_instances=None):
        app = get_app(app_name)
        print("SERVER APP NAME")
        print(app.name)
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





