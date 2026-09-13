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
