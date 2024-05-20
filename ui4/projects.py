import json
import os
import threading
import time
import uuid
from typing import Type, Dict
import pathlib
import datetime

import simpy

import config
from config import load_config, get_type
from metrics import Metric
from ng.eventlog import Event
from simulation import Simulation

# Folder structure:
# projects
# - [project]
# -- .ngs
# -- config.json
# -- runs
# --- [run]
# ---- config.json
# ---- events.byline
# ---- metrics
# ---- metrics.ngs
# ---- [comp]
# ----- [metric]

def ensure_dir_exists(path):
    so_far = []
    for part in pathlib.Path(path).parts:
        so_far.append(part)
        p = pjoin(*so_far)
        if not os.path.exists(p):
            os.mkdir(p)

pjoin = os.path.join

class Project:

    projects_path = ""
    alive = {}
    projects: Dict[str, "Project"] = {}

    @staticmethod
    def create(projects_path, project_name: str):
        # sanitize name
        project_name = project_name.strip()
        if project_name == "":
            return False

        proj_root = pjoin(projects_path, project_name)
        if os.path.exists(proj_root):
            return False

        os.mkdir(proj_root)
        ngs_path = pjoin(proj_root, ".ngs")
        open(os.path.abspath(ngs_path), "a").close()  # touch ngs file
        with open(os.path.abspath(pjoin(proj_root, "config.json")), "w") as f:
            f.write("{}")
        os.mkdir(pjoin(proj_root, "runs"))
        return True

    @staticmethod
    def get_project(project):
        # synchronize with disk

        remaining_projects = set(Project.projects.keys())

        with os.scandir(Project.projects_path) as it:
            for entry in it:
                if entry.name.startswith(".") or not entry.is_dir():
                    continue
                if not os.path.exists(pjoin(entry.path, ".ngs")):
                    continue
                if entry.name not in Project.projects:
                    Project.projects[entry.name] = Project(pjoin(entry.path), entry.name)
                else:
                    # todo: check runs
                    remaining_projects.remove(entry.name)
                    pass

        if len(remaining_projects) > 0:
            print("WARNING: Disk out of sync: projects deleted on disk that are present in memory: ", remaining_projects)

        if project not in Project.projects:
            return None
        return Project.projects[project]

    @staticmethod
    def load_from_disk(projects_path):
        Project.projects_path = projects_path
        with os.scandir(projects_path) as it:
            for entry in it:
                if entry.name.startswith(".") or not entry.is_dir():
                    continue
                if not os.path.exists(pjoin(entry.path, ".ngs")):
                    continue
                Project.projects[entry.name] = Project(pjoin(entry.path), entry.name)

    def __init__(self, p, name):
        self.root_p = p
        self.runs_p = pjoin(p, "runs")
        self.config_p = pjoin(p, "config.json")
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
        t = time.time_ns()
        run_id = str(uuid.uuid1())

        run_p = pjoin(self.runs_p, run_id)
        os.mkdir(run_p)

        config_p = pjoin(run_p, "config.json")
        with open(config_p, "w") as f:
            json.dump(self.config, f)

        with open(pjoin(run_p, "events.byline"), "w") as f:
            f.write("{}")

        os.mkdir(pjoin(run_p, "metrics"))

        sim = load_config(self.config)

        with open(pjoin(run_p, "run.ngs"), "w") as f:
            json.dump({
                "time": t,
                "started": None,
                "stopped": None,
                "duration_ts": None,
                "ms_per_ts": sim.ms_per_ts
            }, f)

        self.runs[run_id] = {
            "thr": None,
            "creation_time": t,
            "status": "CREATED",
            "started": None,
            "stopped": None,
            "duration_ts": None,
            "simulation": sim,
            "config": self.config,
            "ms_per_ts": sim.ms_per_ts,
            "events": [],
            "metrics": [],
            "topologies": [],
        }
        return run_id

    def load_run(self, run):
        run_p = pjoin(self.runs_p, run)
        
        with open(pjoin(run_p, "run.ngs")) as f:
            run_meta = json.load(f)

        config_p = pjoin(run_p, "config.json")
        with open(config_p, "r") as f:
            config = json.load(f)

        with open(pjoin(run_p, "events.byline"), "r") as f:
            evs = [ Event.deserialize(ev) for ev in json.load(f) ]

        metrics_p = pjoin(self.runs_p, run, "metrics")
        metrics = []

        with os.scandir(metrics_p) as comp_it:
            for comp_entry in comp_it:
                comp = comp_entry.name
                with os.scandir(pjoin(metrics_p, comp)) as metric_it:
                    for metric_entry in metric_it:
                        metric_p = metric_entry.path
                        with open(pjoin(metric_p, ".ngs")) as f:
                            meta = json.load(f)
                        comp = meta["comp"]
                        name = meta["name"]
                        print(meta["_type"])
                        typ: Type[Metric] = get_type(meta["_type"])

                        with open(pjoin(metric_p, "values"), "r") as f:
                            values = typ.deserialize_values(f)

                        metrics.append({
                            "comp": comp,
                            "name": name,
                            "values": values
                        })

        # todo: load metrics
        self.runs[run] = {
            "thr": None,
            "creation_time": run_meta["time"],
            "status": "DEAD",
            "started": run_meta["started"],
            "stopped": run_meta["stopped"],
            "duration_ts": run_meta["duration_ts"],
            "simulation": None,
            "config": config,
            "ms_per_ts": run_meta["ms_per_ts"],
            "events": [ev.serialize() for ev in evs],
            "metrics": metrics,
            "topologies": [],
        }

    def start_run(self, run_id):
        if run_id not in self.runs or self.runs[run_id]["status"] != "CREATED":
            return False
        
        run_p = pjoin(self.runs_p, run_id)
        meta_p = pjoin(run_p, "run.ngs")
        with open(meta_p) as f:
            meta = json.load(f)

        run = self.runs[run_id]
        run["status"] = "RUNNING"
        run["started"] = datetime.datetime.utcnow().isoformat()

        meta["started"] = run["started"]
        with open(meta_p, "w") as f:
            json.dump(meta, f)

        env = run["simulation"].env
        stop_ev = simpy.Event(env)

        def do():
            metrics_p = pjoin(self.runs_p, run_id, "metrics")
            events_p = pjoin(self.runs_p, run_id, "events.byline")
            simulator: Simulation = self.runs[run_id]["simulation"]
            env = simulator.env

            def log():
                while True:
                    time.sleep(.1)
                    yield env.timeout(10)
                    evs = [ev.serialize() for ev in simulator.eventlog.events]
                    with open(events_p, "w") as f:
                        json.dump(evs, f)
                    metrics = []

                    for metric in simulator.metric_writer.metrics:
                        comp = str(metric.comp)
                        name = metric.name
                        typ = config.get_type_fqn(metric)

                        meta = {
                            "comp": comp,
                            "name": name,
                            "_type": typ
                        }

                        metric_p = pjoin(metrics_p, comp, name)
                        ensure_dir_exists(metric_p)

                        with open(pjoin(metric_p, ".ngs"), "w") as f:
                            json.dump(meta, f)

                        with open(pjoin(metric_p, "values"), "w") as f:
                            metric.serialize_values(f, metric.get_values())

                        metrics.append({
                            "comp": comp,
                            "name": name,
                            "values": metric.get_values()
                        })
                    topology = None # todo record topology
                    run["metrics"] = metrics
                    run["events"] = evs
                    run["topologies"].append(topology)

            env.process(log())
            simulator.run(stop_ev)
            run["status"] = "STOPPED"
            run["stopped"] = datetime.datetime.utcnow().isoformat()
            meta["stopped"] = run["stopped"]
            meta["duration_ts"] = env.now
            run["duration_ts"] = env.now
            with open(meta_p, "w") as f:
                json.dump(meta, f)
            print("> STOPPED RUN", run_id, env.now)

        thr = threading.Thread(target=do, args=[])
        self.runs[run_id]["thr"] = thr
        self.runs[run_id]["stop_ev"] = stop_ev
        thr.start()
        return True

    def stop_run(self, run_id):
        if run_id in self.runs and "stop_ev" in self.runs[run_id]:
            self.runs[run_id]["stop_ev"].succeed()
