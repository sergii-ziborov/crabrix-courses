#!/usr/bin/env python3
"""Fill the Academy's illustration gaps without changing lesson identities.

Atlas lessons point to their existing, pattern-specific five-panel diagram. Other
lessons receive a compact, lesson-specific code → rule → observation diagram.
The latter are deterministic PNGs so code and technical text stay exact.
"""

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1] / "courses"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"
BG = "#08192d"
CARD = "#112b43"
WHITE = "#f3f8ff"
MUTED = "#a8c3d6"
MINT = "#71e3be"
CORAL = "#ff8582"
GOLD = "#ffce69"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_lines(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont,
              width: int, max_lines: int) -> list[str]:
    words = re.sub(r"\s+", " ", value.strip()).split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=face) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while draw.textlength(lines[-1] + "…", font=face) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines


def paragraph(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width: int,
              size: int, color: str, max_lines: int, leading: int = 1) -> int:
    face = font(FONT, size)
    for line in fit_lines(draw, text, face, width, max_lines):
        draw.text((x, y), line, font=face, fill=color)
        y += size + leading
    return y


def code_excerpt(value: str) -> list[str]:
    source = [line.rstrip() for line in value.splitlines()]
    while source and not source[0]:
        source.pop(0)
    face = font(MONO, 38)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    output: list[str] = []
    for line in source:
        remaining = line
        while measure.textlength(remaining, font=face) > 925:
            split = len(remaining)
            while split > 1 and measure.textlength(remaining[:split], font=face) > 925:
                split -= 1
            boundary = max((position + 1 for position, character in enumerate(remaining[:split])
                            if character in " ,;" and position > 8), default=0)
            if boundary:
                split = boundary
            output.append(remaining[:split])
            remaining = "↳ " + remaining[split:]
            if len(output) >= 11:
                break
        if len(output) >= 11:
            break
        output.append(remaining)
        if len(output) >= 11:
            break
    if len(output) < len(source) or len(output) >= 11:
        output = output[:11] + ["…"]
    return output


def draw_code(draw: ImageDraw.ImageDraw, value: str) -> None:
    face = font(MONO, 38)
    emoji_face = font("/System/Library/Fonts/Apple Color Emoji.ttc", 40)
    x, y = 125, 445
    max_width = 950
    for line in code_excerpt(value):
        if not line:
            y += 52
            continue
        visible = line
        cursor = x
        for token in re.findall(r'"(?:\\.|[^"\\])*"|\b(?:fn|let|mut|if|else|for|while|match|return|use|impl|pub|struct|enum|trait|async|await|move|true|false|Some|None|Ok|Err)\b|\b\d+\b|[^\w"\d]+|\w+', visible):
            color = WHITE
            if token.startswith('"'):
                color = MINT
            elif re.fullmatch(r'\d+', token):
                color = GOLD
            elif token in {'fn','let','mut','if','else','for','while','match','return','use','impl','pub','struct','enum','trait','async','await','move'}:
                color = CORAL
            elif token in {'true','false','Some','None','Ok','Err'}:
                color = GOLD
            for character in token:
                if ord(character) >= 0x1F000:
                    draw.text((cursor, y), character, font=emoji_face, embedded_color=True)
                    cursor += draw.textlength(character, font=emoji_face)
                else:
                    draw.text((cursor, y), character, font=face, fill=color)
                    cursor += draw.textlength(character, font=face)
        y += 59


def render_rust(lesson: dict, output: Path) -> None:
    code_lines = code_excerpt(lesson["writing"]["exampleCode"])
    code_bottom = max(675, 445 + len(code_lines) * 59 + 45)
    rule_top = code_bottom + 65
    observation_top = rule_top + 280
    height = observation_top + 295
    image = Image.new("RGB", (1200, height), BG)
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((28, 28, 1172, height - 28), radius=42, outline="#31516a", width=3)
    d.rounded_rectangle((74, 74, 1126, 144), radius=28, fill="#153954")
    d.text((107, 90), "CRABRIX  /  LESSON MAP", font=font(BOLD, 35), fill=MINT)
    title_face = font(BOLD, 66)
    title = lesson["title"]
    while d.textlength(title, font=title_face) > 1035:
        title_face = font(BOLD, title_face.size - 2)
    d.text((82, 177), title, font=title_face, fill=WHITE)
    concept = lesson["concept"]
    paragraph(d, concept, 85, 267, 1020, 37, MUTED, 2)

    d.rounded_rectangle((78, 350, 1122, code_bottom), radius=28, fill="#0b223a", outline="#42617b", width=3)
    d.text((122, 365), "01  CODE EXCERPT", font=font(BOLD, 32), fill=MINT)
    draw_code(d, lesson["writing"]["exampleCode"])

    d.line((600, code_bottom + 3, 600, rule_top - 28), fill=CORAL, width=7)
    d.polygon([(582, rule_top - 35), (618, rule_top - 35), (600, rule_top - 10)], fill=CORAL)
    d.rounded_rectangle((78, rule_top, 1122, rule_top + 230), radius=28, fill=CARD, outline=MINT, width=3)
    d.text((120, rule_top + 23), "02  THE RULE", font=font(BOLD, 31), fill=MINT)
    rule = lesson["writing"]["rule"]
    rule_size = 43
    while len(fit_lines(d, rule, font(FONT, rule_size), 955, 99)) > 3:
        rule_size -= 2
    paragraph(d, rule, 120, rule_top + 80, 955, rule_size, WHITE, 3, 7)

    d.line((600, rule_top + 234, 600, observation_top - 28), fill=CORAL, width=7)
    d.polygon([(582, observation_top - 35), (618, observation_top - 35), (600, observation_top - 10)], fill=CORAL)
    d.rounded_rectangle((78, observation_top, 1122, observation_top + 225), radius=28, fill=CARD, outline=CORAL, width=3)
    d.text((120, observation_top + 23), "03  WHAT IT SHOWS", font=font(BOLD, 31), fill=CORAL)
    evidence = lesson["writing"]["exampleCaption"]
    if evidence.strip().casefold() == lesson["writing"]["rule"].strip().casefold():
        evidence = lesson["depth"]["traceSteps"][-1]["detail"]
    paragraph(d, evidence, 120, observation_top + 80, 955, 40, WHITE, 3, 7)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true",
                        help="Regenerate the deterministic lesson maps after editing lesson text")
    args = parser.parse_args()
    count = 0
    refreshed = 0
    for course in sorted(ROOT.iterdir()):
        if not (course / "course.json").is_file() or course.name == "examples":
            continue
        if course.name == "algorithms":
            for unit_path in sorted((course / "units").glob("*.json")):
                unit = json.loads(unit_path.read_text())
                ids = unit["lessonIDs"]
                assert len(ids) == 30
                for index, lesson_id in enumerate(ids):
                    path = course / "lessons" / f"{lesson_id}.json"
                    lesson = json.loads(path.read_text())
                    if "illustration" in lesson:
                        continue
                    variant = "a" if index // 3 < 5 else "b"
                    panel = index // 3 % 5 + 1
                    title = lesson["algorithm"]["patternID"].replace("-", " ").title()
                    image_path = f"media/{unit['id']}-{variant}.png"
                    assert (course / image_path).is_file()
                    lesson["illustration"] = {
                        "path": image_path,
                        "alt": f"Five-panel {unit['title']} infographic; panel {panel} illustrates {title}.",
                        "caption": f"{title}: follow panel {panel} to see the operation, then trace this lesson's example.",
                    }
                    path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n")
                    count += 1
        else:
            for path in sorted((course / "lessons").glob("*.json")):
                lesson = json.loads(path.read_text())
                if "illustration" in lesson:
                    if args.refresh and lesson["illustration"]["alt"].startswith("Diagram for "):
                        render_rust(lesson, course / lesson["illustration"]["path"])
                        refreshed += 1
                    continue
                image_path = f"media/{lesson['id']}.png"
                render_rust(lesson, course / image_path)
                lesson["illustration"] = {
                    "path": image_path,
                    "alt": f"Diagram for {lesson['title']}: a Rust code example flows to the lesson rule and the key observation.",
                    "caption": lesson["writing"]["exampleCaption"],
                }
                path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n")
                count += 1
    lessons = [json.loads(path.read_text()) for path in ROOT.glob("*/lessons/*.json")]
    if len(lessons) != 742 or any(not lesson.get("illustration") for lesson in lessons):
        raise ValueError("Academy illustration coverage is incomplete")
    print(f"Filled {count} missing illustrations; refreshed {refreshed}; covered {len(lessons)} lessons")


if __name__ == "__main__":
    main()
