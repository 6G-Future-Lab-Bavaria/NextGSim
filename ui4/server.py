import os

import flask
from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
from projects import Project
import time
import json

from simulation import Simulation

projects_folder = os.path.join(os.getcwd(), "ui4/projects")

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

    i_ev = 0

    if run["status"] != "DEAD":
        sim: Simulation = run["simulation"]
        while run["status"] == "RUNNING":
            time.sleep(1)
            ws.send(json.dumps({
                "type": "TIME",
                "data": sim.env.now
            }))
            #events = sim.eventlog.events[i_ev:]
            events = run["events"]
            ws.send(json.dumps({
                "type": "EVENTS",
                "data": events[i_ev:],
            }))
            i_ev = len(events)
            ws.send(json.dumps({
                "type": "METRICS",
                "data": run["metrics"], # todo: stream this
            }))
            topology = {
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
            ws.send(json.dumps({
                "type": "TOPOLOGY",
                "data": topology
            }))
        ws.send(json.dumps({
            "type": "END",
        }))

    events = run["events"]
    ws.send(json.dumps({
        "type": "EVENTS",
        "data": events[i_ev:],
    }))
    ws.send(json.dumps({
        "type": "METRICS",
        "data": run["metrics"],  # todo: stream this
    }))



# ---------- BACKEND ------------------

@app.get("/api/projects")
def get_projects():
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
    if name in Project.projects:
        return Project.get_project(name).config, 200
    else:
        return "", 404

@app.post("/api/projects/<string:project>/config")
def post_config(project):
    config = flask.request.json
    #projects = Project.load_from_disk(projects_folder)
    # todo: validate config somehow?
    if project in Project.projects:
        Project.get_project(project).overwrite_config(config)
        return ('', 200)
    else:
        return ('', 404)

@app.get("/api/projects/<string:project>/runs")
def get_runs(project):
    #projects = Project.load_from_disk(projects_folder)
    if project not in Project.projects:
        return "", 404
    return [{
        "run_id": run_id,
        "started": run["started"],
        "stopped": run["stopped"],
        "status": run["status"],
    } for run_id, run in Project.get_project(project).runs.items()], 200

@app.get("/api/projects/<string:proj_name>/runs/<string:run_id>")
def get_run(proj_name, run_id):
    #projects = Project.load_from_disk(projects_folder)
    if proj_name not in Project.projects:
        return "project not found", 404

    project = Project.get_project(proj_name)
    if run_id not in project.runs:
        return "run not found", 404

    run = project.runs[run_id]

    return {
        "config": run["config"],
        "status": run["status"],
    }, 200

@app.post("/api/projects/<string:project>/runs")
def post_runs(project):
    #projects = Project.load_from_disk(projects_folder)
    if project not in Project.projects:
        return "", 404
    project = Project.get_project(project)
    run_id = project.create_run()
    if run_id is None:
        return ('', 500)

    # start already
    success = project.start_run(run_id)
    return run_id, (200 if success else 500)

@app.post("/api/projects/<string:proj_name>/runs/<string:run_id>/stop")
def post_stop_runs(proj_name, run_id):
    if proj_name not in Project.projects:
        return "project not found", 404

    project = Project.get_project(proj_name)
    if run_id not in project.runs:
        return "run not found", 404

    run = project.runs[run_id]

    if run["status"] != "RUNNING":
        return "not running", 400

    project.stop_run(run_id)

    return "", 200

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