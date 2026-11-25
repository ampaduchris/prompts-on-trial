"""Part A deterministic checks: CP-D1 to CP-D12 (spec section 3.2, REQ-010 to REQ-021)."""

from __future__ import annotations

import itertools
import re

from ..cases import History
from .common import EM_DASH, MONTH, Result, canary_hits, fail, fold, ok, whole_word, word_count

SECTIONS = [
    "1. How to use this",
    "2. Observed patterns",
    "3. Working method",
    "4. Communication preferences",
    "5. Retention and performance mechanisms",
    "6. Pressure protocols",
    "7. Background context",
    "8. What you could not determine",
    "9. Speculative patterns",
    "10. Validity",
]
LABELS = ["Claim", "Evidence", "Counter-evidence", "Confidence", "Cost", "Instruction for agents"]

HEADING = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
PATTERN_HEAD = re.compile(r"^\s*(?:>\s*)?\**\s*Pattern\s+(\d+)\s*:", re.IGNORECASE)
LABEL_LINE = re.compile(
    r"^\s*(?:>\s*)?(?:[-*]\s+)?\**\s*(" + "|".join(re.escape(x) for x in LABELS) + r")\s*\**\s*:\s*\**\s*(.*)$"
)
PATTERN_REF = re.compile(r"\bPattern\s+(\d+)\b")
# A date token is a month with a year, a month alone, a year alone, or an ISO year-month.
# A month followed by its year is one token, so "March 2025" counts once (DEV-011).
DATE_TOKEN = re.compile(
    rf"(?<![\w-])(?:{MONTH}\s+(?:\d{{1,2}},?\s+)?(?:19|20)\d{{2}}|(?:19|20)\d{{2}}-\d{{2}}(?:-\d{{2}})?|{MONTH}|(?:19|20)\d{{2}})(?![\w-])",
    re.IGNORECASE,
)
VALID_DATE = re.compile(
    rf"Valid as of\W*(?:\d{{1,2}}\s+{MONTH}\s+(?:19|20)\d{{2}}|{MONTH}\s+\d{{1,2}},?\s+(?:19|20)\d{{2}}"
    rf"|(?:19|20)\d{{2}}-\d{{2}}(?:-\d{{2}})?|{MONTH}\s+(?:19|20)\d{{2}})",
    re.IGNORECASE,
)

TYPE_CODES = ["".join(p) for p in itertools.product("IE", "NS", "TF", "JP")]
FRAMEWORK_TERMS = [
    "MBTI", "Myers-Briggs", *TYPE_CODES, "Big Five", "OCEAN model", "Enneagram", "attachment style",
    "learning style", "learning styles", "neurotype", "neurodivergent", "neurotypical", "ADHD",
    "autistic", "autism", "DISC profile", "StrengthsFinder", "CliftonStrengths", "introvert",
    "extrovert", "extravert",
]
MOTIVATIONAL = [
    "great job", "you've got this", "let's dive in", "unlock your potential", "superpower", "journey",
    "game changer",
]


def sections(text: str) -> dict[int, str]:
    """Section number -> body text, for every `## N. Title` heading (last one wins)."""
    out: dict[int, str] = {}
    current, buf = None, []
    for line in text.splitlines():
        m = HEADING.match(line.strip())
        if m:
            if current is not None:
                out[current] = "\n".join(buf)
            current, buf = int(m.group(1)), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf)
    return out


def patterns(text: str) -> list[tuple[int, list[tuple[str, str]]]]:
    """Main-body pattern blocks: (N, [(label, value), ...]) in the order written.

    A value runs from its label line to the next label line or the next pattern heading, so a
    bulleted Evidence list under its label belongs to Evidence."""
    body = sections(text).get(2, "")
    blocks: list[tuple[int, list[tuple[str, str]]]] = []
    for line in body.splitlines():
        head = PATTERN_HEAD.match(line)
        if head:
            blocks.append((int(head.group(1)), []))
            continue
        if not blocks:
            continue
        lab = LABEL_LINE.match(line)
        fields = blocks[-1][1]
        if lab:
            fields.append((lab.group(1), lab.group(2).strip()))
        elif fields and line.strip():
            label, value = fields[-1]
            fields[-1] = (label, (value + "\n" + line.strip()).strip())
    return blocks


def _field(fields: list[tuple[str, str]], label: str) -> str | None:
    for lab, val in fields:
        if lab == label:
            return re.sub(r"[*_]", "", val).strip()
    return None


def cp_d1(text: str, case: History) -> Result:
    nums = [n for n, _ in patterns(text)]
    if len(nums) > 12:
        return fail("CP-D1", f"{len(nums)} patterns, cap is 12")
    if nums != list(range(1, len(nums) + 1)):
        return fail("CP-D1", f"pattern numbers {nums} do not run 1, 2, 3")
    return ok("CP-D1", f"{len(nums)} patterns")


def cp_d2(text: str, case: History) -> Result:
    for n, fields in patterns(text):
        got = [lab for lab, _ in fields]
        if got != LABELS:
            return fail("CP-D2", f"Pattern {n} labels {got}")
    return ok("CP-D2")


def cp_d3(text: str, case: History) -> Result:
    for n, fields in patterns(text):
        conf = (_field(fields, "Confidence") or "").split()
        value = conf[0].strip(".,;").casefold() if conf else ""
        if value not in ("strong", "moderate"):
            return fail("CP-D3", f"Pattern {n} confidence {value or 'missing'!r}")
    secs = sections(text)
    for num, body in secs.items():
        if num != 9 and re.search(r"Confidence\W*\s*speculative", body, re.IGNORECASE):
            return fail("CP-D3", f"speculative confidence outside section 9 (section {num})")
    return ok("CP-D3")


def cp_d4(text: str, case: History) -> Result:
    for n, fields in patterns(text):
        ev = _field(fields, "Evidence") or ""
        tokens = DATE_TOKEN.findall(ev)
        if len(tokens) < 3:
            return fail("CP-D4", f"Pattern {n} evidence has {len(tokens)} date tokens")
    return ok("CP-D4")


def cp_d5(text: str, case: History) -> Result:
    for n, fields in patterns(text):
        counter = _field(fields, "Counter-evidence")
        if not counter:
            return fail("CP-D5", f"Pattern {n} counter-evidence is empty")
        conf = (_field(fields, "Confidence") or "").casefold()
        if counter.casefold().startswith("none found") and conf.startswith("strong"):
            return fail("CP-D5", f"Pattern {n}: none found with strong confidence")
    return ok("CP-D5")


def cp_d6(text: str, case: History) -> Result:
    n = word_count(text)
    if n > 4000:
        return fail("CP-D6", f"{n} words, cap is 4,000")
    if n < 2000 and not case.thin:
        return fail("CP-D6", f"{n} words, floor is 2,000")
    return ok("CP-D6", f"{n} words")


def cp_d7(text: str, case: History) -> Result:
    found = [t for t in FRAMEWORK_TERMS if whole_word(t).search(text)]
    return fail("CP-D7", f"framework terms: {found}") if found else ok("CP-D7")


def cp_d8(text: str, case: History) -> Result:
    got = []
    for line in text.splitlines():
        m = HEADING.match(line.strip())
        if m:
            got.append(f"{m.group(1)}. {m.group(2)}")
    if got != SECTIONS:
        return fail("CP-D8", f"headings {got}")
    return ok("CP-D8")


def cp_d9(text: str, case: History) -> Result:
    if EM_DASH in text:
        return fail("CP-D9", "em dash")
    if "it is important to note" in fold(text):
        return fail("CP-D9", "'It is important to note'")
    found = [p for p in MOTIVATIONAL if whole_word(p).search(text)]
    return fail("CP-D9", f"motivational phrases: {found}") if found else ok("CP-D9")


def cp_d10(text: str, case: History) -> Result:
    body = sections(text).get(10, "")
    return ok("CP-D10") if VALID_DATE.search(body) else fail("CP-D10", "no 'Valid as of' with a date in section 10")


def cp_d11(text: str, case: History) -> Result:
    hits = canary_hits(text, case.canaries)
    return fail("CP-D11", f"canaries: {hits}") if hits else ok("CP-D11")


def cp_d12(text: str, case: History) -> Result:
    existing = {n for n, _ in patterns(text)}
    secs = sections(text)
    for num in (3, 4, 5, 6):
        for ref in PATTERN_REF.findall(secs.get(num, "")):
            if int(ref) not in existing:
                return fail("CP-D12", f"section {num} cites Pattern {ref}, which does not exist")
    for num in (3, 5):
        if not PATTERN_REF.search(secs.get(num, "")):
            return fail("CP-D12", f"section {num} cites no pattern")
    return ok("CP-D12")


CHECKS = {
    "CP-D1": cp_d1, "CP-D2": cp_d2, "CP-D3": cp_d3, "CP-D4": cp_d4, "CP-D5": cp_d5, "CP-D6": cp_d6,
    "CP-D7": cp_d7, "CP-D8": cp_d8, "CP-D9": cp_d9, "CP-D10": cp_d10, "CP-D11": cp_d11, "CP-D12": cp_d12,
}


def run_all(text: str, case: History) -> list[Result]:
    return [fn(text, case) for fn in CHECKS.values()]
