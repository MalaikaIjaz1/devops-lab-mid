# Assignment Submission Portal — CSC418 DevOps Lab Mid Project

A small but complete DevOps assignment project for **COMSATS University Islamabad, Attock Campus**.

It contains a Flask web application that accepts student assignment submissions, an automated
pytest suite, a local HTTP receiver that stores real CI test results as `test-report.json`, a
GitHub Actions pipeline with three jobs (test → email report, test → GitHub Pages deploy), an
automatic email report script, and a static GitHub Pages demo of the portal.

> **All commands in this file are Windows PowerShell commands.**
> They assume the project is stored at `D:\Uni\Semester 08\DevOps\Lab Mid`.
> If your folder is somewhere else, only change the `cd` command.

---

## 1. Project introduction

The portal lets a student submit:

- Student Name
- Registration Number
- Assignment Title
- Submission URL

Every field is required, the URL is validated, invalid submissions are rejected with a clear
message, and valid submissions are stored persistently in a local SQLite database and listed on
the same page.

On top of the core assignment, the project demonstrates a realistic CI/CD pipeline:

1. A **Windows self-hosted GitHub Actions runner** runs on the same computer as the student.
2. The `test` job runs pytest and sends the real JSON results to `http://127.0.0.1:5001/report`.
3. A **local receiver** writes those results to `test-report.json` in the project root.
4. The `email-report` job emails the report (passing **and** failing runs).
5. The `deploy` job publishes the static demo in `docs/` to GitHub Pages, but **only** when the
   tests passed **and** the branch is `main`.

### Architecture

```
┌──────────────────────────────────────────── Windows computer (yours) ───────────────────────────────────────────┐
│                                                                                                                 │
│   GitHub (cloud)                     Self-hosted runner (background Windows service / console window)            │
│  ┌──────────────────┐   job    ┌───────────────────────────────────────────────────────────┐                     │
│  │  Actions runner  │ ───────► │ test job: python scripts/run_tests.py --require-receiver   │                     │
│  │  picks up the    │          │   • runs pytest                                            │                     │
│  │  workflow        │          │   • writes test-report.json                                │                     │
│  └──────────────────┘          │   • POST http://127.0.0.1:5001/report  ──────────────┐    │                     │
│                                └───────────────────────────────────────────────────────┼────┘                     │
│                                                                                        ▼                        │
│                                                    ┌──────────────────────────────────────────┐                 │
│                                                    │ receiver/server.py  (Flask, 127.0.0.1:5001)│                 │
│                                                    │ saves the payload as test-report.json      │                 │
│                                                    └──────────────────────────────────────────┘                 │
│                                                                                                                 │
│   email-report job ──► scripts/send_email_report.py ──► SMTP (port 587 STARTTLS or 465 SSL) ──► your inbox       │
│   deploy job (ubuntu-latest) ──► actions/deploy-pages ──► GitHub Pages (docs/index.html)                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Why a self-hosted runner is required:** a GitHub-hosted runner runs on GitHub's machines, so
`127.0.0.1` inside that runner means *GitHub's* computer, not yours. The report would never reach
your PC. A self-hosted runner runs on your computer, so `127.0.0.1:5001` is your receiver.

---

## 2. Features

**Core**

- Flask portal with four required fields.
- Server-side URL validation (`http://` / `https://`, real domain, no spaces).
- Clear, per-field validation messages; invalid submissions return HTTP 400 and are never saved.
- Persistent storage in SQLite (`instance/submissions.db`) that survives restarts.
- A table listing every saved submission.
- Seven pytest tests, including the three required scenarios.
- Local HTTP report receiver on `127.0.0.1:5001` with `POST /report`.
- Real `test-report.json` (repository, branch, commit SHA, run ID, timestamp, per-test results,
  failure messages, totals, overall status) — never hand-written.
- Reports delivered for both passing and failing runs.
- Documented pass → fail → fix demonstration.
- `.gitignore` that keeps venv, databases, reports and runner credentials out of git.

**Bonus 1 — conditional GitHub Pages deployment**

- `docs/index.html` static demo of the portal with browser-side validation.
- Deploy only after tests succeed, only from `main`.
- Failed runs never publish, so the previously deployed site stays online.

**Bonus 2 — automatic email report**

- `scripts/send_email_report.py` reads the real `test-report.json`.
- Sends after passing and failing runs, with all metadata and the JSON file attached.
- Credentials only from environment variables / GitHub Secrets.
- Supports SMTP 587 (STARTTLS) and 465 (SSL).

---

## 3. Technologies used

| Technology | Purpose |
|---|---|
| Python 3.12 | Application and scripts |
| Flask 3.0 | Web application and local report receiver |
| SQLite (standard library) | Persistent storage for submissions |
| pytest 8.3 | Automated tests |
| JUnit XML → JSON | Turning raw pytest output into the required report |
| GitHub Actions | CI/CD pipeline (three jobs) |
| Windows self-hosted runner | Lets CI reach `127.0.0.1:5001` on your computer |
| GitHub Pages Actions | Publishing the static demo |
| SMTP + Gmail App Password | Email reports |

---

## 4. Project structure

```
Lab Mid/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── routes.py            # "/" and "/submit" routes
│   ├── storage.py           # SQLite persistence (create, insert, list, count)
│   └── validation.py        # Required-field and URL validation rules
├── templates/
│   └── index.html           # Portal page: form, errors, saved submissions table
├── tests/
│   ├── conftest.py          # Temporary database + Flask test client fixtures
│   └── test_submissions.py  # 7 tests (includes the 3 required ones)
├── receiver/
│   └── server.py            # Local HTTP receiver (127.0.0.1:5001, POST /report)
├── scripts/
│   ├── run_tests.py         # pytest → JUnit XML → test-report.json → POST to receiver
│   └── send_email_report.py # Reads test-report.json and emails it
├── docs/
│   └── index.html           # Static GitHub Pages demo
├── .github/
│   └── workflows/
│       └── ci.yml           # test + email-report + deploy jobs
├── pytest.ini               # testpaths, pythonpath, addopts
├── requirements.txt         # Flask + pytest
├── .gitignore
├── run.py                   # Starts the Flask portal on http://127.0.0.1:5000
├── README.md                # This file
├── SETUP_GUIDE.md           # Step-by-step guide from a blank computer
└── SUBMISSION_REPORT.md     # Submission cover document and checklists
```

Generated at runtime (ignored by git): `instance/submissions.db`, `test-report.json`,
`__pycache__/`, `.pytest_cache/`, `.venv/`.

---

## 5. Python installation requirements

- **Python 3.10 or newer** (tested with Python 3.12).
- **Git for Windows**.
- **VS Code** (optional but recommended).
- Windows 10 or Windows 11.

Check what you already have:

```powershell
python --version
git --version
```

If `python --version` prints `Python 3.12.x` (or any 3.10+), you are ready.
If the command is not recognised, install Python from <https://www.python.org/downloads/windows/>
and tick **“Add python.exe to PATH”** in the installer.

---

## 6. Virtual environment setup

A virtual environment keeps this project’s packages separate from the rest of your computer.

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once and then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Your prompt now starts with `(.venv)`. To leave the environment:

```powershell
deactivate
```

---

## 7. Dependency installation

With the virtual environment activated:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify both packages import:

```powershell
python -c "import flask, pytest; print(flask.__version__, pytest.__version__)"
```

Expected output is similar to `3.0.3 8.3.3`.

---

## 8. Running the Flask application

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python run.py
```

Open <http://127.0.0.1:5000> in your browser.

- Fill in all four fields and press **Save submission** → a green confirmation appears and the row
  is added to *Saved submissions*.
- Leave *Registration Number* empty → the submission is rejected with
  “Registration number is required.” and nothing is saved.
- Enter `not-a-url` as the URL → rejected with a URL validation message.
- Stop the server with `CTRL+C`. Start it again and reload the page: submissions are still there,
  because they are stored in `instance/submissions.db`.

Optional: the app signs its flash-message cookie with a random key generated at start-up. Set the
`SECRET_KEY` environment variable if you want that cookie to survive a restart (not required for
the assignment, and never commit a real value):

```powershell
$env:SECRET_KEY = "any-long-random-string-you-generate-yourself"
```

---

## 9. Running pytest

Run the whole suite:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python -m pytest
```

Run a single test:

```powershell
python -m pytest tests/test_submissions.py::test_submission_without_registration_number_is_rejected -v
```

Run the tests **and** produce/deliver the JSON report (this is what CI runs):

```powershell
python scripts/run_tests.py
```

Useful options:

| Command | Behaviour |
|---|---|
| `python scripts/run_tests.py` | Runs tests, writes `test-report.json`, tries to POST it |
| `python scripts/run_tests.py --no-deliver` | Writes the report but does not contact the receiver |
| `python scripts/run_tests.py --require-receiver` | Fails with exit code 3 if delivery fails (used in CI) |
| `python scripts/run_tests.py -k url` | Forwards `-k url` to pytest |

Exit codes: `0` = all tests passed, `1` = at least one test failed, `3` = the report could not be delivered.

The three required tests, mapped to the assignment:

| Requirement | Test |
|---|---|
| Complete valid submission is saved and displayed | `test_valid_submission_is_saved_and_displayed` |
| Missing registration number is rejected and not saved | `test_submission_without_registration_number_is_rejected` |
| Invalid URL is rejected and not saved | `test_submission_with_invalid_url_is_rejected` |

---

## 10. Starting the local report receiver

Open a **separate** PowerShell window (keep it open) and run:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python receiver/server.py
```

You should see:

```
==============================================================
 Local test report receiver
 Listening on : http://127.0.0.1:5001
 POST reports : http://127.0.0.1:5001/report
 Report file  : D:\Uni\Semester 08\DevOps\Lab Mid\test-report.json
 Press CTRL+C to stop.
==============================================================
```

Check it is alive:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5001/health
```

Read the last received report:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5001/report
```

Now, in another window, run `python scripts/run_tests.py`. The receiver prints a line such as:

```
[receiver] 2026-11-11T10:15:03Z | your-name/devops-lab-mid | main | run 1234567890 | PASSED | 7/7 passed
```

and `test-report.json` appears in the project root.

Received reports are saved to `test-report.json`, which is **git-ignored** on purpose: it is
generated evidence, not source code. Screenshot it for your submission.

**Where exactly is the file written?** Next to the receiver script you started — that is, the
project root when you start it from this folder. The `test` job also starts its own copy of the
receiver as a fallback if nothing is listening; that copy lives inside the runner’s checkout folder
(`_work\<repo>\<repo>`). The artifact and the email always use that checkout copy, so both work
either way. For the evidence in your project root, keep the receiver from step 10 running.

### Report schema

```json
{
  "repository": "student-name/devops-lab-mid",
  "branch": "main",
  "commit_sha": "9f2c1a4e...",
  "run_id": "1234567890",
  "workflow": "CI - Test, Email Report, Deploy",
  "event": "push",
  "actor": "student-name",
  "runner": "DESKTOP-ABC",
  "timestamp": "2026-11-11T10:15:03Z",
  "duration_seconds": 3.42,
  "overall_status": "passed",
  "total_tests": 7,
  "passed_tests": 7,
  "failed_tests": 0,
  "skipped_tests": 0,
  "tests": [
    { "name": "tests.test_submissions::test_valid_submission_is_saved_and_displayed",
      "result": "passed", "duration_seconds": 0.021 }
  ]
}
```

Failing tests add a `failure_message` field to the affected test object.

---

## 11. Configuring the Windows self-hosted runner

You must do this once, on the same computer where the receiver runs.

1. Push the project to GitHub first (see section 15 / SETUP_GUIDE.md step 10–11).
2. In your repository, open **Settings → Actions → Runners → New self-hosted runner**.
3. Choose **Windows** and **x64**. GitHub shows the exact download and configuration commands —
   **use the versions and token GitHub shows you**.
4. Install the runner **outside** the project folder, for example `C:\actions-runner`:

```powershell
cd C:\
New-Item -ItemType Directory -Path C:\actions-runner -Force
cd C:\actions-runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-win-x64-2.319.1.zip -OutFile actions-runner-win-x64.zip
Expand-Archive -Path actions-runner-win-x64.zip -DestinationPath C:\actions-runner -Force
```

5. Configure it (replace the URL; paste the token GitHub generated for you — **never** commit it):

```powershell
cd C:\actions-runner
.\config.cmd --url https://github.com/<your-username>/<your-repo> --token <TOKEN_FROM_GITHUB>
```

Accept the default runner group, the default name, and the default work folder `_work`.
When asked for extra labels, just press **Enter**.

6. Start the runner and keep the window open while you demonstrate:

```powershell
cd C:\actions-runner
.\run.cmd
```

You should see `Listening for Jobs`. The runner appears as **Idle** on the Settings → Actions →
Runners page.

7. Optional — run the runner as a Windows service so it survives closing the window:

```powershell
cd C:\actions-runner
.\svc.cmd install
.\svc.cmd start
```

The workflow targets the default labels of that runner: `self-hosted`, `Windows`, `X64`.
If your runner has different labels, edit `runs-on` in `.github/workflows/ci.yml`.

**Security:** the `.runner` file, `_work/`, `_diag/` and the whole `actions-runner` folder contain
credentials. They are in `.gitignore`; keep them outside the repository as well.

---

## 12. GitHub Actions workflow explanation

`.github/workflows/ci.yml` runs on every push to `main` and can also be started manually
(**Actions → CI - Test, Email Report, Deploy → Run workflow**).

```
push to main
     │
     ▼
┌─────────┐   success or failure   ┌───────────────┐
│  test   │ ─────────────────────► │ email-report  │
│ (Windows│                        │ (Windows      │
│  self-  │                        │  self-hosted) │
│ hosted) │                        └───────────────┘
│         │   success + main only
│         │ ─────────────────────► ┌──────────┐
└─────────┘                        │  deploy  │ → GitHub Pages
                                   │(ubuntu)  │
                                   └──────────┘
```

**Job 1 — `test`** (Windows self-hosted runner)

1. `actions/checkout@v4`
2. Verifies Python.
3. Installs `requirements.txt`.
4. Makes sure the local receiver is running: it calls `/health`, and if the receiver is not up it
   starts `python receiver/server.py` in the background and waits up to 20 seconds.
5. Runs `python scripts/run_tests.py --require-receiver`, which returns a **non-zero exit code
   when any test fails**, so the job (and the whole workflow) fails.
6. Shows `test-report.json`.
7. Uploads `test-report.json` with `actions/upload-artifact@v4` and **`if: always()`**, so the
   artifact exists for failing runs too.

**Job 2 — `email-report`**

- `needs: test`
- `if: ${{ !cancelled() && needs.test.result != 'cancelled' }}` → runs after success **or**
  failure, never after cancellation.
- Downloads the `test-report` artifact and runs `python scripts/send_email_report.py`.
- Receives all SMTP values from GitHub Secrets.
- It is **not** a dependency of `deploy`, so a mail problem can never block the website.

**Job 3 — `deploy`**

- `needs: test`
- `if: ${{ needs.test.result == 'success' && github.ref == 'refs/heads/main' }}` → skipped when
  tests fail, and skipped on other branches.
- Permissions: `contents: read`, `pages: write`, `id-token: write`.
- `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3` (path `docs`) →
  `actions/deploy-pages@v4`.

Because a failed run never runs the deploy job, the **previously deployed website stays online**.

---

## 13. GitHub Pages configuration

1. Push the code to GitHub with the default branch named `main`.
2. Repository **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **GitHub Actions**.
4. Push a commit to `main`. When the `test` job passes, `deploy` publishes the site.
5. Your URL appears in **Settings → Pages** and in the workflow summary:
   `https://<your-username>.github.io/<your-repo>/`
6. Paste that URL into `SUBMISSION_REPORT.md`.

No `gh-pages` branch is needed — the modern Pages actions publish directly.

---

## 14. Email secrets configuration

Create these six **repository secrets** in **Settings → Secrets and variables → Actions →
New repository secret**:

| Secret | Example value | Notes |
|---|---|---|
| `MAIL_SERVER` | `smtp.gmail.com` | Your SMTP host |
| `MAIL_PORT` | `587` | `587` = STARTTLS, `465` = SSL |
| `MAIL_USERNAME` | `you@gmail.com` | Full email address |
| `MAIL_PASSWORD` | *(App Password)* | **Not** your normal password |
| `MAIL_FROM` | `you@gmail.com` | Sender address |
| `MAIL_TO` | `you@gmail.com` | One address, or several separated by commas |

Gmail App Password (requires 2-Step Verification): Google Account → Security → 2-Step
Verification → App passwords → create one for “Mail / Windows Computer”. Copy the 16-character
value into `MAIL_PASSWORD` and store the password in your password manager.

**Never** put these values in code, in the README, in screenshots or in chat.

Test the script locally without sending anything:

```powershell
python scripts/send_email_report.py --dry-run
```

Send a real email locally (values only in this PowerShell session):

```powershell
$env:MAIL_SERVER = "smtp.gmail.com"
$env:MAIL_PORT = "587"
$env:MAIL_USERNAME = "you@gmail.com"
$env:MAIL_PASSWORD = "your-app-password"
$env:MAIL_FROM = "you@gmail.com"
$env:MAIL_TO = "you@gmail.com"
python scripts/send_email_report.py
Remove-Item Env:MAIL_PASSWORD
```

Use `MAIL_PORT=465` if your network blocks 587; the script switches to SSL automatically.
If a secret is missing the script exits with an error listing the missing variable **names** — it
never prints values.

---

## 15. Running the complete demonstration

Prepare once: receiver running (section 10), runner running (section 11), secrets added
(section 14), Pages source set to GitHub Actions (section 13).

### Phase 1 — green run

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
git add .
git commit -m "feat: assignment submission portal with CI pipeline"
git push origin main
```

Watch **Actions → CI - Test, Email Report, Deploy**.

- `Run pytest and deliver JSON report` → **success** (7 tests).
- Receiver console prints `PASSED | 7/7 passed`.
- `Email the test report` → **success**, email arrives with the JSON attached.
- `Deploy static demo to GitHub Pages` → **success**, site published.

Take screenshots of: the green workflow, the receiver console, the email, the report file and the
live site.

### Phase 2 — introduce the deliberate defect

Open `app/validation.py` and change the required-field loop so the registration number is not
required:

```python
    for field, label in FIELD_LABELS.items():
        if field == "registration_number":
            continue  # DELIBERATE DEFECT - remove after the demo
        if not cleaned[field]:
            errors[field] = f"{label} is required."
```

Also delete the `if not errors.get("registration_number"):` block, so an empty registration number
slips through. Then:

```powershell
python -m pytest -v
git add app/validation.py
git commit -m "test: demonstrate failing validation (deliberate defect)"
git push origin main
```

### Phase 3 — red run

- `Run pytest and deliver JSON report` → **failure** (`test_submission_without_registration_number_is_rejected`).
- Receiver console prints `FAILED | 6/7 passed` and `test-report.json` now contains the failure
  message.
- `Email the test report` → **success**, email subject starts with `[FAILED]`.
- `Deploy static demo to GitHub Pages` → **skipped**, so the previous site is still online.
- Artifact `test-report` is still uploaded (`if: always()`).

### Phase 4 — fix the defect

```powershell
git revert --no-edit HEAD
```

or edit `app/validation.py` back to its correct form, then:

```powershell
git add app/validation.py
git commit -m "fix: restore registration number validation"
git push origin main
```

### Phase 5 — green run again

- 7/7 tests pass, report shows `PASSED`, a green email arrives, and Pages deploys again.

**Never leave the defect in the final code.** Confirm with:

```powershell
git log --oneline -3
python -m pytest -q
```

### Optional — trigger a run manually

```powershell
gh workflow run "CI - Test, Email Report, Deploy"
```

(then `gh run watch`) — or use the **Run workflow** button on the Actions page.

---

## 16. Common errors and solutions

| Symptom | Cause | Fix |
|---|---|---|
| `'python' is not recognized` | Python not on PATH | Reinstall Python with “Add python.exe to PATH”, or use `py -3` |
| `ModuleNotFoundError: No module named 'flask'` | Virtual environment not active | `.\.venv\Scripts\Activate.ps1` |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `pytest: command not found` | pytest not installed / not on PATH | `python -m pytest` after activating the venv |
| `Delivery attempt 1/5 failed: [WinError 10061]` / `Connection refused` | Receiver not running | Start `python receiver/server.py` in its own window |
| `OSError: [WinError 10048] only one usage of each socket address` | Port 5001 (or 5000) already in use | `netstat -ano \| findstr :5001` then `Stop-Process -Id <PID>` |
| Workflow waits forever on `Run pytest...` with no output | Runner offline or wrong labels | Start `C:\actions-runner\run.cmd`; check labels `self-hosted`, `Windows`, `X64` |
| Workflow fails at “Make sure the local report receiver is running” | Receiver could not start or is blocked | Start it manually, check `Invoke-RestMethod http://127.0.0.1:5001/health` |
| `email-report` fails with “missing required environment variables” | Secrets not created | Add all six secrets (section 14) |
| `SMTPAuthenticationError: 535` | Normal password used instead of an App Password | Create a Gmail App Password and update `MAIL_PASSWORD` |
| `TimeoutError` / `ConnectionRefusedError` on port 587 | ISP blocks the port | Set `MAIL_PORT` to `465` |
| `deploy` job is skipped | Tests failed, or branch is not `main` | Fix tests; merge/push to `main` |
| GitHub Pages shows 404 | Pages source not set to **GitHub Actions** | Settings → Pages → Source → GitHub Actions, then re-run the workflow |
| `git push` rejected (`non-fast-forward`) | Remote has commits you do not have | `git pull --rebase origin main` then push |
| `git push` asks for a password | GitHub requires a token | Use a Personal Access Token as the password, or `gh auth login` |
| `test-report.json` is missing after a run | Report never delivered and script not used | Run `python scripts/run_tests.py`; check the receiver window |
| `actions/upload-artifact` warning “no files found” | `run_tests.py` crashed before writing the report | Read the pytest log in the failed step |
| YAML error: `mapping values are not allowed here` | Bad indentation in `ci.yml` | YAML uses spaces only; keep two-space indentation |
| Tests pass locally but fail in CI | Different Python or stale DB | Delete `instance/`, re-run `python -m pip install -r requirements.txt` |

---

## Reference — exit codes and generated files

| Item | Path | Committed? |
|---|---|---|
| Submission database | `instance/submissions.db` | No (git-ignored) |
| Test report | `test-report.json` | No (git-ignored, uploaded as a CI artifact) |
| Receiver | `receiver/server.py` | Yes |
| Static demo | `docs/index.html` | Yes |

| `scripts/run_tests.py` exit code | Meaning |
|---|---|
| `0` | All tests passed |
| `1` | At least one test failed |
| `3` | Report could not be delivered (`--require-receiver`) |

---

## Manual steps that only you can do

The code is complete, but these actions need your GitHub account, your email account and your
computer — they are **not** done automatically:

1. Create the GitHub repository and push (SETUP_GUIDE.md steps 9–10).
2. Create, configure and start the Windows self-hosted runner (section 11).
3. Start the receiver on your computer (section 10).
4. Add the six repository secrets (section 14).
5. Set Pages source to **GitHub Actions** (section 13).
6. Run the pass → fail → fix demonstration and take your screenshots (section 15).
7. Fill in your details and URLs in `SUBMISSION_REPORT.md`.
