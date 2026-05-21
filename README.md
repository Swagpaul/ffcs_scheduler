# FFCS Scheduler

A desktop application for VIT students to automatically generate clash-free timetables from their course and slot preferences — no more manually checking combinations.

---

## What it does

- Add your courses, professors, and slot combinations
- Set priorities for each option (which professor/slot combo you prefer most)
- Hit **Generate** — the app produces all valid, clash-free timetable options, ranked by your preferences
- If two courses have conflicting lab slots, the app generates **separate timetables** for each option instead of forcing a clash
- Download any timetable as an image

---

## How it works

**Backtracking Algorithm** — recursively tries every course-professor-slot combination. If a clash is detected, it backtracks and tries the next option.

**Smart Clash Handling** — when a clash is unavoidable (e.g. two lab courses share the same slot), separate timetables are generated — one with each course — so you can choose.

**Heuristic Scoring** — timetables are ranked by your professor priorities, schedule compactness, and gap minimization.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Desktop shell | Electron.js |
| Backend | Flask (Python) |
| Database | SQLite (local) |
| Packaging | PyInstaller + electron-builder |

---

## Running locally

**Prerequisites:** Python 3.10+, Node.js 18+

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Flask app
python run.py
```

To build the desktop `.exe`:

```bash
npm install
npm run dist
```

The installer and portable executable will be in `dist_electron/`.

---

## Distribution

The app is packaged as a standalone Windows `.exe` — no Python, Node.js, or any other installation required on the recipient's machine. Data persists locally between sessions via SQLite.

---

## Built by

**Swagata Paul** — made this because FFCS was genuinely painful.
