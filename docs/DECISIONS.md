# DECISIONS.md — Decisions Made & Open Questions

## Decisions already made (in initial planning)

| # | Decision | Why |
|---|---|---|
| 1 | Custom user model built in Phase 0, before first migration | Django makes this extremely hard to add later |
| 2 | SQLite first, PostgreSQL only if justified later | Avoids unnecessary setup complexity for a single-office system |
| 3 | Django Templates + local Bootstrap + Alpine.js for frontend (not a separate JS framework) | No build step, works offline, matches non-programmer maintenance |
| 4 | Django's built-in test runner (not pytest) | One less tool to learn |
| 5 | Deterministic logic before any AI/LLM layer, always | Reliability and explainability for office records |
| 6 | Notices/Circulars modeled as an Inward/Outward Register, not generic file uploads | Matches real Establishment Branch office workflow |
| 7 | Role-based access control (Admin/EstablishmentOfficer/Clerk/ReadOnly) built starting Phase 1 | Staff data is sensitive; costly to retrofit |
| 8 | Telegram bot restricted to whitelisted chat IDs mapped to system users, deterministic commands only at first | Security for sensitive data; matches deterministic-first philosophy |
| 9 | Apps grouped under `apps/` folder, all templates share a root `templates/base.html` | Keeps structure clean and consistent as apps grow |
| 10 | Faculty/Staff data modeled as Core + Extension tables | Lets new fields be added later with minimal risk to existing screens/reports |
| 11 | Faculty/Staff data entry supported via both Web form and Excel import from Phase 1, sharing one validation path | Owner needs both channels from the start; shared logic keeps data quality consistent |
| 12 | Interactive Login/Logout/Registration pages and a dashboard shell are built in Phase 0 (foundation), not deferred | Owner wants early, visible progress and a real (non-admin-panel) look and feel from the start |
| 13 | Backup system infrastructure built in Phase 0; actively exercised/validated starting Phase 1 | Protects data from the first real record entered, without waiting for a later phase |
| 14 | Project folder/repo name: **Sthapana**, located at `D:\Sthapana\` | Owner's choice — Sanskrit for "establishment/founding," short and fitting |

## Open questions (need owner's explicit decision)

### OQ-1: Single-user or multi-user access?
Will only you use this system, or will other Establishment Branch staff
need their own logins (e.g., accessing it over the office LAN)?
- **If single-user:** Phase 0/1 can be simpler — one admin account is
  enough for now, though we'd still build the role structure for future
  flexibility.
- **If multi-user:** Login, roles, and permissions become load-bearing
  from day one, and we should discuss whether the PC hosting this will be
  reliably reachable by others on the office network.
- **Status:** Not yet decided. Blocks finalizing Phase 0 details.

### OQ-5: Open self-registration vs admin-created/approved accounts?
The Registration page could let anyone create an account (open
self-signup), or require an Admin to create the account / approve a
request first.
- **Recommendation:** admin-created or admin-approved, since this system
  holds staff HR data and open signup would let anyone on the network
  create a login.
- **Status:** Not yet confirmed — decide at Phase 0 kickoff.

### OQ-2: Where does the Telegram bot's authorized user list come from?
Should Telegram chat-ID-to-user mapping be manually configured by you, or
should there be a simple in-app screen for it?
- **Status:** Not urgent — decide at Phase 7 planning.

### OQ-3: Data retention/archival policy
Should old notices/tasks/meetings (e.g., 5+ years old) be archived,
hidden, or kept fully visible indefinitely?
- **Status:** Not urgent — decide at Phase 5 planning, once real data
  volume is visible.

---
*Add new open questions here as they arise. Move resolved ones to the
"Decisions already made" table with the date and outcome.*
