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


def load_config(config):
    config = res(config)
    tr = init(config)

    sim = tr[0]
    return sim