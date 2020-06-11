import os
import shutil
import subprocess
import traceback
import uuid
from threading import Thread
import multiprocessing as mp

from .models import Project, BuildResult, TaskResult
from . import vcs


def run_external(builder, cmd: str) -> str:
    """Run external program, return output to stdout"""
    p = subprocess.run(cmd,
                       shell=True,
                       cwd=builder.work_dir,
                       capture_output=True)
    if p.stdout:
        return p.stdout.decode('utf8')
    return None


def run_venv(builder, config: dict) -> TaskResult:
    venv_name, package_file = config["name"], config['packages-file']
    builder.run_cmd(f"python3 -m venv {venv_name}")
    builder.run_cmd(f"{venv_name}/bin/pip install -r {package_file}")
    builder.venv_name = venv_name
    return None


def run_pylint(builder, config: dict) -> TaskResult:
    venv_name, pattern = builder.venv_name, config["pattern"]
    output = builder.run_cmd(f"{venv_name}/bin/pylint {pattern}")
    return TaskResult('pylint', output)


def run_unittest(builder, config: dict) -> TaskResult:
    venv_name, params = builder.venv_name, config["params"]
    output = builder.run_cmd(f"{venv_name}/bin/python -m unittest {params} 2>&1")
    return TaskResult('unittest', output)


class ProjectBuilder(Thread):
    """Build single project in a separated thread"""
    def __init__(self, agent, project: Project):
        super().__init__()
        self.agent = agent
        self.project = project
        self.result = BuildResult()
        self.result.project_id = project.id
        self.result.commit_id = project.pending_commit
        self.result.agent_id = agent.id
        self.work_dir = None
        self.venv_name = 'venv'

    def run(self):
        """
        Build steps:

        1. Clone project in a separated directory
        2. Use venv to create virtual environment
        3. Run each task in config
        4. Cleanup and save result
        """
        self.work_dir = os.path.join(self.agent.workDir(), uuid.uuid4().hex)
        try:
            vcs.clone(self.project.config["url"], self.work_dir, commit_id=self.project.pending_commit)
            for task_config in self.project.config["tasks"]:
                self.run_task(task_config)
        except Exception as e:
            self.result.fail(e)
            traceback.print_exc()
        finally:
            shutil.rmtree(self.work_dir)
            self.result.finish()
            self.agent.result_queue.put(self.result)

    def run_cmd(self, cmd: str) -> str:
        """Run external program, return output to stdout"""
        p = subprocess.run(cmd,
                           shell=True,
                           cwd=self.work_dir,
                           capture_output=True)
        if p.stdout:
            return p.stdout.decode('utf8')
        return None

    def run_task(self, config: dict):
        task_type = config['type']
        runner_type = {
            'venv': run_venv,
            'pylint': run_pylint,
            'unittest': run_unittest,
        }
        assert task_type in runner_type, f"Unsupported task type: {task_type}"
        runner = runner_type[task_type]
        result = runner(self, config)
        if result:
            result.type = task_type
            self.result.tasks.append(result)


class Agent:
    """Build agent"""
    def __init__(self, config):
        self.config = config
        self.project_queue = mp.Queue()
        self.result_queue = mp.Queue()

    @property
    def id(self) -> str:
        return self.config["id"]

    def workDir(self) -> str:
        return os.path.expandvars(self.config["workDir"])

    def schedule(self, project: Project):
        """Put project in build queue"""
        project.processing = True
        self.project_queue.put(project)
        print(f"Project {project.id} with commit {project.pending_commit} scheduled to {self.id}")

    def __call__(self, *args, **kwargs):
        while True:
            project = self.project_queue.get()
            builder = ProjectBuilder(self, project)
            builder.start()
