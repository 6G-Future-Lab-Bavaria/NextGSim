from edge.entities.Entity import USER_LIST, USER_COUNTER, EntityID_to_DeviceID_Map, \
    DeviceID_to_EntityID_Map, get_and_increment_user_counter
from edge.entities.ComputeNode import ComputeNode
from edge.network.Link import NetworkTopology, LINK_LIST, add_link, delete_link
from edge.core.MECSimulation import get_sim

topology = NetworkTopology()


class MobileDevice(ComputeNode):
    def __init__(self, name=None, entity_id=None, model="mobile_device", location=None, user_id=None,
                 attached_bs=None, velocity=1, num_of_cpus=1):
        super().__init__(name=name, entity_id=entity_id, model=model,
                         location=location, user_id=user_id, num_of_cpus=num_of_cpus)
        self.attached_bs = None
        self.uplink_rate = 10 ** 4
        self.velocity = velocity
        self.user_id = get_and_increment_user_counter()
        self.is_mobile_device = True
        self.bs_uplink = None
        self.bs_downlink = None
        self.bound_server = None
        self.bound_vm = None
        self.running_apps = []
        USER_LIST[self.user_id] = self
        EntityID_to_DeviceID_Map[self.entity_id] = self.user_id
        DeviceID_to_EntityID_Map[self.user_id] = self.entity_id
        self.devices = {}

        if attached_bs is not None:
            add_link(source=self, destination=attached_bs, bandwidth=self.uplink_rate, latency=0)
            add_link(source=attached_bs, destination=self, bandwidth=self.uplink_rate, latency=0)

        add_mobile_device(self)



    def add_app(self, app):
        self.running_apps.append(app)

    def get_running_apps(self):
        return self.running_apps

    def attach_to_closest_bs(self):
        # bs = get_closest_base_station(self.location)
        bs = get_closest_base_station(self)
        self.attached_bs = bs
        self.bs_uplink = add_link(source=self, destination=bs)
        self.bs_downlink = add_link(source=bs, destination=self)
        topology.G.add_edge(self.entity_id, bs.entity_id)
        topology.plainG.add_edge(self.entity_id, bs.entity_id)
        topology.G.add_edge(bs.entity_id, self.entity_id)
        topology.plainG.add_edge(bs.entity_id, self.entity_id)

    def attach_to_bs(self, bs):
        self.attached_bs = bs
        self.bs_uplink = add_link(source=self, destination=bs)
        self.bs_downlink = add_link(source=bs, destination=self)
        topology.G.add_edge(self.entity_id, bs.entity_id)
        topology.plainG.add_edge(self.entity_id, bs.entity_id)
        topology.G.add_edge(bs.entity_id, self.entity_id)
        topology.plainG.add_edge(bs.entity_id, self.entity_id)

    def detach_from_bs(self):
        if self.attached_bs is not None:
            topology.G.remove_edge(self.entity_id, self.attached_bs.entity_id)
            topology.plainG.remove_edge(self.entity_id, self.attached_bs.entity_id)
            topology.G.remove_edge(self.attached_bs.entity_id, self.entity_id)
            topology.plainG.remove_edge(self.attached_bs.entity_id, self.entity_id)
            delete_link(self.bs_uplink)
            delete_link(self.bs_downlink)
            self.attached_bs = None


    def request_vm(self, request):
        request["device"] = self
        self.bound_server, self.bound_vm = self.orchestrator.deploy_vm(request)

    def deploy_app_to_vm_and_device(self, app):
        sim = get_sim()
        app.set_user_id(self.user_id)
        for service in app.hosted_services:
            if service.is_deployed_at_edge:
                service.deploy_service(sim, self.bound_vm)
            else:
                service.deploy_service(sim, self)

    def deploy_app(self, app):
        sim = get_sim()
        app.set_user_id(self.user_id)

        for service in app.hosted_services:
            if not service.is_deployed_at_edge:
                service.deploy_service(sim, self)



