import _queue
import random
import time
from threading import Thread
import multiprocessing as mp

from .models import Project, BuildResult
from .agent import Agent
from . import vcs


class Master(Thread):
    def __init__(self, config, db):
        super().__init__()
        self.config = config
        self.db = db
        self.agents = [self.start_agent(x) for x in config["agents"]]

    def start_agent(self, config):
        agent = Agent(config)
        p = mp.Process(target=agent, daemon=True)
        p.start()
        return agent

    def run(self):
        while True:
            for project in self.db.projects:
                self.detect_change(project)
            for agent in self.agents:
                try:
                    result = agent.result_queue.get(block=False)
                    result.dump()
                    self.process_result(result)
                except _queue.Empty:
                    pass
            time.sleep(10)

    def detect_change(self, project: Project):
        if project.processing:
            return
        commit_id = vcs.get_last_commit_id(project.config['url'])
        if commit_id != project.current_commit:
            project.pending_commit = commit_id
            project.processing = True
            agent = self.choose_agent(project)
            print(f"Project {project.id} has new commit {commit_id}, schedule to {agent.id}")
            agent.project_queue.put(project)

    def choose_agent(self, project: Project):
        return random.choice(self.agents)

    def process_result(self, result: BuildResult):
        project = self.db.find_project(result.project_id)
        project.end_build(result)
