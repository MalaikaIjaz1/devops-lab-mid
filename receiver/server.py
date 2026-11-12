"""Local HTTP report receiver.

Runs on http://127.0.0.1:5001 and accepts POST /report from the CI job.
Every received report is written to ``test-report.json`` in the project root,
so the JSON file always contains real results produced by real test runs.

Start it with:
    python receiver/server.py
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = Path(
    os.environ.get("REPORT_PATH", str(PROJECT_ROOT / "test-report.json"))
)
HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))

# The receiver refuses incomplete reports, so a broken CI payload is noticed
# immediately instead of producing a half-empty report file.
REQUIRED_FIELDS = (
    "repository",
    "branch",
    "commit_sha",
    "run_id",
    "timestamp",
    "overall_status",
    "total_tests",
    "passed_tests",
    "failed_tests",
    "tests",
)

app = Flask(__name__)


@app.get("/health")
def health():
    """Small endpoint used by the CI job to check that the receiver is alive."""
    return jsonify({"status": "ok", "report_path": str(REPORT_PATH)})


@app.get("/report")
def show_report():
    """Return the last saved report (helpful when demonstrating the result)."""
    if not REPORT_PATH.exists():
        return jsonify({"error": "No report has been received yet."}), 404
    return jsonify(json.loads(REPORT_PATH.read_text(encoding="utf-8")))


@app.post("/report")
def receive_report():
    """Validate the incoming payload and save it as test-report.json."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return (
            jsonify({"error": "Report is missing required fields.", "missing": missing}),
            400,
        )

    payload["received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        f"[receiver] {payload['timestamp']} | {payload['repository']} | "
        f"{payload['branch']} | run {payload['run_id']} | "
        f"{payload['overall_status'].upper()} | "
        f"{payload['passed_tests']}/{payload['total_tests']} passed",
        flush=True,
    )
    print(f"[receiver] report saved to {REPORT_PATH}", flush=True)

    return (
        jsonify(
            {
                "status": "saved",
                "saved_to": str(REPORT_PATH),
                "overall_status": payload["overall_status"],
            }
        ),
        201,
    )


if __name__ == "__main__":
    print("=" * 62)
    print(" Local test report receiver")
    print(f" Listening on : http://{HOST}:{PORT}")
    print(f" POST reports : http://{HOST}:{PORT}/report")
    print(f" Report file  : {REPORT_PATH}")
    print(" Press CTRL+C to stop.")
    print("=" * 62, flush=True)
    app.run(host=HOST, port=PORT, debug=False)
