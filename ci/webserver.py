import logging
import re
from threading import Thread

from flask import Flask, render_template

from .models import Database, TaskResult, LintIssue, UnitTestResult


class ArtifactHandler:
    """Handle artifact from build result"""
    def parse(self, text: str) -> object:
        """parse build output to view model"""
        raise NotImplementedError()

    def render(self, model: object) -> str:
        """Render view model to html"""
        raise NotImplementedError()


class PyLintHandler(ArtifactHandler):
    """Handle pylint result"""
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


class UnitTestHandler(ArtifactHandler):
    """Handle unittest result"""
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
    """Render task result to html"""
    handlers = {
        'pylint': PyLintHandler,
        'unittest': UnitTestHandler,
    }
    assert result.type in handlers, f"Unsupported task result: {result.type}"
    handler = handlers[result.type]()
    model = handler.parse(result.content)
    return handler.render(model)


class WebServer(Thread):
    """start flask server to show build output as html"""
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
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        app.run()
