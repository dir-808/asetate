"""WSGI entry point for production deployment."""

import os

from dotenv import load_dotenv

load_dotenv()

from asetate import create_app

config_name = os.environ.get("FLASK_ENV", "production")
app = create_app(config_name)

if __name__ == "__main__":
    app.run()
