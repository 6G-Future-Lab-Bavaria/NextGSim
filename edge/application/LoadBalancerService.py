from edge.application.Microservice import Microservice
from edge.application.Message import Message
from edge.entities.Entity import Entity, get_sim
from edge.application.Application import get_AppName_to_AppInst_Map


class GatewayMicroservice(Microservice):
    def __init__(self,
                 name=None,
                 app=None,
                 app_name=None,
                 destination_service=None,
                 is_deployed_at_edge=False,
                 is_shared=False,
                 **param):

        """
        Args:
            name:
            required_memory:
            service_type:
            host_entity_model:
            message_in:
            message_out:
            required_cpu:
            module_dest:
            **param:
        """
        super().__init__(
            name=name,
            app=app,
            app_name=app_name,
            destination_service=destination_service,
            is_deployed_at_edge=is_deployed_at_edge,
            is_shared=is_shared,
            **param)
