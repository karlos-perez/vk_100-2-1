from aiohttp.web import run_app

from app.web.app import setup_app
from app.web.config import config as app_config

if __name__ == "__main__":
    run_app(setup_app(), port=app_config["server"]["port"])
