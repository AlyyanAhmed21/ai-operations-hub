# core/main.py
import subprocess
import sys
import threading
import time
import signal
import os

# ANSI color codes for premium visual console output
COLOR_FE = "\033[96m"   # Cyan
COLOR_BE = "\033[92m"   # Green
COLOR_SYS = "\033[93m"  # Yellow
COLOR_RESET = "\033[0m"

processes = []

def log_stream(stream, prefix, color_code):
    """Concurrently reads lines from stdout/stderr of a subprocess and prints them with a prefix."""
    try:
        for line in iter(stream.readline, ''):
            if not line:
                break
            stripped = line.strip()
            if stripped:
                print(f"{color_code}[{prefix}] {stripped}{COLOR_RESET}")
                sys.stdout.flush()
    except Exception:
        pass

def start_processes():
    print(f"{COLOR_SYS}[SYSTEM] Starting AI Operations Hub Orchestrator...{COLOR_RESET}")
    print(f"{COLOR_SYS}[SYSTEM] Note: Automation layer is cloud-hosted (Make.com).{COLOR_RESET}")
    
    # 1. Start Frontend (Node.js http server)
    try:
        print(f"{COLOR_SYS}[SYSTEM] Launching Frontend (node server.js)...{COLOR_RESET}")
        fe_proc = subprocess.Popen(
            ["node", "server.js"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True
        )
        processes.append((fe_proc, "FRONTEND", COLOR_FE))
    except Exception as e:
        print(f"{COLOR_SYS}[SYSTEM] Failed to launch FRONTEND: {e}{COLOR_RESET}")

    # 2. Start Backend (FastAPI via Conda run LearnAgents)
    try:
        print(f"{COLOR_SYS}[SYSTEM] Launching Backend (conda run -n LearnAgents python main.py)...{COLOR_RESET}")
        be_proc = subprocess.Popen(
            ["conda", "run", "-n", "LearnAgents", "python", "main.py"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True
        )
        processes.append((be_proc, "BACKEND", COLOR_BE))
    except Exception as e:
        print(f"{COLOR_SYS}[SYSTEM] Failed to launch BACKEND: {e}{COLOR_RESET}")

    # Start thread-safe logging readers for all stdout and stderr streams
    for proc, name, color in processes:
        t_out = threading.Thread(target=log_stream, args=(proc.stdout, name, color), daemon=True)
        t_err = threading.Thread(target=log_stream, args=(proc.stderr, name, color), daemon=True)
        t_out.start()
        t_err.start()

def cleanup(signum, frame):
    """Gracefully terminates all background subprocess trees to prevent port binding conflicts."""
    print(f"\n{COLOR_SYS}[SYSTEM] KeyboardInterrupt/SIGTERM received. Cleaning up child process trees...{COLOR_RESET}")
    for proc, name, color in list(processes):
        if proc.poll() is None:
            print(f"{COLOR_SYS}[SYSTEM] Terminating {name} (PID: {proc.pid})...{COLOR_RESET}")
            try:
                if os.name == 'nt':
                    # Kill the entire process tree on Windows using taskkill
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    proc.terminate()
            except Exception as e:
                print(f"{COLOR_SYS}[SYSTEM] Error killing {name}: {e}{COLOR_RESET}")
                proc.kill()
    print(f"{COLOR_SYS}[SYSTEM] Cleanup completed. Exiting orchestrator.{COLOR_RESET}")
    sys.exit(0)

# Register signals for cleanup
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == "__main__":
    start_processes()
    
    try:
        while True:
            time.sleep(1)
            # Monitor process life
            for item in list(processes):
                proc, name, color = item
                ret = proc.poll()
                if ret is not None:
                    print(f"{COLOR_SYS}[SYSTEM] {name} process exited with code {ret}{COLOR_RESET}")
                    processes.remove(item)
            if len(processes) == 0:
                print(f"{COLOR_SYS}[SYSTEM] All child processes exited. Exiting orchestrator.{COLOR_RESET}")
                break
    except KeyboardInterrupt:
        cleanup(None, None)