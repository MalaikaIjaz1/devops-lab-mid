"""Web routes for the Assignment Submission Portal."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import storage
from .validation import validate_submission

bp = Blueprint("portal", __name__)


def render_portal(errors=None, form_data=None, status_code=200):
    """Render the portal page with the current list of submissions."""
    html = render_template(
        "index.html",
        submissions=storage.list_submissions(),
        total=storage.count_submissions(),
        errors=errors or {},
        form_data=form_data or {},
    )
    return html, status_code


@bp.get("/")
def index():
    """Show the submission form and every saved submission."""
    return render_portal()


@bp.post("/submit")
def submit():
    """Validate the form, save it when valid, otherwise show the errors."""
    cleaned, errors = validate_submission(request.form)

    if errors:
        # Status 400 makes the rejection explicit for browsers, tests and CI.
        return render_portal(errors=errors, form_data=cleaned, status_code=400)

    storage.add_submission(**cleaned)
    flash("Submission saved successfully.", "success")
    return redirect(url_for("portal.index"))
