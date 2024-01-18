from edge.entities.Entity import Entity, get_entity_by_id
from edge.entities.cpu.Cpu import Cpu

VM_LIST = []


class Vm(Entity):
    def __init__(self, name=None, model='vm', num_of_cpus=2, storage=10**6, bw=10**6, user=None, host=None):
        super().__init__(name=name, model=model)
        self.host = host
        self.running_services = []
        self.num_of_cpus = num_of_cpus
        self.available_cpu_share = num_of_cpus
        self.cpu = Cpu(num_of_cores=self.num_of_cpus, clock_speed=self.host.cpu_clock_speed, host_entity=self.entity_id)
        self.storage = storage
        self.bw = bw
        self.user = user
        self.services = {}
        self.service_map = {}
        VM_LIST.append(self)

    def update_service_map(self):
        self.service_map = self.host.orchestrator.get_service_map(self)
        return self.service_map

    def deploy_service(self, service, process_id):
        """
        Current service deployment model is to offload it to a random available cpu
        """
        service.process_id = process_id
        if service.request_cpu_share < self.available_cpu_share and service.required_memory < self.storage:
            self.services[service.name] = process_id
            self.cpu.deploy_service(service)
            self.storage -= service.required_memory
            return True
        else:
            print("Process %d of service %s could not be deployed at Entity : %d" % (
                process_id, service.name, self.entity_id))

