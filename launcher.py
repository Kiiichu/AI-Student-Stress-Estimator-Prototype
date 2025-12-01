import subprocess
import time
import sys
import os
import requests
import webbrowser

BACKEND_FILE = "app.py"
FRONTEND_FILE = "gradio_stress_visual.py"
BACKEND_URL = "http://127.0.0.1:8000/docs"
FRONTEND_URL = "http://127.0.0.1:7860"

# --- Start backend ---
if os.name == "nt":
    backend_proc = subprocess.Popen([sys.executable, BACKEND_FILE], creationflags=subprocess.CREATE_NEW_CONSOLE)
else:
    backend_proc = subprocess.Popen([sys.executable, BACKEND_FILE])

# --- Wait for backend ---
print("Waiting for backend to start...")
max_retries = 30
backend_ready = False
for i in range(max_retries):
    try:
        r = requests.get(BACKEND_URL)
        if r.status_code == 200:
            backend_ready = True
            print("Backend ready!")
            time.sleep(1)
            break
    except requests.exceptions.ConnectionError:
        pass
    print(f"Backend not ready yet ({i+1}/{max_retries})...")
    time.sleep(1)

if not backend_ready:
    print("Backend failed to start. Exiting launcher.")
    backend_proc.terminate()
    sys.exit(1)

# --- Run frontend in same process ---
print("Starting Gradio frontend...")
# Using exec so it runs in the current Python process
with open(FRONTEND_FILE, encoding="utf-8") as f:
    code = f.read()
exec(code)

# --- Open browser ---
webbrowser.open(FRONTEND_URL)

# --- Keep launcher alive ---
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
    backend_proc.terminate()
    print("Launcher terminated.")
