from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.a733_compare import extract_key_values


RADXA_PRODUCTS = Path("src/share/rsdk/configs/products.json")
RADXA_SOCS = Path("src/share/rsdk/configs/socs.json")
RADXA_KDE = Path("src/share/rsdk/build/mod/packages/kde.libjsonnet")
RADXA_CORE = Path("src/share/rsdk/build/mod/packages/categories/core.libjsonnet")

ORANGEPI_BOARD_4PRO = Path("external/config/boards/orangepi4pro.conf")
ORANGEPI_BOARD_Z3W = Path("external/config/boards/orangepizero3w.conf")
ORANGEPI_FAMILY = Path("external/config/sources/families/sun60iw2.conf")


def _read_text(root: Path, relative: Path) -> str:
    path = root / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _parse_radxa_product(root: Path) -> dict[str, object]:
    path = root / RADXA_PRODUCTS
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    for item in data:
        if item.get("product") == "radxa-a733":
            return item
    return {}


def _parse_radxa_soc(root: Path) -> dict[str, object]:
    path = root / RADXA_SOCS
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    for item in data:
        if item.get("soc_family") == "allwinner" and "a733" in item.get("soc_list", []):
            return item
    return {}


def _format_list(values: object) -> str:
    if isinstance(values, list):
        return ", ".join(str(item) for item in values) if values else "(none)"
    if values:
        return str(values)
    return "(missing)"


def _render_section(title: str, lines: list[str]) -> list[str]:
    output = [f"## {title}", ""]
    if not lines:
        output.append("- None")
        return output
    output.extend(f"- {line}" for line in lines)
    return output


def _summarize_radxa_signals(kde_text: str, core_text: str) -> list[str]:
    lines: list[str] = []
    if 'radxa-a733' in kde_text or 'a733' in kde_text:
        lines.append("A733 product is exposed as `radxa-a733`.")
    if 'libqt5gui5-gles' in kde_text:
        lines.append("KDE on A733 uses `libqt5gui5-gles` for GLES-backed GUI acceleration.")
    if 'GDM' in kde_text and 'not support GDM' in kde_text:
        lines.append("Radxa says the A733 GPU driver does not support GDM for now.")
    if 'kmscon' in core_text:
        lines.append("On `trixie`, A733 switches the default tty terminal to `kmscon` with a DRM backend.")
    if 'limited support of a733 for framebuffer' in core_text:
        lines.append("Radxa documents limited framebuffer support for A733.")
    if 'libtsm4/trixie-backports' in core_text:
        lines.append("A733 `trixie` support depends on `libtsm4/trixie-backports`.")
    return lines


def _summarize_orangepi_signals(orange_4pro: dict[str, str], orange_z3w: dict[str, str], orange_family_text: str) -> list[str]:
    lines: list[str] = []
    if orange_4pro:
        lines.append("Orange Pi 4 Pro exposes A733 with `pvrsrvkm` in the board module list.")
        if orange_4pro.get("DISTRIB_TYPE_CURRENT"):
            lines.append(f"Orange Pi 4 Pro includes `{orange_4pro['DISTRIB_TYPE_CURRENT']}` as a supported release set.")
    if orange_z3w:
        lines.append("Orange Pi Zero 3W uses the same `sun60iw2` A733 family path.")
    if 'sun60i-a733' in orange_family_text:
        lines.append("Orange Pi uses the `sun60i-a733` overlay prefix for A733 boards.")
    if 'linux-sun60iw2-current-a733' in orange_family_text or 'linux-sun60iw2-legacy-a733' in orange_family_text:
        lines.append("Orange Pi has A733-specific Linux config variants for both legacy and current branches.")
    if 'pvrsrvkm.ko' in orange_family_text:
        lines.append("Orange Pi installs the `pvrsrvkm.ko` module into the image.")
    if 'libAWIspApi' in orange_family_text:
        lines.append("Orange Pi carries A733 ISP user-space packages into the image.")
    return lines


def build_report(radxa_root: Path, orangepi_root: Path) -> str:
    radxa_root = Path(radxa_root)
    orangepi_root = Path(orangepi_root)

    product = _parse_radxa_product(radxa_root)
    soc = _parse_radxa_soc(radxa_root)

    kde_text = _read_text(radxa_root, RADXA_KDE)
    core_text = _read_text(radxa_root, RADXA_CORE)

    orange_4pro = extract_key_values(orangepi_root / ORANGEPI_BOARD_4PRO) if (orangepi_root / ORANGEPI_BOARD_4PRO).exists() else {}
    orange_z3w = extract_key_values(orangepi_root / ORANGEPI_BOARD_Z3W) if (orangepi_root / ORANGEPI_BOARD_Z3W).exists() else {}
    orange_family_text = _read_text(orangepi_root, ORANGEPI_FAMILY)

    radxa_lines = [
        f"product: `{product.get('product', '(missing)')}`",
        f"supported suite: {_format_list(product.get('supported_suite'))}",
        f"supported edition: {_format_list(product.get('supported_edition'))}",
        f"soc family: `{soc.get('soc_family', '(missing)')}`",
        f"soc list: {_format_list(soc.get('soc_list'))}",
    ]
    radxa_lines.extend(_summarize_radxa_signals(kde_text, core_text))

    orange_lines = []
    if orange_4pro:
        orange_lines.append(f"orangepi4pro BOARDFAMILY: `{orange_4pro.get('BOARDFAMILY', '(missing)')}`")
        orange_lines.append(f"orangepi4pro BOOT_FDT_FILE: `{orange_4pro.get('BOOT_FDT_FILE', '(missing)')}`")
        orange_lines.append(f"orangepi4pro MODULES: `{orange_4pro.get('MODULES', '(missing)')}`")
        orange_lines.append(f"orangepi4pro DISTRIB_TYPE_CURRENT: `{orange_4pro.get('DISTRIB_TYPE_CURRENT', '(missing)')}`")
    if orange_z3w:
        orange_lines.append(f"orangepizero3w BOARDFAMILY: `{orange_z3w.get('BOARDFAMILY', '(missing)')}`")
        orange_lines.append(f"orangepizero3w BOOT_FDT_FILE: `{orange_z3w.get('BOOT_FDT_FILE', '(missing)')}`")
        orange_lines.append(f"orangepizero3w DISTRIB_TYPE_CURRENT: `{orange_z3w.get('DISTRIB_TYPE_CURRENT', '(missing)')}`")
    orange_lines.extend(_summarize_orangepi_signals(orange_4pro, orange_z3w, orange_family_text))

    missing: list[str] = []
    if not product:
        missing.append("Radxa product metadata for radxa-a733 is missing.")
    if not soc:
        missing.append("Radxa Allwinner a733 SoC metadata is missing.")
    if "trixie" not in _format_list(product.get("supported_suite")):
        missing.append("Radxa does not expose a trixie target for radxa-a733.")
    if "bookworm" not in _format_list(product.get("supported_suite")):
        missing.append("Radxa public SDK does not expose a Debian 12 (bookworm) target for radxa-a733.")
    if not orange_4pro:
        missing.append("Orange Pi 4 Pro board config is missing.")
    if "pvrsrvkm" not in str(orange_4pro.get("MODULES", "")):
        missing.append("Orange Pi 4 Pro does not expose pvrsrvkm in MODULES.")
    missing.append("No real Debian 12 build/boot validation on a physical A7Z has been recorded yet.")

    recommended = [
        "Use Radxa Debian 11 as the boot/display baseline, but move the rootfs and desktop layer toward Debian 12.",
        "Keep Micro HDMI as the first bring-up path.",
        "Treat Orange Pi 4 Pro Bookworm wiring as a packaging reference, not as a drop-in board config.",
    ]

    lines = ["# Radxa Cubie A7Z Debian 12 Migration Report", ""]
    lines.extend(_render_section(
        "Inputs",
        [
            f"Radxa tree: `{radxa_root}`",
            f"Orange Pi tree: `{orangepi_root}`",
            "Primary target: Debian 12",
            "Secondary target: Debian 13",
            "Fallback: Armbian",
        ],
    ))
    lines.append("")
    lines.extend(_render_section("Radxa signals", radxa_lines))
    lines.append("")
    lines.extend(_render_section("Orange Pi signals", orange_lines))
    lines.append("")
    lines.extend(_render_section(
        "Debian 12 desktop implications",
        [
            "The local Radxa trial branch now exposes Bookworm for radxa-a733, so the next question is runtime validation.",
            "Orange Pi shows explicit Bookworm desktop packaging and pvrsrvkm wiring for A733 boards.",
            "Micro HDMI should be validated before any secondary display path.",
            "Desktop bring-up should accept limited graphics acceleration at first.",
        ],
    ))
    lines.append("")
    lines.extend(_render_section("Missing pieces", missing or ["(none)"]))
    lines.append("")
    lines.extend(_render_section("Recommended next action", [f"Gap-aware: {item}" for item in recommended]))
    lines.append("")

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an A7Z Debian 12 migration report.")
    parser.add_argument("radxa_root", type=Path, help="Path to the Radxa RSDK tree")
    parser.add_argument("orangepi_root", type=Path, help="Path to the Orange Pi build tree")
    parser.add_argument("--output", type=Path, help="Write the report to this file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = build_report(args.radxa_root, args.orangepi_root)
    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
