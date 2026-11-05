#!/usr/bin/env python3
"""Execute reference, wrong-result, unchanged, and forged-verdict submissions."""
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def run(source, harness, folder):
    (folder / "solution.rs").write_text(source)
    (folder / "main.rs").write_text(harness)
    built = subprocess.run(["rustc", "--edition=2024", "main.rs", "-o", "run"], cwd=folder,
                           capture_output=True, text=True, timeout=30)
    if built.returncode:
        return {"compiled": False, "passed": False, "stderr": built.stderr}
    ran = subprocess.run([str(folder / "run")], cwd=folder, capture_output=True, text=True, timeout=10)
    expected = harness.split('println!("')[-1].split('");')[0] + "\n"
    return {"compiled": True, "passed": ran.returncode == 0 and ran.stdout == expected,
            "exitCode": ran.returncode, "stdout": ran.stdout, "stderr": ran.stderr}


def main():
    labs = json.loads((BASE / "lab-references.json").read_text())
    results = []
    for item in labs:
        with tempfile.TemporaryDirectory(prefix="crabrix-lab-") as temp:
            folder = Path(temp)
            # Match the app's private-verdict property: a submission cannot print
            # the public PASS text and exit before assertions finish.
            public = item["expectedOutput"].strip()
            private = public + " verifier-private-nonce"
            harness = item["harness"].replace('println!("' + public + '");', 'println!("' + private + '");')
            prefix = item["source"].split(item["signature"])[0]
            wrong = prefix + item["signature"] + " { " + item["mutant"] + " }\n"
            forged = prefix + item["signature"] + ' { println!("' + public + '"); std::process::exit(0); }\n'
            contract = {key: item[key] for key in ["source", "starter", "harness", "mutant"]}
            record = {"id": item["id"], "contractSHA256": hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest(), "reference": run(item["source"], harness, folder),
                      "unchanged": run(item["starter"], harness, folder),
                      "wrong": run(wrong, harness, folder), "forgedVerdict": run(forged, harness, folder)}
            results.append(record)
            assert record["reference"]["passed"], record
            for key in ["unchanged", "wrong", "forgedVerdict"]:
                assert record[key]["compiled"] and not record[key]["passed"], (item["id"], key, record[key])
            print(item["id"], "reference passed; unchanged/wrong/forged rejected", flush=True)
    (BASE / "verification.json").write_text(json.dumps({"compiler": subprocess.check_output(["rustc", "--version"], text=True).strip(),
                                                      "labs": results}, indent=2) + "\n")


if __name__ == "__main__":
    main()
