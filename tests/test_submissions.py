"""Automated tests for the Assignment Submission Portal.

These cover the three required scenarios:
  1. a complete, valid submission is saved and displayed,
  2. a submission without a registration number is rejected and not saved,
  3. a submission with an invalid URL is rejected and not saved.
"""

from app import storage

VALID_SUBMISSION = {
    "student_name": "Ayesha Khan",
    "registration_number": "FA22-BCS-123",
    "assignment_title": "DevOps Lab Mid Project",
    "submission_url": "https://github.com/ayesha-khan/devops-lab-mid",
}


def saved_rows(app):
    """Read the submissions table inside an application context."""
    with app.app_context():
        return storage.list_submissions()


def test_valid_submission_is_saved_and_displayed(client, app):
    """Test 1: a complete and valid submission is saved and displayed."""
    response = client.post(
        "/submit", data=VALID_SUBMISSION, follow_redirects=True
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Submission saved successfully." in body
    assert VALID_SUBMISSION["student_name"] in body
    assert VALID_SUBMISSION["registration_number"] in body
    assert VALID_SUBMISSION["assignment_title"] in body
    assert VALID_SUBMISSION["submission_url"] in body

    rows = saved_rows(app)
    assert len(rows) == 1
    assert rows[0]["registration_number"] == VALID_SUBMISSION["registration_number"]
    assert rows[0]["submission_url"] == VALID_SUBMISSION["submission_url"]


def test_submission_without_registration_number_is_rejected(client, app):
    """Test 2: a missing registration number is rejected and nothing is saved."""
    data = dict(VALID_SUBMISSION)
    data.pop("registration_number")

    response = client.post("/submit", data=data)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Registration number is required." in body
    assert saved_rows(app) == []


def test_submission_with_invalid_url_is_rejected(client, app):
    """Test 3: an invalid submission URL is rejected and nothing is saved."""
    data = dict(VALID_SUBMISSION, submission_url="this-is-not-a-url")

    response = client.post("/submit", data=data)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Submission URL must be a valid" in body
    assert saved_rows(app) == []


def test_submission_without_student_name_is_rejected(client, app):
    """A missing student name is rejected with a clear message."""
    data = dict(VALID_SUBMISSION, student_name="   ")

    response = client.post("/submit", data=data)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Student name is required." in body
    assert saved_rows(app) == []


def test_submission_url_must_use_http_or_https(client, app):
    """A URL without an http(s) scheme is rejected."""
    data = dict(VALID_SUBMISSION, submission_url="www.github.com/ayesha")

    response = client.post("/submit", data=data)

    assert response.status_code == 400
    assert saved_rows(app) == []


def test_saved_submissions_survive_a_new_request(client):
    """Saved submissions are displayed again on the next page load."""
    client.post("/submit", data=VALID_SUBMISSION)

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert VALID_SUBMISSION["registration_number"] in body
    assert "Saved submissions (1)" in body


def test_empty_portal_lists_no_submissions(client):
    """The portal page renders correctly before any submission exists."""
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No submissions saved yet." in body
