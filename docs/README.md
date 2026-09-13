# Sthapana — Establishment Branch Data & Reporting System

Project location: `D:\Sthapana\`

A locally-run system to manage Faculty & Staff data, office file records
(notices/circulars), tasks & reminders, and meeting notes/records for the
Establishment Branch of the University.

This is a **non-programmer-led, phase-by-phase build**. No phase starts
without explicit owner approval. See `AGENT.md` for the rules any AI
assistant (Claude) must follow while working on this project.

## Continuing across chat threads

This is a long, multi-session project. To avoid losing context when a new
chat thread is needed:

1. Create a **Claude Project** named "Sthapana" in claude.ai.
2. Upload all seven files below to its Project Knowledge.
3. Start all future Sthapana chat threads from inside that Claude Project.
4. After every phase completion, re-upload the updated `PROGRESS.md` and
   `CURRENT_STATUS.md` (and any other changed docs) to replace the old
   versions in Project Knowledge.

See `AGENT.md` → "Continuity across chat threads" for the full protocol.

## Start here (in order)

1. **AGENT.md** — Rules for how the AI assistant must work on this project.
   Read this first, every session.
2. **ARCHITECTURE.md** — The technical design: tech stack, folder layout,
   apps, and the phased system layers (deterministic core → Tools →
   Intent Router → LLM).
3. **TODO.md** — The master phase-by-phase roadmap with checkboxes.
4. **CURRENT_STATUS.md** — A one-page snapshot of exactly where the
   project stands right now. Always check this before resuming work.
5. **PROGRESS.md** — A running log of what was completed, phase by phase.
6. **DECISIONS.md** — Why we chose what we chose, and open questions
   awaiting your decision.
7. **GLOSSARY.md** — Plain-English explanations of technical terms used
   elsewhere in these docs.

## Project owner profile (for the AI assistant's benefit)

- Non-programmer. Needs plain English explanations of technical terms.
- Works on Windows, using PowerShell + VS Code.
- Wants one complete, approved phase at a time — never several phases mixed.
- Wants exact PowerShell commands and exact file paths, separated clearly.
- Wants a smoke test at the end of every phase before moving on.
