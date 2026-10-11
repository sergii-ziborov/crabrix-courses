"""Run the authored program: reproducibility, valid canvas and bounded placement."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "courses/examples/library-projects/constellation-generator/src/main.rs"


class ConstellationGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rustc = shutil.which("rustc")
        if cls.rustc is None:
            raise unittest.SkipTest("Host Rust is needed to run the authored example")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.debug = cls.compile("debug", SOURCE.read_text())
        cls.release = cls.compile("release", SOURCE.read_text(), optimized=True)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @classmethod
    def compile(cls, name, source, optimized=False):
        path = cls.root / f"{name}.rs"
        path.write_text(source)
        binary = cls.root / name
        command = [cls.rustc, "--edition=2024", "-D", "warnings", str(path), "-o", str(binary)]
        if optimized:
            command.append("-O")
        subprocess.run(command, check=True, capture_output=True, timeout=45)
        return binary

    def run_sky(self, binary):
        output = subprocess.check_output([str(binary)], text=True, timeout=5)
        records = [line.removeprefix("CRABRIX_CANVAS:") for line in output.splitlines()
                   if line.startswith("CRABRIX_CANVAS:")]
        self.assertEqual(len(records), 1)
        canvas = json.loads(records[0])
        self.assertEqual((canvas["width"], canvas["height"]), (64, 40))
        self.assertEqual(len(canvas["pixels"]), 64 * 40)
        self.assertEqual(len(canvas["palette"]), 10)
        self.assertTrue(all(re.fullmatch(r"#[0-9A-F]{6}", color) for color in canvas["palette"]))
        self.assertTrue(all(0 <= int(pixel, 16) < len(canvas["palette"]) for pixel in canvas["pixels"]))
        rows = [line for line in output.splitlines() if line.startswith("│")]
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(len(row[1:-1]) == 38 for row in rows))
        return output, canvas

    def test_same_seed_is_identical_in_debug_release_and_repeated_runs(self):
        first, canvas = self.run_sky(self.debug)
        self.assertEqual(first, self.run_sky(self.debug)[0])
        self.assertEqual(first, self.run_sky(self.release)[0])
        self.assertGreater(len(set(canvas["pixels"])), 1)
        self.assertIn("40 stars", first)

    def test_different_seed_changes_pixels_and_keeps_the_display_contract(self):
        variant = SOURCE.read_text().replace("const SEED: u32 = 0xC0FFEE;", "const SEED: u32 = 0x12345678;")
        self.assertNotEqual(variant, SOURCE.read_text())
        changed = self.compile("other_seed", variant)
        _, original = self.run_sky(self.debug)
        _, updated = self.run_sky(changed)
        self.assertNotEqual(original["pixels"], updated["pixels"])
        self.assertEqual(original["palette"], updated["palette"])

    def test_dense_sky_stops_retrying_and_reports_actual_placement(self):
        variant = SOURCE.read_text().replace("const STAR_COUNT: usize = 40;", "const STAR_COUNT: usize = 400;")
        self.assertNotEqual(variant, SOURCE.read_text())
        output, _ = self.run_sky(self.compile("dense", variant))
        count = int(re.search(r"^(\d+) stars", output, flags=re.MULTILINE)[1])
        self.assertGreater(count, 40)
        self.assertLess(count, 400)


if __name__ == "__main__":
    unittest.main()
