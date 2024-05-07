import os

import flask
from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
from projects import Project


projects_folder = os.path.join(os.getcwd(), "ui4/projects")

root = os.getcwd()

app = Flask(__name__, static_url_path='', template_folder="templates/")
sock = Sock(app)
CORS(app)
Project.load_from_disk(projects_folder)

# ---------- WEBSOCKET ----------------



# ---------- BACKEND ------------------

@app.get("/api/projects")
def get_projects():
    return list(Project.load_from_disk(projects_folder).keys())

@app.post("/api/projects/<string:name>")
def post_projects(name):
    res = Project.create(projects_folder, name)
    print(name)
    if res:
        return name, 200
    else:
        return "", 400

@app.get("/api/projects/<string:name>/config")
def get_config(name):
    projects = Project.load_from_disk(projects_folder)
    if name in projects:
        return projects[name].config, 200
    else:
        return "", 404

@app.post("/api/projects/<string:project>/config")
def post_config(project):
    config = flask.request.json
    projects = Project.load_from_disk(projects_folder)
    # todo: validate config somehow?
    if project in projects:
        projects[project].overwrite_config(config)
        return ('', 200)
    else:
        return ('', 404)

@app.get("/api/projects/<string:project>/runs")
def get_runs(project):
    projects = Project.load_from_disk(projects_folder)
    if project not in projects:
        return "", 404
    return list(projects[project].runs.keys()), 200

@app.post("/api/projects/<string:project>/runs/<string:run>/load")
def post_runs_load(project, run):
    projects = Project.load_from_disk(projects_folder)
    if project not in projects:
        return "", 404
    project = projects[project]
    if run not in project.runs:
        return "", 404
    run = project.runs[run]



# ------------ FRONTEND ---------------

@app.route("/static/<path:path>")
def send_js(path):
    return flask.send_from_directory('dist', path)

@app.get("/")
def index():
    return flask.render_template("index.html", page="index")

@app.get("/projects/<string:proj>/")
def project(proj):
    return flask.render_template("index.html", page="project", project=proj)

@app.get("/projects/<string:proj>/runs/<string:run>")
def run(proj, run):
    return flask.render_template("index.html", page="run", project=proj, run=run)

@app.get("/projects/<string:proj>/<path:path>")
def project_catchall(proj, path):
    return flask.render_template("index.html", page="project", project=proj)