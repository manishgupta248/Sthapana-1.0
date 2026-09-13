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
| 15 | Single-user access for now (role structure still built for future flexibility) | Owner is currently the only user; LAN/multi-user deployment deferred until actually needed |
| 16 | Registration page built as Option A: public form exists, but new accounts start inactive (`is_active=False`) until an Admin manually activates them via /admin/ | Matches admin-approved requirement for HR-sensitive data while still having a working, tested registration flow ready for when a second user is added |
| 17 | Python 3.13.3 used instead of the originally planned 3.12 | Owner's informed choice; Django's current LTS supports 3.13, avoiding an unnecessary second Python install |
| 18 | Login by username, not email | Owner's choice — simplest, matches Django's default behavior |

## Open questions (need owner's explicit decision)


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
