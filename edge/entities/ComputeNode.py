from edge.entities.Entity import Entity
from edge.entities.cpu.Cpu import Cpu
from edge.entities.vm.Vm import Vm
from edge.network.Link import add_link
import random


class ComputeNode(Entity):
    def __init__(self, num_of_cpus=1, cpu_clock_speed=3 * 10 ** 5,
                 memory=10 ** 9, location=None):
        self.num_of_cpus = num_of_cpus
        self.cpu_clock_speed = cpu_clock_speed
        self.cpu = Cpu(num_of_cores=self.num_of_cpus, clock_speed=self.cpu_clock_speed, host_entity=self)
        self.memory = memory
        self.orchestrator = None
        self.service_map = {}
        self.services = {}
        self.assigned_services = {}
        self.hosted_vms = []
        super().__init__(location=location)

    @property
    def available_cpu_share(self):
        return self.cpu.available_share

    def update_service_map(self):
        self.service_map = self.orchestrator.get_service_map(self)
        return self.service_map

    def find_services(self, app_name, service_name, user_id):
        services = []
        if app_name in self.service_map:
            if service_name in self.service_map[app_name]:
                if user_id in self.service_map[app_name][service_name]:
                    services.append(self.service_map[app_name][service_name][user_id])
                if "public" in self.service_map[app_name][service_name]:
                    services.append(self.service_map[app_name][service_name]["public"])
        return services

    def has_enough_capacity_for_the_service(self, service):
        if service.required_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
            return True
        else:
            return False

    def undeploy_service(self, service):
        self.cpu.release_service(service)
        service.delete_service()
        self.memory += service.required_memory
        self.remove_from_service_list(service)

    def deploy_service(self, request):
        service = request["service"]
        user = request["user"]
        if service.is_shared is False:
            if service.required_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
                service.user = user
                service.deploy(self, user)
                self.add_to_service_list(service)
                self.cpu.deploy_service(service)
                self.memory -= service.required_memory
                return True
            else:
                print("Service %s could not be deployed at Entity : %d" % (service.name, self.entity_id))
                return False
        else:
            if user == "public":
                if service.required_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
                    self.cpu.deploy_service(service)
                    self.memory -= service.required_memory
                    service.user = "public"
                    self.add_to_service_list(service)
                    service.deploy(self, user)
                    return True
                else:
                    print("Service %s could not be deployed at Entity : %d" % (service.name, self.entity_id))
                    return False
            else:
                if self.does_service_exist(service):
                    self.get_service_instance(service).register_user(user)
                else:
                    if service.required_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
                        self.cpu.deploy_service(service)
                        self.memory -= service.required_memory
                        self.add_to_service_list(service)
                        service.deploy(self, user)
                        return True
                    else:
                        print("Service %s could not be deployed at Entity : %d" % (service.name, self.entity_id))
                        return False

    def migrate_service(self, service):
        if service.required_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
            self.cpu.deploy_service(service)
            self.memory -= service.required_memory
            self.add_to_service_list(service)
            service.migrate(self)
            return True
        else:
            print("Service %s could not be migrated at Entity : %d" % (service.name, self.entity_id))
            return False

    def get_service_instance(self, service, public=False):
        if self.does_service_exist(service):
            if public:
                return random.choice(self.services[service.app.name][service.name]["public"])
            else:
                return random.choice(self.services[service.app.name][service.name][service.user])
        else:
            return False

    def add_to_service_list(self, service):
        if service.app_name not in self.services:
            self.services[service.app_name] = {}
        if service.name not in self.services[service.app_name]:
            self.services[service.app_name][service.name] = {}
        if service.user in self.services[service.app_name][service.name]:
            self.services[service.app_name][service.name][service.user].append(service)
        else:
            self.services[service.app_name][service.name][service.user] = [service]

    # this compute node should go to service to perform that service
    def add_assigned_service(self, service):
        if service.app_name not in self.assigned_services:
            self.assigned_services[service.app_name] = {}
        self.assigned_services[service.app_name][service.name] = service

    def get_assigned_service(self, service):
        if service.app_name not in self.assigned_services:
            return None
        if service.name not in self.assigned_services[service.app_name]:
            return None
        else:
            return self.assigned_services[service.app_name][service.name]

    def change_assigned_service(self,service):
        if service.app_name not in self.assigned_services or service.name not in self.assigned_services[service.app_name]:
            return False
        else:
            self.assigned_services[service.app_name][service.name] = service

    def does_service_exist(self, service):
        if service.app_name not in self.services:
            return False
        elif service.name not in self.services[service.app_name]:
            return False
        else:
            return True

    def remove_from_service_list(self, service):
        self.services[service.app_name][service.name][service.user].remove(service)

    def deploy_app(self, app):
        raise NotImplementedError("App deployment not implemented!")

    def bind_to_orchestrator(self, orchestrator):
        raise NotImplementedError("Orchestration binding not implemented!")
