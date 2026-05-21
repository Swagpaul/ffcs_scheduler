# FFCS Scheduler

A simple desktop app built for VIT students to automatically generate clash-free timetables. Instead of spending hours checking every single slot and professor combination manually, you just plug in your preferences and let the app handle the math.

## What it does

* Enter all your courses, professors, and slot combinations in one place.
* Set priorities for each option, like if you prefer a specific teacher or timing.
* Generate every possible valid, clash-free timetable. They are ranked automatically based on your priorities.
* If a clash is completely unavoidable (like two labs sharing the same slot), the app will output separate timetables for each option so you can decide which one to go with.
* Download any generated timetable as an image.

## How it works

The app uses a backtracking algorithm that tries every combination of your preferred courses, slots, and professors. When it hits a clash, it backtracks and tries the next combination, kind of like how a Sudoku solver works.

It also has a heuristic scoring system that ranks the schedules based on your preferred professors and tries to minimize gaps between classes so you do not get stuck with awkward 3-hour breaks.

## Tech Stack

* **Frontend:** Electron.js
* **Backend:** Python / Flask
* **Database:** SQLite (local persistence)
* **Packaging:** PyInstaller and electron-builder. The app is packaged into a single standalone `.exe` file that works out of the box without needing Python or Node installed.

## Running it locally

If you want to run the code locally, make sure you have Python 3.10+ and Node.js 18+ installed.

### Python Backend
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the Flask server:
   ```bash
   python run.py
   ```

### Electron Frontend & Packaging
1. Install Node modules:
   ```bash
   npm install
   ```
2. Run the desktop app in development mode:
   ```bash
   npm run dev
   ```
3. Build the standalone installer and portable `.exe` files:
   ```bash
   npm run dist
   ```
   The output files will be created in the `dist_electron` directory.

## How data is saved

The app is entirely local-first. All your entered courses, priorities, and schedules are saved locally on your machine using SQLite. Your data stays on your computer and persists when you close and reopen the app.

---

Created by Swagata Paul because manually scheduling FFCS was too painful.
