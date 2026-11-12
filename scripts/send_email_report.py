"""Send the JSON test report by email.

Reads the real ``test-report.json`` (written by scripts/run_tests.py) and emails
it after a passing OR failing test run. All credentials come from environment
variables, never from code:

    MAIL_SERVER    smtp.gmail.com
    MAIL_PORT      587 (STARTTLS) or 465 (SSL)
    MAIL_USERNAME  your full email address
    MAIL_PASSWORD  Gmail App Password (never your normal password)
    MAIL_FROM      sender address shown in the email
    MAIL_TO        one address, or several separated by commas

Usage:
    python scripts/send_email_report.py
    python scripts/send_email_report.py --report test-report.json
    python scripts/send_email_report.py --dry-run
"""

import argparse
import html
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = PROJECT_ROOT / "test-report.json"

REQUIRED_ENV_VARS = (
    "MAIL_SERVER",
    "MAIL_PORT",
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "MAIL_FROM",
    "MAIL_TO",
)


def load_report(report_path):
    """Read and parse the JSON report."""
    if not report_path.exists():
        raise SystemExit(
            f"ERROR: report file not found: {report_path}\n"
            "Run the tests first: python scripts/run_tests.py"
        )
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: report file is not valid JSON: {exc}") from exc


def format_text_body(report):
    """Plain-text email body."""
    lines = [
        "Assignment Submission Portal - automated test report",
        "",
        f"Repository  : {report.get('repository', 'unknown')}",
        f"Branch      : {report.get('branch', 'unknown')}",
        f"Commit SHA  : {report.get('commit_sha', 'unknown')}",
        f"Run ID      : {report.get('run_id', 'unknown')}",
        f"Workflow    : {report.get('workflow', 'unknown')}",
        f"Timestamp   : {report.get('timestamp', 'unknown')}",
        f"Overall     : {str(report.get('overall_status', 'unknown')).upper()}",
        "",
        f"Total tests : {report.get('total_tests', 0)}",
        f"Passed      : {report.get('passed_tests', 0)}",
        f"Failed      : {report.get('failed_tests', 0)}",
        f"Skipped     : {report.get('skipped_tests', 0)}",
        "",
        "Test results",
        "------------",
    ]

    for test in report.get("tests", []):
        lines.append(f"[{test.get('result', 'unknown').upper()}] {test.get('name', 'unknown')}")
        if test.get("failure_message"):
            lines.append(f"    Failure: {test['failure_message']}")

    lines.extend(
        [
            "",
            "The complete JSON report is attached.",
            "",
            "-- ",
            "Sent automatically by scripts/send_email_report.py",
        ]
    )
    return "\n".join(lines)


def format_html_body(report):
    """HTML email body with a small results table."""
    status = str(report.get("overall_status", "unknown")).upper()
    status_colour = "#157347" if status == "PASSED" else "#b02a37"

    rows = []
    for test in report.get("tests", []):
        result = str(test.get("result", "unknown"))
        colour = "#157347" if result == "passed" else "#b02a37"
        failure = test.get("failure_message", "")
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(test.get('name', 'unknown')))}</td>"
            f'<td style="color:{colour};font-weight:600">{html.escape(result.upper())}</td>'
            f"<td>{html.escape(failure)}</td>"
            "</tr>"
        )

    if not rows:
        rows.append('<tr><td colspan="3">No test results found in the report.</td></tr>')

    return f"""<html>
  <body style="font-family:Segoe UI,Arial,sans-serif;color:#1f2933">
    <h2 style="margin-bottom:4px">Assignment Submission Portal - test report</h2>
    <p style="font-size:22px;font-weight:700;color:{status_colour};margin:4px 0 16px">
      {html.escape(status)}
    </p>
    <table cellpadding="6" style="border-collapse:collapse;font-size:14px">
      <tr><td><strong>Repository</strong></td><td>{html.escape(str(report.get('repository', 'unknown')))}</td></tr>
      <tr><td><strong>Branch</strong></td><td>{html.escape(str(report.get('branch', 'unknown')))}</td></tr>
      <tr><td><strong>Commit SHA</strong></td><td>{html.escape(str(report.get('commit_sha', 'unknown')))}</td></tr>
      <tr><td><strong>GitHub run ID</strong></td><td>{html.escape(str(report.get('run_id', 'unknown')))}</td></tr>
      <tr><td><strong>Workflow</strong></td><td>{html.escape(str(report.get('workflow', 'unknown')))}</td></tr>
      <tr><td><strong>Timestamp</strong></td><td>{html.escape(str(report.get('timestamp', 'unknown')))}</td></tr>
      <tr><td><strong>Total / Passed / Failed</strong></td>
          <td>{report.get('total_tests', 0)} / {report.get('passed_tests', 0)} / {report.get('failed_tests', 0)}</td></tr>
    </table>
    <h3 style="margin-top:24px">Test results</h3>
    <table cellpadding="6" style="border-collapse:collapse;font-size:13px;border:1px solid #dde3ea">
      <thead>
        <tr style="background:#f7f9fc;text-align:left">
          <th align="left">Test</th><th align="left">Result</th><th align="left">Failure message</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <p style="font-size:12px;color:#5c6b7a;margin-top:20px">
      The complete JSON report is attached to this email.
    </p>
  </body>
</html>"""


def build_message(report, report_path):
    """Create the email message with text body, HTML body and JSON attachment."""
    repository = str(report.get("repository", "unknown"))
    branch = str(report.get("branch", "unknown"))
    status = str(report.get("overall_status", "unknown")).upper()

    message = EmailMessage()
    message["Subject"] = f"[{status}] Test report - {repository} ({branch})"
    message["From"] = os.environ["MAIL_FROM"].strip()

    recipients = [
        address.strip()
        for address in os.environ["MAIL_TO"].split(",")
        if address.strip()
    ]
    message["To"] = ", ".join(recipients)

    message.set_content(format_text_body(report))
    message.add_alternative(format_html_body(report), subtype="html")
    message.add_attachment(
        report_path.read_bytes(),
        maintype="application",
        subtype="json",
        filename=report_path.name,
    )
    return message


def send_email(message, server, port, username, password):
    """Send the message with SSL (465) or STARTTLS (587 and anything else)."""
    context = ssl.create_default_context()

    if port == 465:
        print(f"Connecting to {server}:{port} using SSL ...", flush=True)
        with smtplib.SMTP_SSL(server, port, timeout=30, context=context) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
        return

    print(f"Connecting to {server}:{port} using STARTTLS ...", flush=True)
    with smtplib.SMTP(server, port, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Email the JSON test report.")
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Path to test-report.json (default: project root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the email body without contacting the SMTP server.",
    )
    args = parser.parse_args(argv)

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = PROJECT_ROOT / report_path

    report = load_report(report_path)

    if args.dry_run:
        print("=" * 62)
        print(" DRY RUN - no email will be sent")
        print("=" * 62)
        print(format_text_body(report))
        return 0

    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name, "").strip()]
    if missing:
        raise SystemExit(
            "ERROR: missing required environment variables: "
            + ", ".join(missing)
            + "\nSet them as GitHub Secrets, or export them locally before running."
        )

    mail_server = os.environ["MAIL_SERVER"].strip()
    try:
        mail_port = int(os.environ["MAIL_PORT"].strip())
    except ValueError:
        raise SystemExit("ERROR: MAIL_PORT must be a number, for example 587 or 465.")

    message = build_message(report, report_path)
    send_email(
        message,
        server=mail_server,
        port=mail_port,
        username=os.environ["MAIL_USERNAME"].strip(),
        password=os.environ["MAIL_PASSWORD"],
    )

    print(
        f"Email sent to {os.environ['MAIL_TO'].strip()} "
        f"(status: {report.get('overall_status', 'unknown').upper()}).",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
