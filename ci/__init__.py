import json
import os

from .models import Database
from .master import Master
from .webserver import WebServer


def read_config():
    """Read from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    config = read_config()
    db = Database(config)
    master = Master(config, db)
    master.start()
    web_server = WebServer(db)
    web_server.start()

