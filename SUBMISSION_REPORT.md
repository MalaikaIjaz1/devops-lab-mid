# SUBMISSION REPORT — CSC418 DevOps Lab Mid Project

## Assignment title

**CSC418 DevOps Lab Mid Project — Assignment Submission Portal with CI/CD, Local JSON Report
Receiver, Conditional GitHub Pages Deployment and Automatic Email Reports**

## Student information

| Field | Value |
|---|---|
| Student Name | _<fill in your full name>_ |
| Registration Number | _<fill in your registration number>_ |
| Class / Section | _<fill in your class and section>_ |
| Course | CSC418 — DevOps |
| Instructor | _<fill in your instructor’s name>_ |
| Campus | COMSATS University Islamabad, Attock Campus |
| Submission Date | _<fill in the submission date>_ |

## Repository and deployment URLs

| Item | URL |
|---|---|
| GitHub repository | _<https://github.com/your-username/devops-lab-mid>_ |
| GitHub Pages site | _<https://your-username.github.io/devops-lab-mid/>_ |
| GitHub Actions runs | _<https://github.com/your-username/devops-lab-mid/actions>_ |

> These are placeholders on purpose. Replace them with your real URLs after you push the project.
> Do not leave placeholder text in the final PDF.

---

## 1. Project overview

The project is a Flask **Assignment Submission Portal** with four required fields (Student Name,
Registration Number, Assignment Title, Submission URL), server-side URL validation, clear
per-field error messages, rejection of invalid submissions (HTTP 400) and persistent storage in a
local SQLite database. Saved submissions are listed on the same page.

Around the application sits a complete CI/CD demonstration:

- **pytest** suite with seven automated tests, including the three required scenarios.
- **Local HTTP report receiver** (`receiver/server.py`) on `127.0.0.1:5001`, which saves real CI
  results as `test-report.json` in the project root.
- **Windows self-hosted GitHub Actions runner**, so the CI job can reach the receiver on the
  student’s own computer (`127.0.0.1` inside a GitHub-hosted runner is not the student’s machine).
- **GitHub Actions workflow** with three jobs: `test`, `email-report` and `deploy`.
- **Bonus 1:** conditional GitHub Pages deployment of `docs/index.html` after green tests on `main`.
- **Bonus 2:** automatic email report after passing and failing runs, with the JSON attached.

### Repository contents (what the marker can inspect)

| Path | Purpose |
|---|---|
| `app/__init__.py` | Flask application factory, configuration, database path |
| `app/routes.py` | `/` (form + list) and `/submit` (validate, save, or reject) |
| `app/storage.py` | SQLite persistence (create table, insert, list, count) |
| `app/validation.py` | Required-field checks and URL validation |
| `templates/index.html` | Portal UI with inline error messages and submissions table |
| `tests/conftest.py` | Temporary database and Flask test-client fixtures |
| `tests/test_submissions.py` | 7 pytest tests |
| `receiver/server.py` | Local report receiver (`POST /report`, `GET /health`, `GET /report`) |
| `scripts/run_tests.py` | Runs pytest → JUnit XML → `test-report.json` → POST to receiver |
| `scripts/send_email_report.py` | Emails the real report (SMTP 587 STARTTLS / 465 SSL) |
| `docs/index.html` | Static GitHub Pages demo with browser-side validation |
| `.github/workflows/ci.yml` | The three CI jobs |
| `README.md` | Feature list, setup, workflow and error documentation |
| `SETUP_GUIDE.md` | 21-step guide from a blank Windows computer |

---

## 2. Core requirements checklist

| # | Requirement | Marks | Status | Where it is implemented / evidence |
|---|---|---|---|---|
| 1 | Flask app with Student Name, Registration Number, Assignment Title, Submission URL | 8 | ☐ Done | `app/routes.py`, `templates/index.html` |
| 2 | All fields required | | ☐ Done | `app/validation.py` (`FIELD_LABELS` loop) |
| 3 | Submission URL validated | | ☐ Done | `app/validation.py` `is_valid_url()` |
| 4 | Clear validation messages shown | | ☐ Done | Per-field `<p class="field-error">` in `templates/index.html` |
| 5 | Invalid submissions rejected | | ☐ Done | `POST /submit` returns HTTP 400, nothing saved |
| 6 | Valid submissions saved persistently | | ☐ Done | `app/storage.py` (SQLite `instance/submissions.db`) |
| 7 | All saved submissions displayed | | ☐ Done | “Saved submissions (n)” table in `templates/index.html` |
| 8 | No file upload | | ☐ Done | Only text/URL fields exist |
| 9 | GitHub-ready repository (app, tests, workflow, receiver, report scripts, email script, static demo, README) | 4 | ☐ Done | See repository contents table above |
| 10 | pytest with the three required tests | 10 | ☐ Done | `tests/test_submissions.py` |
| 11 | Failing test makes the CI test job fail | | ☐ Done | `run_tests.py` exits 1; the `test` job step fails |
| 12 | Local receiver on `127.0.0.1:5001`, `POST /report` | 14 | ☐ Done | `receiver/server.py` |
| 13 | Saves received report as `test-report.json` in project root | | ☐ Done | `REPORT_PATH` in `receiver/server.py` |
| 14 | Report contains repository, branch, commit SHA, run ID, timestamp, per-test name/result/failure message, totals, overall status | | ☐ Done | `build_report()` in `scripts/run_tests.py` |
| 15 | Reports delivered for passing **and** failing runs | | ☐ Done | Delivery happens before the exit code is returned |
| 16 | No fake or manually copied reports | | ☐ Done | Report is produced from the real JUnit XML of the run |
| 17 | Windows self-hosted runner documented | | ☐ Done | README §11, SETUP_GUIDE steps 11–13 |
| 18 | Pass → fail → fix demonstration prepared | 4 | ☐ Done | README §15, SETUP_GUIDE steps 16–18, section 6 below |

---

## 3. Bonus requirements checklist

### Bonus 1 — Conditional GitHub Pages deployment (5 marks)

| Requirement | Status | Where |
|---|---|---|
| `docs/index.html` static demo | ☐ Done | `docs/index.html` |
| Resembles the Flask portal | ☐ Done | Same layout, colours and four fields |
| Student name, registration number, assignment title, submission URL fields | ☐ Done | Demo form |
| Browser-side validation | ☐ Done | Inline `<script>` `validate()` / `isValidUrl()` |
| Displays sample submitted assignments | ☐ Done | “Sample submissions” table (labelled example data) |
| Explains it is a static demonstration | ☐ Done | Yellow notice banner and section labels |
| Tests run before deployment | ☐ Done | `deploy` has `needs: test` |
| Deploy only after all tests pass | ☐ Done | `needs.test.result == 'success'` |
| Deploy only from `main` | ☐ Done | `github.ref == 'refs/heads/main'` |
| Skipped after failed tests | ☐ Done | Condition false → job skipped |
| Previous site preserved after a failed run | ☐ Done | Failed runs never call `deploy-pages` |
| Workflow permissions `contents: read`, `pages: write`, `id-token: write` | ☐ Done | Workflow-level `permissions` block |
| Deployment job depends on the test job | ☐ Done | `needs: test` |

### Bonus 2 — Automatic email report (5 marks)

| Requirement | Status | Where |
|---|---|---|
| `scripts/send_email_report.py` | ☐ Done | Script exists |
| Reads the real `test-report.json` | ☐ Done | `load_report()` |
| Sends after successful runs | ☐ Done | `if: ${{ !cancelled() }}` on the job |
| Sends after failed runs | ☐ Done | Same condition (failure is not cancellation) |
| Includes repository, branch, commit SHA, run ID, overall status | ☐ Done | `format_text_body()` / `format_html_body()` |
| Includes total, passed and failed counts | ☐ Done | Totals block |
| Includes individual test names and results | ☐ Done | Per-test list / table |
| Includes failure messages | ☐ Done | `failure_message` per failing test |
| Attaches the JSON report | ☐ Done | `add_attachment(..., subtype="json")` |
| Environment variables only (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_TO`) | ☐ Done | `REQUIRED_ENV_VARS` |
| SMTP 587 STARTTLS and 465 SSL | ☐ Done | `send_email()` |
| No hardcoded credentials | ☐ Done | Only `os.environ[...]` |
| Values passed through GitHub Secrets | ☐ Done | `env:` block of the email step |
| Separate email job after the test job | ☐ Done | `email-report` job, `needs: test` |
| Runs on success or failure, not on cancellation | ☐ Done | `!cancelled() && needs.test.result != 'cancelled'` |
| Downloads the uploaded artifact | ☐ Done | `actions/download-artifact@v4` |
| Test job uploads with `actions/upload-artifact@v4` and `if: always()` | ☐ Done | Upload step |
| Email job cannot block deployment | ☐ Done | `deploy` depends only on `test` |

---

## 4. Test case descriptions

All tests live in `tests/test_submissions.py`. Every test uses its own temporary SQLite database,
so no test can affect another one or the real database.

### Required Test 1 — valid submission

**Test:** `test_valid_submission_is_saved_and_displayed`

**Input:** all four fields filled; registration `FA22-BCS-123`; URL
`https://github.com/ayesha-khan/devops-lab-mid`.

**Expected:** HTTP 200 after the redirect, the success message appears, the new row is rendered,
and exactly one row exists in the database with the same registration number and URL.

### Required Test 2 — missing registration number

**Test:** `test_submission_without_registration_number_is_rejected`

**Input:** a valid submission with `registration_number` removed.

**Expected:** HTTP 400, the message “Registration number is required.” is rendered, and the
database stays empty.

### Required Test 3 — invalid URL

**Test:** `test_submission_with_invalid_url_is_rejected`

**Input:** a valid submission with `submission_url = "this-is-not-a-url"`.

**Expected:** HTTP 400, a “Submission URL must be a valid …” message, and no database row.

### Additional tests

| Test | Purpose |
|---|---|
| `test_submission_without_student_name_is_rejected` | Blank/whitespace names are trimmed and rejected |
| `test_submission_url_must_use_http_or_https` | `www.github.com/...` (no scheme) is rejected |
| `test_saved_submissions_survive_a_new_request` | The list is rendered again on the next request |
| `test_empty_portal_lists_no_submissions` | The empty state renders correctly |

Local result at the time of writing: **7 passed**.

---

## 5. Setup instructions

### 5.1 Quick local run

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Open <http://127.0.0.1:5000>.

### 5.2 Local tests

```powershell
python -m pytest -v
python scripts/run_tests.py --require-receiver
```

### 5.3 Report receiver (separate window, keep open)

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python receiver/server.py
```

### 5.4 Push to GitHub

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
git init
git branch -M main
git add .
git commit -m "feat: assignment submission portal with CI pipeline"
git remote add origin https://github.com/<your-username>/devops-lab-mid.git
git push -u origin main
```

### 5.5 One-time GitHub configuration

1. **Settings → Actions → Runners → New self-hosted runner → Windows x64**, then configure and
   start it from `C:\actions-runner` (`.\config.cmd --url ... --token ...`, `.\run.cmd`).
2. **Settings → Pages → Source: GitHub Actions**.
3. **Settings → Secrets and variables → Actions → New repository secret** for `MAIL_SERVER`,
   `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_TO`.

The full beginner-level version of every step is in `SETUP_GUIDE.md`.

---

## 6. Pass–fail–fix demonstration instructions

### Phase 1 — green run

```powershell
git push origin main
```

Expected: `test` ✅ (7 passed) → `email-report` ✅ → `deploy` ✅.
Receiver prints `PASSED | 7/7 passed`; `test-report.json` shows `"overall_status": "passed"`.

### Phase 2 — introduce the defect

In `app/validation.py`, inside `validate_submission`, skip the registration number in the
required-field loop:

```python
    for field, label in FIELD_LABELS.items():
        if field == "registration_number":
            continue  # DELIBERATE DEFECT
        if not cleaned[field]:
            errors[field] = f"{label} is required."
```

and remove the minimum-length check for the registration number. Then:

```powershell
python -m pytest -v
git add app/validation.py
git commit -m "test: deliberate validation defect for the demo"
git push origin main
```

### Phase 3 — red run

Expected: `test` ❌ (`test_submission_without_registration_number_is_rejected` fails),
artifact uploaded anyway, `email-report` ✅ with a `[FAILED]` email, `deploy` ⏭️ skipped.
Receiver prints `FAILED | 6/7 passed`; the report contains the failure message.

### Phase 4 — fix

```powershell
git revert --no-edit HEAD
git push origin main
```

### Phase 5 — green run again

Expected: all three jobs green, `PASSED` report and email, Pages redeployed.

**Final check that no defect remains:**

```powershell
git log --oneline -3
python -m pytest -q
```

---

## 7. Evidence checklist

Tick each item and attach the screenshot or file. Nothing here is pre-filled: these must come from
your own run.

| # | Evidence | How to capture | Done |
|---|---|---|---|
| 1 | Portal page with the form and a saved submission | Screenshot `http://127.0.0.1:5000` after a valid submission | ☐ |
| 2 | Rejection of a missing registration number | Screenshot of the red “Registration number is required.” message | ☐ |
| 3 | Rejection of an invalid URL | Screenshot of the URL validation message | ☐ |
| 4 | Local pytest output (7 passed) | Screenshot of `python -m pytest -v` | ☐ |
| 5 | Receiver console showing a received report | Screenshot of the `[receiver] ... PASSED` line | ☐ |
| 6 | Passing `test-report.json` | Copy/screenshot of the file, or the uploaded artifact | ☐ |
| 7 | Failing `test-report.json` (with failure message) | Copy/screenshot taken right after the deliberate-defect run | ☐ |
| 8 | Green workflow run (3 jobs) | Screenshot of the Actions run summary | ☐ |
| 9 | Red workflow run (test failed, deploy skipped) | Screenshot of the same summary page | ☐ |
| 10 | Artifact `test-report` present on the failed run | Screenshot of the run’s Artifacts section | ☐ |
| 11 | `[FAILED]` email received | Screenshot of the inbox and the opened email | ☐ |
| 12 | `[PASSED]` email received | Screenshot of the inbox and the opened email | ☐ |
| 13 | Email attachment is the JSON report | Screenshot showing `test-report.json` attached | ☐ |
| 14 | Deployed GitHub Pages site | Screenshot of the live URL | ☐ |
| 15 | Pages site still online after a failed run | Screenshot of the site plus the skipped deploy job | ☐ |
| 16 | Self-hosted runner idle/online | Screenshot of Settings → Actions → Runners | ☐ |
| 17 | Repository file tree | Screenshot of the GitHub repository root | ☐ |
| 18 | No secrets committed | Screenshot of `.gitignore` and a search for `MAIL_PASSWORD` returning nothing | ☐ |

---

## 8. Notes and limitations (honest declaration)

- The GitHub repository, GitHub Pages site, self-hosted runner, email secrets and email deliveries
  have **not** been created or configured by this project generation. They require the student’s
  own GitHub and email accounts and must be completed manually using `SETUP_GUIDE.md`.
- No screenshots, test runs, artifact IDs, run IDs, repository URLs or email evidence are invented
  in this document. All such fields are placeholders to be filled by the student.
- `test-report.json` and `instance/submissions.db` are generated locally and are **git-ignored** on
  purpose; the report is transported to the email job as a GitHub artifact instead.
- The receiver is a local development server (Flask’s built-in server). It is intentionally bound
  to `127.0.0.1` so it is never exposed to the network.
- Passwords, App Passwords, runner registration tokens and `.env` files must never be committed or
  shown in screenshots.
