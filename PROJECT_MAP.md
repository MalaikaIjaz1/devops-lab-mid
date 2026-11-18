# PROJECT MAP — Where Everything Is and How It Fits Together

A single-file orientation guide for this repository (CSC418 DevOps Lab Mid).

If you only read one thing: **you are looking at four separate programs that talk to each other
through files, HTTP and GitHub**, not one program.

| # | Question | The one-line answer | Main file(s) |
|---|---|---|---|
| 1 | Where is the main assignment portal? | A Flask app started by `run.py`, serving `http://127.0.0.1:5000` | `run.py`, `app/`, `templates/` |
| 2 | Where is the test that will run? | The pytest suite in `tests/`, executed by `pytest` or by CI | `tests/`, `pytest.ini` |
| 3 | Where is the thing that sends the report to localhost? | Two halves: a **receiver** (`receiver/server.py`, port 5001) and a **sender** (`scripts/run_tests.py`) | `receiver/server.py`, `scripts/run_tests.py` |
| 4 | Where is the mail / Pages deployment? | Two more jobs in the same workflow file | `scripts/send_email_report.py`, `.github/workflows/ci.yml`, `docs/` |

---

## 1. The main assignment portal

This is **requirement 1** (8 marks): the app a student actually uses.

### Files

| File | Role |
|---|---|
| `run.py` | Entry point. Creates the app and runs it on `127.0.0.1:5000`. **This is the "start the portal" button.** |
| `app/__init__.py` | Application factory `create_app()`. Configures the secret key, the SQLite path, registers the blueprint, creates the table. |
| `app/routes.py` | The two routes: `GET /` shows the form + saved list; `POST /submit` validates, saves, or rejects. |
| `app/validation.py` | `validate_submission()` (all four fields required) and `is_valid_url()` (`http`/`https`, no spaces, real host). |
| `app/storage.py` | SQLite persistence: `init_db()`, `add_submission()`, `list_submissions()`, `count_submissions()`. |
| `templates/index.html` | The page itself: form, per-field error messages, "Saved submissions (n)" table. |
| `instance/submissions.db` | Created at first run. **Your real data.** Git-ignored. |

### How a request flows

```
Browser
  │  GET /
  ▼
app/routes.py :: index()
  │  storage.list_submissions()  ──► instance/submissions.db
  ▼
templates/index.html  ──► HTML

Browser
  │  POST /submit  (student_name, registration_number, assignment_title, submission_url)
  ▼
app/routes.py :: submit()
  │
  ├─ app/validation.py :: validate_submission()
  │     errors?  ──► render templates/index.html with messages, HTTP 400, nothing saved
  │
  └─ no errors ──► storage.add_submission(...) ──► 302 redirect to "/" + flash message
```

The `400` status on rejection is deliberate: it makes the rejection machine-checkable, which is
exactly what the tests in section 2 assert.

### Run it

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python run.py
# open http://127.0.0.1:5000
```

---

## 2. The tests that will run

This is **requirement 3** (10 marks).

### Files

| File | Role |
|---|---|
| `tests/test_submissions.py` | The **3 required test cases**, and nothing else (deliberately kept to exactly 3). |
| `tests/conftest.py` | Fixtures: an `app` with a throwaway temp SQLite file per test, and a `client`. Real `instance/submissions.db` is never touched. |
| `pytest.ini` | Points pytest at `tests/`, adds the project root to `pythonpath`. |

### The three tests → the three assignment rows

| Test function | Assignment case | What it asserts |
|---|---|---|
| `test_valid_submission_is_saved_and_displayed` | Complete details + valid URL | HTTP 200, success message, values visible in the list, row really in the DB |
| `test_submission_without_registration_number_is_rejected` | Missing registration number | HTTP 400, "Registration number is required.", DB still empty |
| `test_submission_with_invalid_url_is_rejected` | Invalid submission URL | HTTP 400, URL error message, DB still empty |

### Run them

```powershell
python -m pytest              # all 3
python -m pytest -v           # with test names
python -m pytest -k url       # filter by keyword
```

Expected output: `3 passed`.

**Nothing else runs tests.** `pytest.ini` has `testpaths = tests`, so a stray file elsewhere is not
collected.

---

## 3. The thing that sends the report to localhost

This is **requirement 4** (14 marks). It is **not one file — it's a sender and a receiver.**

```
scripts/run_tests.py  ──POST JSON──►  receiver/server.py  ──write──►  test-report.json
   (the sender)                        (the receiver)                    (the evidence)
   127.0.0.1:5001                      127.0.0.1:5001
```

### 3a. The receiver — `receiver/server.py`

A tiny second Flask app. **This is the "localhost" endpoint.**

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness probe. The CI job calls it before running tests, and auto-starts the receiver if it is down. |
| `POST /report` | Accepts the JSON report, rejects it if any required field is missing, then writes `test-report.json` in the project root. |
| `GET /report` | Returns the last saved report (handy for the demo). |

- Listens on `http://127.0.0.1:5001` (override with `RECEIVER_HOST` / `RECEIVER_PORT`).
- Writes `test-report.json` at the project root (override with `REPORT_PATH`).
- This is the **only** place the report file is written on your machine.

### 3b. The sender — `scripts/run_tests.py`

This is the piece that CI actually executes. It does four things in order:

1. Runs `pytest` in a child process, with `--junitxml` into a temp file.
2. Parses the JUnit XML into the assignment's JSON schema — `repository`, `branch`, `commit_sha`,
   `run_id`, `timestamp`, per-test `name` / `result` / `failure_message`, `total_tests`,
   `passed_tests`, `failed_tests`, `overall_status`.
3. Writes `test-report.json` locally.
4. `POST`s the same JSON to `http://127.0.0.1:5001/report`, retrying 5 times over ~10 seconds.

Metadata is real, never invented: `GITHUB_*` environment variables when in CI, otherwise `git` and
`"local-run"` fallbacks.

**Exit codes — this is what makes a failing test fail the pipeline:**

| Code | Meaning |
|---|---|
| `0` | All tests passed (and the report was delivered) |
| `1` | At least one test failed → the CI job fails → deploy is skipped |
| `3` | Report could not be delivered (only when `--require-receiver` is used) |

Useful flags: `--require-receiver`, `--no-deliver`, `--receiver-url`, and anything else is forwarded
to pytest (`python scripts/run_tests.py -k url`).

### 3c. Why `localhost` works here at all

The assignment warns that a GitHub-hosted runner's `127.0.0.1` is *GitHub's* machine. This project
solves it the second way the brief allows: **the CI runner runs on your own PC**, so
`127.0.0.1:5001` really is your receiver. No tunnel is needed.

- The runner lives in `actions-runner/` (git-ignored, ~650 generated files — never commit it).
- `ci.yml` targets `runs-on: [self-hosted, Windows, X64]` for the `test` and `email-report` jobs.
- The runner must be running for a push to be picked up at all.

Start it manually for the demo:

```powershell
python receiver/server.py     # window 1 — the receiver
cd actions-runner; .\run.cmd  # window 2 — the runner that executes the CI
```

### 3d. The report file

`test-report.json` in the project root, rewritten on every run (passing *or* failing). It is
git-ignored on purpose: it is local evidence, not source code. Both the passing and failing versions
must be demonstrated live.

---

## 4. Mail, Pages deployment and the pipeline that ties it all together

This is **requirement 5** plus **both bonus tasks**, all defined in one file:
`.github/workflows/ci.yml`.

### The three jobs

```
push to main
     │
     ▼
┌──────────────────────────────────────────────┐
│ JOB 1  test        (self-hosted, Windows)    │
│  • install dependencies                      │
│  • GET /health → auto-start receiver if down │
│  • python scripts/run_tests.py --require-receiver
│      → pytest → test-report.json → POST      │
│  • print + upload test-report.json artifact  │
└───────────────┬──────────────────────────────┘
                │
     ┌──────────┴───────────┐
     ▼                      ▼
┌──────────────────────┐  ┌────────────────────────────────┐
│ JOB 2 email-report   │  │ JOB 3 deploy (ubuntu-latest)   │
│  if !cancelled()     │  │  if test == success            │
│  download artifact   │  │  upload docs/ → GitHub Pages   │
│  send_email_report.py│  │  (previous version untouched   │
│  SMTP → your inbox   │  │   on a failing run)            │
└──────────────────────┘  └────────────────────────────────┘
```

**Job 2 — the mail (bonus, 5 marks).** `scripts/send_email_report.py` reads the real
`test-report.json` and sends an email with a text body, an HTML results table, and the JSON attached.
It runs on `if: ${{ !cancelled() && needs.test.result != 'cancelled' }}`, so you get mail for
**both** green and red runs. Supports SMTP 587 (STARTTLS) and 465 (SSL).

Credentials come only from secrets — never code — read as env vars in `ci.yml`:
`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_TO`.
Run `python scripts/send_email_report.py --dry-run` to preview the body with no SMTP connection.

**Job 3 — the Pages deployment (bonus, 5 marks).** Publishes `docs/index.html`, a standalone static
demo of the portal with browser-side validation (Pages cannot run Flask). It is gated on
`needs.test.result == 'success' && github.ref == 'refs/heads/main'`, so a failing revision never
publishes. Job 2 is deliberately **not** a dependency of job 3, so a mail failure cannot block the
deployment.

### One-time settings outside the repo

| Setting | Where |
|---|---|
| Runner registration | GitHub → Settings → Actions → Runners |
| Pages source | Settings → Pages → Source = **GitHub Actions** |
| Six mail secrets | Settings → Secrets and variables → Actions |

---

## 5. Full file map

```
Lab Mid/
├── run.py                        ← START THE PORTAL (port 5000)
├── app/
│   ├── __init__.py               ← app factory, config, DB path
│   ├── routes.py                 ← "/" and "/submit"
│   ├── validation.py             ← required fields + URL rules
│   └── storage.py                ← SQLite
├── templates/index.html          ← portal UI
├── tests/
│   ├── conftest.py               ← temp DB + test client fixtures
│   └── test_submissions.py       ← THE 3 TESTS
├── pytest.ini                    ← testpaths = tests
├── receiver/server.py            ← THE LOCALHOST RECEIVER (port 5001)
├── scripts/
│   ├── run_tests.py              ← THE SENDER: pytest → JSON → POST
│   └── send_email_report.py      ← THE EMAILER
├── docs/index.html               ← static demo shipped to GitHub Pages
├── .github/workflows/ci.yml      ← THE PIPELINE (test / email-report / deploy)
├── requirements.txt              ← Flask, pytest
├── .gitignore                    ← keeps venv, DB, report, runner out of git
├── README.md                     ← full setup + demonstration walkthrough
├── SETUP_GUIDE.md                ← 21 steps from a blank Windows PC
└── SUBMISSION_REPORT.md          ← cover document + mark checklists
```

Git-ignored at runtime: `instance/submissions.db`, `test-report.json`, `.venv/`, `venv/`,
`actions-runner/`, `__pycache__/`, `.pytest_cache/`.

---

## 6. The demonstration, in pipeline terms

| Phase | What you do | What proves it worked |
|---|---|---|
| 1. Green | Push a good commit | Job `test` green, `test-report.json` shows `3 passed` / `overall_status: passed`, mail arrives, Pages updates |
| 2. Break | Remove the registration-number check (see `d71b275` in history) | — |
| 3. Red | Push the defect | `test` job **fails** (`run_tests.py` exits `1`), `test-report.json` overwritten with `failed`, mail arrives with the failure message, **Pages unchanged** |
| 4. Fix | Restore the check | — |
| 5. Green again | Push the fix | Everything green again, JSON back to `passed` |

The git history already contains exactly this sequence, so it can be replayed.

---

## 7. Quick reference — the four things you asked about

```powershell
# 1. the portal
python run.py                          # → http://127.0.0.1:5000

# 2. the tests
python -m pytest -v                    # → tests/test_submissions.py

# 3. the localhost receiver (+ the sender)
python receiver/server.py              # → http://127.0.0.1:5001  writes test-report.json
python scripts/run_tests.py            # → runs tests, builds JSON, POSTs it there

# 4. mail (bonus 2) and Pages (bonus 1)
python scripts/send_email_report.py --dry-run   # preview the email
# Pages: push to main with green tests → job "deploy" publishes docs/index.html
```
