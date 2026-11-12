"""Persistent storage for submissions, backed by SQLite.

SQLite is part of the Python standard library, so no extra service is needed and
the data survives application restarts.
"""

import sqlite3
from datetime import datetime, timezone

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    registration_number TEXT NOT NULL,
    assignment_title TEXT NOT NULL,
    submission_url TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_db():
    """Return the database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the submissions table if it does not exist yet."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def init_app(app):
    """Register storage hooks and make sure the table exists."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def add_submission(
    student_name, registration_number, assignment_title, submission_url
):
    """Insert one validated submission and commit it to disk."""
    db = get_db()
    db.execute(
        """
        INSERT INTO submissions
            (student_name, registration_number, assignment_title, submission_url, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            student_name,
            registration_number,
            assignment_title,
            submission_url,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )
    db.commit()


def list_submissions():
    """Return every saved submission, newest first."""
    rows = get_db().execute(
        "SELECT * FROM submissions ORDER BY id DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def count_submissions():
    """Return how many submissions are stored."""
    row = get_db().execute("SELECT COUNT(*) AS total FROM submissions").fetchone()
    return row["total"]
