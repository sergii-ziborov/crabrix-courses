#!/usr/bin/env python3
"""Attach the authored infographic metadata after ImageGen assets are copied in."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--version", required=True, help="New Examples content version")
    parser.add_argument("--revision", help="Description of this content revision")
    args = parser.parse_args()
    root = args.root / "courses/examples"
    prompts = json.loads((args.root / "artwork/examples/imagegen-prompts.json").read_text())
    for spec in prompts["examples"]:
        image = root / "media" / f"{spec['id']}.png"
        if not image.is_file():
            raise ValueError(f"Missing final ImageGen asset: {image}")
        path = root / "library-projects" / spec["id"] / "project.json"
        project = json.loads(path.read_text())
        illustration = {"path": f"media/{spec['id']}.png", "alt": spec["alt"], "caption": spec["caption"]}
        if project.get("illustration") != illustration:
            project["illustration"] = illustration
            path.write_text(json.dumps(project, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    for path in (root / "library-projects").glob("*/project.json"):
        if not json.loads(path.read_text()).get("illustration"):
            raise ValueError(f"Unillustrated example: {path.parent.name}")
    # Bind every authored example, README and infographic to this editorial version.
    files = sorted(p for folder in ("library-projects", "media") for p in (root / folder).rglob("*") if p.is_file())
    lines = [p.relative_to(root).as_posix() + "\0" + hashlib.sha256(p.read_bytes()).hexdigest() + "\n" for p in files]
    digest = hashlib.sha256("".join(lines).encode()).hexdigest()
    for name in ("course.json", "provenance.json"):
        path = root / name
        value = json.loads(path.read_text())
        value["contentVersion"] = args.version
        value["contentDigest" if name == "course.json" else "editorialDigest"] = digest
        if name == "provenance.json" and args.revision:
            value["editorialRevision"] = args.revision
        path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(f"Examples {args.version}: all 46 illustrations attached; editorial digest", digest)


if __name__ == "__main__":
    main()
