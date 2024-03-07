from typing import Dict

import flask
from flask import Flask
import os
from flask_cors import CORS
import json
from flask_sock import Sock
from config import load_config
import time
from shutil import copy
import threading
from simulation import Simulation

projects_folder = os.path.join(os.getcwd(), "ui/projects")

root = os.getcwd()

app = Flask(__name__, static_url_path='/static/')
sock = Sock(app)
CORS(app)


class Project:

    def __init__(self, p):
        self.root_p = p
        self.runs_p = os.path.join(p, "runs")
        self.config_p = os.path.join(p, "config.json")
        self.runs = {}

        if not os.path.exists(self.runs_p):
            os.mkdir(self.runs_p)

        if not os.path.exists(self.config_p):
            with open(self.config_p, "w") as f:
                f.write("{}")

        self._read_config()

        with os.scandir(self.runs_p) as it:
            for entry in it:
                self.runs[entry.name] = {}

        for run in self.runs.keys():
            self.load_run(run)

    def _read_config(self):
        try:
            with open(self.config_p, "r") as f:
                self.config = json.load(f)
        except Exception as e:
            raise Exception("Error while reading project config:", e)

    def overwrite_config(self, config):
        with open(self.config_p, "w") as f:
            json.dump(config, f)
        self._read_config()

    def get_run_names(self):
        return self.runs.keys()

    def create_run(self):
        t = str(time.time_ns())
        os.mkdir(os.path.join(self.runs_p, t))
        config_p = os.path.join(self.runs_p, t, "config.json")
        with open(config_p, "w") as f:
            json.dump(self.config, f)
        self.runs[t] = {
            "thr": None,
            "simulation": load_config(self.config),
            "events": [],
            "metrics": [],
            "topologies": [],
        }
        return t

    def load_run(self, run):
        config_p = os.path.join(self.runs_p, run, "config.json")
        with open(config_p, "r") as f:
            config = json.load(f)
        self.runs[run] = {
            "thr": None,
            "simulation": load_config(config),
            "events": [],
            "metrics": [],
            "topologies": [],
        }

    def start_run(self, run, t):
        def do():
            events_p = os.path.join(self.runs_p, run, "events.byline")
            simulator: Simulation = self.runs[run]["simulation"]
            env = simulator.env

            def log():
                while True:
                    time.sleep(.1)
                    print("T", env.now)
                    yield env.timeout(10)
                    print("T1", env.now)
                    with open(events_p, "w") as f:
                        json.dump([ev.serialize() for ev in simulator.eventlog.events], f)

            env.process(log())
            simulator.run(t)

        thr = threading.Thread(target=do, args=[])
        self.runs[run]["thr"] = thr
        thr.start()


sims: Dict[str, Project] = {}

def load_from_disk():
    projects = []
    with os.scandir(projects_folder) as it:
        for entry in it:
            if entry.name.startswith(".") or not entry.is_dir():
                continue
            if not os.path.exists(os.path.join(entry.path, ".ngs")):
                continue
            sims[entry.name] = Project(os.path.join(entry.path))
            projects.append(entry.name)

@sock.route("/projects/<string:project>/api/runs/<string:run>/ws")
def run_ws(ws, project, run):
    sim: Simulation = sims[project].runs[run]["simulation"]
    i_ev = 0
    while True:
        time.sleep(1)
        ws.send(json.dumps({
            "type": "TIME",
            "data": sim.env.now
        }))
        events = sim.eventlog.events[i_ev:]
        i_ev += len(events)
        ws.send(json.dumps({
            "type": "EVENTS",
            "data": [ev.serialize() for ev in events],
        }))
        metrics = sim.metric_writer.metrics # todo: better streaming
        ws.send(json.dumps({
            "type": "METRICS",
            "data": [
                {
                    "comp": str(metric.comp),
                    "name": metric.name,
                    "values": metric.get_values(),
                } for metric in metrics
            ]
        }))

@app.post("/projects/<string:project>/api/runs/")
def create_run(project):
    run = sims[project].create_run()
    if run is None:
        return ('', 500)
    return ('', 204)

@app.post("/projects/<string:project>/api/runs/<string:run>/load")
def load_run(project, run):
    sims[project].load_run(run)
    return ('', 204)

@app.post("/projects/<string:project>/api/runs/<string:run>/start")
def start_sim(project, run):
    if project not in sims:
        return ('', 400)
    sims[project].start_run(run, 500)
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

@app.route("/projects/<string:project>/api/runs/<string:run>/network")
def get_network(project, run):
    if project not in sims:
        return ('', 400)
    sim = sims[project].runs[run]["simulation"]
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

@app.route("/projects/<string:project>/api/runs/<string:run>/events")
def get_events(project, run):
    if project not in sims:
        return ('', 400)
    sim = sims[project].runs[run]["simulation"]
    return [
        ev.serialize() for ev in sim.eventlog.events
    ]

@app.route("/projects/<string:project>/api/runs/<string:run>/metrics")
def get_metrics(project, run):
    if project not in sims:
        return ('', 400)
    sim = sims[project].runs[run]["simulation"]
    return [
        {
            "comp": str(metric.comp),
            "name": metric.name,
            "values": metric.get_values(),
        } for metric in sim.metric_writer.metrics
    ]

@app.get("/projects/<string:project>/api/config")
def get_config(project):
    if project in sims:
        return sims[project].config
    return ('', 404)

@app.post("/projects/<string:project>/api/config")
def post_config(project):
    config = flask.request.json
    # todo: validate config somehow?
    if project in sims:
        sims[project].overwrite_config(config)
        return ('', 200)
    else:
        return ('', 404)

@app.get("/projects/<string:project>/api/runs")
def get_runs(project):
    if project in sims:
        return list(sims[project].runs.keys())
    return ('', 404)

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

load_from_disk()