from datetime import datetime


class Project:
    def __init__(self, config=None):
        self.config = config
        self.current_commit = None
        self.pending_commit = None
        self.processing = False
        self.build_results = []
        self.work_dir = None
        self.venv_name = None

    @property
    def id(self) -> str:
        return self.config["id"]

    def end_build(self, result):
        self.build_results.append(result)
        self.current_commit = self.pending_commit
        self.pending_commit = None
        self.processing = False


class BuildResult:
    def __init__(self):
        self.project_id = None
        self.success = True
        self.error = None
        self.agent_id = None
        self.start_time = datetime.now()
        self.end_time = None
        self.tasks = []

    def fail(self, e: Exception):
        self.success = False
        self.error = str(e)

    def finish(self):
        self.end_time = datetime.now()

    def dump(self):
        print(f"Build result: {self.success}, {self.error}, {self.agent_id}, {self.start_time}, {self.end_time}")
        for task in self.tasks:
            task.dump()


class TaskResult:
    def __init__(self, fmt=None, content=None):
        self.success = True
        self.type = type
        self.format = fmt
        self.content = content

    def dump(self):
        print(f"    ====Task({self.success}, {self.format}, content len: {len(self.content)}====)")


class Database:
    def __init__(self, config):
        self.projects = [Project(x) for x in config["projects"]]

    def find_project(self, project_id: str) -> Project:
        for project in self.projects:
            if project.id == project_id:
                return project
        return None
