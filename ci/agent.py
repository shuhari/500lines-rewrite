import io
import os
import shutil
import subprocess
import uuid
from threading import Thread
import multiprocessing as mp

from .models import Project, BuildResult, TaskResult
from . import vcs


class TaskRunner:
    def run(self, parent, config: dict, workDir: str):
        self.parent = parent
        self.config = config
        self.workDir = workDir
        self.result = TaskResult()
        self.run_core()

    def run_core(self):
        raise NotImplementedError()


def run_external(cmd: str, work_dir: str):
    p = subprocess.run(cmd, shell=True, cwd=work_dir, capture_output=True)
    if p.stdout:
        return p.stdout.decode('utf8')
    return None


def init_venv(project: Project):
    project.venv_name = 'venv'
    cmd = f"python3 -m venv {project.venv_name}"
    run_external(cmd, project.work_dir)


def run_pip(project: Project, config: dict) -> TaskResult:
    args = f"{project.venv_name}/bin/pip install -r {config['file']}"
    run_external(args, project.work_dir)


def run_pylint(project: Project, config: dict) -> TaskResult:
    args = f"venv/bin/pylint *.py"
    output = run_external(args, project.work_dir)
    return TaskResult('pylint', output)


def run_unittest(project: Project, config: dict) -> TaskResult:
    args = f"venv/bin/python -m unittest {config['params']} 2>&1"
    output = run_external(args, project.work_dir)
    return TaskResult('unittest', output)


class ProjectRunner(Thread):
    def __init__(self, agent, project: Project):
        super().__init__()
        self.agent = agent
        self.project = project
        self.result = BuildResult()
        self.result.project_id = project.id
        self.result.agent_id = agent.id

    def run(self):
        clone_dir = os.path.join(self.agent.workDir(), uuid.uuid4().hex)
        try:
            vcs.clone(self.project.config["url"], clone_dir, self.project.pending_commit)
            self.project.work_dir = clone_dir
            init_venv(self.project)
            for task_config in self.project.config["tasks"]:
                task_runner = self.get_task_runner(task_config["type"])
                task_result = task_runner(self.project, task_config)
                if task_result:
                    task_result.type = task_config['type']
                    self.result.tasks.append(task_result)
        except Exception as e:
            self.result.fail(e)
            import traceback; traceback.print_exc()
        finally:
            shutil.rmtree(clone_dir)
            self.result.finish()
            self.agent.result_queue.put(self.result)

    def get_task_runner(self, task_type: str):
        registered_runners = {
            'pip': run_pip,
            'pylint': run_pylint,
            'unittest': run_unittest,
        }
        assert task_type in registered_runners, f"Unsupported task type: {task_type}"
        return registered_runners[task_type]


class Agent:
    def __init__(self, config):
        self.config = config
        self.project_queue = mp.Queue()
        self.result_queue = mp.Queue()

    @property
    def id(self) -> str:
        return self.config["id"]

    def workDir(self) -> str:
        return os.path.expandvars(self.config["workDir"])

    def __call__(self, *args, **kwargs):
        while True:
            project = self.project_queue.get()
            runner = ProjectRunner(self, project)
            runner.start()
