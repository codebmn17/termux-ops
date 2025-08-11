#!/usr/bin/env python3
# StormREPL v0 — lightweight local Replit-style runner (no deps)
import os, sys, subprocess, time, json
from datetime import datetime

ROOT   = os.path.abspath(os.path.dirname(__file__))
APP    = os.path.join(ROOT, "main.py")
LOGDIR = os.path.join(ROOT, ".repl_logs")
HIST   = os.path.join(ROOT, ".repl_history.json")

def ensure_project():
    os.makedirs(LOGDIR, exist_ok=True)
    if not os.path.exists(APP):
        with open(APP, "w", encoding="utf-8") as f:
            f.write(
                "# main.py — your app entrypoint\n"
                "print('StormREPL online. Edit main.py and press Run again!')\n"
            )

def save_history(entry):
    try:
        data = []
        if os.path.exists(HIST):
            with open(HIST, "r", encoding="utf-8") as f:
                data = json.load(f)
        data.append(entry)
        with open(HIST, "w", encoding="utf-8") as f:
            json.dump(data[-200:], f, ensure_ascii=False, indent=2)  # keep last 200
    except Exception:
        pass

def run_app():
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(LOGDIR, f"run-{ts}.log")
    print(f"\n[StormREPL] Running: python {APP}\n")
    proc = subprocess.Popen(
        [sys.executable, APP],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    out, _ = proc.communicate()
    code = proc.returncode
    print(out)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(out)
        f.write(f"\n[exit_code]={code}\n")
    save_history({"ts": ts, "exit": code, "log": os.path.basename(log_path)})
    print(f"\n[StormREPL] Exit code: {code}")
    print(f"[StormREPL] Log saved: {log_path}")

def menu():
    ensure_project()
    while True:
        print("\n=== StormREPL ===")
        print("[1] Run main.py")
        print("[2] Show last run log")
        print("[3] Open project path")
        print("[4] Git commit (snapshot)")
        print("[5] Quit")
        choice = input("> ").strip()
        if choice == "1":
            run_app()
        elif choice == "2":
            try:
                logs = sorted(os.listdir(LOGDIR))
                if not logs: print("No logs yet."); continue
                last = os.path.join(LOGDIR, logs[-1])
                print(f"\n--- {last} ---\n")
                with open(last, "r", encoding="utf-8") as f:
                    print(f.read())
            except Exception as e:
                print("Error:", e)
        elif choice == "3":
            print(f"\nProject folder:\n{ROOT}\n")
            print("Tip: open Acode ➜ browse to this path and edit main.py")
        elif choice == "4":
            msg = input("Commit message (default: snapshot): ").strip() or "snapshot"
            subprocess.run(["git", "add", "-A"], cwd=ROOT)
            subprocess.run(["git", "commit", "-m", msg], cwd=ROOT)
            print("Committed.")
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    menu()
