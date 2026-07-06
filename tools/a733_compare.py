from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


BOARD_CONFIG_DIR = Path("external/config/boards")
FAMILY_CONFIG_DIR = Path("external/config/sources/families")
DTS_ROOT = Path("arch/arm64/boot/dts")


def _iter_files(root: Path, relative_dir: Path, patterns: Iterable[str]) -> list[Path]:
    base = root / relative_dir
    if not base.exists():
        return []
    files: list[Path] = []
    for pattern in patterns:
        if relative_dir == DTS_ROOT:
            files.extend(sorted(base.rglob(pattern)))
        else:
            files.extend(sorted(base.glob(pattern)))
    return files


def discover_relevant_files(root: Path) -> list[str]:
    root = Path(root)
    files: list[Path] = []
    files.extend(_iter_files(root, BOARD_CONFIG_DIR, ("*.conf",)))
    files.extend(_iter_files(root, FAMILY_CONFIG_DIR, ("*.conf",)))
    files.extend(_iter_files(root, DTS_ROOT, ("*.dts", "*.dtsi", "*.dtbo")))

    seen: set[str] = set()
    ordered: list[str] = []
    for path in sorted(files):
        rel = path.relative_to(root).as_posix()
        if rel not in seen:
            seen.add(rel)
            ordered.append(rel)
    return ordered


def extract_key_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def _first_file(root: Path, relative_dir: Path, patterns: Iterable[str]) -> Path | None:
    candidates = _iter_files(root, relative_dir, patterns)
    return candidates[0] if candidates else None


def _format_path(path: Path | None, root: Path) -> str:
    if path is None:
        return "(missing)"
    return path.relative_to(root).as_posix()


def _render_file_list(title: str, items: list[str]) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        lines.append("- None")
        return lines
    for item in items:
        lines.append(f"- `{item}`")
    return lines


def _render_key_diff(left: dict[str, str], right: dict[str, str], left_label: str, right_label: str) -> list[str]:
    keys = sorted(set(left) | set(right))
    lines = ["| Key | " + left_label + " | " + right_label + " |", "| --- | --- | --- |"]
    for key in keys:
        lval = left.get(key, "")
        rval = right.get(key, "")
        if lval == rval:
            continue
        lines.append(f"| {key} | `{lval}` | `{rval}` |")
    if len(lines) == 2:
        lines.append("| (none) |  |  |")
    return lines


def build_report(left_root: Path, right_root: Path, left_label: str, right_label: str) -> str:
    left_root = Path(left_root)
    right_root = Path(right_root)

    left_files = set(discover_relevant_files(left_root))
    right_files = set(discover_relevant_files(right_root))

    left_only = sorted(left_files - right_files)
    right_only = sorted(right_files - left_files)
    shared = sorted(left_files & right_files)

    left_board = _first_file(left_root, BOARD_CONFIG_DIR, ("*.conf",))
    right_board = _first_file(right_root, BOARD_CONFIG_DIR, ("*.conf",))
    left_family = _first_file(left_root, FAMILY_CONFIG_DIR, ("*.conf",))
    right_family = _first_file(right_root, FAMILY_CONFIG_DIR, ("*.conf",))

    lines = ["# A733 Source Comparison", ""]
    lines.append(f"- Left: {left_label}")
    lines.append(f"- Right: {right_label}")
    lines.append("")
    lines.append("## Selected configs")
    lines.append("")
    lines.append(f"- Primary board config for {left_label}: `{_format_path(left_board, left_root)}`")
    lines.append(f"- Primary board config for {right_label}: `{_format_path(right_board, right_root)}`")
    lines.append(f"- Primary family config for {left_label}: `{_format_path(left_family, left_root)}`")
    lines.append(f"- Primary family config for {right_label}: `{_format_path(right_family, right_root)}`")
    lines.append("")

    lines.extend(_render_file_list(f"Files only in {left_label}", left_only))
    lines.append("")
    lines.extend(_render_file_list(f"Files only in {right_label}", right_only))
    lines.append("")
    lines.append("## Shared files")
    lines.append("")
    if shared:
        for item in shared:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Board config key differences")
    lines.append("")
    if left_board and right_board:
        left_values = extract_key_values(left_board)
        right_values = extract_key_values(right_board)
        lines.extend(_render_key_diff(left_values, right_values, left_label, right_label))
    else:
        lines.append("- One or both primary board configs are missing.")
    lines.append("")

    lines.append("## Family config key differences")
    lines.append("")
    if left_family and right_family:
        left_values = extract_key_values(left_family)
        right_values = extract_key_values(right_family)
        lines.extend(_render_key_diff(left_values, right_values, left_label, right_label))
    else:
        lines.append("- One or both primary family configs are missing.")
    lines.append("")

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two A733 vendor source trees and render a Markdown report."
    )
    parser.add_argument("left_root", type=Path, help="Path to the left source tree")
    parser.add_argument("right_root", type=Path, help="Path to the right source tree")
    parser.add_argument("--left-label", default="Left tree", help="Label for the left tree")
    parser.add_argument("--right-label", default="Right tree", help="Label for the right tree")
    parser.add_argument("--output", type=Path, help="Write the report to this file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = build_report(args.left_root, args.right_root, args.left_label, args.right_label)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
