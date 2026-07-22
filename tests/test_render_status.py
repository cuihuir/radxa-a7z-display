import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tools.render_status import (
    build_outputs,
    load_status,
    render_baseline_table,
    render_capability_table,
    replace_generated_block,
)


class RenderStatusTests(unittest.TestCase):
    def test_current_status_source_has_unique_supported_capabilities(self) -> None:
        data = load_status()

        self.assertGreater(len(data["capabilities"]), 10)
        self.assertEqual(date.fromisoformat(data["snapshot_date"]).isoformat(), data["snapshot_date"])

    def test_table_uses_localized_status_labels(self) -> None:
        data = load_status()

        english = render_capability_table(data, "en")
        chinese = render_capability_table(data, "zh")

        self.assertIn("✅ Working (first port)", english)
        self.assertIn("PowerVR-accelerated KWin", english)
        self.assertIn("✅ 第一版已解决", chinese)
        self.assertIn("PowerVR 加速的 KWin", chinese)

    def test_baseline_is_localized_from_the_same_source(self) -> None:
        data = load_status()

        self.assertIn("vendor fallback on `l1`", render_baseline_table(data, "en"))
        self.assertIn("early-fsck recovery on `a7z-recovery`", render_baseline_table(data, "en"))
        self.assertIn("原厂回退使用 `l1`", render_baseline_table(data, "zh"))
        self.assertIn("早期 fsck 恢复使用 `a7z-recovery`", render_baseline_table(data, "zh"))

    def test_unknown_status_is_rejected(self) -> None:
        data = json.loads(Path("docs/status.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["status"] = "mystery"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown status"):
                load_status(path)

    def test_generated_block_replacement_preserves_surrounding_text(self) -> None:
        text = "before\n<!-- start -->\nold\n<!-- end -->\nafter\n"

        rendered = replace_generated_block(text, "<!-- start -->", "<!-- end -->", "new")

        self.assertEqual(rendered, "before\n<!-- start -->\nnew\n<!-- end -->\nafter\n")

    def test_generated_status_documents_are_current(self) -> None:
        for path, expected in build_outputs().items():
            self.assertEqual(path.read_text(encoding="utf-8"), expected, str(path))


if __name__ == "__main__":
    unittest.main()
