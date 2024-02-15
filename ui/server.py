import flask
from flask import Flask
import typing
import os

from ng.simulation import Simulation
from ng.main import dummy_sim

projects_folder = os.path.join(os.getcwd(), "ui/projects")

root = os.getcwd()

app = Flask(__name__, static_url_path='/static/')

sim: typing.Optional[Simulation] = None

@app.route("/projects/<string:project>/api/create")
def create_sim(project):
    global sim
    sim = dummy_sim()
    return ('', 204)

@app.route("/projects/<string:project>/api/start")
def start_sim(project):
    sim.run(100)
    return ('', 204)

@app.route("/projects/<string:project>/api/physical")
def get_ues(project):
    return {
        "area": {
            "lower_corner": sim.physical.lower_corner.serialize(),
            "higher_corner": sim.physical.higher_corner.serialize(),
        },
        "gnbs": [],
        "ues": [
            {
                "id": node.id,
                "coords": node.coords.serialize(),
            }
            for node in sim.physical.nodes
        ]
    }

@app.route("/projects/<string:project>/api/network")
def get_network(project):
    return {
        "nodes": [
            {
                "id": node.id,
            }
            for node in sim.network.nodes
        ],
        "links": [
            {
                "from": { "node": n0, "if": if0 },
                "to": { "node": n1, "if": if1 },
            }
            for [n0, if0, n1, if1] in sim.network.get_links()
        ]
    }

@app.route("/projects/<string:project>/api/events")
def get_events(project):
    return [
        ev.serialize() for ev in sim.eventlog.events
    ]

@app.route("/tree/<path:path>")
def get_tree(path):
    path = os.path.normpath(path)
    while path.startswith("/"):  # remove leading /
        path = path[1:]
    folder = os.path.join(root, path)
    if not os.path.exists(folder):
        return "Not found", 404
    res = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                res.append([entry.name, "d"])
            elif entry.is_file():
                res.append([entry.name, "f"])
    return res

@app.route("/tree/")
def get_tree_root():
    return get_tree("")

# i think its best to hide the folder structure from the user and handle it only server-side

@app.get("/api/projects")
def get_projects():
    res = []
    with os.scandir(projects_folder) as it:
        for entry in it:
            if entry.name.startswith(".") or not entry.is_dir():
                continue
            if not os.path.exists(os.path.join(entry.path, ".ngs")):
                continue
            res.append(entry.name)
    return res


def create_project_structure(root):
    ngs_path = os.path.join(root, ".ngs")
    open(os.path.abspath(ngs_path), "a").close()  # touch ngs file
    os.mkdir(os.path.join(root, "scenarios"))
    os.mkdir(os.path.join(root, "runs"))


@app.post("/api/projects")
def create_projects():
    data = flask.request.get_json()
    name = data["name"] # todo only alphanumeric and _
    proj_root = os.path.join(projects_folder, name)
    if os.path.exists(proj_root):
        return "exists", 400
    os.mkdir(proj_root)
    create_project_structure(proj_root)
    return name, 200


@app.get("/")
def index():
    return flask.send_file("./index.html")


@app.get("/projects/<string:name>/")
def project(name):
    return flask.send_file("./app.html")

