# AGENT.md — Rules for the AI Assistant on This Project

Read this in full before doing anything on this project, every session.
These rules apply whether this is the first message of a new chat or the
five-hundredth message of a long one.

## Who you are working with

The project owner is **non-technical**. They are capable and organized, but
they are not a programmer. Every technical term must be explained in plain
English the first time it's used in a session. Never assume familiarity with
programming jargon, even common terms like "migration," "endpoint," or
"virtual environment."

## Non-negotiable working rules

1. **Discuss before building.** For every phase or step: explain the
   objective, the realistic options, and the implications (time, risk,
   what it enables/blocks later) — and get explicit approval — before
   writing or generating any code for it.
2. **Plain English always.** No unexplained jargon. If a technical term is
   necessary, define it in one simple sentence the first time it appears.
3. **One complete phase/step at a time.** Do not blend in work from a
   future phase "while we're at it." If something belongs to a later
   phase, name it and defer it — don't build it early.
4. **Clearly separate deliverables** into exactly two kinds, labeled:
   - **(a) PowerShell commands** — for the owner to run themselves.
   - **(b) File code** — exact file path, then the full file content to
     create or paste.
   Never mix these into a single unlabeled block.
5. **Smoke test at the end of every step/phase.** Give one clear, simple
   test the owner can run themselves to confirm it worked, in plain
   language (what to click/type, what they should see).
6. **Git and documentation updates happen only at major step/phase
   completion** — not after every small change. Don't ask the owner to
   commit mid-step.
7. **Best practices, applied from day one, not bolted on later:**
   - `.gitignore` correct from the first commit — secrets must never
     reach git.
   - Settings split into `base.py` / `development.py` / `production.py`
     from day one (see ARCHITECTURE.md).
   - Minimum: each Django app gets at least a few automated tests before
     its phase is considered "done."
   - One git branch per phase; merge to main only after the owner's
     smoke test passes.
   - No phase mixes in concerns that belong to a later phase.
8. **Before starting any new phase**, briefly restate:
   - What this phase **will** include.
   - What this phase will **not** include (explicitly name what's being
     deferred).
   - Any implications of building it now vs. later.
   ...then wait for approval before giving commands/code.
9. **Deterministic first, AI second.** Every feature must work with plain
   rule-based logic before any LLM/AI layer is added on top of it. The AI
   layer, when it arrives, is a convenience on top of a working
   deterministic system — never a replacement for one.
10. **Security and privacy by default.** Faculty/Staff data is sensitive
    personal data. Role-based access control and an audit trail (who
    changed what, when) are treated as core requirements, not optional
    extras — see ARCHITECTURE.md's access-control section.

## Continuity across chat threads (long project, many sessions)

This project will span many separate chat threads over time. Chat threads
do not automatically see each other's history, so continuity depends
entirely on the `docs/` folder being accurate and being made available at
the start of each new thread. Treat this as load-bearing, not optional.

**Recommended setup (do this once):** Create a **Claude Project** (a
persistent workspace in claude.ai, separate from this software project)
named "Sthapana," and upload all seven files in `D:\Sthapana\docs\` to
its Project Knowledge. Every new chat thread started inside that Claude
Project will then automatically have access to these files without
re-uploading them each time. Exact upload limits and steps can change —
check claude.ai's own Projects help page if anything looks different from
this description.

**If a Claude Project isn't used, or a thread is started outside it:** at
minimum, attach/paste `CURRENT_STATUS.md` at the very start of the
thread, and ideally all seven docs. Do not rely on the AI's memory of
past conversations alone — always ground the session in the actual files.

**Keeping it accurate:**
- `docs/` lives inside the git repo (`D:\Sthapana\docs\`), so it's
  version-controlled along with the code.
- Every time `PROGRESS.md` and `CURRENT_STATUS.md` are updated (i.e., at
  phase completion, per rule 6), the owner should also re-upload the
  updated files to the Claude Project's Knowledge, replacing the old
  versions — otherwise a new thread will start from stale information.
- The assistant should explicitly remind the owner to do this refresh at
  the end of any phase-completion step.

## Session startup checklist (do this at the start of every session)

1. Open and read `CURRENT_STATUS.md` — this tells you exactly what phase
   is active, what branch is checked out, and what the last confirmed
   smoke test result was.
2. Check `DECISIONS.md` for any open questions that need the owner's
   input before proceeding.
3. Do not assume anything was completed unless `PROGRESS.md` or
   `CURRENT_STATUS.md` says so explicitly.

## What "done" means for a phase

A phase is only marked done in `TODO.md` and `PROGRESS.md` when **all** of
the following are true:
- The owner has explicitly approved the phase's plan before it was built.
- The code/files described in the phase exist and match what was discussed.
- Minimal automated tests exist and pass.
- The owner has personally run the smoke test and confirmed success.
- `.gitignore`/secrets hygiene has been checked.
- Git branch for the phase has been merged to main.
- `PROGRESS.md` and `CURRENT_STATUS.md` have been updated.
