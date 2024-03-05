import simpy

from mec.service import GW


def dummy_sim():
    from ng.physical_node import PhysicalNode
    from ng.mec.message import Message
    from ng.networking.interface.eth import EthernetInterface, FiberConnection
    from ng.networking.interface.radio import RadioInterface, RadioConnection
    from ng.physical import PhysicalEnvironment, Coords2D
    from ng.simulation import Simulation
    from ng.networking.routing import ShortestPathRouting

    phy_env = PhysicalEnvironment(Coords2D(0, 0), Coords2D(200, 100))
    sim = Simulation(phy_env, ShortestPathRouting, lambda e : e)

    phy_env.nodes = [
        PhysicalNode(sim, 0, Coords2D(10, 30)),
        PhysicalNode(sim, 1, Coords2D(50, 40)),
        PhysicalNode(sim, 2, Coords2D(10, 10)),
        PhysicalNode(sim, 3, Coords2D(10, 10))
    ]
    devs = phy_env.nodes

    devs[0].attach_if(EthernetInterface(sim, 0))

    devs[1].attach_if(EthernetInterface(sim, 0))
    devs[1].attach_if(EthernetInterface(sim, 1))

    devs[2].attach_if(EthernetInterface(sim, 0))
    devs[2].attach_if(EthernetInterface(sim, 1))

    devs[3].attach_if(RadioInterface(sim, 0))

    FiberConnection(sim, phy_env.dist(devs[0].coords, devs[1].coords), devs[0].intf(0), devs[1].intf(0))
    FiberConnection(sim, phy_env.dist(devs[1].coords, devs[2].coords), devs[1].intf(1), devs[2].intf(0))

    # RadioConnection(sim, devs[3].intf(0), devs[2].intf(1))

    def t():
        for i in range(10):
            devs[0]._send_data(2, Message(-1, 2, 2, "hi" + str(i)), 2)
            yield sim.env.timeout(1)
            # devs[1].intf(0).disconnect()

    sim.env.process(t())

    return sim

def test1():
    sim = dummy_sim()
    print(list(sim.network.get_links()))

    sim.run(100)

    for ev in sim.eventlog.events:
        print(ev.time, ev.component, ev.type)


def test2():
    env = simpy.Environment()

    def yieldable():
        return simpy.Event(env).succeed(3)

    def proc():
        d = yield yieldable()
        print(d)

    env.process(proc())

    env.run()

def test3():
    env = simpy.Environment()

    def proc1():
        #try:
        if True:
            yield env.timeout(10)
            print(env.now, "proc1 done")
        #except simpy.Interrupt:
        #    print(env.now, "proc1 int")

    def proc2():
        #try:
        if True:
            yield env.timeout(10)
            print(env.now, "proc2 done")
        #except simpy.Interrupt:
        #    print(env.now, "proc2 int")

    def proc3():
        procs = [env.process(proc1()), env.process(proc2())]
        try:
            yield simpy.AllOf(env, procs)
        except simpy.Interrupt:
            for proc in procs:
                proc.interrupt()
            print(env.now, "proc3 int")

    def main():
        p = env.process(proc3())
        yield env.timeout(5)
        p.interrupt()

    env.process(main())
    env.run(100)

def dummy_sim_mec():
    from ng.networking.interface.eth import EthernetInterface, FiberConnection
    from ng.physical import PhysicalEnvironment, Coords2D
    from ng.simulation import Simulation
    from ng.networking.routing import ShortestPathRouting
    from ng.mec.entity import Entity
    from ng.mec.cpu import SimpleSingleThreadedCPU
    from ng.mec.service import ExampleProc, ExampleGen
    from ng.mec.orchestrator import SimpleOrchestrator

    phy_env = PhysicalEnvironment(Coords2D(0, 0), Coords2D(200, 100))
    sim = Simulation(phy_env, ShortestPathRouting, SimpleOrchestrator)

    entities = [
        Entity(sim, 0, SimpleSingleThreadedCPU.create_type(1000)),
        Entity(sim, 1, SimpleSingleThreadedCPU.create_type(100)),
        Entity(sim, 2, SimpleSingleThreadedCPU.create_type(100)),
    ]
    devs = entities

    devs[0].attach_if(EthernetInterface(sim, 0))

    devs[1].attach_if(EthernetInterface(sim, 0))
    devs[1].attach_if(EthernetInterface(sim, 1))

    devs[2].attach_if(EthernetInterface(sim, 0))
    devs[2].attach_if(EthernetInterface(sim, 1))

    FiberConnection(sim, 2, devs[0].intf(0), devs[1].intf(0))
    FiberConnection(sim, 3, devs[1].intf(1), devs[2].intf(0))

    # static orchestration:

    entities[0].deploy_service(ExampleProc(sim, 0, "ExampleProc_i0"))
    gw = GW(sim, 0, "ExampleProc")
    gw.mapping["ExampleProc"] = ["ExampleProc_i0"]
    entities[1].deploy_service(gw)
    entities[2].deploy_service(ExampleGen(sim, 1, "ExampleGen"))

    entities[2].dns_cache["ExampleProc"] = 1
    entities[1].dns_cache["ExampleProc_i0"] = 0

    # but ideally, this should suffice:
    #entities[2].deploy_service(ExampleGen(sim, 1, "ExampleGen"))

    return sim

def test4():
    sim = dummy_sim_mec()
    sim.run(200)

    for ev in sim.eventlog.events:
        print(ev.time, ev.component, ev.type, ev.data)

    print(sim.metric_writer.metrics)
    print(sim.metric_writer.metrics[1].get_values())

test4()
