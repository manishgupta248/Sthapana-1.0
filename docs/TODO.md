# TODO.md — Master Phase Roadmap

Rules: no phase starts without explicit approval (see AGENT.md). Check off
a phase only when PROGRESS.md and CURRENT_STATUS.md both confirm it's
done, including a passed owner smoke test.

## Phase 0 — Foundation & Environment
- [x] Git repo initialized, `.gitignore` in place
- [x] Python virtual environment set up on Windows/PowerShell
- [x] Django project skeleton (`config/`) created
- [x] Settings split: `base.py` / `development.py` / `production.py`
- [x] `.env` + `django-environ` wired up; `.env.example` committed
- [x] Custom user model app (`apps/accounts`) created *before first migration*
- [x] Logging with rotation configured
- [x] Custom exception-handling scaffold
- [ ] Root `templates/base.html` layout + `static/` + `media/` folders configured
- [x] Custom-styled Login / Logout / Registration pages (using custom user model)
- [x] Dashboard shell template (empty summary cards, ready for Phase 1 data)
- [x] Backup system infrastructure: scheduled SQLite copy script + pruning
      (exercised for real starting Phase 1, once data exists)
- [x] Minimal smoke-test app to confirm server runs, admin login works
- [x] Decision made: single-user access (see DECISIONS.md #15)
- [x] Decision made: admin-approved registration, Option A — accounts start inactive (see DECISIONS.md #16)

## Phase 1 — Faculty & Staff Data (`apps/people`) — first "early gain"

### Step 1.1 — Employee Foundation — COMPLETE
- [x] Department & Designation lookup lists
- [x] Core Employee model (Employee ID, Full Name, Department, Designation, Status, Date Joined, Employment Type)
- [x] Audit trail (django-simple-history) built in from the start
- [x] Role-based permissions (Admin / EstablishmentOfficer / Clerk / ReadOnly)
- [x] Full web CRUD (list/add/edit/view) — delete restricted to Admin, logged
- [x] Django admin registration
- [x] Excel (.xlsx) import for Core fields, sharing web-form validation
- [x] Dashboard populated with real Faculty/Staff count
- [x] Minimal automated tests (4 tests, passing)

### Step 1.2 — Contact Details — COMPLETE
- [x] ContactDetails extension table (one-to-one with Employee)
- [x] Web form (add/edit/delete), linked from Employee detail page
- [x] "Same as current address" convenience checkbox
- [x] Django admin registration
- [x] Excel import, matched by Employee ID
- [x] Minimal automated tests

### Steps 1.3–1.9 — ON HOLD (paused at owner's request, 2026-09-14)
Owner will implement Personal Information, Qualifications, Employment
Details, Salary History, Promotion History, Leave Records, and the
tabbed employee detail page independently. Resume only when the owner
explicitly reopens this part of the roadmap.

### Additional Enhancements (owner-requested, outside the numbered roadmap)
- [ ] Bulk Excel import for Department and Designation lookup lists,
      accessible from the Django admin panel

### Step 1.3 — Personal Information (not started)
- [ ] PAN, Aadhar, Date of Birth, Bank details — Admin-only, masked by default with logged reveals
- [ ] Minimal automated tests

### Step 1.4 — Qualifications (not started)
- [ ] Multiple qualification records per employee (degree, institution, year)
- [ ] Minimal automated tests

### Step 1.5 — Employment Details (not started)
- [ ] PF number, pension scheme, probation/confirmation dates
- [ ] Minimal automated tests

### Step 1.6 — Salary History (not started)
- [ ] Full pay history (effective date, basic pay, allowances, order reference)
- [ ] Minimal automated tests

### Step 1.7 — Promotion History (not started)
- [ ] Promotion events (old/new designation, date, order reference); updates Employee's current designation
- [ ] Minimal automated tests

### Step 1.8 — Leave Records (not started)
- [ ] Leave events (type, dates, status, remarks)
- [ ] Minimal automated tests

### Step 1.9 — Employee Detail Page & Phase 1 Close-out (not started)
- [ ] Tabbed employee detail page (Alpine.js) tying together all Step 1.2–1.8 tables
- [ ] Owner-tested backup restore drill, using real data
- [ ] Full Phase 1 documentation and git close-out

## Phase 2 — Office Records: Notices & Circulars (`apps/records`)
- [ ] Inward/Outward register model (diary number, direction, date, subject)
- [ ] File upload handling (media folder structure, file type validation)
- [ ] List/search/filter by date, subject, department
- [ ] Minimal automated tests

## Phase 3 — Tasks & Reminders (`apps/tasks`)
- [ ] Task model: assignee, due date, status, priority
- [ ] Optional linking to a Record or Meeting action item
- [ ] Simple reminder mechanism (in-app list first; email/Telegram later)
- [ ] Minimal automated tests

## Phase 4 — Meetings Notes & Records (`apps/meetings`)
- [ ] Meeting model: date, attendees (linked to `people`), minutes text
- [ ] Action items (convertible into `tasks`)
- [ ] Minimal automated tests

## Phase 5 — Reporting & Dashboard
- [ ] Homepage dashboard: counts/summary across apps
- [ ] Cross-app filters/reports
- [ ] Export to Excel/PDF (may pull forward part of the Tools layer early — decide when we get here)

## Phase 6 — REST API Layer (Django REST Framework)
- [ ] DRF installed and configured
- [ ] Serializers/viewsets for people, records, tasks, meetings
- [ ] API authentication (token-based)
- [ ] API tests

## Phase 7 — Telegram Bot (deterministic commands only)
- [ ] Bot registered, webhook or polling configured
- [ ] Whitelist of authorized Telegram chat IDs mapped to system users
- [ ] Deterministic slash-commands (e.g. `/addtask`, `/todaysnotices`)
- [ ] Bot calls the REST API — no direct DB access from the bot

## Phase 8 — Backup & Maintenance Hardening
- [ ] Review/upgrade backup automation based on real usage
- [ ] Log rotation review
- [ ] Admin housekeeping/cleanup tools

## Phase 9 — Tools Applications
- [ ] Filesystem tool wrapper
- [ ] Excel tool wrapper (read/write reports)
- [ ] Word tool wrapper (generate letters/notices from templates)
- [ ] PDF tool wrapper
- [ ] Google tools: Gmail, Drive, Calendar, Sheets (OAuth2 setup)

## Phase 10 — Intent Router Layer
- [ ] Rule-based command matching
- [ ] Fuzzy text matching for near-miss phrasing
- [ ] Router sits in front of Telegram bot and (optionally) a web command box

## Phase 11 — AI / LLM Layer
- [ ] LLM called only when Intent Router can't resolve a request
- [ ] Clear logging of when/why the LLM layer was invoked (for trust/debugging)

## Phase 12 — PostgreSQL Migration (only if justified by real need)
- [ ] Re-evaluate: is SQLite actually a bottleneck yet?
- [ ] If yes: migration plan, data migration, connection settings update

---
**Note:** Phase numbers are sequence, not fixed scope — a phase's exact
task list gets finalized (and possibly adjusted based on what we learn) in
the "discuss objectives/options/implications" conversation right before it
starts, per AGENT.md rule 1.
