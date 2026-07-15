#!/usr/bin/env python3
"""Render current project status from docs/status.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/status.json"
TABLE_START = "<!-- status-table:start -->"
TABLE_END = "<!-- status-table:end -->"
BASELINE_START = "<!-- status-baseline:start -->"
BASELINE_END = "<!-- status-baseline:end -->"
SUMMARY_START = "<!-- status-summary:start -->"
SUMMARY_END = "<!-- status-summary:end -->"

STATUS_LABELS = {
    "working": {"en": "✅ Working", "zh": "✅ 已解决"},
    "working_first_port": {"en": "✅ Working (first port)", "zh": "✅ 第一版已解决"},
    "documented": {"en": "📘 Documented", "zh": "📘 已文档化"},
    "not_validated": {"en": "🧪 Not validated", "zh": "🧪 未验证"},
    "in_progress": {"en": "🚧 In progress", "zh": "🚧 进行中"},
    "not_started": {"en": "⬜ Not started", "zh": "⬜ 未开始"},
}

LEGENDS = {
    "en": "Status: ✅ working · 📘 documented · 🧪 awaiting validation · 🚧 in progress · ⬜ not started",
    "zh": "状态：✅ 已解决 · 📘 已文档化 · 🧪 待验证 · 🚧 进行中 · ⬜ 未开始",
}


def load_status(path: Path = SOURCE) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = [item["id"] for item in data["capabilities"]]
    if len(ids) != len(set(ids)):
        raise ValueError("capability ids must be unique")
    unknown = {item["status"] for item in data["capabilities"]} - STATUS_LABELS.keys()
    if unknown:
        raise ValueError(f"unknown status values: {sorted(unknown)}")
    return data


def render_capability_table(data: dict, lang: str) -> str:
    headers = {
        "en": ("Area", "Current status", "Notes"),
        "zh": ("能力", "当前状态", "说明"),
    }[lang]
    lines = [
        LEGENDS[lang],
        "",
        f"| {headers[0]} | {headers[1]} | {headers[2]} |",
        "| --- | --- | --- |",
    ]
    for item in data["capabilities"]:
        lines.append(
            f'| {item["area"][lang]} | {STATUS_LABELS[item["status"]][lang]} | '
            f'{item["notes"][lang]} |'
        )
    return "\n".join(lines)


def render_summary(data: dict, lang: str) -> str:
    return "\n".join(f'- {item[lang]}' for item in data["summary"])


def localized(value: str | dict, lang: str) -> str:
    return value[lang] if isinstance(value, dict) else value


def render_baseline_table(data: dict, lang: str) -> str:
    headers = {
        "en": ("Item", "Verified result"),
        "zh": ("项目", "验证结果"),
    }[lang]
    lines = [f"| {headers[0]} | {headers[1]} |", "| --- | --- |"]
    for item in data["baseline"]:
        lines.append(f'| {item["key"][lang]} | {localized(item["value"], lang)} |')
    return "\n".join(lines)


def replace_generated_block(text: str, start: str, end: str, content: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"missing generated block markers: {start} / {end}")
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return f"{prefix}{start}\n{content}\n{end}{suffix}"


def render_status_document(data: dict, lang: str) -> str:
    if lang == "en":
        title = "# Current Status"
        notice = "> Generated from `docs/status.json`. Edit the JSON source, then run `python3 tools/render_status.py`."
        snapshot = "## Verified Baseline"
        capabilities = "## Capability Status"
        milestone = "## Current Milestone"
        next_heading = "## Next Milestones"
    else:
        title = "# 当前状态"
        notice = "> 本文由 `docs/status.json` 生成。请修改 JSON 单一源，然后运行 `python3 tools/render_status.py`。"
        snapshot = "## 已验证基线"
        capabilities = "## 能力状态"
        milestone = "## 当前里程碑"
        next_heading = "## 下一阶段"

    lines = [title, "", notice, "", f'**{data["snapshot_date"]}**', "", snapshot, ""]
    lines.append(render_baseline_table(data, lang))

    lines.extend(["", capabilities, "", render_capability_table(data, lang)])
    lines.extend(["", milestone, "", render_summary(data, lang)])
    lines.extend(["", next_heading, ""])
    lines.extend(f'- {item[lang]}' for item in data["next_milestones"])
    return "\n".join(lines) + "\n"


def build_outputs(root: Path = ROOT, data: dict | None = None) -> dict[Path, str]:
    data = data or load_status(root / "docs/status.json")
    outputs: dict[Path, str] = {}
    for filename, lang in (("README.md", "en"), ("README.zh-CN.md", "zh")):
        path = root / filename
        text = path.read_text(encoding="utf-8")
        text = replace_generated_block(
            text, BASELINE_START, BASELINE_END, render_baseline_table(data, lang)
        )
        text = replace_generated_block(
            text, TABLE_START, TABLE_END, render_capability_table(data, lang)
        )
        text = replace_generated_block(
            text, SUMMARY_START, SUMMARY_END, render_summary(data, lang)
        )
        outputs[path] = text
    outputs[root / "docs/status.md"] = render_status_document(data, "en")
    outputs[root / "docs/status.zh-CN.md"] = render_status_document(data, "zh")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated files are stale")
    args = parser.parse_args()

    stale = []
    for path, expected in build_outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == expected:
            continue
        stale.append(path)
        if not args.check:
            path.write_text(expected, encoding="utf-8")

    if args.check and stale:
        for path in stale:
            print(f"stale generated status: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
