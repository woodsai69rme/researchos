"""
ResearchOS Self-Healing 24/7 Service Supervisor
Monitors Port 8000 & Port 3142; auto-restarts services if down.
"""
import time
import socket
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

# Setup absolute paths
base_dir = Path(r"C:\Users\karma\researchos")
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir.parent))

python_exe = r"C:\Program Files\Python313\python.exe"
log_file = base_dir / "data" / "supervisor.log"
log_file.parent.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_researchos():
    log("[RECOVERY] ResearchOS Port 8000 is inactive. Rebooting daemon...")
    run_server_script = str(base_dir / "run_server.py")
    subprocess.Popen(
        [python_exe, run_server_script],
        cwd=str(base_dir),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    log("[RECOVERY] Dispatched ResearchOS daemon process.")


def start_godmode():
    godmode_dir = Path("C:/Users/karma/ACTIVE_PROJECTS/ai-tools-suite")
    if godmode_dir.exists():
        log("[RECOVERY] God-Mode Port 3142 is inactive. Rebooting Next.js...")
        subprocess.Popen(
            ["cmd.exe", "/c", "npm run dev"],
            cwd=str(godmode_dir),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        log("[RECOVERY] Dispatched God-Mode dev server.")


def main():
    log("============================================================")
    log(" ResearchOS 24/7 Self-Healing Supervisor Daemon Online")
    log("============================================================")
    
    while True:
        try:
            # Check ResearchOS on Port 8000
            if not is_port_open(8000):
                start_researchos()
                time.sleep(5)
            
            # Check God-Mode Dashboard on Port 3142
            if not is_port_open(3142):
                start_godmode()
                time.sleep(5)

        except Exception as e:
            log(f"[ERROR] Supervisor cycle error: {e}")

        # Sleep for 15 seconds between heartbeat health polls
        time.sleep(15)


if __name__ == "__main__":
    main()
