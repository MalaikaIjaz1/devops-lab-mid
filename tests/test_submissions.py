"""Automated tests for the Assignment Submission Portal.

The suite contains exactly the three test cases required by the assignment:

  1. Complete details and a valid submission URL
     -> the submission is saved and appears in the submission list.
  2. Missing registration number
     -> the submission is rejected with a validation message.
  3. Invalid submission URL
     -> the submission is rejected and is not saved.
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
    """Test 1: complete details and a valid submission URL.

    Expected result: the submission is saved and appears in the submission list.
    """
    response = client.post(
        "/submit", data=VALID_SUBMISSION, follow_redirects=True
    )
    body = response.get_data(as_text=True)

    # The page comes back normally after the redirect.
    assert response.status_code == 200
    assert "Submission saved successfully." in body

    # It is rendered in the submission list.
    assert VALID_SUBMISSION["student_name"] in body
    assert VALID_SUBMISSION["registration_number"] in body
    assert VALID_SUBMISSION["assignment_title"] in body
    assert VALID_SUBMISSION["submission_url"] in body
    assert "Saved submissions (1)" in body

    # It really exists in the persistent store.
    rows = saved_rows(app)
    assert len(rows) == 1
    assert rows[0]["student_name"] == VALID_SUBMISSION["student_name"]
    assert rows[0]["registration_number"] == VALID_SUBMISSION["registration_number"]
    assert rows[0]["submission_url"] == VALID_SUBMISSION["submission_url"]


def test_submission_without_registration_number_is_rejected(client, app):
    """Test 2: missing registration number.

    Expected result: the submission is rejected with a validation message.
    """
    data = dict(VALID_SUBMISSION)
    data.pop("registration_number")

    response = client.post("/submit", data=data)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Registration number is required." in body
    assert saved_rows(app) == []


def test_submission_with_invalid_url_is_rejected(client, app):
    """Test 3: invalid submission URL.

    Expected result: the submission is rejected and is not saved.
    """
    data = dict(VALID_SUBMISSION, submission_url="this-is-not-a-url")

    response = client.post("/submit", data=data)
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "Submission URL must be a valid" in body
    assert saved_rows(app) == []
