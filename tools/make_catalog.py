#!/usr/bin/env python3
"""Assemble immutable descriptor references before the privileged signing step."""
import argparse
import hashlib
import json
from pathlib import Path

from coursepack import CATALOG_DOMAIN, DESCRIPTOR_DOMAIN, verify_signature


def version(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"contentVersion must have three numeric parts: {value}")
    return tuple(map(int, parts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--sequence", type=int, required=True)
    parser.add_argument("--release-notes", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--previous-catalog", type=Path,
                        help="Carry unchanged courses from a verified signed catalog")
    parser.add_argument("--keys", type=Path,
                        help="Public keyring; required with --previous-catalog")
    args = parser.parse_args()
    if args.sequence < 1 or not args.base_url.startswith("https://"):
        parser.error("positive sequence and HTTPS base URL required")
    if args.previous_catalog and not args.keys:
        parser.error("--keys is required with --previous-catalog")
    base = args.base_url.rstrip("/")
    previous = {}
    keyring = json.loads(args.keys.read_text(encoding="utf-8")) if args.keys else None
    if args.previous_catalog:
        envelope = json.loads(args.previous_catalog.read_text(encoding="utf-8"))
        payload = verify_signature(envelope, CATALOG_DOMAIN, keyring)
        accepted = json.loads(payload)
        if args.sequence <= accepted["sequence"]:
            parser.error("catalog sequence must increase")
        previous = {(entry["courseID"], entry["language"]): entry
                    for entry in accepted["courses"]}
        if len(previous) != len(accepted["courses"]):
            parser.error("previous catalog has duplicate course identities")
    courses = dict(previous)
    identities = set()
    for path in sorted(args.dist.glob("*.descriptor.json")):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        payload = (verify_signature(envelope, DESCRIPTOR_DOMAIN, keyring)
                   if keyring else __import__("base64").b64decode(
                       envelope["payloadBase64"], validate=True))
        descriptor = json.loads(payload)
        identity = (descriptor["courseID"], descriptor["language"], descriptor["contentVersion"])
        if identity in identities:
            parser.error(f"duplicate course identity: {identity}")
        identities.add(identity)
        key = (descriptor["courseID"], descriptor["language"])
        if key in previous and version(descriptor["contentVersion"]) <= version(previous[key]["contentVersion"]):
            parser.error(f"new content version required for {key[0]} ({previous[key]['contentVersion']})")
        courses[key] = {"courseID": descriptor["courseID"], "language": descriptor["language"],
                        "contentVersion": descriptor["contentVersion"],
                        "descriptorURL": f"{base}/{path.name}",
                        "descriptorSHA256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "archiveURL": f"{base}/{descriptor['archiveName']}",
                        "archiveSHA256": descriptor["archiveSHA256"],
                        "archiveBytes": descriptor["archiveBytes"],
                        "minimumAppVersion": descriptor["minimumAppVersion"],
                        "requiredCapabilities": descriptor["requiredCapabilities"]}
    if not courses:
        parser.error("no signed descriptors found")
    catalog = {"schemaVersion": 1, "sequence": args.sequence,
               "releaseNotes": args.release_notes,
               "courses": [courses[key] for key in sorted(courses)]}
    args.out.write_text(json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
