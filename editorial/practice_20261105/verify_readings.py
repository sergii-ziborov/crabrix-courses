#!/usr/bin/env python3
"""Compile and execute every new reading's complete example, with real crates."""
import json
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
UNITS = {"projects": ["files-data", "reliability-labs"], "ownership": ["api-boundaries"],
         "concurrency": ["async-operations"], "systems": ["wasm-wasi"]}


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="crabrix-readings-") as temp:
        folder = Path(temp)
        (folder / "src/bin").mkdir(parents=True)
        (folder / "src/main.rs").write_text("fn main() {}")
        (folder / "Cargo.toml").write_text('[package]\nname="crabrix-reading-check"\nversion="0.1.0"\nedition="2024"\n[dependencies]\nserde="=1.0.229"\nserde_json="=1.0.151"\ntokio={version="=1.54.1",default-features=false,features=["rt","sync"]}\n')
        subprocess.run(["cargo", "generate-lockfile", "--offline"], cwd=folder, check=True)
        for course, units in UNITS.items():
            for uid in units:
                unit = json.loads((ROOT / "courses" / course / "units" / (uid + ".json")).read_text())
                for lid in unit["lessonIDs"]:
                    lesson = json.loads((ROOT / "courses" / course / "lessons" / (lid + ".json")).read_text())
                    source = lesson["writing"]["exampleCode"]
                    # Only the host test adapts the example's granted guest path.
                    # The installed native test retains /sandbox verbatim.
                    source = source.replace('/sandbox/report.txt', str(folder / 'report.txt'))
                    (folder / "src/bin" / (lid + ".rs")).write_text(source)
                    result = subprocess.run(["cargo", "run", "--offline", "--locked", "--quiet", "--bin", lid],
                                            cwd=folder, capture_output=True, text=True, timeout=180)
                    record = {"id": lid, "passed": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
                    results.append(record)
                    assert record["passed"], record
                    print(lid, "passed", flush=True)
        (BASE / "Cargo.lock").write_bytes((folder / "Cargo.lock").read_bytes())
    (BASE / "reading-verification.json").write_text(json.dumps({"checks": results}, indent=2) + "\n")


if __name__ == "__main__":
    main()
