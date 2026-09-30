#!/usr/bin/env python3
"""Privileged offline signing step. Reads an Ed25519 seed from a local file."""
import argparse
import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

DESCRIPTOR_DOMAIN = b"Crabrix.CourseDescriptor.v1\n"
CATALOG_DOMAIN = b"Crabrix.CourseCatalog.v1\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("descriptor", "catalog"), required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--allow-test-key", action="store_true")
    args = parser.parse_args()
    if args.key_id.startswith("test-") and not args.allow_test_key:
        parser.error("test key requires --allow-test-key; never publish it as production")
    seed = args.key_file.read_bytes()
    if len(seed) != 32:
        parser.error("Ed25519 seed file must contain exactly 32 raw bytes")
    payload = args.payload.read_bytes()
    domain = DESCRIPTOR_DOMAIN if args.kind == "descriptor" else CATALOG_DOMAIN
    signature = Ed25519PrivateKey.from_private_bytes(seed).sign(domain + payload)
    envelope = {"keyID": args.key_id,
                "payloadBase64": base64.b64encode(payload).decode("ascii"),
                "signatureBase64": base64.b64encode(signature).decode("ascii")}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(envelope, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
