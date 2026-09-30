#!/usr/bin/env python3
"""Assemble immutable descriptor references before the privileged signing step."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--sequence", type=int, required=True)
    parser.add_argument("--release-notes", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.sequence < 1 or not args.base_url.startswith("https://"):
        parser.error("positive sequence and HTTPS base URL required")
    base = args.base_url.rstrip("/")
    courses = []
    identities = set()
    for path in sorted(args.dist.glob("*.descriptor.json")):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        payload = __import__("base64").b64decode(envelope["payloadBase64"], validate=True)
        descriptor = json.loads(payload)
        identity = (descriptor["courseID"], descriptor["language"], descriptor["contentVersion"])
        if identity in identities:
            parser.error(f"duplicate course identity: {identity}")
        identities.add(identity)
        courses.append({"courseID": descriptor["courseID"], "language": descriptor["language"],
                        "contentVersion": descriptor["contentVersion"],
                        "descriptorURL": f"{base}/{path.name}",
                        "descriptorSHA256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "archiveURL": f"{base}/{descriptor['archiveName']}",
                        "archiveSHA256": descriptor["archiveSHA256"],
                        "archiveBytes": descriptor["archiveBytes"],
                        "minimumAppVersion": descriptor["minimumAppVersion"],
                        "requiredCapabilities": descriptor["requiredCapabilities"]})
    if not courses:
        parser.error("no signed descriptors found")
    catalog = {"schemaVersion": 1, "sequence": args.sequence,
               "releaseNotes": args.release_notes, "courses": courses}
    args.out.write_text(json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
