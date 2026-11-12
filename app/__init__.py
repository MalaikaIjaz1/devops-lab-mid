"""Application factory for the Assignment Submission Portal."""

import os
import secrets
from pathlib import Path

from flask import Flask

from . import storage
from .routes import bp as portal_bp

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates"


def create_app(test_config=None):
    """Create and configure the Flask application.

    ``test_config`` lets the automated tests replace settings (for example the
    database path) without touching the real application data.
    """
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
    app.config.from_mapping(
        # No secret is hardcoded: a random per-process key is generated unless
        # SECRET_KEY is supplied. It is only used to sign the flash-message cookie.
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get(
            "SUBMISSIONS_DB", str(Path(app.instance_path) / "submissions.db")
        ),
    )

    if test_config is not None:
        app.config.update(test_config)

    # The instance folder holds local data (the SQLite database) and is ignored by git.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    storage.init_app(app)
    app.register_blueprint(portal_bp)

    return app
