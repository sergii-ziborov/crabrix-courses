#!/usr/bin/env python3
"""Deterministic overview diagram for the Basics lesson "What Rust Is"."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from complete_lesson_illustrations import BG, BOLD, CARD, CORAL, FONT, GOLD, MINT, MONO, MUTED, WHITE, font  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "courses/basics/media/what-is-rust.png"
W, H = 1600, 1640
image = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(image)
d.rounded_rectangle((28, 28, W - 28, H - 28), radius=42, outline="#31516a", width=3)
d.rounded_rectangle((74, 74, 560, 140), radius=28, fill="#153954")
d.text((106, 88), "CRABRIX  /  WHAT RUST IS", font=font(BOLD, 33), fill=MINT)
d.text((80, 168), "What Rust Is", font=font(BOLD, 66), fill=WHITE)
d.text((82, 254), "Compiled ahead of time, statically typed, no garbage collector", font=font(FONT, 36), fill=MUTED)


def centered(box, lines, faces, colors, gap=8):
    x0, y0, x1, y1 = box
    heights = [face.size for face in faces]
    total = sum(heights) + gap * (len(lines) - 1)
    y = y0 + (y1 - y0 - total) / 2
    for line, face, color, height in zip(lines, faces, colors, heights):
        d.text(((x0 + x1) / 2 - d.textlength(line, font=face) / 2, y), line, font=face, fill=color)
        y += height + gap


def arrow(x0, y, x1, color=CORAL):
    d.line((x0, y, x1 - 16, y), fill=color, width=6)
    d.polygon([(x1 - 22, y - 13), (x1, y), (x1 - 22, y + 13)], fill=color)


# 01 build, then run
d.text((84, 340), "01  BUILD FIRST, THEN RUN", font=font(BOLD, 31), fill=MINT)
boxes = [(80, 400, 380, 580), (440, 400, 800, 580), (860, 400, 1160, 580), (1220, 400, 1520, 580)]
content = [
    (["main.rs", "your source"], [font(MONO, 34), font(FONT, 28)], [WHITE, MUTED]),
    (["rustc checks", "types, ownership,", "borrowing"], [font(BOLD, 32), font(FONT, 28), font(FONT, 28)], [MINT, WHITE, WHITE]),
    (["LLVM", "machine code", "or WebAssembly"], [font(BOLD, 32), font(FONT, 28), font(FONT, 28)], [WHITE, WHITE, WHITE]),
    (["Your program", "runs on its own"], [font(BOLD, 32), font(FONT, 28)], [WHITE, MUTED]),
]
for index, (box, (lines, faces, colors)) in enumerate(zip(boxes, content)):
    d.rounded_rectangle(box, radius=26, fill=CARD, outline=MINT if index == 1 else "#42617b", width=3)
    centered(box, lines, faces, colors)
for (a, b) in zip(boxes, boxes[1:]):
    arrow(a[2] + 6, 490, b[0] - 6)
d.line((620, 584, 620, 640), fill=CORAL, width=6)
d.polygon([(607, 634), (633, 634), (620, 656)], fill=CORAL)
d.rounded_rectangle((320, 660, 1280, 740), radius=22, fill="#2a1d2a", outline=CORAL, width=3)
centered((320, 660, 1280, 740), ["error[E0308]: mismatched types  →  nothing is built"], [font(MONO, 27)], [CORAL])

# 02 who frees memory
d.text((84, 800), "02  WHO FREES MEMORY", font=font(BOLD, 31), fill=MINT)
columns = [
    ((80, 860, 560, 1110), "C", ["you call free()", "forget it: a leak", "twice: undefined behaviour"], CORAL),
    ((600, 860, 1080, 1110), "JavaScript, Java, Go", ["a garbage collector,", "at a time it chooses,", "while the program runs"], GOLD),
    ((1120, 860, 1520, 1110), "Rust", ["the value's owner,", "when its scope ends,", "exactly once"], MINT),
]
for box, title, lines, color in columns:
    d.rounded_rectangle(box, radius=26, fill=CARD, outline=color, width=3)
    d.text((box[0] + 34, box[1] + 28), title, font=font(BOLD, 34), fill=color)
    y = box[1] + 96
    for line in lines:
        d.text((box[0] + 34, y), line, font=font(FONT, 30), fill=WHITE)
        y += 44

# 03 when mistakes show up
d.text((84, 1170), "03  WHEN A TYPE MISTAKE SHOWS UP", font=font(BOLD, 31), fill=MINT)
rows = [
    ("Python, JavaScript", "while running, when that line executes", GOLD, 1230),
    ("Rust", "while building, before the program exists", MINT, 1350),
]
for label, text, color, y in rows:
    d.rounded_rectangle((80, y, 1520, y + 96), radius=22, fill=CARD, outline=color, width=3)
    d.text((114, y + 28), label, font=font(BOLD, 34), fill=color)
    d.text((520, y + 30), text, font=font(FONT, 32), fill=WHITE)
d.text((84, 1500), "In Crabrix, rustc runs on your device: Run compiles first and executes only a program that passed.",
       font=font(FONT, 29), fill=MUTED)
image.save(OUT, format="PNG", optimize=True)
print(OUT, image.size)
