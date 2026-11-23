#!/usr/bin/env python3
"""Check the code claims of basics/what-is-rust with rustc 1.89.0 and 1.100.0."""
import json, subprocess, tempfile
from pathlib import Path
lesson = json.loads((Path(__file__).resolve().parents[2] / "courses/basics/lessons/what-is-rust.json").read_text())
example = lesson["writing"]["exampleCode"]
cases = {"example": (example, "run", "area = 12\n"),
         "practice": (lesson["writing"]["practiceCode"], "error", "E0308"),
         "transfer": (example.replace("area(4, 3)", "area(4, -3)"), "error", "E0600")}
for toolchain in ("1.89.0", "1.100.0"):
    rustc = Path.home() / f".rustup/toolchains/{toolchain}-aarch64-apple-darwin/bin/rustc"
    with tempfile.TemporaryDirectory() as tmp:
        for name, (code, kind, expected) in cases.items():
            source = Path(tmp) / f"{name}.rs"; source.write_text(code)
            built = subprocess.run([rustc, "--edition=2024", "-o", Path(tmp) / name, source], capture_output=True, text=True)
            if kind == "run":
                assert built.returncode == 0 and not built.stderr, built.stderr
                out = subprocess.run([Path(tmp) / name], capture_output=True, text=True).stdout
                assert out == expected, out
            else:
                assert built.returncode != 0 and f"error[{expected}]" in built.stderr, built.stderr
            print("ok", toolchain, name)
