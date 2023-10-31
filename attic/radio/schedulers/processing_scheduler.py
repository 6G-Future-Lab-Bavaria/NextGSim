from attic.schedulers import TIME_GRANULARITY


class ProcessingScheduler:

    def __init__(self, name="processing_scheduler", period=10, env=None):
        self.name = name  # name of the scheduler
        self.period = TIME_GRANULARITY  # period in ms
        self.is_active = True
        self.env = env  # environment scheduler is running

    def blink(self):
        while self.is_active:
            yield self.env.timeout(TIME_GRANULARITY)
            print("Processing Scheduler is active at (T: %d)" % self.env.now)

    def start_scheduler(self):
        self.env.process(self.blink())
