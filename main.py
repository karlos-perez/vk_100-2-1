import os

from app.web.app import setup_app
from aiohttp.web import run_app


if __name__ == "__main__":
    run_app(setup_app(), host="127.0.0.1", port=8000)
