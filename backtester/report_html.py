"""Render a study report (the simple Markdown run_studies.py writes) as a readable HTML page."""
from __future__ import annotations

import html
import re

STYLE = """body{font-family:Segoe UI,Arial,sans-serif;margin:32px auto;max-width:1200px;color:#1b2533;line-height:1.5;padding:0 20px}
h1{color:#14324a}h2{color:#14324a;border-bottom:1px solid #d5dde5;padding-bottom:4px;margin-top:36px}
table{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0 16px}
th{background:#14324a;color:#fff;text-align:left;padding:6px 8px}td{padding:5px 8px;border-bottom:1px solid #e3e8ee}
tr:nth-child(even) td{background:#f6f8fa}td.v-Candidate{background:#dff3e4!important;font-weight:600}
td.v-Failed{background:#fdecea!important}code{background:#eef2f6;padding:1px 4px;border-radius:3px}"""


def _inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def _cell(value: str, header: bool) -> str:
    if header:
        return f"<th>{_inline(value)}</th>"
    css = "v-Candidate" if value == "Candidate" else "v-Failed" if value == "Failed holdout" else ""
    return f'<td class="{css}">{_inline(value)}</td>' if css else f"<td>{_inline(value)}</td>"


def render(markdown: str, title: str = "Backtester report") -> str:
    out, table, items = [], [], []

    def flush():
        if table:
            rows = [r for r in table if not re.fullmatch(r"\|[\s\-|]+\|", r)]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            out.append("<table>" + "".join("<tr>" + "".join(_cell(c, i == 0) for c in row) + "</tr>"
                                            for i, row in enumerate(cells)) + "</table>")
            table.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for line in markdown.splitlines():
        if line.startswith("|"):
            table.append(line)
            continue
        if line.startswith("- "):
            items.append(line[2:])
            continue
        flush()
        if line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.strip():
            out.append(f"<p>{_inline(line)}</p>")
    flush()
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{STYLE}</style></head><body>{''.join(out)}</body></html>")
