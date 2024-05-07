import json
import os
import threading
import time
from typing import Dict

import simpy

from config import load_config
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
#

class Project:

    projects = {}

    @staticmethod
    def create(projects_path, project_name: str):
        # sanitize name
        project_name = project_name.strip()
        if project_name == "":
            return False

        proj_root = os.path.join(projects_path, project_name)
        if os.path.exists(proj_root):
            return False
        os.mkdir(proj_root)
        ngs_path = os.path.join(proj_root, ".ngs")
        open(os.path.abspath(ngs_path), "a").close()  # touch ngs file
        with open(os.path.abspath(os.path.join(proj_root, "config.json")), "w") as f:
            f.write("{}")
        os.mkdir(os.path.join(proj_root, "runs"))
        return True

    @staticmethod
    def load_from_disk(projects_path):
        projects = {}

        with os.scandir(projects_path) as it:
            for entry in it:
                if entry.name.startswith(".") or not entry.is_dir():
                    continue
                if not os.path.exists(os.path.join(entry.path, ".ngs")):
                    continue
                projects[entry.name] = Project(os.path.join(entry.path), entry.name)

        return projects


    def __init__(self, p, name):
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
            "is_live": True,
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
        with open(os.path.join(self.runs_p, run, "events.byline"), "r") as f:
            evs = [ Event.deserialize(ev) for ev in json.load(f) ]
        # todo: load metrics
        self.runs[run] = {
            "thr": None,
            "is_live": False,
            "simulation": None,
            "events": evs,
            "metrics": [],
            "topologies": [],
        }

    def start_run(self, run, t):
        if run not in self.runs or not self.runs[run]["is_live"]:
            return False

        env = self.runs[run]["simulation"].env
        stop_ev = simpy.Event(env)

        def do():
            metrics_p = os.path.join(self.runs_p, run, "metrics")
            events_p = os.path.join(self.runs_p, run, "events.byline")
            simulator: Simulation = self.runs[run]["simulation"]
            env = simulator.env

            def log():
                while True:
                    time.sleep(.1)
                    yield env.timeout(10)
                    with open(events_p, "w") as f:
                        json.dump([ev.serialize() for ev in simulator.eventlog.events], f)
                    for metric in simulator.metric_writer.metrics:
                        path = os.path.join(metrics_p, str(metric.comp)+"/"+metric.name)
                        with open(path) as f:
                            f.write(",".join(metric.get_values()))

            env.process(log())
            simulator.run(stop_ev)
            print("> STOPPED RUN", run, env.now)

        thr = threading.Thread(target=do, args=[])
        self.runs[run]["thr"] = thr
        self.runs[run]["stop_ev"] = stop_ev
        thr.start()

    def stop_run(self, run):
        if run in self.runs and "stop_ev" in self.runs[run]:
            self.runs[run]["stop_ev"].succeed()
