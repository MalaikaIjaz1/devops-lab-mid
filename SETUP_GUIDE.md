# SETUP GUIDE — from a blank Windows computer to a finished assignment

This guide assumes you have **never** used GitHub Actions, a self-hosted runner or GitHub Pages.
It explains every step in plain language.

**Words used in this guide**

| Word | What it means here |
|---|---|
| Terminal | The PowerShell window where you type commands |
| Virtual environment (venv) | A private folder of Python packages for this project only |
| Repository (repo) | Your project folder on GitHub |
| Workflow | The automated pipeline defined in `.github/workflows/ci.yml` |
| Job | One part of a workflow (`test`, `email-report`, `deploy`) |
| Runner | The small program that runs your workflow jobs |
| Self-hosted runner | A runner installed on **your** computer, not GitHub’s |
| Artifact | A file uploaded by a workflow run (here: `test-report.json`) |
| Secret | A password stored safely in GitHub, hidden from logs |

**Project path used below:** `D:\Uni\Semester 08\DevOps\Lab Mid`
If your folder is different, change only the `cd` command.

---

## Step 1 — Install Python

1. Open <https://www.python.org/downloads/windows/> and download **Python 3.12** (64-bit installer).
2. Run the installer.
3. **Important:** on the first screen tick **“Add python.exe to PATH”**, then click *Install Now*.
4. Open a new PowerShell window and check:

```powershell
python --version
```

You should see `Python 3.12.x`. If you see an error, restart the computer and try again.

> Why 3.12? The project uses only standard library features plus Flask, so any Python 3.10+ works.

---

## Step 2 — Install Git

1. Download Git for Windows from <https://git-scm.com/download/win>.
2. Run the installer and keep all default options (just click *Next* / *Install*).
3. Check it:

```powershell
git --version
```

You should see something like `git version 2.4x.x.windows.1`.

4. Tell Git who you are (used in commit history):

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

---

## Step 3 — Install VS Code

1. Download Visual Studio Code from <https://code.visualstudio.com/>.
2. Install it with the default options. Leave **“Add to PATH”** ticked.
3. Open VS Code once so it finishes setting up.

---

## Step 4 — Install GitHub Copilot (optional, recommended)

1. In VS Code, open the Extensions panel (`CTRL+SHIFT+X`).
2. Search for **GitHub Copilot** and click *Install*.
3. Sign in with your GitHub account and make sure your Copilot access is active.
4. This is how you can continue asking an AI assistant to explain or extend the project.

---

## Step 5 — Open the project folder

1. Open VS Code.
2. **File → Open Folder…**
3. Choose `D:\Uni\Semester 08\DevOps\Lab Mid`.
4. Open the built-in terminal: **Terminal → New Terminal** (`CTRL+~`).
   It starts in the project folder.

Check that you see these files: `run.py`, `requirements.txt`, `app`, `tests`, `receiver`,
`scripts`, `docs`, `.github`.

If you downloaded the project as a ZIP instead, extract it first, then open the extracted folder.

---

## Step 6 — Install dependencies

In the VS Code terminal:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell refuses to run `Activate.ps1`, run this once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Confirm the packages:

```powershell
python -c "import flask, pytest; print(flask.__version__, pytest.__version__)"
```

Expected: `3.0.3 8.3.3`.

---

## Step 7 — Run the Flask application

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python run.py
```

Open <http://127.0.0.1:5000>.

Try three submissions:

1. **Valid:** name `Ayesha Khan`, registration `FA22-BCS-123`, title `DevOps Lab Mid`,
   URL `https://github.com/ayesha/devops-lab-mid` → green message, row appears.
2. **Missing registration number:** leave it empty → red message
   “Registration number is required.”, nothing added.
3. **Invalid URL:** type `not-a-url` → red message about a valid http(s) link.

Press `CTRL+C` in the terminal to stop the server.

---

## Step 8 — Run the tests

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

Expected result: **7 passed**.

Then run the reporting version (it writes `test-report.json`):

```powershell
python scripts/run_tests.py
```

The report is written even if a test fails. Delivery to the receiver is tested in step 12.

---

## Step 9 — Create the GitHub repository

1. Open <https://github.com/new>.
2. **Repository name:** `devops-lab-mid` (or any name you like).
3. **Visibility:** Public (easiest for the instructor to check) or Private.
4. **Do not** tick “Add a README”, “Add .gitignore” or “Choose a license” — the project already has
   these files, and extra ones cause a merge conflict on the first push.
5. Click **Create repository**. Keep the page open; you need the URL.

If this is your first push, also install the GitHub CLI (easiest way to log in):

```powershell
winget install --id GitHub.cli
```

Close and reopen the terminal, then:

```powershell
gh auth login
```

Choose **GitHub.com → HTTPS → Login with a web browser** and follow the browser prompt.

---

## Step 10 — Push the code

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
git init
git branch -M main
git add .
git commit -m "feat: assignment submission portal with CI pipeline"
git remote add origin https://github.com/<your-username>/devops-lab-mid.git
git push -u origin main
```

Replace `<your-username>` and the repository name with yours.

Reload the GitHub page: your files should appear. Check that `.venv/`, `instance/` and
`test-report.json` are **not** there — that is the `.gitignore` doing its job.

> If `git push` asks for a password, GitHub wants a **Personal Access Token**
> (GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) →
> Generate new token with the `repo` scope). Paste the token as the password. With `gh auth login`
> you do not need this.

---

## Step 11 — Create the Windows self-hosted runner

1. On GitHub open your repository → **Settings → Actions → Runners → New self-hosted runner**.
2. Choose **Windows** and **x64**. GitHub shows the exact commands including the download version
   and your registration token — use those.
3. In PowerShell (the runner goes **outside** the project, for example `C:\actions-runner`):

```powershell
cd C:\
New-Item -ItemType Directory -Path C:\actions-runner -Force
cd C:\actions-runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-win-x64-2.319.1.zip -OutFile actions-runner-win-x64.zip
Expand-Archive -Path actions-runner-win-x64.zip -DestinationPath C:\actions-runner -Force
```

4. Configure the runner (paste the token GitHub shows you — a token is valid for about one hour;
   if it expires, click *New self-hosted runner* again to get a fresh one):

```powershell
cd C:\actions-runner
.\config.cmd --url https://github.com/<your-username>/devops-lab-mid --token <TOKEN_FROM_GITHUB>
```

Answer the questions by pressing **Enter** for every default (runner group, name, work folder
`_work`, labels). Do not add extra labels.

5. **Do not start the runner yet** — first start the receiver (step 12), then the runner (step 13).

**Security:** the runner folder contains credentials. Never copy it into the repository and never
share the token. `.gitignore` already excludes `actions-runner/`, `_work/`, `_diag/` and `.runner`.

---

## Step 12 — Start the local receiver

The receiver is a tiny Flask app that listens on `127.0.0.1:5001` and saves every report it receives
as `test-report.json` in the project root. **Keep this window open during the whole demonstration.**

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python receiver/server.py
```

Leave it running. In a **second** PowerShell window check it:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5001/health
```

Expected output: `status ok` with `report_path`.

Now prove delivery works before using CI:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python scripts/run_tests.py --require-receiver
```

The receiver window prints a `PASSED` line and `test-report.json` appears in the project root.

> The workflow also tries to start the receiver automatically if it is not running, but keeping it
> open in its own window is easier to demonstrate. Note that an automatically started receiver
> lives inside the runner’s checkout folder (`_work\<repo>\<repo>`), so the copy of
> `test-report.json` in **your** project root only appears when the receiver in this step is the one
> that receives the report.

---

## Step 13 — Start the runner

In a third PowerShell window:

```powershell
cd C:\actions-runner
.\run.cmd
```

Wait for `Listening for Jobs`. On GitHub, **Settings → Actions → Runners** now shows the runner as
**Idle**.

> Optional: to keep the runner running after you close the window:
> `.\svc.cmd install` then `.\svc.cmd start`.

---

## Step 14 — Configure GitHub Pages

1. Repository → **Settings → Pages**.
2. **Build and deployment → Source:** choose **GitHub Actions** (not “Deploy from a branch”).
3. Do not create a `gh-pages` branch — the workflow publishes directly.
4. After the first successful run on `main`, the site URL is displayed here:
   `https://<your-username>.github.io/<your-repo>/`

---

## Step 15 — Add all six email secrets

Repository → **Settings → Secrets and variables → Actions → New repository secret**.
Add each one (name must match exactly):

| Name | Value |
|---|---|
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` (or `465` for SSL) |
| `MAIL_USERNAME` | your full email address |
| `MAIL_PASSWORD` | a Gmail **App Password** (not your normal password) |
| `MAIL_FROM` | the sender address, usually the same as `MAIL_USERNAME` |
| `MAIL_TO` | where reports go; several addresses separated by commas |

How to get a Gmail App Password:

1. Google Account → **Security** → turn on **2-Step Verification**.
2. Security → **App passwords** → app: *Mail*, device: *Windows Computer* → **Generate**.
3. Copy the 16-character value into `MAIL_PASSWORD`.

If your provider is not Gmail, use its SMTP settings; `465` means implicit SSL, `587` means STARTTLS.

**Never** type these values into the README, into chat, into code or into a screenshot.

---

## Step 16 — Run a successful workflow

Both windows must be open: the receiver (step 12) and the runner (step 13).

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
git add .
git commit -m "chore: trigger first CI run" --allow-empty
git push origin main
```

On GitHub open **Actions → CI - Test, Email Report, Deploy** and click the newest run.

Expected:

| Job | Result |
|---|---|
| Run pytest and deliver JSON report | ✅ success, 7 tests |
| Email the test report | ✅ success |
| Deploy static demo to GitHub Pages | ✅ success |

In the receiver window you should see `PASSED | 7/7 passed`.
Download the artifact `test-report` from the run summary if you want extra evidence.

---

## Step 17 — Run a deliberately failing workflow

The assignment requires proof that a defect makes the pipeline fail.

1. Open `app/validation.py`.
2. Inside `validate_submission`, make the registration number optional by skipping it in the
   required-field loop:

```python
    for field, label in FIELD_LABELS.items():
        if field == "registration_number":
            continue  # DELIBERATE DEFECT - will be reverted in step 18
        if not cleaned[field]:
            errors[field] = f"{label} is required."
```

3. Also delete (or comment out) the `if not errors.get("registration_number"):` block so an empty
   registration number is accepted.
4. Point out the failure locally first:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

`test_submission_without_registration_number_is_rejected` now **fails**.

5. Commit and push the defect:

```powershell
git add app/validation.py
git commit -m "test: deliberate validation defect for the demo"
git push origin main
```

Expected in the new run:

| Job | Result |
|---|---|
| Run pytest and deliver JSON report | ❌ failure |
| Show the generated report | runs (`if: always()`) |
| Upload test report artifact | runs (`if: always()`) |
| Email the test report | ✅ success, subject starts with `[FAILED]` |
| Deploy static demo to GitHub Pages | ⏭️ skipped — the old site stays online |

The receiver prints `FAILED | 6/7 passed`.

Screenshots to take now: the red job, the receiver console, the `[FAILED]` email, the skipped
deploy job.

---

## Step 18 — Fix the defect

The cleanest fix is a revert of the bad commit:

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
git revert --no-edit HEAD
git push origin main
```

Or edit `app/validation.py` back by hand:

```python
    for field, label in FIELD_LABELS.items():
        if not cleaned[field]:
            errors[field] = f"{label} is required."
```

plus the original minimum-length check for the registration number, then:

```powershell
python -m pytest -q
git add app/validation.py
git commit -m "fix: restore registration number validation"
git push origin main
```

Expected: a third run where all three jobs are green again, and the receiver prints
`PASSED | 7/7 passed`.

**Confirm the final code has no defect:**

```powershell
git log --oneline -3
python -m pytest -q
```

---

## Step 19 — Verify both JSON reports

After the failing run and the fixing run, open `test-report.json` in the project root.

```powershell
cd "D:\Uni\Semester 08\DevOps\Lab Mid"
Get-Content .\test-report.json
```

Check the values that matter:

| Field | Failing run | Fixing run |
|---|---|---|
| `overall_status` | `"failed"` | `"passed"` |
| `failed_tests` | `1` | `0` |
| `passed_tests` | `6` | `7` |
| `commit_sha` | SHA of the defect commit | SHA of the fix commit |
| `run_id` | the failing run’s ID | the fixing run’s ID |
| `tests[].failure_message` | present on the failing test | absent |

Useful one-liners:

```powershell
(Get-Content .\test-report.json -Raw | ConvertFrom-Json).overall_status
(Get-Content .\test-report.json -Raw | ConvertFrom-Json).commit_sha
```

Save both versions as evidence, for example:

```powershell
Copy-Item .\test-report.json .\evidence-failed-run.json
```

(the failed report must be copied while it is still the newest one — that is, right after step 17).

Check the GitHub run ID matches the workflow run page URL (`.../actions/runs/<run_id>`).

---

## Step 20 — Verify email delivery

1. Open your inbox.
2. You should have **two** emails from `MAIL_FROM`:
   - `[FAILED] Test report - <repo> (main)` — lists the failing test and its message,
   - `[PASSED] Test report - <repo> (main)` — lists all seven tests as passed.
3. Each email must contain repository, branch, commit SHA, run ID, overall status, totals and the
   per-test table.
4. Each email must have `test-report.json` attached.

If an email is missing, open the `email-report` job log on GitHub. The script prints the exact
missing secret **name** (never the value) or the SMTP error.

Test locally without sending (safe):

```powershell
python scripts/send_email_report.py --dry-run
```

---

## Step 21 — Verify the deployed website

1. Open `https://<your-username>.github.io/<your-repo>/`.
2. Check the page shows the portal form with the yellow “static demonstration” notice.
3. Press **Save submission** with empty fields → the browser shows validation messages.
4. Fill all four fields with a valid URL → the row is added to *Submissions added on this page*.
5. Reload the page → your demo row disappears (proof that it is static, not a database).
6. Go back to the failed run from step 17 and confirm the `deploy` job was skipped; the site stayed
   online the whole time.

Finally, fill in your details in `SUBMISSION_REPORT.md` and take the screenshots listed in its
evidence checklist.

---

## Quick daily workflow (after everything is set up)

```powershell
# window 1
cd "D:\Uni\Semester 08\DevOps\Lab Mid"; .\.venv\Scripts\Activate.ps1; python receiver/server.py

# window 2
cd C:\actions-runner; .\run.cmd

# window 3 - work on the code
cd "D:\Uni\Semester 08\DevOps\Lab Mid"; .\.venv\Scripts\Activate.ps1
python -m pytest -q
git add .; git commit -m "your message"; git push origin main
```
