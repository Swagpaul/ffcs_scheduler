const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const net = require('net');
const http = require('http');

let mainWindow = null;
let backendProcess = null;
let backendPort = null;

// Determine if we are in development
const isDev = !app.isPackaged;

// Find a free TCP port dynamically
function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      server.close(() => {
        resolve(port);
      });
    });
  });
}

// Start the Flask backend
async function startBackend(port) {
  return new Promise((resolve, reject) => {
    let pythonPath;
    let args;

    if (isDev) {
      // In development, run python.exe from the virtual environment
      pythonPath = path.join(__dirname, 'venv', 'Scripts', 'python.exe');
      args = [path.join(__dirname, 'run.py')];
    } else {
      // In production, run the bundled PyInstaller executable
      pythonPath = path.join(process.resourcesPath, 'backend', 'ffcs_backend.exe');
      args = [];
    }

    console.log(`Starting backend: ${pythonPath} ${args.join(' ')} on port ${port}`);

    // Set environment variables for the child process
    const env = {
      ...process.env,
      PORT: port.toString(),
      ELECTRON_RUN: '1',
      FLASK_ENV: isDev ? 'development' : 'production'
    };

    backendProcess = spawn(pythonPath, args, {
      cwd: isDev ? __dirname : path.join(process.resourcesPath, 'backend'),
      env,
      windowsHide: true // CRITICAL: Hides the command prompt window on Windows
    });

    // Stream logs to console
    backendProcess.stdout.on('data', (data) => {
      console.log(`[Backend STDOUT]: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`[Backend STDERR]: ${data}`);
    });

    backendProcess.on('error', (err) => {
      console.error(`Failed to start backend: ${err}`);
      reject(err);
    });

    backendProcess.on('exit', (code, signal) => {
      console.log(`Backend process exited with code ${code} and signal ${signal}`);
    });

    // Wait for the Flask server to become responsive
    const checkServer = () => {
      const req = http.get(`http://127.0.0.1:${port}/login`, (res) => {
        console.log(`Backend is ready! Status: ${res.statusCode}`);
        resolve();
      });
      
      req.on('error', () => {
        // Try again in 100ms
        setTimeout(checkServer, 100);
      });
    };

    // Start polling after a short delay
    setTimeout(checkServer, 200);
  });
}

function createWindow(port) {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    title: 'FFCS Scheduler',
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Load the Flask server
  mainWindow.loadURL(`http://127.0.0.1:${port}/`);

  // Handle page crashes or connection failures
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error(`Failed to load: ${errorDescription} (${errorCode})`);
    if (errorCode !== -3) { // Ignore aborted loads
      mainWindow.loadURL(`data:text/html,<html><body style="font-family: 'Outfit', sans-serif; background: #0b0f19; color: #fff; text-align: center; padding-top: 100px;">
        <h1 style="color: #ff3b30;">Connection Error</h1>
        <p>Could not connect to the backend scheduler. Details: ${errorDescription}</p>
        <button onclick="window.location.reload()" style="background: #5e5ce6; border: none; color: #fff; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Retry</button>
      </body></html>`);
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  try {
    backendPort = await findFreePort();
    await startBackend(backendPort);
    createWindow(backendPort);
  } catch (err) {
    console.error(`Initialization error: ${err}`);
    app.quit();
  }
});

// Clean up background processes on exit
function cleanUp() {
  if (backendProcess) {
    console.log('Killing backend process...');
    if (process.platform === 'win32') {
      // Terminate the process tree recursively and forcefully
      exec(`taskkill /pid ${backendProcess.pid} /T /F`, (err) => {
        if (err) console.error(`Error executing taskkill: ${err}`);
      });
    } else {
      backendProcess.kill();
    }
    backendProcess = null;
  }
}

app.on('window-all-closed', () => {
  cleanUp();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  cleanUp();
});
