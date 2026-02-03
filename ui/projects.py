import json
import os
import threading
import time
import uuid
from typing import Type, Dict
import pathlib
import datetime

import simpy

from ng import config
from ng.config import load_config, get_type
from ng.metrics import Metric
from ng.networklog import NetworkLog
from ng.eventlog import Event
from ng.simulation import Simulation

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

class Run:

    def __init__(self, p, run_id, thread, run_meta, status, sim, config, topologies, events, metrics):
        self.run_p = p
        self.id = run_id
        self.thread = thread
        self.creation_time = run_meta["created"]
        self.status = status
        self.started = run_meta["started"]
        self.stopped = run_meta["stopped"]
        self.duration_ts = run_meta["duration_ts"]
        self.sim: Simulation = sim
        self.config = config
        self.ms_per_ts = run_meta["ms_per_ts"]
        self.topologies = topologies
        self.events = events
        self.metrics = metrics
        self.stop_ev = None

        self.meta_p = pjoin(p, "run.ngs")
        self.metrics_p = pjoin(p, "metrics")
        self.topologies_p = pjoin(p, "topologies")
        self.events_p = pjoin(p, "events.byline")

    def start(self):
        if self.status != "CREATED":
            print(f"Cannot start run {self.id}, already running or done")
            return False

        meta_p = self.meta_p

        with open(meta_p) as f:
            meta = json.load(f)

        self.status = "RUNNING"
        self.started = datetime.datetime.utcnow().isoformat()

        meta["started"] = self.started
        with open(meta_p, "w") as f:
            json.dump(meta, f)

        env = self.sim.env
        stop_ev = simpy.Event(env)

        def do():
            simulator: Simulation = self.sim
            env = simulator.env

            def log():
                while True:
                    time.sleep(.1)
                    yield env.timeout(10)

                    metrics = []

                    for metric in simulator.metric_writer.metrics:
                        comp = str(metric.comp)
                        name = metric.name

                        metrics.append({
                            "comp": comp,
                            "name": name,
                            "values": metric.get_values(),
                            "typ": type(metric)
                        })

                    self.metrics = metrics
                    self.topologies = simulator.networklog.get_states()
                    self.events = self.sim.eventlog.events

                    self.write_to_disk()

            env.process(log())
            simulator.run(stop_ev)
            self.status = "STOPPED"
            self.stopped = datetime.datetime.utcnow().isoformat()
            self.duration_ts = env.now

            metrics = []
            for metric in simulator.metric_writer.metrics:
                comp = str(metric.comp)
                name = metric.name

                metrics.append({
                    "comp": comp,
                    "name": name,
                    "values": metric.get_values(),
                    "typ": type(metric)
                })
            self.topologies = simulator.networklog.get_states()
            self.events = self.sim.eventlog.events

            self.write_to_disk()

            print("> STOPPED RUN", self.id, env.now)

        thr = threading.Thread(target=do, args=[])
        self.thread = thr
        self.stop_ev = stop_ev
        thr.start()
        return True

    def is_running(self):
        return self.status == "RUNNING"

    def stop(self):
        if not self.is_running():
            print(f"Cannot stop run {self.id}: is not running")
            return False
        self.stop_ev.succeed()
        return True

    def get_metrics(self):
        return [
            {
                "comp": m["comp"],
                "name": m["name"],
                "values": m["values"],
            }
            for m in self.metrics]

    def write_to_disk(self):
        with open(self.meta_p, "w") as f:
            json.dump({
                "created": self.creation_time,
                "started": self.started,
                "stopped": self.stopped,
                "duration_ts": self.duration_ts,
                "ms_per_ts": self.ms_per_ts
            }, f)

        metrics_p = self.metrics_p
        topologies_p = self.topologies_p
        events_p = self.events_p

        evs = [ev.serialize() for ev in self.events]
        with open(events_p, "w") as f:
            json.dump(evs, f)

        for metric in self.metrics:
            comp = metric["comp"]
            name = metric["name"]
            typ = metric["typ"]

            meta = {
                "comp": comp,
                "name": name,
                "_type": config.get_type_fqn_from_type(typ)
            }

            metric_p = pjoin(metrics_p, comp, name)
            ensure_dir_exists(metric_p)

            with open(pjoin(metric_p, ".ngs"), "w") as f:
                json.dump(meta, f)

            with open(pjoin(metric_p, "values"), "w") as f:
                typ.serialize_values(f, metric["values"])

        NetworkLog.write_states_to_disk(self.topologies, topologies_p)

    @staticmethod
    def load_from_disk(run_p, run_id):
        with open(pjoin(run_p, "run.ngs")) as f:
            run_meta = json.load(f)

        config_p = pjoin(run_p, "config.json")
        with open(config_p, "r") as f:
            config = json.load(f)

        with open(pjoin(run_p, "events.byline"), "r") as f:
            evs = [Event.deserialize(ev) for ev in json.load(f)]

        metrics_p = pjoin(run_p, "metrics")
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
                        typ: Type[Metric] = get_type(meta["_type"])

                        with open(pjoin(metric_p, "values"), "r") as f:
                            values = typ.deserialize_values(f)

                        metrics.append({
                            "comp": comp,
                            "name": name,
                            "values": values,
                            "typ": typ
                        })

        topologies = NetworkLog.load_states_from_disk(pjoin(run_p, "topologies"))

        return Run(run_p,  run_id,None, run_meta, "DEAD", None, config, topologies, evs, metrics)

    @staticmethod
    def create(run_p, run_id, config):
        print(config)
        sim = load_config(config)

        os.mkdir(run_p)

        config_p = pjoin(run_p, "config.json")
        with open(config_p, "w") as f:
            json.dump(config, f)

        with open(pjoin(run_p, "events.byline"), "w") as f:
            f.write("{}")

        os.mkdir(pjoin(run_p, "metrics"))
        os.mkdir(pjoin(run_p, "topologies"))

        run_meta = {
                "created": datetime.datetime.utcnow().isoformat(),
                "started": None,
                "stopped": None,
                "duration_ts": 0,
                "ms_per_ts": sim.ms_per_ts
            }

        with open(pjoin(run_p, "run.ngs"), "w") as f:
            json.dump(run_meta, f)

        return Run(run_p, run_id, None, run_meta, "CREATED", sim, config, [], [], [])


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

        for run_id in self.runs.keys():
            self.runs[run_id] = Run.load_from_disk(pjoin(self.runs_p, run_id), run_id)

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

    def start_run(self, run_id):
        if run_id not in self.runs:
            print(f"Cannot start run {run_id}: doesn't exist")
            return False

        return self.runs[run_id].start()

    def create_run(self):
        run_id = str(uuid.uuid1())
        r = Run.create(pjoin(self.runs_p, run_id), run_id, self.config)
        self.runs[run_id] = r
        return run_id

    def stop_run(self, run_id):
        if run_id not in self.runs:
            print(f"Cannot stop run {run_id}: doesn't exist")
            return False

        return self.runs[run_id].stop()
