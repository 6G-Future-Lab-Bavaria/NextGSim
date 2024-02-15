import json

logger = None


def init(file, sim):
    global logger
    logger = {
        "sim": sim,
        "file": open(file, "w")
    }


def log(comp: str, msg: object):
    global logger
    logger["file"].write(str(logger["sim"].env.now) + "," + comp + "," + json.dumps(msg) + "\n")


def close():
    global logger
    logger["file"].close()
