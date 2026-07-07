import tempfile
import unittest
from pathlib import Path

from tools.a7z_debian12_report import build_report


class A7zDebian12ReportTests(unittest.TestCase):
    def test_report_includes_radxa_a733_trixie_and_kmscon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "rsdk/src/share/rsdk/configs").mkdir(parents=True)
            (root / "rsdk/src/share/rsdk/build/mod/packages").mkdir(parents=True)
            (root / "rsdk/src/share/rsdk/build/mod/packages/categories").mkdir(parents=True)
            (root / "rsdk/src/share/rsdk/configs/products.json").write_text(
                '{"product":"radxa-a733","supported_suite":["trixie"],"supported_edition":["kde","cli"]}',
                encoding="utf-8",
            )
            (root / "rsdk/src/share/rsdk/configs/socs.json").write_text(
                '[{"soc_family":"allwinner","soc_list":["a733"],"soc_install_recommends":["bullseye","trixie"]}]',
                encoding="utf-8",
            )
            (root / "rsdk/src/share/rsdk/build/mod/packages/kde.libjsonnet").write_text(
                'if std.contains(product_soc_array(product), "a733") then ["libqt5gui5-gles"] else []\n'
                '// a733 GPU driver does not support GDM for now\n',
                encoding="utf-8",
            )
            (root / "rsdk/src/share/rsdk/build/mod/packages/categories/core.libjsonnet").write_text(
                'if suite == "trixie" && std.contains(product_soc_array(product), "a733") then ["kmscon", "libtsm4/trixie-backports"] else []\n',
                encoding="utf-8",
            )

            report = build_report(root / "rsdk", root / "orangepi-build")

            self.assertIn("Radxa", report)
            self.assertIn("trixie", report)
            self.assertIn("kmscon", report)
            self.assertIn("GDM", report)

    def test_report_includes_orangepi_a733_bookworm_and_pvrsrvkm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "orangepi-build/external/config/boards").mkdir(parents=True)
            (root / "orangepi-build/external/config/sources/families").mkdir(parents=True)
            (root / "orangepi-build/external/config/boards/orangepi4pro.conf").write_text(
                'BOARDFAMILY="sun60iw2"\nBOOT_FDT_FILE="allwinner/sun60i-a733-orangepi-4-pro.dtb"\nMODULES="aic8800_fdrv aic8800_btlpm pvrsrvkm"\nDISTRIB_TYPE_CURRENT="bookworm jammy bullseye"\n',
                encoding="utf-8",
            )
            (root / "orangepi-build/external/config/sources/families/sun60iw2.conf").write_text(
                'LINUXFAMILY=sun60iw2\nif [[ "${BOARD}" =~ "orangepi4pro"|"orangepizero3w" ]]; then OVERLAY_PREFIX="sun60i-a733"; fi\n',
                encoding="utf-8",
            )
            (root / "orangepi-build/external/config/boards/orangepizero3w.conf").write_text(
                'BOARDFAMILY="sun60iw2"\nBOOT_FDT_FILE="allwinner/sun60i-a733-orangepi-zero3w.dtb"\nDISTRIB_TYPE_CURRENT="bookworm jammy bullseye"\n',
                encoding="utf-8",
            )

            report = build_report(root / "rsdk", root / "orangepi-build")

            self.assertIn("bookworm", report)
            self.assertIn("pvrsrvkm", report)
            self.assertIn("sun60i-a733", report)

    def test_report_flags_missing_builder_tree_as_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "rsdk/src/share/rsdk/configs").mkdir(parents=True)
            (root / "rsdk/src/share/rsdk/configs/products.json").write_text(
                '{"product":"radxa-a733","supported_suite":["trixie"],"supported_edition":["kde","cli"]}',
                encoding="utf-8",
            )

            report = build_report(root / "rsdk", root / "orangepi-build")

            self.assertIn("missing", report.lower())
            self.assertIn("Gap", report)


if __name__ == "__main__":
    unittest.main()
