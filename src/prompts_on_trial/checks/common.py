"""Shared parts of the deterministic checks."""

from __future__ import annotations

import re
from dataclasses import dataclass

EM_DASH = "—"

MONTHS = (
    "january february march april may june july august september october november december"
).split()
MONTH_ABBR = [m[:3] for m in MONTHS]
_MONTH_ALT = "|".join(MONTHS + [m for m in MONTH_ABBR if m != "may"] + ["sept"])
MONTH = rf"(?:{_MONTH_ALT})\.?"

WORD = re.compile(r"[A-Za-z0-9À-ɏ]+(?:['’\-.,][A-Za-z0-9À-ɏ]+)*")
URL = re.compile(r"https?://[^\s)\]>|]+")


@dataclass(frozen=True)
class Result:
    check: str
    passed: bool
    detail: str = ""

    def __str__(self) -> str:
        return f"{self.check} {'PASS' if self.passed else 'FAIL'}{': ' + self.detail if self.detail else ''}"


def ok(check: str, detail: str = "") -> Result:
    return Result(check, True, detail)


def fail(check: str, detail: str) -> Result:
    return Result(check, False, detail)


def word_count(text: str) -> int:
    return len(WORD.findall(text))


def fold(text: str) -> str:
    return text.casefold()


def whole_word(term: str) -> re.Pattern[str]:
    """Case-folded whole-word pattern. Spaces in the term match any run of whitespace."""
    body = r"\s+".join(re.escape(part) for part in term.split())
    return re.compile(rf"(?<![\w-]){body}(?![\w-])", re.IGNORECASE)


def canary_hits(text: str, canaries: tuple[str, ...] | list[str]) -> list[str]:
    """REQ-003: case-folded substring search. A canary made of digits (and separators) only
    must not sit inside a longer number, so that `20` does not match the year 2023 (DEV-012)."""
    hits = []
    folded = fold(text)
    for c in canaries:
        if re.fullmatch(r"[\d,.]+", c):
            if re.search(rf"(?<![\d,.]){re.escape(c)}(?![\d]|[,.]\d)", folded):
                hits.append(c)
        elif fold(c) in folded:
            hits.append(c)
    return hits


def strip_urls(text: str) -> str:
    return URL.sub(" ", text)


def table_rows(block: str) -> list[list[str]]:
    """Body rows of the first markdown table in a block (header and separator dropped)."""
    rows: list[list[str]] = []
    seen_sep = False
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if seen_sep:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            seen_sep = True
            continue
        if seen_sep:
            rows.append(cells)
    return rows


def split_sections(text: str, pattern: re.Pattern[str]) -> list[tuple[str, str]]:
    """Split text at lines matching `pattern`. Returns (heading line, body) in order."""
    out: list[tuple[str, str]] = []
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        if pattern.match(line.strip()):
            if current is not None:
                out.append((current, "\n".join(buf)))
            current, buf = line.strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out.append((current, "\n".join(buf)))
    return out


def clean(cell: str) -> str:
    """A table cell or line without markdown emphasis."""
    return re.sub(r"[*_`]", "", cell).strip()
