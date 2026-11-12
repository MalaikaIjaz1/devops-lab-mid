"""Validation rules for the submission form."""

from urllib.parse import urlparse

ALLOWED_URL_SCHEMES = ("http", "https")

FIELD_LABELS = {
    "student_name": "Student name",
    "registration_number": "Registration number",
    "assignment_title": "Assignment title",
    "submission_url": "Submission URL",
}


def is_valid_url(url):
    """Return True when ``url`` is a usable http(s) link."""
    if not url or any(character.isspace() for character in url):
        return False

    parsed = urlparse(url)
    if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
        return False
    if not parsed.netloc:
        return False

    host = parsed.hostname or ""
    if not host:
        return False

    # A real domain contains a dot; "localhost" is allowed for offline demos.
    return "." in host or host == "localhost"


def validate_submission(form):
    """Validate the submitted form.

    Returns a tuple ``(cleaned, errors)`` where ``cleaned`` contains trimmed
    values for every field and ``errors`` maps a field name to a friendly
    message. An empty ``errors`` dictionary means the submission is valid.
    """
    cleaned = {}
    for field in FIELD_LABELS:
        cleaned[field] = (form.get(field) or "").strip()

    errors = {}

    for field, label in FIELD_LABELS.items():
        if not cleaned[field]:
            errors[field] = f"{label} is required."

    if not errors.get("student_name") and len(cleaned["student_name"]) < 3:
        errors["student_name"] = "Student name must be at least 3 characters long."

    if not errors.get("registration_number"):
        if len(cleaned["registration_number"]) < 3:
            errors["registration_number"] = (
                "Registration number must be at least 3 characters long."
            )

    if not errors.get("submission_url") and not is_valid_url(
        cleaned["submission_url"]
    ):
        errors["submission_url"] = (
            "Submission URL must be a valid http:// or https:// link, "
            "for example https://github.com/username/repository"
        )

    return cleaned, errors
