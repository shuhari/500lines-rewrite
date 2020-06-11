import _queue
import random
import time
from threading import Thread
import multiprocessing as mp

from .models import Project
from .agent import Agent
from . import vcs


class Scheduler(Thread):
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
                self.detect_result(agent)
            time.sleep(10)

    def detect_change(self, project: Project):
        """Check if project has pending commits, queue for build if found."""
        if project.processing:
            return
        commit_id = vcs.get_last_commit_id(project.config['url'])
        if commit_id != project.current_commit:
            project.pending_commit = commit_id
            agent = self.choose_agent(project)
            agent.schedule(project)

    def choose_agent(self, project: Project):
        """Choose an compatible agent base on project nature. currently just select a random one"""
        return random.choice(self.agents)

    def detect_result(self, agent: Agent):
        """Get build result from agent queue"""
        try:
            result = agent.result_queue.get(block=False)
            print(f'{agent.id} got build result: {result}')
            result.agent_id = agent.id
            project = self.db.find_project(result.project_id)
            project.end_build(result)
            print(f"Project {project.id} end build, commit={project.current_commit}")
        except _queue.Empty:
            pass
