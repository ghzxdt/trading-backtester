"""What a recorded run must say about itself: the code it ran, its settings, and where its files go.

A trial record names the commit (with "+dirty" when code or settings were changed but not committed), the
settings that shape results, and a report file that no later run can overwrite.
"""
from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CODE_PATHS = ("backtester", "run_studies.py", "run_trades.py", "config.json")  # what decides a result
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _git(*args: str) -> str:
    exe = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    return subprocess.run([exe, *args], cwd=HERE, capture_output=True, text=True, timeout=20,
                          creationflags=NO_WINDOW).stdout.strip()


def code_version() -> str:
    """Short commit hash, plus '+dirty' if code or config.json differ from that commit."""
    try:
        head = _git("rev-parse", "--short", "HEAD")
        if not head:
            return "uncommitted"
        return head + ("+dirty" if _git("status", "--porcelain", "--", *CODE_PATHS) else "")
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def settings(cfg: dict) -> dict:
    """The settings that shape results (the research app's folder is this machine's business, not a setting)."""
    return {k: v for k, v in cfg.items() if k != "research_app"}


def report_stem(kind: str, started: datetime) -> str:
    """Report file name without extension. The UTC time keeps two runs on one day from sharing a file."""
    return f"{started:%Y-%m-%d-%H%M%S}-{kind}"
