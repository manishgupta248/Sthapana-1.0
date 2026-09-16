# PROGRESS.md — Completed Work Log

Updated only at major step/phase completion (see AGENT.md rule 6). Newest
entries at the top.

---

## Log format (copy this block for each new entry)

```
### Phase X — <name> — COMPLETED <date>
- Branch: phase-X-<name>, merged to main on <date>
- What was built: <short summary>
- Smoke test performed: <what the owner did> — Result: PASS
- Automated tests: <n> tests, all passing
- Git tag: v0.X
- Notes/deviations from original plan: <if any>
```

---

*### Phase 0 — Foundation & Environment — COMPLETED 2026-09-13
- Branch: main (deviation — no phase branch was created for Phase 0;
  branch-per-phase starts properly with Phase 1)
- What was built: Git repo + .gitignore, Python virtual environment,
  Django project skeleton with settings split (base/development/
  production), django-environ + .env secrets handling, custom User
  model (apps/accounts, username-based login) created before first
  migration, four role groups (Admin/EstablishmentOfficer/Clerk/
  ReadOnly), custom-styled Login/Registration pages with admin-approval
  gating (new accounts start inactive), Logout, root templates/base.html
  + navbar + modern color theme (CSS custom properties, native system
  font stack, no external font downloads), dashboard shell with 4
  placeholder summary cards, local Bootstrap 5.3.3 + Alpine.js (no CDN),
  rotating file logging (5MB/5 backups), custom exception scaffold
  (apps/core/exceptions.py), custom 500 error page, PowerShell backup
  script with 30-day pruning.
- Smoke test performed: Full end-to-end walkthrough in a private browser
  window — unauthenticated redirect to login, login with modern styling,
  dashboard display, logout, registration creating an inactive account,
  login blocked pre-activation, admin activation via /admin/, login
  succeeding post-activation. — Result: PASS
- Automated tests: 6 tests (apps/accounts), all passing
- Git tag: v0.0
- Notes/deviations from original plan:
  - Python 3.13.3 used instead of the planned 3.12 (owner's informed
    choice — Django's current LTS supports 3.13; documented as a
    deliberate deviation, not an oversight).
  - Login method: username (Django default), not email — owner's choice.
  - Registration: Option A implemented — public form exists, but new
    accounts are created with is_active=False and require manual
    activation by an Admin via /admin/.
  - Phase 0 was built directly on the `main` branch rather than a
    dedicated phase branch, deviating from AGENT.md's branch-per-phase
    rule. No functional impact; corrected starting Phase 1.

### Phase 1 — Step 1.1: Employee Foundation — COMPLETED 2026-09-14
- Branch: phase-1-step-1-1-employee-foundation, merged to main on 2026-09-14
- What was built: Department and Designation lookup lists; Core Employee
  model (Employee ID, Full Name, Department, Designation, Status, Date
  Joined, Employment Type); full change history via django-simple-history;
  role-based permissions (Admin/EstablishmentOfficer/Clerk/ReadOnly)
  enforced via a data migration; custom-styled web CRUD pages (list, add,
  edit, view — delete restricted to Admin and itself logged in history);
  Django admin registration for all three models; Excel (.xlsx) importer
  for Core fields sharing the same validation as the web form, with
  per-row error reporting; dashboard "Faculty & Staff" card now shows the
  real employee count.
- Smoke test performed: Owner created Departments/Designations via admin,
  added an employee via the web form, confirmed duplicate Employee ID is
  rejected, ran a small Excel import, confirmed a Clerk-role test user
  cannot see the Delete button, confirmed dashboard count updates live.
  — Result: PASS
- Automated tests: 4 tests (apps/people), all passing
- Git tag: none (tags are reserved for full phase completion, not
  individual sub-steps — see Phase 0's v0.0 for comparison)
- Notes/deviations from original plan: none

### Phase 1 — Step 1.2: Contact Details — COMPLETED 2026-09-14
- Branch: phase-1-step-1-2-contact-details, merged to main on 2026-09-14
- What was built: ContactDetails table (one-to-one with Employee) covering
  mobile numbers, personal/official email, current & permanent address,
  and emergency contact details; "same as current address" convenience
  checkbox on the web form; web form linked from the Employee detail page
  (Add/Edit/Delete, delete restricted to Admin); Django admin
  registration with change history; Excel importer matching by Employee
  ID, updating an existing record rather than duplicating it.
- Smoke test performed: Owner added contact details via the web form,
  confirmed the address checkbox worked, edited an existing record,
  ran an Excel import twice on the same employee to confirm update-not-
  duplicate behaviour, confirmed an unknown Employee ID was reported as
  skipped, confirmed a Clerk-role test user could add/edit but not
  delete. — Result: PASS
- Automated tests: 2 new tests (apps/people), all passing (6 total)
- Git tag: none (tags reserved for full phase completion)
- Notes/deviations from original plan: none

### Enhancement — Sidebar, Footer & Logo — COMPLETED 2026-09-14
- Branch: feature-lookup-excel-import, merged to main on 2026-09-14
- What was built: Site-wide layout update via base.html — a left-hand
  sidebar (always visible) with links to Dashboard, Employees, Add
  Employee, Import Employees, and Django Admin Panel (Admin/staff-only);
  a footer with the Sthapana logo and copyright line; the logo also
  added next to "Sthapana" in the top navbar. New static/css/sidebar.css
  for layout styling. Fixed a pre-existing duplicate Bootstrap CSS
  <link> in base.html found while making this change.
- Smoke test performed: Owner checked login page, dashboard, employee
  list, employee add/edit form, and employee detail page all display
  correctly with the new layout; confirmed Clerk-role test user does not
  see the Django Admin Panel link; confirmed narrow-screen view stacks
  the sidebar instead of squeezing the page; confirmed logo displays
  correctly in both navbar and footer. — Result: PASS
- Automated tests: no new tests (template/styling-only change; no logic
  added)
- Git tag: none
- Notes/deviations from original plan: none — this was an owner-
  requested cosmetic enhancement, not part of the original phase roadmap.

### Enhancement — Admin Excel Import for Department & Designation — COMPLETED 2026-09-14
- Branch: feature-lookup-excel-import, merged to main on 2026-09-14
- What was built: An "Import from Excel" button added to the Department
  and Designation pages inside the Django admin panel. Uses the existing
  openpyxl library (no new dependency). Excel format: a "Name" column
  plus an optional "Is Active" (Yes/No) column. Names that already exist
  (case-insensitive) are skipped and reported rather than duplicated.
  Shared logic (ExcelImportAdminMixin) reused between both admin pages
  since the two tables share the same shape.
- Smoke test performed: Owner uploaded a test file to both the
  Department and Designation admin import pages, confirmed new entries
  were created, confirmed re-uploading the same file skipped existing
  entries instead of duplicating them. — Result: PASS
- Automated tests: 1 new test (apps/people), all passing (7 total)
- Git tag: none
- Notes/deviations from original plan: none — this was an owner-
  requested enhancement, not part of the original phase roadmap.
### Enhancement — Employee Core Fields, Contact Import Discoverability, List Filters & Excel Export — COMPLETED 2026-09-16
- Branch: feature-employee-fields-filters-export, merged to main on 2026-09-16
- What was built (Part A — Core field changes): Added "Initial"
  (Title/Salutation: Shri/Smt./Kum./Dr./Mr./Mrs./Ms./Other, optional) and
  "Employee Category" (Teaching/Workshop/Administrative/Other, required)
  as new fields on Employee, separate from the existing Employment Type
  field. Date Joined changed from required to optional. "Full Name"
  field relabeled to "Name" on all forms/pages (internal field name
  unchanged to limit risk). Excel importer, admin panel, and templates
  updated to match.
- What was built (Part B — Contact Details import discoverability): A
  "Download Sample Template" button added to the Contact Details import
  page (ready-to-fill .xlsx with correct headers and an example row).
  "Import Contact Details" links added to the sidebar and the Employee
  list page (previously built in Step 1.2 but not linked anywhere).
- What was built (Part C — filters): Department, Designation, Status,
  and Employment Type dropdown filters added to the Employee list page,
  usable together with the existing name/ID search box.
- What was built (Part D — sort & export): Clickable, sortable column
  headings on the Employee list page; row checkboxes with "select all";
  an "Export to Excel" button that exports selected rows if any are
  checked, otherwise everything currently shown after filters/search/
  sort are applied.
- Bug found & fixed during this work: a permission-assignment migration
  (from the Contact Details step) had been silently failing to grant
  Contact Details permissions to any group, because it ran before
  Django had created those permissions' database records. This stayed
  invisible because all earlier testing used a superuser account, which
  bypasses permission checks. Fixed with a corrective migration that
  creates the missing permission records first, then reassigns them
  correctly — this also fixed real (non-superuser) Admin-group access
  to Contact Details import, not just the new template download.
- Smoke test performed: Owner confirmed existing test employees display
  correctly with new blank Initial/default Employee Category; new
  fields editable and importable via Excel; Contact Details import
  buttons visible from sidebar and Employee list; sample template
  downloads and re-imports correctly; Department/Status/etc. filters
  work individually and combined; column sorting works both directions
  and persists alongside active filters; Export to Excel respects
  current filters when nothing is checked, and respects checked rows
  when some are selected. — Result: PASS
- Automated tests: 9 new tests (apps/people), all passing (15 total)
- Git tag: none
- Notes/deviations from original plan: none beyond the permission-
  migration bug above, which was found and fixed within this same step
  rather than deferred.

  ### Phase 3 — Tasks & Reminders — COMPLETED 2026-09-14
- Branch: phase-3-tasks-reminders, merged to main on 2026-09-14
- What was built: Task model (title, description, assignee, due date,
  status [Open/In Progress/Completed/Cancelled], priority [Low/Medium/
  High], related link, created-by); TaskAttachment model supporting
  multiple file uploads per task restricted to PDF/Word/Excel/image
  types; full web CRUD (list/add/edit/detail, delete restricted to
  Admin, add/edit open to all roles); Django admin with inline
  attachment editing; change history via django-simple-history; "My
  Tasks" in-app reminder view flagging overdue tasks; dashboard
  "Pending Tasks" card now shows a real count with an overdue badge;
  media file serving configured for local development.
- Smoke test performed: Owner added a task via admin (verified
  created-by fills in correctly), added a task via the web form with
  two attachments and a link, edited an existing task and confirmed
  the change saved and attachments remained intact, opened an
  attachment link and confirmed the file downloads, checked the
  dashboard showed the correct pending/overdue counts, confirmed a
  Clerk-role user could add/edit tasks but not see the Delete button.
  — Result: PASS
- Automated tests: 4 tests (apps/tasks), all passing
- Git tag: v0.3
- Notes/deviations from original plan: built out of the original phase
  order — Phase 1 Steps 1.3–1.9 and Phase 2 remain on hold at owner's
  request, Phase 3 was built ahead of them. Task-to-Record and
  Task-to-Meeting linking deferred since those apps don't exist yet.
  Two fields added beyond the original roadmap scope at owner's
  request: a related link field and multiple file attachments.

### Phase 7 — Telegram Bot Integration — COMPLETED 2026-09-16
- Branch: phase-7-telegram-bot, merged to main on 2026-09-16
- What was built: apps/telegram_bot — TelegramUser (chat-ID whitelist,
  admin-managed) and BotState (tracks last processed message) models;
  a thin requests-based TelegramClient wrapper (no bot framework
  dependency); a flat command registry (commands.py) with /start,
  /help, /newtask, /mytasks, /setstatus, /remind; long-polling loop
  (run_telegram_bot management command) with signal-based clean
  shutdown on Ctrl+C; scheduled daily reminders (send_task_reminders
  management command, run via Windows Task Scheduler) for overdue/
  due-today tasks, sharing logic with /remind via reminders.py; a
  staff-only web page (/telegram/send/) to push an ad-hoc message to
  all linked Telegram users. HTML entities in task titles are escaped
  before being sent, avoiding Telegram parse errors.
- Smoke test performed: Owner confirmed /start and /help with the
  whitelist enforced (unrecognised chats get no reply); Ctrl+C
  shutdown confirmed clean after fixing an initial Windows delayed-
  signal issue (poll timeout shortened from 30s to 5s + explicit
  signal handlers); /newtask creates a task with correct defaults and
  confirmation message; /mytasks lists correctly (after fixing an HTML
  parse error caused by literal <id>/<status> placeholder text in the
  usage message); /setstatus updates status and reflects on the
  website; /remind and the scheduled Task Scheduler job both deliver
  correct overdue/due-today summaries, tested with and without the bot
  polling loop running; the send-message web page is staff-only,
  delivers messages, and validates against empty submissions.
  — Result: PASS
- Automated tests: 12 new tests (apps/telegram_bot), all passing
- Git tag: v0.4
- Notes/deviations from original plan: built out of the original phase
  order (see Decision #33). Two bugs found and fixed during
  development, not deferred: (1) Ctrl+C appeared to hang due to
  Windows' delayed-signal behavior during a 30-second blocking network
  wait — fixed by shortening the poll interval and adding explicit
  SIGINT/SIGTERM handlers; (2) /mytasks crashed with a Telegram "can't
  parse entities" error because literal <id>/<status> placeholder text
  in a usage hint was misread as HTML — fixed by rewording placeholders
  and adding systematic HTML-escaping for any database-sourced text
  (task titles) inserted into bot messages.