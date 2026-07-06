import tempfile
import unittest
from pathlib import Path

from tools.a733_compare import (
    build_report,
    discover_relevant_files,
    extract_key_values,
    validate_tree,
)


class A733CompareTests(unittest.TestCase):
    def test_discover_relevant_files_finds_board_and_family_configs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "external/config/boards").mkdir(parents=True)
            (root / "external/config/sources/families").mkdir(parents=True)
            (root / "external/config/boards/board.conf").write_text("BOARD=1\n", encoding="utf-8")
            (root / "external/config/sources/families/sun60iw2.conf").write_text("FAMILY=1\n", encoding="utf-8")

            files = discover_relevant_files(root)

            self.assertEqual(
                files,
                [
                    "external/config/boards/board.conf",
                    "external/config/sources/families/sun60iw2.conf",
                ],
            )

    def test_extract_key_values_ignores_comments_and_quotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "board.conf"
            path.write_text(
                """
                # comment
                BOARDFAMILY="sun60iw2"
                MODULES="pvrsrvkm usb"
                EMPTY=
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            values = extract_key_values(path)

            self.assertEqual(values["BOARDFAMILY"], "sun60iw2")
            self.assertEqual(values["MODULES"], "pvrsrvkm usb")
            self.assertEqual(values["EMPTY"], "")
            self.assertNotIn("# comment", values)

    def test_build_report_includes_primary_differences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left"
            right = Path(tmp) / "right"
            (left / "external/config/boards").mkdir(parents=True)
            (left / "external/config/sources/families").mkdir(parents=True)
            (right / "external/config/boards").mkdir(parents=True)
            (right / "external/config/sources/families").mkdir(parents=True)

            (left / "external/config/boards/radxa-a7z.conf").write_text(
                'BOARDFAMILY="sun60iw2"\nMODULES="pvrsrvkm"\nBOOT_FDT_FILE="allwinner/a7z.dtb"\n',
                encoding="utf-8",
            )
            (left / "external/config/sources/families/sun60iw2.conf").write_text(
                'DISTRIB_TYPE_CURRENT="bookworm"\n',
                encoding="utf-8",
            )
            (right / "external/config/boards/orangepizero3w.conf").write_text(
                'BOARDFAMILY="sun60iw2"\nMODULES="pvrsrvkm aic8800_fdrv"\nBOOT_FDT_FILE="allwinner/orangepi-zero-3w.dtb"\n',
                encoding="utf-8",
            )
            (right / "external/config/sources/families/sun60iw2.conf").write_text(
                'DISTRIB_TYPE_CURRENT="bookworm jammy"\n',
                encoding="utf-8",
            )

            report = build_report(left, right, "Radxa A7Z", "Orange Pi Zero 3W")

            self.assertIn("# A733 Source Comparison", report)
            self.assertIn("Radxa A7Z", report)
            self.assertIn("Orange Pi Zero 3W", report)
            self.assertIn("BOOT_FDT_FILE", report)
            self.assertIn("MODULES", report)
            self.assertIn("DISTRIB_TYPE_CURRENT", report)

    def test_validate_tree_reports_missing_minimum_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tree"
            (root / "external/config/boards").mkdir(parents=True)
            (root / "external/config/sources/families").mkdir(parents=True)
            (root / "external/config/boards/radxa-a7z.conf").write_text(
                'BOARDFAMILY="sun60iw2"\nMODULES="pvrsrvkm"\n',
                encoding="utf-8",
            )

            result = validate_tree(root)

            self.assertFalse(result["ok"])
            self.assertIn("family config", "\n".join(result["missing"]))
            self.assertIn("dts files", "\n".join(result["missing"]))
            self.assertIn("radxa-a7z.conf", result["present"][0])

    def test_validate_tree_accepts_minimal_supported_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tree"
            (root / "external/config/boards").mkdir(parents=True)
            (root / "external/config/sources/families").mkdir(parents=True)
            (root / "arch/arm64/boot/dts/allwinner").mkdir(parents=True)
            (root / "external/config/boards/radxa-a7z.conf").write_text(
                'BOARDFAMILY="sun60iw2"\nMODULES="pvrsrvkm"\nBOOT_FDT_FILE="allwinner/sun60i-a733-radxa-a7z.dtb"\n',
                encoding="utf-8",
            )
            (root / "external/config/sources/families/sun60iw2.conf").write_text(
                'DISTRIB_TYPE_CURRENT="bookworm"\n',
                encoding="utf-8",
            )
            (root / "arch/arm64/boot/dts/allwinner/sun60i-a733-radxa-a7z.dts").write_text(
                "/dts-v1/;\n",
                encoding="utf-8",
            )

            result = validate_tree(root)

            self.assertTrue(result["ok"])
            self.assertEqual(result["missing"], [])
            self.assertIn("radxa-a7z.conf", "\n".join(result["present"]))


if __name__ == "__main__":
    unittest.main()
