import base64
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CLI = ["python3", str(ROOT / "tools/coursepack.py")]


class CoursePackTests(unittest.TestCase):
    def command(self, *args, ok=True):
        result = subprocess.run(CLI + list(map(str, args)), cwd=ROOT, text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_full_parity(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "parity.json"
            self.command("parity", "--legacy", "migration/baseline-inventory.json",
                         "--packages", "dist", "--out", report)
            result = json.loads(report.read_text())
            self.assertTrue(result["passed"])
            self.assertEqual(result["totals"]["lessons"], 742)

    def test_build_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for directory in (a, b):
                self.command("build", "--courses", "courses", "--out", directory, "--deterministic")
            for path in Path(a).glob("*"):
                self.assertEqual(path.read_bytes(), (Path(b) / path.name).read_bytes(), path.name)

    def test_signed_archive_and_tamper(self):
        descriptor = ROOT / "dist/basics.descriptor.json"
        archive = ROOT / "dist/basics-1.0.1.zip"
        keys = ROOT / "keys/production-keyring.json"
        self.command("verify", "--descriptor", descriptor, "--archive", archive, "--keys", keys)
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary) / archive.name
            data = bytearray(archive.read_bytes())
            data[-1] ^= 1
            bad.write_bytes(data)
            self.command("verify", "--descriptor", descriptor, "--archive", bad,
                         "--keys", keys, ok=False)

    def test_catalog_rollback(self):
        catalog = ROOT / "catalog.v1.json"
        keys = ROOT / "keys/production-keyring.json"
        self.command("verify-catalog", "--catalog", catalog, "--keys", keys,
                     "--last-sequence", "4")
        self.command("verify-catalog", "--catalog", catalog, "--keys", keys,
                     "--last-sequence", "5", ok=False)

    def test_examples_are_separate_and_each_has_a_readme(self):
        with zipfile.ZipFile(ROOT / "dist/examples-1.0.2.zip") as archive:
            files = set(archive.namelist())
            ids = {path.split("/")[1] for path in files if path.startswith("library-projects/")}
            self.assertEqual(len(ids), 46)
            for example_id in ids:
                prefix = f"library-projects/{example_id}/"
                self.assertIn(prefix + "README.md", files)
                self.assertIn(prefix + "Cargo.toml", files)
                self.assertIn(prefix + "project.json", files)
                self.assertIn(b"## What to notice", archive.read(prefix + "README.md"))
                self.assertIn(b"## How it works", archive.read(prefix + "README.md"))
                self.assertGreaterEqual(len(archive.read(prefix + "README.md").split()), 140)
            self.assertEqual(
                {name for name in files if name.startswith("media/")},
                {f"media/{name}.png" for name in (
                    "ferris-pixel-art", "run-length-encoder", "maze-bfs", "mandelbrot-canvas")}
            )
        with zipfile.ZipFile(ROOT / "dist/projects-1.0.2.zip") as archive:
            self.assertFalse(any(name.startswith("library-projects/") for name in archive.namelist()))
        self.command("verify", "--descriptor", "dist/examples.descriptor.json",
                     "--archive", "dist/examples-1.0.2.zip",
                     "--keys", "keys/production-keyring.json")

    def test_signature_domain_separation(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        envelope = json.loads((ROOT / "dist/basics.descriptor.json").read_text())
        keys = json.loads((ROOT / "keys/production-keyring.json").read_text())
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(keys["keys"][envelope["keyID"]]))
        payload = base64.b64decode(envelope["payloadBase64"])
        signature = base64.b64decode(envelope["signatureBase64"])
        with self.assertRaises(Exception):
            key.verify(signature, b"Crabrix.CourseCatalog.v1\n" + payload)


if __name__ == "__main__":
    unittest.main()
