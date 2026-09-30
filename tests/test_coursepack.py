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
        archive = ROOT / "dist/basics-1.0.0.zip"
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
                     "--last-sequence", "0")
        self.command("verify-catalog", "--catalog", catalog, "--keys", keys,
                     "--last-sequence", "1", ok=False)

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
