#!/usr/bin/env python3
"""Render the side-by-side comparison diagram for every bridge lesson.

A bridge lesson compares one habit from another language with the Rust
equivalent. The diagram shows both sources exactly as authored (wrapped, never
paraphrased) and the authored contrast rows, so the image can be regenerated
whenever the lesson text changes. Output is deterministic PNG.
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
PANE = "#0b223a"
EDGE = "#42617b"
WHITE = "#f3f8ff"
MUTED = "#a8c3d6"
MINT = "#71e3be"
CORAL = "#ff8582"
GOLD = "#ffce69"
WIDTH = 1800
PANE_WIDTH = 815
CODE_SIZE = 24
CODE_LEADING = 34
MAX_CODE_LINES = 44

KEYWORDS = {
    "rust": {"fn", "let", "mut", "if", "else", "for", "while", "loop", "match", "return", "use",
             "impl", "pub", "struct", "enum", "trait", "async", "await", "move", "mod", "where",
             "in", "as", "const", "static", "unsafe", "extern", "type", "dyn", "ref", "self", "Self"},
    "c": {"int", "char", "void", "unsigned", "signed", "long", "short", "float", "double", "struct",
          "union", "enum", "typedef", "const", "static", "extern", "if", "else", "for", "while", "do",
          "switch", "case", "default", "break", "continue", "return", "sizeof", "restrict",
          "size_t", "uint8_t", "uint32_t", "int32_t", "int64_t", "uint64_t", "bool", "#include",
          "#define", "NULL"},
    "javascript": {"const", "let", "var", "function", "return", "if", "else", "for", "of", "in",
                   "while", "new", "class", "extends", "async", "await", "throw", "try", "catch",
                   "finally", "import", "export", "from", "typeof", "instanceof", "null",
                   "undefined", "this", "switch", "case", "default", "break"},
}
KEYWORDS["typescript"] = KEYWORDS["javascript"] | {"type", "interface", "implements", "readonly",
                                                   "number", "string", "boolean", "unknown", "never",
                                                   "as", "keyof", "void"}
LITERALS = {"true", "false", "Some", "None", "Ok", "Err", "NULL", "null", "undefined", "NaN"}
TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`|#\w+|\b\d[\w.]*\b|\w+|[^\w\s"`]+|["`]|\s+')


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_lines(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words = re.sub(r"\s+", " ", value.strip()).split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=face) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def comment_masks(lines: list[str]) -> list[list[bool]]:
    """Per character: is it inside a // or /* */ comment? Strings are skipped."""
    masks: list[list[bool]] = []
    in_block = False
    for line in lines:
        mask = [False] * len(line)
        index, quote = 0, None
        while index < len(line):
            if in_block:
                mask[index] = True
                if line.startswith("*/", index):
                    mask[index + 1] = True
                    index, in_block = index + 2, False
                else:
                    index += 1
            elif quote:
                if line[index] == "\\":
                    index += 2
                    continue
                if line[index] == quote:
                    quote = None
                index += 1
            elif line[index] in '"`':
                quote = line[index]
                index += 1
            elif line.startswith("//", index):
                mask[index:] = [True] * (len(line) - index)
                break
            elif line.startswith("/*", index):
                mask[index] = mask[index + 1] = True
                index, in_block = index + 2, True
            else:
                index += 1
        masks.append(mask)
    return masks


def wrap_code(value: str, face: ImageFont.FreeTypeFont, width: int) -> list[tuple[str, list[bool]]]:
    """Wrap long lines with a ↳ continuation; every display line keeps its comment mask."""
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    source = [line.rstrip().replace("\t", "    ") for line in value.strip("\n").splitlines()]
    output: list[tuple[str, list[bool]]] = []
    for line, mask in zip(source, comment_masks(source)):
        indent = len(line) - len(line.lstrip(" "))
        prefix = ""
        remaining, remaining_mask = line, mask
        while measure.textlength(prefix + remaining, font=face) > width:
            split = len(remaining)
            while split > 1 and measure.textlength(prefix + remaining[:split], font=face) > width:
                split -= 1
            boundary = max((position + 1 for position, character in enumerate(remaining[:split])
                            if character in " ,;(" and position > 8), default=0)
            split = boundary or split
            chunk = remaining[:split].rstrip()
            output.append((prefix + chunk, [False] * len(prefix) + remaining_mask[:len(chunk)]))
            rest = remaining[split:]
            stripped = len(rest) - len(rest.lstrip())
            remaining, remaining_mask = rest[stripped:], remaining_mask[split + stripped:]
            prefix = " " * (indent + 2) + "↳ "
        output.append((prefix + remaining, [False] * len(prefix) + remaining_mask))
    if len(output) > MAX_CODE_LINES:
        output = output[:MAX_CODE_LINES - 1] + [("…", [False])]
    return output


def draw_code(draw: ImageDraw.ImageDraw, lines: list[tuple[str, list[bool]]], language: str, x: int, y: int) -> None:
    face = font(MONO, CODE_SIZE)
    keywords = KEYWORDS[language]
    for line, mask in lines:
        cursor = x
        runs: list[tuple[str, bool]] = []
        for character, is_comment in zip(line, mask):
            if runs and runs[-1][1] == is_comment:
                runs[-1] = (runs[-1][0] + character, is_comment)
            else:
                runs.append((character, is_comment))
        for text, is_comment in runs:
            for token in ([text] if is_comment else TOKENS.findall(text)):
                color = WHITE
                if is_comment or token == "↳":
                    color = MUTED
                elif token[:1] in {'"', "'", "`"} and len(token) > 1:
                    color = MINT
                elif re.fullmatch(r"\d[\w.]*", token) or token in LITERALS:
                    color = GOLD
                elif token in keywords:
                    color = CORAL
                draw.text((cursor, y), token, font=face, fill=color)
                cursor += draw.textlength(token, font=face)
        y += CODE_LEADING


def plain(text: str) -> str:
    return text.replace("`", "")


def render(lesson: dict, output: Path) -> None:
    bridge = lesson["bridge"]
    label = bridge["fromLabel"]
    language = bridge["from"]
    code_face = font(MONO, CODE_SIZE)
    inner = PANE_WIDTH - 70
    left = wrap_code(bridge["fromCode"], code_face, inner)
    right = wrap_code(lesson["writing"]["exampleCode"], code_face, inner)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    row_face = font(FONT, 27)
    rows = [(fit_lines(measure, plain(row["from"]), row_face, PANE_WIDTH - 90),
             fit_lines(measure, plain(row["rust"]), row_face, PANE_WIDTH - 90))
            for row in bridge["contrasts"]]

    pane_top = 330
    pane_bottom = pane_top + 95 + max(len(left), len(right)) * CODE_LEADING + 40
    contrast_top = pane_bottom + 60
    row_heights = [40 + max(len(a), len(b)) * 37 + 18 for a, b in rows]
    height = contrast_top + 80 + sum(row_heights) + 22 * len(rows) + 70

    image = Image.new("RGB", (WIDTH, height), BG)
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((28, 28, WIDTH - 28, height - 28), radius=42, outline="#31516a", width=3)
    pill = f"CRABRIX  /  {label.upper()}  →  RUST"
    pill_face = font(BOLD, 33)
    d.rounded_rectangle((74, 74, 74 + d.textlength(pill, font=pill_face) + 70, 140), radius=28, fill="#153954")
    d.text((109, 88), pill, font=pill_face, fill=MINT)
    title_face = font(BOLD, 62)
    title = lesson["title"]
    while d.textlength(title, font=title_face) > WIDTH - 170:
        title_face = font(BOLD, title_face.size - 2)
    d.text((80, 168), title, font=title_face, fill=WHITE)
    concept_face = font(FONT, 34)
    concept = fit_lines(d, plain(lesson["concept"]), concept_face, WIDTH - 170)[:1]
    d.text((82, 252), concept[0], font=concept_face, fill=MUTED)

    for index, (name, lines, lang, accent) in enumerate(
            ((label, left, language, CORAL), ("Rust", right, "rust", MINT))):
        x = 78 + index * (PANE_WIDTH + 14)
        d.rounded_rectangle((x, pane_top, x + PANE_WIDTH, pane_bottom), radius=26, fill=PANE,
                            outline=accent, width=3)
        d.text((x + 36, pane_top + 26), f"{'01' if index == 0 else '02'}  {name.upper()}",
               font=font(BOLD, 30), fill=accent)
        draw_code(d, lines, lang, x + 36, pane_top + 90)

    d.text((84, contrast_top + 8), "03  WHAT CHANGES", font=font(BOLD, 30), fill=GOLD)
    y = contrast_top + 80
    for (a, b), row_height in zip(rows, row_heights):
        for index, (lines, accent, name) in enumerate(((a, CORAL, label), (b, MINT, "Rust"))):
            x = 78 + index * (PANE_WIDTH + 14)
            d.rounded_rectangle((x, y, x + PANE_WIDTH, y + row_height), radius=22, fill=CARD,
                                outline=EDGE, width=2)
            d.text((x + 34, y + 14), name, font=font(BOLD, 22), fill=accent)
            line_y = y + 46
            for line in lines:
                d.text((x + 34, line_y), line, font=row_face, fill=WHITE)
                line_y += 37
        y += row_height + 22
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course", nargs="*", help="Bridge course IDs (default: every course with bridge lessons)")
    parser.add_argument("--courses", type=Path, default=ROOT)
    args = parser.parse_args()
    roots = [args.courses / name for name in args.course] if args.course else sorted(
        path for path in args.courses.iterdir() if (path / "course.json").is_file())
    count = 0
    for course in roots:
        for path in sorted((course / "lessons").glob("*.json")):
            lesson = json.loads(path.read_text(encoding="utf-8"))
            if "bridge" not in lesson:
                continue
            image_path = f"media/{lesson['id']}.png"
            render(lesson, course / image_path)
            label = lesson["bridge"]["fromLabel"]
            lesson["illustration"] = {
                "path": image_path,
                "alt": f"Side-by-side comparison: the {label} version on the left, the Rust version on the right, "
                       f"then {len(lesson['bridge']['contrasts'])} rows naming what changes.",
                "caption": f"{lesson['title']}: the same task in {label} and in Rust, with the differences that matter.",
            }
            path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            count += 1
    print(f"Rendered {count} bridge comparison diagrams")


if __name__ == "__main__":
    main()
