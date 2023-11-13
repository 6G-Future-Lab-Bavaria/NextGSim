import simpy

def process(fnc):
    if Env.INSTANCE is None:
        return None
    else:
        Env.INSTANCE.process(fnc)


class Env:
    sim = None
    INSTANCE = None

    def __init__(self, sim):
        if Env.INSTANCE is not None:
            Env.sim = sim
            pass
        else:
            Env.INSTANCE = simpy.Environment()
            Env.sim = sim

    def __call__(self):
        return Env.INSTANCE

    def timeout(self, duration):
        Env.INSTANCE.timeout(duration)

    def run(self, time):
        Env.INSTANCE.run(time)

    def process(self, fnc):
        process(fnc)

    @property
    def now(self):
        return Env.INSTANCE.now

    @now.setter
    def now(self, value):
        pass

    @now.deleter
    def now(self):
        pass
