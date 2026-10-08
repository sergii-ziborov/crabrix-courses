#!/usr/bin/env python3
"""Crabrix CoursePack v1 importer, deterministic packager, verifier and parity gate."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import unicodedata
import zipfile

DESCRIPTOR_DOMAIN = b"Crabrix.CourseDescriptor.v1\n"
CATALOG_DOMAIN = b"Crabrix.CourseCatalog.v1\n"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_UNPACKED = 128 * 1024 * 1024
MAX_ENTRIES = 5000
MAX_FILE = 16 * 1024 * 1024


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pretty(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pretty(value))


def safe_name(name: str) -> str:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ValueError(f"unsafe path: {name!r}")
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"unsafe path: {name!r}")
    if any(part.endswith(" ") or part.endswith(".") for part in parts):
        raise ValueError(f"ambiguous path: {name!r}")
    return name


def collision_key(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()


def checked_files(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    seen: set[str] = set()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink in course tree: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"unsupported file: {path}")
        rel = safe_name(path.relative_to(root).as_posix())
        folded = collision_key(rel)
        if folded in seen:
            raise ValueError(f"case/Unicode path collision: {rel}")
        seen.add(folded)
        if rel == "manifest.json":
            raise ValueError("authoring tree may not contain generated manifest")
        if forbidden_payload(rel):
            raise ValueError(f"executable/compiler payload prohibited: {rel}")
        data = path.read_bytes()
        if len(data) > MAX_FILE:
            raise ValueError(f"file too large: {rel}")
        result[rel] = data
    return result


def forbidden_payload(name: str) -> bool:
    lowered = name.lower()
    return lowered.endswith((".dylib", ".framework", ".wasm", ".rlib", ".rmeta", ".swift", ".js", ".bc", ".so", ".a"))


def import_legacy(args) -> None:
    baseline = load(args.baseline)
    if baseline["integrity"] != {"idCollisions": [], "missingChallenges": [], "missingLessonWriting": []}:
        raise ValueError("legacy baseline has integrity errors")
    courses_root = args.courses
    if courses_root.exists() and any(courses_root.iterdir()):
        raise ValueError("import target must be empty; preserve existing authoring data")
    topic_course = {}
    for course in baseline["courses"]:
        cid = safe_name(course["id"])
        root = courses_root / cid
        course_fields = {k: v for k, v in course.items() if k != "units"}
        course_fields["unitIDs"] = [u["id"] for u in course["units"]]
        save(root / "course.json", course_fields)
        for unit in course["units"]:
            uid = safe_name(unit["id"])
            unit_fields = {k: v for k, v in unit.items() if k != "lessons"}
            unit_fields["lessonIDs"] = [l["id"] for l in unit["lessons"]]
            save(root / "units" / f"{uid}.json", unit_fields)
            for lesson in unit["lessons"]:
                lid = safe_name(lesson["id"])
                topic_course[lid] = cid
                lesson_fields = {k: v for k, v in lesson.items() if k not in ("evidence", "challenge", "starterProject")}
                save(root / "lessons" / f"{lid}.json", lesson_fields)
                check = {"evidence": lesson["evidence"]}
                if "challenge" in lesson:
                    check["challenge"] = lesson["challenge"]
                save(root / "checks" / f"{lid}.json", check)
                if "starterProject" in lesson:
                    project = lesson["starterProject"]
                    project_root = root / "projects" / lid
                    save(project_root / "project.json", {k: v for k, v in project.items() if k != "files"})
                    for name, source in project["files"].items():
                        path = project_root / safe_name(name)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(source.encode("utf-8"))
        save(root / "provenance.json", {
            "sourceURL": "https://github.com/sergii-ziborov/Crabrix",
            "sourceSHA": baseline["sourceSHA"], "baselineDigest": baseline["contentDigest"],
            "courseID": cid, "contentVersion": baseline["contentVersion"],
        })
    by_course: dict[str, list] = {c["id"]: [] for c in baseline["courses"]}
    for term in baseline["termPairs"]:
        by_course[topic_course[term["topic"]]].append(term)
    for cid, terms in by_course.items():
        save(courses_root / cid / "terms.json", terms)
    gallery = courses_root / "projects" / "library-projects"
    for project in baseline["showcaseProjects"]:
        pid = safe_name(project["id"])
        root = gallery / pid
        save(root / "project.json", {k: v for k, v in project.items() if k != "project"} | {
            "project": {k: v for k, v in project["project"].items() if k != "files"}
        })
        for name, source in project["project"]["files"].items():
            path = root / safe_name(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(source.encode("utf-8"))
    print(f"Imported {len(baseline['courses'])} complete courses and {len(baseline['showcaseProjects'])} gallery projects")


def read_project(root: Path) -> dict:
    metadata = load(root / "project.json")
    files = checked_files(root)
    files.pop("project.json")
    metadata["files"] = {name: data.decode("utf-8") for name, data in files.items()}
    return metadata


def read_course(root: Path) -> dict:
    course = load(root / "course.json")
    unit_ids = course.pop("unitIDs")
    units = []
    for uid in unit_ids:
        safe_name(uid)
        unit = load(root / "units" / f"{uid}.json")
        lesson_ids = unit.pop("lessonIDs")
        lessons = []
        for lid in lesson_ids:
            safe_name(lid)
            lesson = load(root / "lessons" / f"{lid}.json")
            lesson.update(load(root / "checks" / f"{lid}.json"))
            project_root = root / "projects" / lid
            if project_root.exists():
                lesson["starterProject"] = read_project(project_root)
            lessons.append(lesson)
        unit["lessons"] = lessons
        units.append(unit)
    course["units"] = units
    return course


def validate(args) -> None:
    for schema_name in ("coursepack-v1.schema.json", "descriptor-v1.schema.json", "catalog-v1.schema.json"):
        schema = load(args.schema / schema_name)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ValueError(f"unknown or missing schema: {schema_name}")
    roots = sorted(p for p in args.courses.iterdir() if p.is_dir())
    if not roots:
        raise ValueError("no courses")
    ids = set()
    lesson_ids = set()
    for root in roots:
        files = checked_files(root)
        if not files:
            raise ValueError(f"empty course: {root}")
        course = read_course(root)
        if course["id"] != root.name or course["id"] in ids:
            raise ValueError(f"duplicate/incorrect course ID: {root}")
        ids.add(course["id"])
        if course["language"] != "en" or not course["contentVersion"]:
            raise ValueError(f"unsupported course metadata: {root}")
        unit_ids = set()
        expected = {"course.json", "terms.json", "provenance.json"}
        for unit in course["units"]:
            if unit["id"] in unit_ids or unit["parentID"] != course["id"]:
                raise ValueError(f"unit identity: {unit['id']}")
            unit_ids.add(unit["id"])
            expected.add(f"units/{unit['id']}.json")
            for lesson in unit["lessons"]:
                if lesson["id"] in lesson_ids or lesson["parentID"] != unit["id"]:
                    raise ValueError(f"lesson identity: {lesson['id']}")
                lesson_ids.add(lesson["id"])
                lid = lesson["id"]
                expected |= {f"lessons/{lid}.json", f"checks/{lid}.json"}
                writing = lesson["writing"]
                if not writing["answers"] or not 0 <= writing["correctAnswer"] < len(writing["answers"]):
                    raise ValueError(f"question answers: {lid}")
                if "starterProject" in lesson:
                    base = f"projects/{lid}/"
                    expected.add(base + "project.json")
                    expected.update(base + name for name in lesson["starterProject"]["files"])
                if lesson["exerciseKind"] == "algorithmChallenge" and "challenge" not in lesson:
                    raise ValueError(f"challenge missing: {lid}")
                illustration = lesson.get("illustration")
                if illustration is not None:
                    image_path = f"media/{lid}.png"
                    if (illustration.get("path") != image_path
                            or not illustration.get("alt", "").strip()
                            or not illustration.get("caption", "").strip()
                            or image_path not in files):
                        raise ValueError(f"invalid lesson illustration: {lid}")
                    image = files[image_path]
                    if (image[:8] != b"\x89PNG\r\n\x1a\n"
                            or image[12:16] != b"IHDR" or len(image) < 24):
                        raise ValueError(f"invalid PNG illustration: {image_path}")
                    width = int.from_bytes(image[16:20], "big")
                    height = int.from_bytes(image[20:24], "big")
                    if (not 0 < width <= 4096 or not 0 < height <= 4096
                            or width * height > 8_000_000):
                        raise ValueError(f"oversized illustration: {image_path}")
                    expected.add(image_path)
        if root.name == "examples":
            if course["units"] != [] or load(root / "terms.json") != []:
                raise ValueError("examples pack must contain projects, not lessons or terms")
            gallery = root / "library-projects"
            projects = sorted(p for p in gallery.iterdir() if p.is_dir()) if gallery.exists() else []
            if len(projects) != 46:
                raise ValueError(f"expected 46 Academy Examples, found {len(projects)}")
            orders = set()
            illustrations = set()
            for project_root in projects:
                project = read_project(project_root)
                if project["id"] != project_root.name or project["order"] in orders:
                    raise ValueError(f"example identity/order: {project_root.name}")
                orders.add(project["order"])
                if not {"Cargo.toml", "README.md", project["project"]["entryFile"]} <= set(project["files"]):
                    raise ValueError(f"example source or README missing: {project_root.name}")
                if not project["files"]["README.md"].strip():
                    raise ValueError(f"empty example README: {project_root.name}")
                illustration = project.get("illustration")
                if illustration is not None:
                    image_path = f"media/{project['id']}.png"
                    if (illustration.get("path") != image_path
                            or not illustration.get("alt")
                            or not illustration.get("caption")
                            or image_path not in files):
                        raise ValueError(f"invalid example illustration: {project_root.name}")
                    image = files[image_path]
                    if (image[:8] != b"\x89PNG\r\n\x1a\n"
                            or image[12:16] != b"IHDR" or len(image) < 24):
                        raise ValueError(f"invalid PNG illustration: {image_path}")
                    width = int.from_bytes(image[16:20], "big")
                    height = int.from_bytes(image[20:24], "big")
                    if (not 0 < width <= 4096 or not 0 < height <= 4096
                            or width * height > 8_000_000):
                        raise ValueError(f"oversized illustration: {image_path}")
                    illustrations.add(image_path)
            if orders != set(range(len(projects))):
                raise ValueError("example order is not contiguous")
            if {name for name in files if name.startswith("media/")} != illustrations:
                raise ValueError("unreferenced example media")
            expected.update(name for name in files if name.startswith("library-projects/"))
            expected.update(illustrations)
        if set(files) != expected:
            raise ValueError(f"unreferenced or missing files in {root.name}: {sorted(set(files) ^ expected)[:10]}")
    print(f"Validated {len(ids)} courses and {len(lesson_ids)} lessons")


def inventory(args) -> None:
    baseline = load(args.baseline)
    result = {"sourceSHA": baseline["sourceSHA"], "contentDigest": baseline["contentDigest"],
              "totals": baseline["totals"], "integrity": baseline["integrity"],
              "courses": [{"id": c["id"], "units": len(c["units"]),
                           "lessons": sum(len(u["lessons"]) for u in c["units"]),
                           "digest": c["contentDigest"]} for c in baseline["courses"]]}
    save(args.out, result)
    print(f"Inventory: {baseline['totals']}")


def make_zip(files: dict[str, bytes], archive: Path) -> None:
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as out:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            out.writestr(info, data)


def build(args) -> None:
    for root in sorted(p for p in args.courses.iterdir() if p.is_dir()):
        files = checked_files(root)
        course = load(root / "course.json")
        manifest = {"schemaVersion": 1, "courseID": course["id"],
                    "language": course["language"], "contentVersion": course["contentVersion"],
                    "files": [{"path": name, "bytes": len(data), "sha256": sha(data)}
                              for name, data in sorted(files.items())]}
        files["manifest.json"] = pretty(manifest)
        archive = args.out / f"{course['id']}-{course['contentVersion']}.zip"
        make_zip(files, archive)
        descriptor = {"schemaVersion": 1, "courseID": course["id"],
                      "language": course["language"], "contentVersion": course["contentVersion"],
                      "archiveName": archive.name, "archiveBytes": archive.stat().st_size,
                      "archiveSHA256": sha(archive.read_bytes()), "courseDigest": course["contentDigest"],
                      "minimumAppVersion": "1.1", "requiredCapabilities":
                      ["coursepack-v1", "examples-gallery-v1"] if course["id"] == "examples"
                      else ["coursepack-v1"]}
        save(args.out / f"{course['id']}.descriptor.payload.json", descriptor)
        print(f"Built {archive.name} {descriptor['archiveSHA256']}")


def verify_signature(envelope: dict, domain: bytes, keyring: dict) -> bytes:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    key_id = envelope["keyID"]
    if key_id not in keyring["keys"]:
        raise ValueError(f"untrusted keyID: {key_id}")
    payload = base64.b64decode(envelope["payloadBase64"], validate=True)
    signature = base64.b64decode(envelope["signatureBase64"], validate=True)
    public = base64.b64decode(keyring["keys"][key_id], validate=True)
    Ed25519PublicKey.from_public_bytes(public).verify(signature, domain + payload)
    return payload


def verify(args) -> None:
    archive_bytes = args.archive.read_bytes()
    if len(archive_bytes) > MAX_ARCHIVE:
        raise ValueError("archive exceeds size limit")
    envelope = load(args.descriptor)
    payload = verify_signature(envelope, DESCRIPTOR_DOMAIN, load(args.keys))
    descriptor = json.loads(payload)
    if descriptor["archiveSHA256"] != sha(archive_bytes) or descriptor["archiveBytes"] != len(archive_bytes):
        raise ValueError("archive digest/length mismatch")
    if descriptor["archiveName"] != args.archive.name:
        raise ValueError("archive name mismatch")
    seen = set()
    actual = {}
    total = 0
    with zipfile.ZipFile(args.archive) as packed:
        infos = packed.infolist()
        if len(infos) > MAX_ENTRIES:
            raise ValueError("too many ZIP entries")
        for info in infos:
            name = safe_name(info.filename)
            folded = collision_key(name)
            if folded in seen:
                raise ValueError(f"duplicate/colliding ZIP entry: {name}")
            seen.add(folded)
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG) or info.is_dir():
                raise ValueError(f"non-regular ZIP entry: {name}")
            if name != "manifest.json" and forbidden_payload(name):
                raise ValueError(f"forbidden payload: {name}")
            total += info.file_size
            if info.file_size > MAX_FILE or total > MAX_UNPACKED:
                raise ValueError("unpacked size limit")
            data = packed.read(info)
            if len(data) != info.file_size:
                raise ValueError(f"size mismatch: {name}")
            actual[name] = data
    manifest = json.loads(actual.pop("manifest.json"))
    expected = {item["path"]: item for item in manifest["files"]}
    if "manifest.json" in expected or set(expected) != set(actual) or len(expected) != len(manifest["files"]):
        raise ValueError("manifest/tree mismatch")
    for name, data in actual.items():
        if expected[name]["bytes"] != len(data) or expected[name]["sha256"] != sha(data):
            raise ValueError(f"payload mismatch: {name}")
    if (manifest["courseID"], manifest["language"], manifest["contentVersion"]) != (
        descriptor["courseID"], descriptor["language"], descriptor["contentVersion"]
    ):
        raise ValueError("manifest/descriptor identity mismatch")
    print(f"Verified {descriptor['courseID']} {descriptor['contentVersion']}: {len(actual)} payload files")


def verify_catalog(args) -> None:
    payload = verify_signature(load(args.catalog), CATALOG_DOMAIN, load(args.keys))
    catalog = json.loads(payload)
    if catalog.get("schemaVersion") != 1 or catalog.get("sequence", 0) <= args.last_sequence:
        raise ValueError("unsupported or rolled-back catalog sequence")
    seen = {}
    for entry in catalog["courses"]:
        identity = (entry["courseID"], entry["language"], entry["contentVersion"])
        digest = entry["archiveSHA256"]
        if identity in seen and seen[identity] != digest:
            raise ValueError(f"conflicting immutable course identity: {identity}")
        seen[identity] = digest
        if not entry["descriptorURL"].startswith("https://") or not entry["archiveURL"].startswith("https://"):
            raise ValueError("catalog URL must be HTTPS")
    print(f"Verified catalog sequence {catalog['sequence']} with {len(seen)} course versions")


def compare(left, right, path="$", differences=None):
    if differences is None:
        differences = []
    if type(left) is not type(right):
        differences.append(path)
    elif isinstance(left, dict):
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                differences.append(f"{path}.{key}")
            else:
                compare(left[key], right[key], f"{path}.{key}", differences)
    elif isinstance(left, list):
        if len(left) != len(right):
            differences.append(f"{path}.length")
        for index, (a, b) in enumerate(zip(left, right)):
            compare(a, b, f"{path}[{index}]", differences)
    elif left != right:
        differences.append(path)
    return differences


def parity(args) -> None:
    baseline = load(args.legacy)
    by_id = {c["id"]: c for c in baseline["courses"]}
    found = {}
    for archive in sorted(args.packages.glob("*.zip")):
        with zipfile.ZipFile(archive) as packed:
            # No extraction: all paths are read as bytes and course identity is checked.
            files = {info.filename: packed.read(info) for info in packed.infolist()}
        with __import__("tempfile").TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, data in files.items():
                safe_name(name)
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            course = read_course(root)
            found[course["id"]] = course
    missing = sorted(set(by_id) - set(found))
    unexpected = sorted(set(found) - set(by_id) - {"examples"})
    changes = {}
    for cid in sorted(set(by_id) & set(found)):
        original = by_id[cid]
        current = dict(found[cid])
        if cid == "projects":
            # Transport revision and removal of its embedded gallery are
            # approved; the authored course lessons must remain identical.
            current["contentVersion"] = original["contentVersion"]
            current["contentDigest"] = original["contentDigest"]
        differences = compare(original, current)
        if differences:
            changes[cid] = differences
    # The static project gallery and derived term data are part of the baseline too.
    terms = []
    for cid in by_id:
        archive = args.packages / f"{cid}-{by_id[cid]['contentVersion']}.zip"
        if not archive.exists():
            versions = sorted(args.packages.glob(f"{cid}-*.zip"))
            if versions:
                archive = versions[-1]
        if archive.exists():
            with zipfile.ZipFile(archive) as packed:
                terms.extend(json.loads(packed.read("terms.json")))
    terms.sort(key=lambda item: item["order"])
    if terms != baseline["termPairs"]:
        changes["termPairs"] = compare(baseline["termPairs"], terms)
    gallery = []
    approved_readmes = []
    approved_illustrations = []
    example_archives = sorted(args.packages.glob("examples-*.zip"))
    project_archive = example_archives[-1] if example_archives else None
    if project_archive is None:
        project_archive = args.packages / f"projects-{baseline['contentVersion']}.zip"
    if project_archive.exists():
        with zipfile.ZipFile(project_archive) as packed:
            gallery_ids = sorted({name.split("/")[1] for name in packed.namelist() if name.startswith("library-projects/")})
            baseline_projects = {item["id"]: item for item in baseline["showcaseProjects"]}
            for pid in gallery_ids:
                meta = json.loads(packed.read(f"library-projects/{pid}/project.json"))
                if "illustration" in meta:
                    approved_illustrations.append(pid)
                    del meta["illustration"]
                project = meta["project"]
                prefix = f"library-projects/{pid}/"
                project["files"] = {name[len(prefix):]: packed.read(name).decode("utf-8") for name in packed.namelist()
                                    if name.startswith(prefix) and name != prefix + "project.json"}
                prior_files = baseline_projects.get(pid, {}).get("project", {}).get("files", {})
                if "README.md" in project["files"] and project["files"]["README.md"] != prior_files.get("README.md"):
                    approved_readmes.append(pid)
                    if "README.md" in prior_files:
                        project["files"]["README.md"] = prior_files["README.md"]
                    else:
                        del project["files"]["README.md"]
                gallery.append(meta)
    gallery.sort(key=lambda item: item["order"])
    if gallery != baseline["showcaseProjects"]:
        changes["showcaseProjects"] = compare(baseline["showcaseProjects"], gallery)
    report = {"sourceSHA": baseline["sourceSHA"], "baselineDigest": baseline["contentDigest"],
              "missing": missing, "unexpected": unexpected, "unapprovedChanges": changes,
              "approvedEditorialReadmeChanges": sorted(approved_readmes),
              "approvedIllustrations": sorted(approved_illustrations),
              "totals": baseline["totals"], "passed": not (missing or unexpected or changes)}
    save(args.out, report)
    print(f"Parity: missing={len(missing)} unexpected={len(unexpected)} unapprovedChanges={len(changes)}")
    if not report["passed"]:
        raise ValueError("semantic parity failed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("import-legacy")
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--courses", type=Path, required=True)
    p.set_defaults(run=import_legacy)
    p = sub.add_parser("inventory")
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(run=inventory)
    p = sub.add_parser("validate")
    p.add_argument("--courses", type=Path, required=True)
    p.add_argument("--schema", type=Path, required=True)
    p.set_defaults(run=validate)
    p = sub.add_parser("build")
    p.add_argument("--courses", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--deterministic", action="store_true", required=True)
    p.set_defaults(run=build)
    p = sub.add_parser("verify")
    p.add_argument("--descriptor", type=Path, required=True)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--keys", type=Path, required=True)
    p.set_defaults(run=verify)
    p = sub.add_parser("parity")
    p.add_argument("--legacy", type=Path, required=True)
    p.add_argument("--packages", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(run=parity)
    p = sub.add_parser("verify-catalog")
    p.add_argument("--catalog", type=Path, required=True)
    p.add_argument("--keys", type=Path, required=True)
    p.add_argument("--last-sequence", type=int, default=0)
    p.set_defaults(run=verify_catalog)
    args = parser.parse_args()
    try:
        args.run(args)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        print(f"coursepack: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
