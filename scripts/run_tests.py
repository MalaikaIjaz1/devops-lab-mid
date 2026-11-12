"""Run the pytest suite, build test-report.json and deliver it to the receiver.

What the script does, step by step:
1. runs pytest and stores the raw result in a temporary JUnit XML file,
2. converts that XML into the JSON report required by the assignment
   (repository, branch, commit SHA, run ID, timestamp, per-test results,
   totals and overall status),
3. writes ``test-report.json`` in the project root,
4. POSTs the same JSON to the local receiver (http://127.0.0.1:5001/report).

Exit codes
0 -> every test passed (and, with --require-receiver, the report was delivered)
1 -> at least one test failed
3 -> the report could not be delivered to the local receiver
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / "test-report.json"
DEFAULT_RECEIVER_URL = "http://127.0.0.1:5001/report"


def run_git_command(*args):
    """Return the output of a git command, or an empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def detect_repository():
    """owner/repository, from GitHub Actions or from the git remote."""
    value = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if value:
        return value

    remote = run_git_command("config", "--get", "remote.origin.url")
    remote = remote.removesuffix(".git")
    if remote.startswith("git@github.com:"):
        return remote.split(":", 1)[1]
    if "github.com/" in remote:
        return remote.split("github.com/", 1)[1]
    return PROJECT_ROOT.name


def detect_branch():
    return (
        os.environ.get("GITHUB_HEAD_REF")
        or os.environ.get("GITHUB_REF_NAME")
        or run_git_command("rev-parse", "--abbrev-ref", "HEAD")
        or "unknown"
    )


def detect_commit_sha():
    return os.environ.get("GITHUB_SHA") or run_git_command("rev-parse", "HEAD") or "unknown"


def detect_run_id():
    return os.environ.get("GITHUB_RUN_ID") or "local-run"


def run_pytest(extra_args, xml_path):
    """Run pytest in a child process so its exit code and output are real."""
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        f"--junitxml={xml_path}",
        "-v",
        "--no-header",
        *extra_args,
    ]
    print("Running: " + " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=PROJECT_ROOT)
    return completed.returncode


def parse_junit_xml(xml_path):
    """Convert a JUnit XML file into a list of simple test dictionaries."""
    if not xml_path.exists():
        return []

    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return []

    results = []
    for case in root.iter("testcase"):
        classname = case.get("classname", "")
        name = case.get("name", "unknown test")
        full_name = f"{classname}::{name}" if classname else name

        outcome = "passed"
        failure_message = ""

        for child in case:
            tag = child.tag.lower()
            if tag in ("failure", "error"):
                outcome = "failed"
                message = child.get("message") or (child.text or "")
                failure_message = " ".join(message.split())[:4000]
                break
            if tag == "skipped":
                outcome = "skipped"
                message = child.get("message") or ""
                failure_message = " ".join(message.split())[:2000]

        item = {
            "name": full_name,
            "result": outcome,
            "duration_seconds": round(float(case.get("time", "0") or 0), 3),
        }
        if failure_message:
            item["failure_message"] = failure_message
        results.append(item)

    return results


def build_report(tests, started_at, duration_seconds):
    """Build the JSON document required by the assignment."""
    total = len(tests)
    passed = sum(1 for test in tests if test["result"] == "passed")
    failed = sum(1 for test in tests if test["result"] == "failed")
    skipped = sum(1 for test in tests if test["result"] == "skipped")

    return {
        "repository": detect_repository(),
        "branch": detect_branch(),
        "commit_sha": detect_commit_sha(),
        "run_id": detect_run_id(),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "local run"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "actor": os.environ.get("GITHUB_ACTOR", "local user"),
        "runner": os.environ.get("RUNNER_NAME", "local machine"),
        "timestamp": started_at.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round(duration_seconds, 2),
        "overall_status": "passed" if total > 0 and failed == 0 else "failed",
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "skipped_tests": skipped,
        "tests": tests,
    }


def deliver_report(report, receiver_url, attempts=5, delay_seconds=2.0):
    """POST the report to the local receiver, retrying a few times."""
    payload = json.dumps(report).encode("utf-8")

    for attempt in range(1, attempts + 1):
        http_request = request.Request(
            receiver_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=10) as response:
                response.read()
                print(
                    f"Report delivered to {receiver_url} (HTTP {response.status}).",
                    flush=True,
                )
                return True
        except error.HTTPError as exc:
            reason = f"HTTP {exc.code} {exc.reason}"
        except (error.URLError, OSError) as exc:
            reason = getattr(exc, "reason", exc)

        print(
            f"Delivery attempt {attempt}/{attempts} failed: {reason}",
            flush=True,
        )
        if attempt < attempts:
            time.sleep(delay_seconds)

    return False


def print_summary(report):
    line = "=" * 62
    print("", flush=True)
    print(line)
    print(" TEST REPORT SUMMARY")
    print(line)
    print(f" Repository    : {report['repository']}")
    print(f" Branch        : {report['branch']}")
    print(f" Commit SHA    : {report['commit_sha']}")
    print(f" Run ID        : {report['run_id']}")
    print(f" Overall status: {report['overall_status'].upper()}")
    print(f" Total tests   : {report['total_tests']}")
    print(f" Passed        : {report['passed_tests']}")
    print(f" Failed        : {report['failed_tests']}")
    print(f" Report file   : {REPORT_PATH}")
    print(line, flush=True)


def split_arguments(raw_args):
    """Separate this script's own options from the arguments meant for pytest.

    The order of the pytest arguments is preserved, so ``-k url`` keeps its
    value next to it.
    """
    own_args = []
    pytest_args = []
    index = 0

    while index < len(raw_args):
        token = raw_args[index]
        if token in ("--require-receiver", "--no-deliver", "-h", "--help"):
            own_args.append(token)
        elif token == "--receiver-url":
            own_args.append(token)
            if index + 1 < len(raw_args):
                own_args.append(raw_args[index + 1])
                index += 1
        elif token.startswith("--receiver-url="):
            own_args.append(token)
        elif token == "--":
            pytest_args.extend(raw_args[index + 1 :])
            break
        else:
            pytest_args.append(token)
        index += 1

    return own_args, pytest_args


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the tests and deliver a JSON report to the local receiver.",
        epilog=(
            "Any other argument is forwarded to pytest, "
            "for example: python scripts/run_tests.py -k url"
        ),
    )
    parser.add_argument(
        "--receiver-url",
        default=os.environ.get("RECEIVER_URL", DEFAULT_RECEIVER_URL),
        help="URL of the local report receiver (default: %(default)s)",
    )
    parser.add_argument(
        "--require-receiver",
        action="store_true",
        help="Fail with exit code 3 when the report cannot be delivered.",
    )
    parser.add_argument(
        "--no-deliver",
        action="store_true",
        help="Only write test-report.json, do not contact the receiver.",
    )

    raw_args = list(sys.argv[1:] if argv is None else argv)
    own_args, pytest_args = split_arguments(raw_args)
    args = parser.parse_args(own_args)

    started_at = datetime.now(timezone.utc)
    start = time.perf_counter()

    with tempfile.TemporaryDirectory() as temp_dir:
        xml_path = Path(temp_dir) / "junit.xml"
        exit_code = run_pytest(pytest_args, xml_path)
        tests = parse_junit_xml(xml_path)

    duration = time.perf_counter() - start

    if not tests and exit_code != 0:
        # This happens when pytest cannot even collect the tests (import error).
        tests = [
            {
                "name": "tests::pytest-collection",
                "result": "failed",
                "failure_message": (
                    "pytest could not collect or run the tests. "
                    "See the pytest output above for details."
                ),
            }
        ]

    report = build_report(tests, started_at, duration)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print_summary(report)

    delivered = True
    if not args.no_deliver:
        delivered = deliver_report(report, args.receiver_url)

    if not delivered and args.require_receiver:
        print(
            "ERROR: the JSON report could not be delivered to the local receiver. "
            "Start it with: python receiver/server.py",
            file=sys.stderr,
            flush=True,
        )
        return 3

    if report["overall_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
