import flask
from flask import Flask
import os
from flask_cors import CORS, cross_origin
import json

from config import load_config

projects_folder = os.path.join(os.getcwd(), "ui/projects")

root = os.getcwd()

app = Flask(__name__, static_url_path='/static/')
CORS(app)

sims = {}

def get_project_config(proj):
    p = os.path.join(projects_folder, proj, "config.json")
    print(p)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error while reading config:", e)
        return None

def overwrite_project_config(proj, config):
    p = os.path.join(projects_folder, proj, "config.json")
    if not os.path.exists(p):
        return False
    try:
        with open(p, "w") as f:
            json.dump(config, f)
            return True
    except Exception as e:
        print("Error while writing config:", e)
        return False

def get_run_names(proj):
    p = os.path.join(projects_folder, proj, "runs")
    if not os.path.exists(p):
        return None
    res = []
    with os.scandir(p) as it:
        for entry in it:
            ts = entry.name
            #details_path = os.path.join(entry.path, "details")
            res.append(ts)
    return res

@app.route("/projects/<string:project>/api/create")
def create_sim(project):
    config = get_project_config(project)
    if config is None:
        print("Bad config for project", project)
        return ('', 500)
    sims[project] = load_config(config)
    return ('', 204)

@app.route("/projects/<string:project>/api/start")
def start_sim(project):
    if project not in sims:
        return ('', 400)
    sims[project].run(200)
    return ('', 204)

@app.route("/projects/<string:project>/api/physical")
def get_ues(project):
    return {
        "area": {
            "lower_corner": 0,# sim.physical.lower_corner.serialize(),
            "higher_corner": 0,#sim.physical.higher_corner.serialize(),
        },
        "gnbs": [],
        "ues": [
            {
                "id": node.id,
                "coords": node.coords.serialize(),
            }
            for node in [] #sim.physical.nodes
        ]
    }

@app.route("/projects/<string:project>/api/network")
def get_network(project):
    if project not in sims:
        return ('', 400)
    sim = sims[project]
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
    if project not in sims:
        return ('', 400)
    sim = sims[project]
    return [
        ev.serialize() for ev in sim.eventlog.events
    ]

@app.route("/projects/<string:project>/api/metrics")
def get_metrics(project):
    if project not in sims:
        return ('', 400)
    sim = sims[project]
    return [
        {
            "comp": str(metric.comp),
            "name": metric.name,
            "values": metric.get_values(),
        } for metric in sim.metric_writer.metrics
    ]

@app.get("/projects/<string:project>/api/config")
def get_config(project):
    config = get_project_config(project)
    if config is None:
        print("Bad config for project", project)
        return ('', 500)
    return config

@app.post("/projects/<string:project>/api/config")
def post_config(project):
    config = get_project_config(project)
    if config is None:
        print("Bad config for project", project)
        return ('', 500)
    config = flask.request.json
    # todo: validate config somehow?
    success = overwrite_project_config(project, config)
    return ('', 200 if success else 500)

@app.get("/projects/<string:project>/api/runs")
def get_runs(project):
    runs = get_run_names(project)
    return runs

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

