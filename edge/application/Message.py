SOURCE = "SOURCE"
COMPUTE = "COMPUTE"
SINK = "SINK"


class Message:
    """
    A output_message consisting the following values:

    Args:
        name (str): Name of the output_message (unique for each application)

        source_service (str): Name of the service who sends this output_message

        destination_service (dst): Name of the service who receives this output_message

        msg_type(str):

        instructions (int): Number of instructions to be executed ((by default 0)

        bytes (float): the size in bits (by default 0)

    """

    def __init__(self, name=None, source_service=None, destination_service=None,
                 instructions=0, bytes=0, msg_type='COMPUTE', delay_budget=None):
        self.name = name
        self.user_id = None
        self.source_id = None
        self.source_service = source_service
        self.source_service_instance = None
        self.source_service_id = None
        self.destination_id = None
        self.destination_service = destination_service
        self.destination_service_instance = None
        self.destination_service_id = None
        self.sender_id = -1
        self.receiver_id = -1
        self.location = None
        self.instructions = instructions
        self.remaining_instructions_to_compute = instructions
        self.bits = bytes
        self.remaining_bytes_to_send = bytes
        self.delay_budget = None
        self.msg_type = msg_type
        self.timestamp = 0
        self.path = []
        self.app_name = None
        self.is_scheduled_by_ran = False
        self.processing_percentage = 0
        self.sequence_number = 0
        self.delay_budget = delay_budget
        self.payload = {}
        self.ul_latency = 0
        self.entry_time_to_backhaul = 0
        self.start_of_processing = None
        self.processing_time_of_message = 0
        self.latency_experienced = 0

    def set_instructions(self, instructions):
        self.instructions = instructions
        self.remaining_instructions_to_compute = instructions

    def set_bits(self, bits):
        self.bits = bits

    def set_destination_service(self, destination_service):
        self.destination_service = destination_service

    def set_delay_budget(self, delay_budget):
        self.delay_budget = delay_budget
