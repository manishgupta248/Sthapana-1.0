# ARCHITECTURE.md — Technical Design

This document describes *how* the system is built. It will be updated as
decisions are confirmed. Anything marked **(Open Decision)** is not yet
finalized — see `DECISIONS.md`.

## 1. Guiding principle: Deterministic first, AI later

The system is built in layers. Each layer only gets added once the layer
below it is solid and tested:

```
Layer 5:  AI / LLM Layer                (fallback interpreter, last resort)
Layer 4:  Intent Router (rules + fuzzy) (understands human-like commands)
Layer 3:  Tools Layer                   (Filesystem, Excel, Word, PDF, Google)
Layer 2:  Telegram Bot (deterministic commands only, e.g. /addtask)
Layer 1:  REST API (Django REST Framework)
Layer 0:  Core Django Apps + Database   <-- THE FOUNDATION, built first
```

Every layer above Layer 0 is optional convenience. The system must be
fully usable through the plain website (Layer 0) alone. No feature is ever
*only* reachable through the AI layer.

## 2. Technology stack

| Concern | Choice | Plain-English reason |
|---|---|---|
| Language | Python 3.12 | Widely supported, matches Django's recommended version |
| Web framework | Django (latest LTS) | Batteries-included, good admin panel, mature |
| API framework | Django REST Framework (DRF) | Standard choice for exposing data to bots/Tools/Telegram |
| Database (now) | SQLite | Zero setup, file-based, fine for one office's data volumes |
| Database (later, if needed) | PostgreSQL | Only if multiple people write data simultaneously at volume |
| Frontend (initial) | Django Templates + Bootstrap (local copy, no CDN) + Alpine.js | No separate frontend build step; works offline |
| Version control | Git (local + optional private remote) | Tracks every change, allows safe rollback per phase |
| Editor | VS Code | Owner's chosen tool |
| Shell | PowerShell (Windows) | Owner's OS |
| Secrets | `.env` file + `django-environ` | Keeps passwords/keys out of code and out of git |
| Testing | Django's built-in `unittest`-based test runner (`manage.py test`) | No extra tool to learn; ships with Django |
| Task/reminder scheduling (later) | Django management command + Windows Task Scheduler, upgrading to Celery+Redis only if truly needed | Avoids installing a message broker before it's justified |

## 3. Project folder layout

```
Sthapana/                              <- git repo root, located at D:\Sthapana\
│
├── .env                               <- secrets (NEVER committed)
├── .env.example                       <- template of required vars (committed)
├── .gitignore
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── config/                            <- the Django "project" (settings live here)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                              <- all our custom Django apps live here
│   ├── accounts/                      <- custom user model, roles, permissions
│   ├── people/                        <- Faculty & Staff data (Phase 1)
│   ├── records/                       <- Notices/Circulars, Inward-Outward register (Phase 2)
│   ├── tasks/                         <- Tasks & Reminders (Phase 3)
│   ├── meetings/                      <- Meeting notes & records (Phase 4)
│   ├── reporting/                     <- Cross-app dashboards/exports (Phase 5)
│   ├── api/                           <- DRF serializers/viewsets tying apps together (Phase 6)
│   ├── telegram_bot/                  <- Telegram integration (Phase 7)
│   ├── tools/                         <- Filesystem/Excel/Word/PDF/Google tool wrappers (Phase 9)
│   ├── intent_router/                 <- Rule-based + fuzzy command understanding (Phase 11)
│   └── ai_layer/                      <- LLM integration (Phase 12)
│
├── templates/                         <- ALL templates, shared layout at root
│   ├── base.html                      <- common layout every page extends
│   └── includes/                      <- shared partials (navbar, footer, etc.)
│
├── static/                            <- root-level static files (CSS/JS/local Bootstrap+Alpine)
├── media/                             <- uploaded files (notices, scanned circulars, etc.)
│
├── backups/                           <- database backup snapshots (git-ignored)
├── logs/                              <- rotating log files (git-ignored)
│
└── docs/                              <- this documentation set
    ├── AGENT.md
    ├── ARCHITECTURE.md
    ├── TODO.md
    ├── PROGRESS.md
    ├── CURRENT_STATUS.md
    ├── DECISIONS.md
    └── GLOSSARY.md
```

**Why apps live under `apps/`:** keeps the project root uncluttered and
makes it obvious at a glance which folders are "our code" vs. Django/config
plumbing.

## 4. Core foundation decisions (Phase 0, built once)

- **Custom user model** (`apps/accounts`) — created *before* the first
  migration ever runs. Django makes this very hard to retrofit later, so
  it must be the very first app.
- **Role-based access control** — built on top of Django's Groups/
  Permissions from Phase 1 onward. Planned roles: `Admin`,
  `EstablishmentOfficer`, `Clerk`, `ReadOnly`. Field-level restriction
  (e.g., salary visible only to Admin) is added once the `people` app
  exists.
- **Audit trail** — every change to Faculty/Staff records and office file
  records logs who changed what and when. (Likely via `django-simple-
  history` or an equivalent lightweight approach — confirmed in Phase 1
  planning.)
- **Custom exception handling** — a small `apps/core` (or similar) module
  defines project-specific exceptions and a consistent error page/response
  shape, so errors are predictable instead of raw Django tracebacks.
- **Logging with rotation** — Python's `RotatingFileHandler` writes to
  `logs/`, so log files don't grow forever.
- **Environment variables** — all secrets (`SECRET_KEY`, DB path overrides,
  API keys added later) come from `.env`, never hard-coded.
- **Settings split** — `base.py` (shared), `development.py` (local, DEBUG
  on), `production.py` (hardened, DEBUG off) — chosen even though
  "production" here just means "the everyday-use version on your PC," to
  build the right habit from day one.
- **Interactive auth system, built in the foundation, not deferred** —
  custom-styled (not bare Django-admin) Login, Logout, and Registration
  pages, using the custom user model. **(Open Decision)**: should
  "Registration" be open self-signup, or admin-created/admin-approved
  accounts? For a system holding staff HR data, admin-created or
  admin-approved is the safer default — see DECISIONS.md.
- **Dashboard shell, built in the foundation** — an empty dashboard
  template (with the common layout, navigation, and placeholder summary
  cards) is created in Phase 0 so that Phase 1 only has to plug real
  Faculty/Staff numbers into an already-working page, rather than
  building the page itself from scratch.

## 5. Database & backup strategy

- Start on **SQLite** — a single file, no server needed, perfectly fine
  for one office's data.
- **Backup system** (the infrastructure is built in **Phase 0**, as part
  of the foundation, so it's protecting data from the very first record
  entered in Phase 1 — not bolted on after data already exists):
  - A scheduled copy of the SQLite file into `backups/`, named with a
    timestamp (e.g. `db_2026-09-12_1800.sqlite3`).
  - Automatic pruning of backups older than a set number of days.
  - A documented, **owner-tested** restore procedure — a backup that's
    never been restored from isn't a real backup.
- **Migration to PostgreSQL** is deferred until there's an actual need:
  multiple people writing data at the same time, or data volume that
  SQLite struggles with. This is a Phase 13+ decision, revisited later,
  not assumed now.

## 6. Office-domain modeling notes

- **Faculty & Staff (`apps/people`)** — designed for growth without
  breaking existing screens/reports, using a **Core + Extension**
  pattern:
  - **Core model**: the small set of fields nearly every screen needs and
    that are unlikely to ever disappear (name, employee ID, department,
    designation, status). Kept deliberately minimal and stable.
  - **Extension models**: linked one-to-one with Core, grouped by theme
    (e.g. `ContactDetails`, `EmploymentDetails`, `QualificationDetails`).
    When a new field is needed later, it usually goes into an existing
    extension table (a simple, low-risk migration) or into a brand-new
    extension table (zero risk to existing tables/screens) — Core rarely
    needs to change.
  - Exact field grouping is finalized together at Phase 1 kickoff, not
    guessed now.
  - Sensitive fields (salary, personal ID numbers, home address) are
    restricted by role regardless of which table they live in.
  - **Data entry from two channels, both from Phase 1 onward**: a web
    form, and an Excel (.xlsx) importer. Both funnel through the *same*
    shared "save a Person record" logic, so validation rules (required
    fields, duplicate employee IDs, etc.) are enforced identically no
    matter which channel was used — the Excel importer is not a separate,
    looser path into the database.
- **Records (`apps/records`)**: modeled on a real office **Inward/Outward
  Register** — every notice/circular gets a diary number, direction
  (inward/outward), date, subject, linked file(s), and status — not just
  a generic file upload. This matches how Establishment Branches actually
  track paperwork and makes the system immediately familiar to staff.
- **Tasks (`apps/tasks`)**: assignable, due-dated, status-tracked; can
  optionally link to a Record or a Meeting action item.
- **Meetings (`apps/meetings`)**: meeting record with linked attendees
  (from `people`) and action items (which can become `tasks`).

## 7. Access model **(Open Decision — see DECISIONS.md)**

Two possible modes:
- **Single-user mode**: only the owner uses the system on their own PC.
- **Multi-user mode**: other Establishment Branch staff access it too
  (e.g., over the office LAN), requiring individual logins and role
  enforcement from the start.

**Working assumption until confirmed:** build with role-based login from
Phase 1 regardless, since it costs little now and is expensive to retrofit
— but the *deployment* question (LAN-accessible or single PC only) is
deferred to a dedicated decision before Phase 1 begins.

## 8. Later layers (kept deliberately vague until their phase arrives)

- **Telegram bot**: deterministic slash-commands only at first (e.g.
  `/addtask`, `/todaysnotices`), restricted to a whitelist of authorized
  Telegram chat IDs mapped to system users.
- **Tools layer**: thin wrapper apps that let both the website and the bot
  generate/read Excel, Word, PDF files, and interact with Gmail/Drive/
  Calendar/Sheets via Google's official APIs (OAuth2).
- **Intent Router**: rule-based command matching first, fuzzy text
  matching (e.g. `rapidfuzz`) second, so "add task remind me tmrw" is
  understood without needing an LLM.
- **AI/LLM layer**: only called when the Intent Router genuinely can't
  resolve a request. Never the first thing consulted.

## 9. Testing approach

Each app ships with at least a few automated tests (using Django's
built-in test runner) covering its core behavior before its phase is
marked done — e.g., "a Staff record can be created and retrieved,"
"a Clerk cannot see salary field," "a backup file is created and is a
valid SQLite file."
