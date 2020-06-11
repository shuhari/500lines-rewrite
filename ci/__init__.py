import json
import os

from .models import Database
from .scheduler import Scheduler
from .webserver import WebServer


def read_config():
    """Read from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    config = read_config()
    db = Database(config)
    scheduler = Scheduler(config, db)
    scheduler.start()
    web_server = WebServer(db)
    web_server.start()

