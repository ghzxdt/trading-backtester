"""Desktop app for the trading backtester (opened by the "Trading Backtester" desktop shortcut).

Buttons run the studies and tests with the research app's Python, open the latest report in the browser, and
open the research app's control panel. Nothing here trades or writes into the research app.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import traceback
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

HERE = Path(__file__).resolve().parent
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def research_root() -> Path:
    return Path(json.loads((HERE / "config.json").read_text(encoding="utf-8"))["research_app"])


def python_exe() -> Path:
    return research_root() / ".venv" / "Scripts" / "python.exe"


def latest_report() -> Path | None:
    reports = sorted((HERE / "reports").glob("*-indicator-studies.md"))
    if not reports:
        return None
    page = reports[-1].with_suffix(".html")
    if not page.exists():
        from backtester.report_html import render
        page.write_text(render(reports[-1].read_text(encoding="utf-8"), reports[-1].stem), encoding="utf-8")
    return page


def status_text() -> str:
    parts = []
    try:
        lines = (research_root() / "data" / "raw" / "etfs.csv").read_text(encoding="utf-8").splitlines()
        parts.append(f"Research data through {lines[-1].split(',')[0]}")
    except (OSError, IndexError):
        parts.append("Research app data not found; check config.json")
    try:
        from backtester import registry
        parts.append(f"{registry.total_tests(HERE / 'trials.jsonl')} tests recorded")
    except Exception as exc:
        parts.append(f"Trial record unreadable: {exc}")
    report = latest_report()
    parts.append(f"Latest report: {report.stem}" if report else "No report yet")
    return "   ·   ".join(parts)


class App:
    def __init__(self, root: tk.Tk):
        self.root, self.events, self.busy = root, queue.Queue(), False
        root.title("Trading Backtester")
        root.geometry("900x600")
        root.minsize(720, 460)
        icon = HERE / "assets" / "backtester.ico"
        if icon.exists():
            root.iconbitmap(str(icon))
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Trading Backtester", font=("Segoe UI Semibold", 18)).pack(anchor="w")
        ttk.Label(frame, text="Tests chart-indicator rules on the research app's data. Reads that app; never changes it.",
                  foreground="#555").pack(anchor="w", pady=(0, 8))
        self.status = tk.StringVar(value=status_text())
        ttk.Label(frame, textvariable=self.status, foreground="#14324a").pack(anchor="w", pady=(0, 10))
        bar = ttk.Frame(frame)
        bar.pack(fill="x", pady=(0, 10))
        self.buttons = []
        for label, action in (("Run indicator studies", self.run_studies), ("Open latest report", self.open_report),
                              ("Open reports folder", lambda: os.startfile(HERE / "reports")),
                              ("Run tests", self.run_tests), ("Open research app", self.open_research)):
            button = ttk.Button(bar, text=label, command=action)
            button.pack(side="left", padx=(0, 8))
            self.buttons.append(button)
        self.output = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 10), wrap="word")
        self.output.pack(fill="both", expand=True)
        self.write("Ready. 'Run indicator studies' takes about 10 seconds and adds a dated report.\n")
        root.after(150, self.drain)

    def write(self, text: str):
        self.output.insert("end", text)
        self.output.see("end")

    def drain(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "line":
                    self.write(value)
                elif kind == "then":
                    value()  # follow-up action, run on the Tk thread
                else:
                    self.busy = False
                    for b in self.buttons:
                        b.state(["!disabled"])
                    self.status.set(status_text())
                    self.write(value + "\n")
        except queue.Empty:
            pass
        self.root.after(150, self.drain)

    def run(self, args: list[str], label: str, after=None):
        if self.busy:
            return
        exe = python_exe()
        if not exe.exists():
            messagebox.showerror("Trading Backtester", f"The research app's Python wasn't found:\n{exe}")
            return
        self.busy = True
        for b in self.buttons:
            b.state(["disabled"])
        self.write(f"\n— {label} —\n")

        def work():
            try:
                proc = subprocess.Popen([str(exe), "-B", *args], cwd=HERE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True, creationflags=NO_WINDOW)
                for line in proc.stdout:
                    self.events.put(("line", line))
                code = proc.wait()
                self.events.put(("done", f"{label}: {'finished' if code == 0 else f'failed (exit {code})'}."))
                if code == 0 and after:
                    self.events.put(("then", after))
            except Exception:
                self.events.put(("done", traceback.format_exc()))
        threading.Thread(target=work, daemon=True).start()

    def run_studies(self):
        self.run(["run_studies.py"], "Indicator studies", after=self.open_report)

    def run_tests(self):
        self.run(["-m", "unittest", "discover", "-s", "tests"], "Tests")

    def open_report(self):
        report = latest_report()
        if report:
            webbrowser.open(report.as_uri())
        else:
            messagebox.showinfo("Trading Backtester", "No report yet. Click 'Run indicator studies' first.")

    def open_research(self):
        root = research_root()
        subprocess.Popen([str(root / ".venv" / "Scripts" / "pythonw.exe"), "-B", str(root / "desktop_app.pyw")],
                         cwd=root, creationflags=NO_WINDOW)


if __name__ == "__main__":
    try:
        os.chdir(HERE)
        import sys
        sys.path.insert(0, str(HERE))
        window = tk.Tk()
        App(window)
        window.mainloop()
    except Exception:
        (HERE / "work").mkdir(exist_ok=True)
        (HERE / "work" / "app_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        raise
