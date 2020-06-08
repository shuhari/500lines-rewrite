import re
from threading import Thread

from flask import Flask, render_template

from .models import Database, TaskResult


class ArtifactHandler:
    def parse(self, text: str) -> object:
        raise NotImplementedError()

    def render(self, model: object) -> str:
        raise NotImplementedError()


class LintIssue:
    def __init__(self, filename, line, column, name, description):
        self.filename = filename
        self.line = line
        self.column = column
        self.name = name
        self.description = description


class PyLintHandler(ArtifactHandler):
    def parse(self, text: str) -> object:
        result = [self.extract_issue(x) for x in text.splitlines()]
        result = [x for x in result if x]
        return result

    def extract_issue(self, line: str) -> LintIssue:
        m = re.match(r'(.+\.py):(\d+):(\d+): ([A-Z0-9]+): (.+)', line)
        if m:
            return LintIssue(m.group(1), int(m.group(2)), int(m.group(3)), m.group(4), m.group(5))
        return None

    def render(self, model: object) -> str:

        def render_row(issue: LintIssue) -> str:
            return f"<tr>" \
                   f"<td>{issue.filename}</td>" \
                   f"<td>{issue.line}:{issue.column}</td>" \
                   f"<td>{issue.name}</td>" \
                   f"<td>{issue.description}</td>" \
                   f"</tr>"

        rows = [render_row(x) for x in model]
        return f"<table border=1>{''.join(rows)}</table>"


class UnitTestResult:
    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0


class UnitTestHandler(ArtifactHandler):
    def parse(self, text: str) -> object:
        result = UnitTestResult()
        first_line = text.splitlines()[0]
        for ch in first_line:
            if ch == '.':
                result.pass_count += 1
            elif ch == 'E':
                result.error_count += 1
            elif ch == 'F':
                result.fail_count += 1
        return result

    def render(self, model: UnitTestResult) -> str:
        return f"<b>{model.pass_count}</b> Passed, <b>{model.fail_count}</b> failed, <b>{model.error_count}</b> Error."


def render_task_result(result: TaskResult) -> str:
    handlers = {
        'pylint': PyLintHandler,
        'unittest': UnitTestHandler,
    }
    assert result.type in handlers, f"Unsupported task result: {result.type}"
    handler = handlers[result.type]()
    model = handler.parse(result.content)
    return handler.render(model)


class WebServer(Thread):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

    def run(self):
        app = Flask(__name__)

        @app.route('/')
        def index():
            return render_template('index.html',
                                   projects=self.db.projects)
        app.jinja_env.globals['render_task_result'] = render_task_result
        app.run(port=5000)
