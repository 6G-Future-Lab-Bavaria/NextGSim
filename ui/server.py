import os
from copy import deepcopy
from typing import Union

import flask
from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
from flask import request
from networkx import MultiDiGraph

from ng import config
from ui.projects import Project, Run
import time
import json

from ng.simulation import Simulation

projects_folder = os.path.join(os.getcwd(), "ui/projects")

root = os.getcwd()

app = Flask(__name__, static_url_path='', template_folder="templates/")
sock = Sock(app)
CORS(app)
Project.load_from_disk(projects_folder)

# ---------- WEBSOCKET ----------------

@sock.route("/api/projects/<string:proj_name>/runs/<string:run_id>/ws")
def run_ws(ws, proj_name, run_id):
    #projects = Project.load_from_disk(projects_folder)
    if proj_name not in Project.projects:
        return "project not found", 404

    project = Project.get_project(proj_name)
    if run_id not in project.runs:
        return "run not found", 404

    run = project.runs[run_id]

    if run.status != "DEAD":
        sim: Simulation = run.sim
        while run.is_running():
            time.sleep(1)
            ws.send(json.dumps({
                "type": "TIME",
                "data": sim.env.now
            }))

    ws.send(json.dumps({
        "type": "END",
        "data": run.duration_ts
    }))

# ---------- BACKEND ------------------

@app.get("/api/projects")
def get_projects():
    Project.get_project("")
    #return list(Project.load_from_disk(projects_folder).keys())
    return list(Project.projects.keys())

@app.post("/api/projects/<string:name>")
def post_projects(name):
    res = Project.create(projects_folder, name)
    if res:
        return name, 200
    else:
        return "", 400

@app.get("/api/projects/<string:name>/config")
def get_config(name):
    #projects = Project.load_from_disk(projects_folder)
    proj = Project.get_project(name)
    if not proj:
        return "", 404
    return proj.config, 200

@app.post("/api/projects/<string:project>/config")
def post_config(project):
    config = flask.request.json
    #projects = Project.load_from_disk(projects_folder)
    # todo: validate config somehow?
    proj = Project.get_project(project)
    if not proj:
        return "", 404
    proj.overwrite_config(config)
    return ('', 200)

@app.get("/api/projects/<string:project>/runs")
def get_runs(project):
    #projects = Project.load_from_disk(projects_folder)
    proj = Project.get_project(project)
    if not proj:
        return "", 404
    return [{
        "run_id": run_id,
        "started": run.started,
        "stopped": run.stopped,
        "status": run.status,
    } for run_id, run in proj.runs.items()], 200

@app.get("/api/projects/<string:proj_name>/runs/<string:run_id>")
def get_run(proj_name, run_id):
    #projects = Project.load_from_disk(projects_folder)
    project = Project.get_project(proj_name)
    if not project:
        return "project not found", 404

    if run_id not in project.runs:
        return "run not found", 404

    run = project.runs[run_id]

    return {
        "config": run.config,
        "status": run.status,
        "duration_ts": run.duration_ts
    }, 200

@app.post("/api/projects/<string:project>/runs")
def post_runs(project):
    #projects = Project.load_from_disk(projects_folder)
    project = Project.get_project(project)

    if not project:
        return "", 404

    try:
        run_id = project.create_run()
    except (ModuleNotFoundError, ImportError) as e:
        return (e, 400)

    if run_id is None:
        return ('', 500)

    # start already
    success = project.start_run(run_id)
    return run_id, (200 if success else 500)

@app.post("/api/projects/<string:proj_name>/runs/<string:run_id>/stop")
def post_stop_runs(proj_name, run_id):
    project = Project.get_project(proj_name)

    if not project:
        return "project not found", 404

    if run_id not in project.runs:
        return "run not found", 404

    run = project.runs[run_id]

    if not run.is_running():
        return "not running", 400

    project.stop_run(run_id)

    return "", 200

@app.get("/api/projects/<string:proj_name>/runs/<string:run_id>/metrics")
def get_metrics(proj_name, run_id):
    project = Project.get_project(proj_name)

    if not project:
        return "project not found", 404

    if run_id not in project.runs:
        return "run not found", 404

    run: Run = project.runs[run_id]

    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    views = []

    if from_ts is None:
        from_ts = 0
    else:
        from_ts = float(from_ts)

    if to_ts is None:
        if run.is_running():
            to_ts = run.sim.env.now
        else:
            to_ts = run.duration_ts
    else:
        to_ts = float(to_ts)

    for metric in run.metrics:
        comp, data = metric["typ"].generate_view(metric["values"], from_ts, to_ts, **request.args.to_dict())
        views.append({
            "comp": metric["comp"],
            "name": metric["name"],
            "ui_comp": comp,
            "data": data
        })

    return views

@app.get("/api/projects/<string:proj_name>/runs/<string:run_id>/events")
def get_events(proj_name, run_id):
    project = Project.get_project(proj_name)

    if not project:
        return "project not found", 404

    if run_id not in project.runs:
        return "run not found", 404

    run: Run = project.runs[run_id]

    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    if from_ts is None:
        from_ts = 0
    else:
        from_ts = float(from_ts)

    if to_ts is None:
        if run.is_running():
            to_ts = run.sim.env.now
        else:
            to_ts = run.duration_ts
    else:
        to_ts = float(to_ts)

    # filter by time
    evs = []

    # assumes run.events are sorted by time

    for event in run.events:
        if event.time < from_ts:
            continue
        if event.time > to_ts:
            break
        evs.append(event)

    # group by comp
    comps = {}
    for ev in evs:
        comp = ev.component_meta["name"] + "/" + ev.component_meta["ref"]
        if comp not in comps:
            comps[comp] = []
        comps[comp].append(ev)

    views = []
    min_ts_between = float(request.args["min_ts_between"])

    for comp in comps.keys():
        evs = comps[comp]

        groups = []
        i = 0
        n = len(evs)

        while i < n:
            j = i+1
            t = evs[i].time
            curr_group_evs = [evs[i]]

            while j < n and (evs[j].time - t) < min_ts_between:
                curr_group_evs.append(evs[j])
                t = evs[j].time
                j += 1

            groups.append({
                "from_ts": curr_group_evs[0].time,
                "to_ts": curr_group_evs[-1].time,
                "evs": [{
                    "comp": comp,
                    "time": ev.time,
                    "type": ev.type,
                    "data": ev.data
                } for ev in curr_group_evs]
            })

            i = j

        views.append({
            "comp": comp,
            "groups": groups
        })

    return views

@app.get("/api/projects/<string:proj_name>/runs/<string:run_id>/topology")
def get_topology(proj_name, run_id):
    project = Project.get_project(proj_name)

    if not project:
        return "project not found", 404

    if run_id not in project.runs:
        return "run not found", 404

    run: Run = project.runs[run_id]

    time_ts = float(request.args.get("time"))

    network_state: Union[MultiDiGraph, None] = None

    for t,net in run.topologies:
        if t > time_ts:
            break
        network_state = net

    if network_state is None:
        return "", 404

    def get_links():
        for n0, n1, a in network_state.edges(data=True):
            edges = network_state[n0][n1].keys()  # list of connected interfaces
            for [if0, if1] in edges:
                yield [n0, if0, n1, if1]

    topology = {
        "nodes": [
            {
                "id": node_id,
                "is_mec": attrs["is_mec"]
            }
            for (node_id, attrs) in network_state.nodes.items()
        ],
        "links": [
            {
                "from": { "node": n0, "if": if0 },
                "to": { "node": n1, "if": if1 },
            }
            for [n0, if0, n1, if1] in get_links()
        ]
    }

    return topology

@app.get("/api/projects/<string:proj_name>/runs/<string:run_id>/config")
def get_run_config(proj_name, run_id):
    project = Project.get_project(proj_name)

    if not project:
        return "project not found", 404

    if run_id not in project.runs:
        return "run not found", 404

    run: Run = project.runs[run_id]

    return run.config

# ------------ FRONTEND ---------------

@app.route("/static/<path:path>")
def send_js(path):
    return flask.send_from_directory('dist', path)

@app.get("/")
def index():
    return flask.render_template("index.html", page="index")

@app.get("/projects/<string:proj>/")
def project(proj):
    if proj not in Project.projects:
        return flask.redirect("/")
    return flask.render_template("index.html", page="project", project=proj)

@app.get("/projects/<string:proj>/runs/<string:run>")
def run(proj, run):
    if proj not in Project.projects:
        return flask.redirect("/")
    if run not in Project.projects[proj].runs:
        return flask.redirect("/projects/" + proj)
    return flask.render_template("index.html", page="run", project=proj, run=run)

@app.get("/projects/<string:proj>/<path:path>")
def project_catchall(proj, path):
    return flask.render_template("index.html", page="project", project=proj)