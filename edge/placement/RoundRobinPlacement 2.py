from edge.placement.ServicePlacement import ServicePlacement
from entities.entity import map_user_id_to_entity_id, get_entity_by_id

rr_counter = 0
placed_services = {}


class SimpleServicePlacementRoundRobin(ServicePlacement):
    def __init__(self, name=None, activation_distribution=None, logger=None):
        super().__init__(name, activation_distribution, logger)

    def initial_allocation(self, sim, app):
        global rr_counter
        global placed_services
        edge_devices = sim.topology.find_device_by_model("edge_server")
        source_services = app.source_services.values()
        sink_services = app.sink_services.values()
        compute_services = app.compute_services.values()

        for service in source_services:
            user_entity_id = map_user_id_to_entity_id(service.user_id)
            user_entity = get_entity_by_id(user_entity_id)
            user_entity = user_entity.devices[service.host_entity_model]
            service.set_app(app)
            service.deploy(sim, user_entity)

        for service in sink_services:
            user_entity_id = map_user_id_to_entity_id(service.user_id)
            user_entity = get_entity_by_id(user_entity_id)
            user_entity = user_entity.devices[service.host_entity_model]
            service.set_app(app)
            service.deploy(sim, user_entity)

        for service in compute_services:
            if service.name in app.number_of_service_instances:
                if app not in placed_services.keys():
                    placed_services[app] = {}
                if service not in placed_services[app].keys():
                    placed_services[app][service] = []
                for _ in range(0, app.number_of_service_instances[service.name]):
                    if service.is_deployed_at_edge:
                        edge_entity = edge_devices[rr_counter % len(edge_devices)]
                        service.set_app(app)
                        service.deploy(sim, edge_entity)
                        placed_services[app][service].append(edge_entity)
                        rr_counter += 1
                    else:
                        user_entity_id = map_user_id_to_entity_id(app.user_id)
                        user_entity = get_entity_by_id(user_entity_id)
                        service.deploy(sim, user_entity)
                        placed_services[app][service].append(user_entity_id)

