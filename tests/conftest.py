"""Shared pytest fixtures.

Every test gets its own temporary SQLite database, so tests never touch the
real ``instance/submissions.db`` file and never depend on each other.
"""

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": str(tmp_path / "test-submissions.db"),
        }
    )
    return application


@pytest.fixture()
def client(app):
    return app.test_client()
