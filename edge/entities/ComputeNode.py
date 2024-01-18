from edge.entities.Entity import Entity
from edge.entities.cpu.Cpu import Cpu
from edge.entities.vm.Vm import Vm
from edge.network.Link import add_link
from edge.application.LoadBalancerService import LoadBalancerService
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
        self.hosted_services = {}
        self.public_services = {}
        self.assigned_services = {}
        self.load_balancers = {}
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
        if app_name in self.hosted_services:
            if service_name in self.hosted_services[app_name]:
                if "public" in self.hosted_services[app_name][service_name]:
                    services.extend(self.hosted_services[app_name][service_name]["public"])
                if user_id is not "public":
                    if user_id in self.hosted_services[app_name][service_name]:
                        services.extend(self.hosted_services[app_name][service_name][user_id])

        return services

    def has_enough_capacity_for_the_service(self, service):
        if service.request_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
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
            if service.request_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
                service.user = user
                service.deploy(self, user)
                self.add_to_hosted_services(service)
                self.cpu.deploy_service(service)
                self.memory -= service.required_memory
                return True
            else:
                print("Service %s could not be deployed at Entity : %d" % (service.name, self.entity_id))
                return False
        else:
            if user == "public":
                if service.request_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
                    service.user = "public"
                    service.deploy(self, user)
                    self.add_to_hosted_services(service)
                    self.cpu.deploy_service(service)
                    self.memory -= service.required_memory
                    return True
                else:
                    print("Service %s could not be deployed at Entity : %d" % (service.name, self.entity_id))
                    return False
            else:
                if self.does_service_exist(service):
                    self.get_service_instance(service).register_user(user)
                else:
                    if service.request_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
                        self.cpu.deploy_service(service)
                        self.memory -= service.required_memory
                        self.add_to_hosted_services(service)
                        service.deploy(self, user)
                        return True
                    else:
                        print("Service %s could not be deployed at Entity : %d" % (service.name, self.entity_id))
                        return False

    def migrate_service(self, service):
        if service.request_cpu_share <= self.available_cpu_share and service.required_memory <= self.memory:
            self.cpu.deploy_service(service)
            self.memory -= service.required_memory
            self.add_to_hosted_services(service)
            service.migrate(self)
            return True
        else:
            print("Service %s could not be migrated at Entity : %d" % (service.name, self.entity_id))
            return False


    def get_service_instance(self, service, public=False):
        if self.does_service_exist(service):
            if public:
                return random.choice(self.hosted_services[service.app.name][service.name]["public"])
            else:
                return random.choice(self.hosted_services[service.app.name][service.name][service.user])
        else:
            return False

    def add_to_hosted_services(self, service_list):
        if not isinstance(service_list, list):
            service_list = [service_list]
        for service in service_list:
            if service.app_name not in self.hosted_services:
                self.hosted_services[service.app_name] = {}
            if service.name not in self.hosted_services[service.app_name]:
                self.hosted_services[service.app_name][service.name] = {}
            if service.user in self.hosted_services[service.app_name][service.name]:
                self.hosted_services[service.app_name][service.name][service.user].append(service)
            else:
                self.hosted_services[service.app_name][service.name][service.user] = [service]

    def add_to_assigned_services(self, service):
        if service.app_name not in self.assigned_services:
            self.assigned_services[service.app_name] = {}
        if service.name not in self.assigned_services[service.app_name]:
            self.assigned_services[service.app_name][service.name] = service

    def get_public_services(self):
        public_services = []
        for app_name in self.hosted_services:
            for service_name in self.hosted_services[app_name]:
                if "public" in self.hosted_services[app_name][service_name]:
                    for service in self.hosted_services[app_name][service_name]["public"]:
                        public_services.append(service)

        return public_services

    def get_public_load_balancers(self):
        public_load_balancers = []
        for app_name in self.load_balancers:
            for service_name in self.load_balancers[app_name]:
                if "public" in self.load_balancers[app_name][service_name]:
                    for service in self.load_balancers[app_name][service_name]["public"]:
                        public_load_balancers.append(service)

        return public_load_balancers

    def add_public_services(self, services):
        if not isinstance(services, list):
            services = [services]
        for service in services:
            if service.app_name not in self.public_services:
                self.public_services[service.app_name] = {}
            if service.name not in self.public_services[service.app_name]:
                self.public_services[service.app_name][service.name] = [service]
            else:
                self.public_services[service.app_name][service.name].append(service)

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
        if service.app_name not in self.hosted_services:
            return False
        elif service.name not in self.hosted_services[service.app_name]:
            return False
        else:
            return True

    def remove_from_service_list(self, service):
        self.hosted_services[service.app_name][service.name][service.user].remove(service)

    def deploy_app(self, app):
        raise NotImplementedError("App deployment not implemented!")

    def bind_to_orchestrator(self, orchestrator):
        raise NotImplementedError("Orchestration binding not implemented!")
