from __future__ import annotations

import argparse
import json
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


def validate_tree(root: Path) -> dict[str, object]:
    root = Path(root)
    present: list[str] = []
    missing: list[str] = []

    board_files = _iter_files(root, BOARD_CONFIG_DIR, ("*.conf",))
    family_files = _iter_files(root, FAMILY_CONFIG_DIR, ("*.conf",))
    dts_files = _iter_files(root, DTS_ROOT, ("*.dts", "*.dtsi", "*.dtbo"))

    if board_files:
        present.append(f"board config: {board_files[0].relative_to(root).as_posix()}")
    else:
        missing.append("board config (*.conf under external/config/boards)")

    if family_files:
        present.append(f"family config: {family_files[0].relative_to(root).as_posix()}")
    else:
        missing.append("family config (*.conf under external/config/sources/families)")

    if dts_files:
        present.append(f"dts files: {dts_files[0].relative_to(root).as_posix()}")
    else:
        missing.append("dts files (arch/arm64/boot/dts/**/*.dts|dtsi|dtbo)")

    values: dict[str, str] = {}
    if board_files:
        values.update(extract_key_values(board_files[0]))
    if family_files:
        values.update(extract_key_values(family_files[0]))

    if values.get("BOARDFAMILY") != "sun60iw2":
        missing.append("BOARDFAMILY=sun60iw2 in board config")
    else:
        present.append("BOARDFAMILY=sun60iw2")

    if "MODULES" not in values:
        missing.append("MODULES entry in board config")
    else:
        present.append("MODULES entry present")

    if "DISTRIB_TYPE_CURRENT" not in values and "DISTRIB_TYPE_LEGACY" not in values:
        missing.append("DISTRIB_TYPE_CURRENT or DISTRIB_TYPE_LEGACY in family config")
    else:
        present.append("distribution type entry present")

    if "BOOT_FDT_FILE" not in values:
        missing.append("BOOT_FDT_FILE entry in board config")
    else:
        present.append("BOOT_FDT_FILE entry present")

    return {
        "ok": not missing,
        "present": present,
        "missing": missing,
        "summary": {
            "board_files": len(board_files),
            "family_files": len(family_files),
            "dts_files": len(dts_files),
        },
    }


def _render_validation_report(result: dict[str, object], root: Path) -> str:
    lines = ["# A733 Tree Check", "", f"- Root: `{root}`", ""]
    lines.append("## Present")
    lines.append("")
    present = result.get("present", [])
    if present:
        for item in present:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Missing")
    lines.append("")
    missing = result.get("missing", [])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary = result.get("summary", {})
    if isinstance(summary, dict):
        for key in ("board_files", "family_files", "dts_files"):
            lines.append(f"- {key}: {summary.get(key, 0)}")
    lines.append("")
    lines.append(f"- ok: `{result.get('ok', False)}`")
    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare or validate A733 vendor source trees."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare = subparsers.add_parser("compare", help="Compare two source trees")
    compare.add_argument("left_root", type=Path, help="Path to the left source tree")
    compare.add_argument("right_root", type=Path, help="Path to the right source tree")
    compare.add_argument("--left-label", default="Left tree", help="Label for the left tree")
    compare.add_argument("--right-label", default="Right tree", help="Label for the right tree")
    compare.add_argument("--output", type=Path, help="Write the report to this file instead of stdout")

    check = subparsers.add_parser("check", help="Validate a single source tree for minimum A733 support")
    check.add_argument("root", type=Path, help="Path to the source tree")
    check.add_argument("--output", type=Path, help="Write the report to this file instead of stdout")
    check.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "compare":
        report = build_report(args.left_root, args.right_root, args.left_label, args.right_label)
    else:
        result = validate_tree(args.root)
        if args.json:
            report = json.dumps(result, indent=2, sort_keys=True)
        else:
            report = _render_validation_report(result, args.root)

    if getattr(args, "output", None):
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
