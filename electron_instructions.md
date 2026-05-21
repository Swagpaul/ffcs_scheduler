# FFCS Scheduler - Desktop Integration Documentation

This document contains instructions for running, building, distributing, and extending the FFCS Scheduler desktop application.

---

## 1. Setup & Installation

Before running the application, ensure you have the following prerequisites installed on your system:
- **Node.js** (v18 or higher)
- **Python 3.11** (or compatible)

### First-Time Project Setup
1. Clone the repository and navigate to the project directory.
2. Ensure the Python virtual environment is set up:
   ```bash
   python -m venv venv
   .\venv\Scripts\pip install -r requirements.txt
   .\venv\Scripts\pip install pyinstaller
   ```
3. Install the Node.js dependencies:
   ```bash
   npm install
   ```

---

## 2. Running in Development Mode

To launch the desktop app in development mode, simply run:
```bash
npm run dev
```

### What happens in the background:
- Electron automatically queries the OS to find a free TCP port (e.g., `5000` or a random high port if `5000` is taken).
- It spawns the Flask backend using the virtual environment's Python interpreter (`venv/Scripts/python.exe run.py`) in headless mode (completely hiding the command line interface from the user).
- Electron polls the Flask server until it responds.
- Once ready, a premium desktop window opens and loads the local port dashboard automatically.
- Upon closing the Electron window, the app runs `taskkill /pid <pid> /T /F` on Windows to clean up all background Python processes recursively.

---

## 3. Generating Executable (.exe) Builds

To generate standalone executables for Windows:
```bash
npm run dist
```

### What this command does:
1. **Compiles the Python Backend:** It invokes PyInstaller, which bundles Python, the Flask server, all dependencies, database models, static templates, and assets into a standalone folder: `dist/ffcs_backend/`.
2. **Packages the Electron Application:** It invokes `electron-builder` which copies the compiled Python binary folder into the Electron App resources (`extraResources`), compiles the JS files into ASAR, and packages them.
3. **Generates Target Outputs:** It generates two outputs inside the `dist_electron/` directory:
   - **Windows Installer (`FFCS Scheduler Setup <version>.exe`):** A professional, customized setup wizard that installs the app into Program Files, creates start menu and desktop shortcuts, and registers uninstall details.
   - **Portable Version (`FFCS Scheduler <version>.exe`):** A standalone executable that runs directly without installation.

---

## 4. Rebuilding After Future Updates

When you make changes to the Flask backend (routes, models, schedules) or frontend (HTML templates, CSS styles, JS scripts):
- **For Dev Testing:** Just run `npm run dev` again. It dynamically loads the local source code directly.
- **For Packaging:** Run `npm run dist` again. The scripts are configured to automatically compile the latest Python and frontend codebase, then bundle it into the new installer build.

---

## 5. Distribution to Other Users

To distribute the app to another Windows machine:
1. Send the user the setup installer `.exe` or portable `.exe` from the `dist_electron/` folder.
2. **Python is not required on the user's machine.** The Python backend is fully compiled with all its dependencies inside the executable.
3. **Database Portability:** On first boot, the application automatically initializes a secure SQLite database file inside the user's AppData directory:
   `%APPDATA%/FFCS-Scheduler/ffcs_scheduler.db`
   This guarantees that database operations succeed without write permission errors (which occur when trying to write to files inside Program Files) and keeps all scheduled timetables 100% private and offline on the user's machine.
4. **Supplying custom Environment Variables:** Users can provide their own keys (like `GROQ_API_KEY` for AI scheduling features) by creating a `.env` file and placing it:
   - Either next to the installed/portable `.exe` file.
   - Or directly in `%APPDATA%/FFCS-Scheduler/.env`.

---

## 6. Future Architecture Guidelines

### A. Offline Local Database
- Already integrated into the core architecture:
  - Inside [config.py](file:///c:/Users/Swagata%20Paul/Desktop/Projects/ffcs_scheduler/config.py), the function `get_db_uri()` checks if the application is frozen. If so, it dynamically overrides the database connection string to point to the local user AppData SQLite file.
  - Inside [app/main.py](file:///c:/Users/Swagata%20Paul/Desktop/Projects/ffcs_scheduler/app/main.py), the `db.create_all()` function is run inside the application context on startup, ensuring that if the database is newly initialized, all tables are created automatically.

### B. Google Drive Synchronisation
- **Mechanism:** To enable backing up or sync of the scheduler data:
  1. Add `google-auth` and `google-api-python-client` to `requirements.txt`.
  2. Implement a sync helper in the Flask API (`app/routes/api.py`) that uploads the file `%APPDATA%/FFCS-Scheduler/ffcs_scheduler.db` to the user's Google AppData folder (a special hidden folder in Drive specifically for app configurations).
  3. In Electron, provide a "Sync with Google Drive" button that triggers this endpoint. The endpoint can handle OAuth2 flows via browser redirect or prompt the user inside a modal.

### C. Auto-Updates
- **Mechanism:** `electron-builder` supports `electron-updater` out of the box.
  1. Configure a `publish` provider in `electron-builder.json`, pointing to a public or private GitHub repository:
     ```json
     "publish": {
       "provider": "github",
       "owner": "username",
       "repo": "repository"
     }
     ```
  2. In `main.js`, import and call `autoUpdater`:
     ```javascript
     const { autoUpdater } = require('electron-updater');
     
     app.on('ready', () => {
       autoUpdater.checkForUpdatesAndNotify();
     });
     ```
  3. When a new release is published on GitHub, the user's app will automatically download the installer, prompt them, and update on exit.
