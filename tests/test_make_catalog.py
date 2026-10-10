import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
KEY_ID = "test-2026-09"
KEY = Ed25519PrivateKey.from_private_bytes(
    (ROOT / "tests/keys/test-publisher.seed").read_bytes()
)


def signed(payload, domain):
    data = json.dumps(payload, sort_keys=True).encode()
    return {
        "keyID": KEY_ID,
        "payloadBase64": base64.b64encode(data).decode(),
        "signatureBase64": base64.b64encode(KEY.sign(domain + data)).decode(),
    }


class IncrementalCatalogTests(unittest.TestCase):
    def test_revised_old_lesson_replaces_only_its_course(self):
        old_basics = {"courseID": "basics", "language": "en", "contentVersion": "1.0.2",
                      "archiveSHA256": "a" * 64}
        other = {"courseID": "algorithms", "language": "en", "contentVersion": "1.0.2",
                 "archiveSHA256": "b" * 64}
        old_catalog = {"schemaVersion": 1, "sequence": 6,
                       "courses": [old_basics, other]}
        descriptor = {"courseID": "basics", "language": "en", "contentVersion": "1.0.3",
                      "archiveName": "basics-1.0.3.zip", "archiveSHA256": "c" * 64,
                      "archiveBytes": 1234, "minimumAppVersion": "1.1",
                      "requiredCapabilities": ["coursepack-v1"]}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dist = root / "dist"
            dist.mkdir()
            (root / "previous.json").write_text(json.dumps(signed(
                old_catalog, b"Crabrix.CourseCatalog.v1\n")))
            (dist / "basics.descriptor.json").write_text(json.dumps(signed(
                descriptor, b"Crabrix.CourseDescriptor.v1\n")))
            command = ["python3", str(ROOT / "tools/make_catalog.py"),
                       "--dist", str(dist), "--base-url", "https://example.test/v2",
                       "--sequence", "7", "--release-notes", "Better first lesson",
                       "--out", str(root / "next.json"),
                       "--previous-catalog", str(root / "previous.json"),
                       "--keys", str(ROOT / "tests/keys/test-keyring.json")]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            updated = json.loads((root / "next.json").read_text())
            self.assertEqual(updated["sequence"], 7)
            self.assertEqual(len(updated["courses"]), 2)
            self.assertEqual(updated["courses"][0], other)
            self.assertEqual(updated["courses"][1]["contentVersion"], "1.0.3")
            self.assertEqual(updated["courses"][1]["archiveURL"],
                             "https://example.test/v2/basics-1.0.3.zip")

            descriptor["contentVersion"] = "1.0.2"
            (dist / "basics.descriptor.json").write_text(json.dumps(signed(
                descriptor, b"Crabrix.CourseDescriptor.v1\n")))
            rejected = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("new content version required", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
