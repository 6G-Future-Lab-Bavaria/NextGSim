SOURCE = "SOURCE"
"e.g a sensor"

COMPUTE = "COMPUTE"
"e.g microservice"

SINK = "SINK"
"e.g an actuator"

AppName_to_AppInst_Map = {}


class Application:
    """
    An application is defined by a directed acyclic graph (DAG) between all_services that generate, compute and receive sink
    messages.

    Args:
        name (str): The name must be unique within the same topology.

    Returns:
        app_name (Application) : An application object

    """

    global APP_LIST
    global COMPUTE
    global SOURCE
    global SINK

    def __init__(self, name):
        self.name = name
        self.user_id = None
        self.services = None
        self.number_of_service_instances = {}
        self.ul_latency = 0
        self.backhaul_ul_latency = 0
        self.processing_latency = 0
        self.dl_latency = 0
        self.latency = 0
        self.app_id = -1
        self.entry_time_to_backhaul = 0
        self.exit_time_from_backhaul = 0
        self.latest_starting_time = 0
        self.latest_ending_time = 0

    def set_services(self, service_list=None, number_of_service_instances=None):
        self.number_of_service_instances = number_of_service_instances
        self.services = service_list
        for service in self.services:
            if service.is_shared:
                service.user = "public"
            elif service.user is None:
                service.user = self.user_id

    def get_id(self):
        """
        Returns:
            app_id(int): Application ID
        """
        return self.app_id

    def set_user_id(self, user_id):
        """

        Args:
            user_id(int): Sets the user_id that is using the application.

        """
        if user_id is not None:
            self.user_id = user_id
            if self.name not in AppName_to_AppInst_Map:
                AppName_to_AppInst_Map[self.name] = {}
            else:
                AppName_to_AppInst_Map[self.name][self.user_id] = self

            # self.name = self.name + '_' + str(self.user_id)


def add_app(app):
    if app.name not in AppName_to_AppInst_Map:
        AppName_to_AppInst_Map[app.name] = {}
    else:
        AppName_to_AppInst_Map[app.name][app.user_id] = app


def get_AppName_to_AppInst_Map():
    return AppName_to_AppInst_Map
