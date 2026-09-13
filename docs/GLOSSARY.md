# GLOSSARY.md — Plain English Explanations

| Term | Plain-English meaning |
|---|---|
| Repository (repo) | The project folder, tracked by Git so every change is recorded and reversible |
| Git branch | A separate, safe copy of the project to work in without disturbing the main working version |
| Commit | A saved checkpoint of changes, with a note describing what changed |
| Migration | A Django-generated instruction file that changes the database structure (e.g., adds a new field) |
| Virtual environment (venv) | An isolated folder holding just this project's Python packages, so it doesn't interfere with anything else on your PC |
| `.env` file | A plain text file holding secret settings (passwords, keys) that is never uploaded to Git |
| Django admin | A ready-made web page Django generates automatically for managing your data, before we build custom pages |
| Model | A Python description of a "thing" your database stores (e.g., a Staff record) and its fields |
| App (Django app) | A self-contained folder of related features (e.g., everything about Tasks lives in one app) |
| Endpoint / API | A specific web address that a program (like the Telegram bot) can call to get or send data, instead of a human clicking a webpage |
| REST API | A standard, predictable way of building those addresses so any program (bot, phone app, etc.) can use them the same way |
| Serializer (DRF) | A translator that converts a database record into a format (JSON) other programs can read, and back again |
| Token authentication | A secret code a program presents instead of a username/password to prove it's allowed to use the API |
| Rotating log | A log file that automatically archives/deletes old entries so it doesn't grow forever and fill your disk |
| Custom exception | A project-specific "error type" we define, so error messages are clear and consistent instead of raw technical crash messages |
| Role-based access control (RBAC) | Giving different people different permissions (e.g., a Clerk can't see salary data, but an Admin can) |
| Audit trail | An automatic record of who changed what data, and when — for accountability |
| Fuzzy matching | Software that can recognize a command even if it's typed slightly wrong (e.g., "remnid me" ≈ "remind me") |
| Intent Router | A layer that figures out *what you meant* from a typed or spoken command, before deciding what action to take |
| LLM (Large Language Model) | The kind of AI (like Claude) that understands and generates natural human language |
| Deterministic | Behavior that always produces the same, predictable result for the same input — the opposite of "AI guesses" |
| Smoke test | A quick, simple check to confirm something basically works, before doing deeper testing |
