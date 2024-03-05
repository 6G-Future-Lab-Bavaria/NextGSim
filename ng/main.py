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
    sim = Simulation(ShortestPathRouting, lambda e : e)

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

    #phy_env = PhysicalEnvironment(Coords2D(0, 0), Coords2D(200, 100))
    sim = Simulation(ShortestPathRouting, SimpleOrchestrator)

    entities = [
        Entity(sim, 0, SimpleSingleThreadedCPU(1000, sim)),
        Entity(sim, 1, SimpleSingleThreadedCPU(100, sim)),
        Entity(sim, 2, SimpleSingleThreadedCPU(100, sim)),
    ]
    devs = entities

    devs[0].attach_if(EthernetInterface(sim, 0))

    devs[1].attach_if(EthernetInterface(sim, 0))
    devs[1].attach_if(EthernetInterface(sim, 1))

    devs[2].attach_if(EthernetInterface(sim, 0))
    devs[2].attach_if(EthernetInterface(sim, 1))

    FiberConnection(sim, 2, [devs[0].intf(0), devs[1].intf(0)])
    FiberConnection(sim, 3, [devs[1].intf(1), devs[2].intf(0)])

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

def create_from_config():
    config = {
        "simulation": {
            "_type": "ng.simulation.Simulation", # fully qualified type name
            "routing": {
                "_type": "ng.networking.routing.ShortestPathRouting",
            },
            "orchestrator": {
                "_type": "ng.mec.orchestrator.SimpleOrchestrator"
            },
            "ms_per_ts": 1
        },
        "nodes": [
            {
                "_type": "ng.mec.entity.Entity",
                "id": 0,
                "ifs": [
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth0",
                    },
                ],
                "cpu": {
                    "_type": "ng.mec.cpu.SimpleSingleThreadedCPU",
                    "clock_speed": 1000,
                },
                "services": [ # services deployed at start
                    {
                        "_type": "ng.mec.service.ExampleProc",
                        "id": 0,
                        "name": "ExampleProc_i0",
                    }
                ],
                "dns": { # dns entries

                }
            },
            {
                "_type": "ng.mec.entity.Entity",
                "id": 1,
                "ifs": [
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth0",
                    },
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth1",
                    }
                ],
                "cpu": {
                    "_type": "ng.mec.cpu.SimpleSingleThreadedCPU",
                    "clock_speed": 100,
                },
                "services": [  # services deployed at start
                    {
                        "_type": "ng.mec.service.GW",
                        "id": 0,
                        "name": "ExampleProc",
                        "mapping": {
                            "ExampleProc": ["ExampleProc_i0"],
                        }
                    }
                ],
                "dns": {  # dns entries
                    "ExampleProc_i0": 0,
                }
            },
            {
                "_type": "ng.mec.entity.Entity",
                "id": 2,
                "ifs": [
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth0",
                    },
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth1",
                    }
                ],
                "cpu": {
                    "_type": "ng.mec.cpu.SimpleSingleThreadedCPU",
                    "clock_speed": 100,
                },
                "services": [  # services deployed at start
                    {
                        "_type": "ng.mec.service.ExampleGen",
                        "id": 1,
                        "name": "ExampleGen",
                    }
                ],
                "dns": {  # dns entries
                    "ExampleProc": 1,
                }
            },
            {
                "_type": "ng.networking.node.Node",
                "id": 3,
                "ifs": [
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth0",
                    },
                    {
                        "_type": "ng.networking.interface.eth.EthernetInterface",
                        "id": "eth1",
                    }
                ],
            }
            # routers, ...
        ],
        "connections": [
            {
                "_type": "ng.networking.interface.eth.FiberConnection",
                "length": 2,
                "ifs": [
                    # references to connected ifs
                    {"node": 0, "if": "eth0"},
                    {"node": 1, "if": "eth0"},
                ]
            },
            {
                "_type": "ng.networking.interface.eth.FiberConnection",
                "length": 2,
                "ifs": [
                    # references to connected ifs
                    {"node": 1, "if": "eth1"},
                    {"node": 2, "if": "eth0"},
                ]
            }
        ],
    }

    import sys, importlib

    def get_type(fqn):
        module = ".".join(fqn.split(".")[:-1])
        typename = fqn.split(".")[-1]

        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            return None

        try:
            typ = getattr(sys.modules[module], typename)
        except AttributeError:
            return None

        return typ

    # resolve types

    def res(tree):
        if type(tree) == dict:
            obj = {}
            for k,v in tree.items():
                if k == "_type":
                    typ = get_type(v)
                    if not typ:
                        raise ImportError(str(v) + " not found.")
                    obj[k] = typ
                else:
                    obj[k] = res(v)
            return obj
        elif type(tree) == list:
            return [res(t) for t in tree]
        return tree

    def init(config):
        sim = config["simulation"]
        nodes = config["nodes"]
        conns = config["connections"]
        sim_t = sim["_type"]
        simulation = sim_t.from_config(sim)

        def res(tree):
            if type(tree) == dict:
                obj = {}
                for k, v in tree.items():
                    if k == "_type":
                        continue # skip
                    else:
                        obj[k] = res(v)
                if "_type" in tree.keys():
                    conf = { **obj, "sim": simulation }
                    return tree["_type"](**conf) # support optional from_config
                return obj
            elif type(tree) == list:
                return [res(t) for t in tree]
            return tree

        nodes = res(nodes)
        nodes = { n.id: n for n in nodes }

        connections = []

        for con in conns:
            typ = con["_type"]
            del con["_type"]
            ifs = []
            for intf_ref in con["ifs"]:
                node, intf = intf_ref["node"], intf_ref["if"]
                ifs.append(nodes[node].intf(intf))

            del con["ifs"]

            connection = typ(**{ **con, "sim": simulation, "ifs": ifs })
            connections.append(connection)

        return simulation, nodes, connections

    config = res(config)
    tr = init(config)

    sim = tr[0]
    return sim

    sim.run(200)

    for ev in sim.eventlog.events:
        print(ev.time, ev.component, ev.type, ev.data)

    print(sim.metric_writer.metrics)
    print(sim.metric_writer.metrics[1].get_values())


def test4():
    sim = dummy_sim_mec()
    sim.run(200)

    for ev in sim.eventlog.events:
        print(ev.time, ev.component, ev.type, ev.data)

    print(sim.metric_writer.metrics)
    print(sim.metric_writer.metrics[1].get_values())

create_from_config()
#test4()
