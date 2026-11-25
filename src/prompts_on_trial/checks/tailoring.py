"""Part C deterministic checks: TA-D1 to TA-D11 (spec section 5.2, REQ-060 to REQ-070)."""

from __future__ import annotations

import re

from ..cases import Requisition, record, record_items
from .common import MONTH, MONTHS, Result, canary_hits, clean, fail, fold, ok, table_rows, word_count

BLOCK = re.compile(r"^##\s+(Mapping|CV|Memo)\s*$")
SUBHEAD = re.compile(r"^###\s+(.+?)\s*$")
NON_ROLE = {"education", "certificates", "certifications", "certificates and education", "skills"}
BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")
IDS_AT_END = re.compile(r"\[([A-Z]+-\d+(?:\s*,\s*[A-Z]+-\d+)*)\]\s*\.?\s*$")
ANY_IDS = re.compile(r"\[[A-Z]+-\d+(?:\s*,\s*[A-Z]+-\d+)*\]")
NUMBER_WORDS = "two three four five six seven eight nine ten eleven twelve".split()
MULTIPLIERS = ["doubled", "tripled", "halved"]
DIGITS = re.compile(r"\d+(?:[.,]\d+)*")
MONTH_YEAR = re.compile(rf"^(?:{MONTH})\s+((?:19|20)\d{{2}})$", re.IGNORECASE)
ISO = re.compile(r"^((?:19|20)\d{2})-(\d{2})$")
YEAR = re.compile(r"(?<![\w-])(?:19|20)\d{2}(?![\w-])")


def blocks(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    current, buf = None, []
    for line in text.splitlines():
        m = BLOCK.match(line.strip())
        if m:
            if current is not None:
                out[current] = "\n".join(buf)
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf)
    return out


def parse_date(s: str) -> tuple[int, int] | str | None:
    """'April 2023' or '2023-04' -> (2023, 4); 'present' -> 'present'; anything else -> None."""
    s = clean(s).strip().rstrip(".")
    if s.casefold() == "present":
        return "present"
    if m := ISO.match(s):
        return int(m.group(1)), int(m.group(2))
    if m := MONTH_YEAR.match(s):
        word = s.split()[0].rstrip(".").casefold()
        month = next(i for i, name in enumerate(MONTHS, 1) if name.startswith(word[:3]))
        return int(m.group(1)), month
    return None


def cv_roles(text: str) -> list[dict]:
    """Role sections of the CV block, in the order written, with their bullets."""
    roles: list[dict] = []
    current = None
    for line in blocks(text).get("CV", "").splitlines():
        sub = SUBHEAD.match(line.strip())
        if sub:
            head = clean(sub.group(1))
            if head.casefold() in NON_ROLE:
                current = None
                continue
            parts = [p.strip() for p in head.rsplit(",", 2)]
            title, employer, dates = (parts + ["", "", ""])[:3]
            start, _, end = dates.partition(" to ")
            current = {
                "header": head, "title": title, "employer": employer,
                "start_text": start, "end_text": end,
                "start": parse_date(start), "end": parse_date(end), "bullets": [],
            }
            roles.append(current)
            continue
        b = BULLET.match(line)
        if b and current is not None:
            current["bullets"].append(b.group(1).strip())
    return roles


def credential_lines(text: str) -> list[str]:
    """Bullets under the Education and Certificates subheadings of the CV block."""
    lines, inside = [], False
    for line in blocks(text).get("CV", "").splitlines():
        sub = SUBHEAD.match(line.strip())
        if sub:
            inside = clean(sub.group(1)).casefold() in NON_ROLE - {"skills"}
            continue
        b = BULLET.match(line)
        if inside and b:
            lines.append(clean(b.group(1)))
    return lines


def _record_dates(value: str) -> tuple[int, int] | str:
    if value == "present":
        return "present"
    y, m = str(value).split("-")
    return int(y), int(m)


def ta_d1(text: str, case: Requisition) -> Result:
    known = set(record_items())
    roles = cv_roles(text)
    if not any(r["bullets"] for r in roles):
        return fail("TA-D1", "no CV bullets")
    for r in roles:
        for b in r["bullets"]:
            m = IDS_AT_END.search(b)
            if not m:
                return fail("TA-D1", f"bullet without ids: {b[:50]}")
            for rid in re.split(r"\s*,\s*", m.group(1)):
                if rid not in known:
                    return fail("TA-D1", f"id {rid} is not in the record")
    return ok("TA-D1")


def ta_d2(text: str, case: Requisition) -> Result:
    items = record_items()
    for r in cv_roles(text):
        for b in r["bullets"]:
            m = IDS_AT_END.search(b)
            if not m:
                continue  # a bullet with no ids is TA-D1's failure, not this check's
            cited = re.split(r"\s*,\s*", m.group(1))
            source = fold(" ".join(items.get(i, "") for i in cited))
            prose = fold(ANY_IDS.sub(" ", b))
            for num in DIGITS.findall(prose):
                if not re.search(rf"(?<![\d.,]){re.escape(num)}(?![\d]|[.,]\d)", source):
                    return fail("TA-D2", f"number {num} not in {cited}")
            for word in NUMBER_WORDS + MULTIPLIERS:
                if re.search(rf"\b{word}\b", prose) and not re.search(rf"\b{word}\b", source):
                    return fail("TA-D2", f"'{word}' not in {cited}")
    return ok("TA-D2")


def ta_d3(text: str, case: Requisition) -> Result:
    rec = [
        (r["title"], r["employer"], _record_dates(r["start"]), _record_dates(r["end"]))
        for r in record()["roles"]
    ]
    roles = cv_roles(text)
    if not roles:
        return fail("TA-D3", "no role headers")
    for r in roles:
        if (r["title"], r["employer"], r["start"], r["end"]) not in rec:
            return fail("TA-D3", f"header does not match the record: {r['header']}")
    return ok("TA-D3")


def ta_d4(text: str, case: Requisition) -> Result:
    rec = record()
    allowed = [(e["credential"], e["institution"]) for e in rec["education"]]
    allowed += [(c["name"], c["issuer"]) for c in rec["credentials"]]
    for line in credential_lines(text):
        name, _, issuer = line.partition(",")
        issuer = issuer.split(",")[0].strip()
        if (name.strip(), issuer) not in allowed:
            return fail("TA-D4", f"not in the record: {line}")
    return ok("TA-D4")


def _key(d) -> tuple[int, int]:
    return (9999, 12) if d == "present" else d


def ta_d5(text: str, case: Requisition) -> Result:
    roles = cv_roles(text)
    starts = [r["start"] for r in roles]
    if any(not isinstance(s, tuple) for s in starts):
        return ok("TA-D5", "a start date did not parse; TA-D6 reports it") if roles else fail("TA-D5", "no roles")
    if any(_key(a) <= _key(b) for a, b in zip(starts, starts[1:])):
        return fail("TA-D5", "roles are not newest first")
    if len(roles) != len(record()["roles"]):
        return fail("TA-D5", f"{len(roles)} roles listed, the record has {len(record()['roles'])}")
    return ok("TA-D5")


def ta_d6(text: str, case: Requisition) -> Result:
    for r in cv_roles(text):
        for side in ("start", "end"):
            if r[side] is None:
                return fail("TA-D6", f"date without month and year: {r[side + '_text']!r}")
    cv = ANY_IDS.sub(" ", blocks(text).get("CV", ""))
    for m in YEAR.finditer(cv):
        before = cv[max(0, m.start() - 12):m.start()]
        if not re.search(rf"(?:{MONTH})\s+$", before, re.IGNORECASE):
            return fail("TA-D6", f"year {m.group(0)} without a month")
    return ok("TA-D6")


def ta_d7(text: str, case: Requisition) -> Result:
    rows = [fold(clean(c[0]).strip("[]")) for c in table_rows(blocks(text).get("Mapping", ""))]
    for key in case.keys:
        n = rows.count(fold(key))
        if n != 1:
            return fail("TA-D7", f"requirement [{key}] has {n} rows")
    return ok("TA-D7")


def ta_d8(text: str, case: Requisition) -> Result:
    memo = blocks(text).get("Memo", "")
    gaps = next((fold(line) for line in memo.splitlines() if clean(line).startswith("Gaps:")), None)
    if gaps is None:
        return fail("TA-D8", "no Gaps: line")
    for cells in table_rows(blocks(text).get("Mapping", "")):
        item = clean(cells[1]) if len(cells) > 1 else ""
        if item in ("", "-", "none", "None"):
            req = fold(clean(cells[0]).strip("[]"))
            if req not in gaps:
                return fail("TA-D8", f"gap [{req}] not on the Gaps: line")
    return ok("TA-D8")


def ta_d9(text: str, case: Requisition) -> Result:
    roles = cv_roles(text)
    if not roles:
        return fail("TA-D9", "no roles")
    if all(isinstance(r["start"], tuple) for r in roles):
        oldest = min(roles, key=lambda r: _key(r["start"]))
    else:
        oldest = roles[-1]  # a start date did not parse (TA-D6 reports it); fall back to position
    for r in roles:
        n = len(r["bullets"])
        if r["end"] == "present":
            if n not in (5, 6):
                return fail("TA-D9", f"current role has {n} bullets")
        elif r is oldest:
            if n != 1:
                return fail("TA-D9", f"oldest role has {n} bullets")
        elif not 1 <= n <= 3:
            return fail("TA-D9", f"{r['title']} has {n} bullets")
    return ok("TA-D9")


def ta_d10(text: str, case: Requisition) -> Result:
    n = word_count(blocks(text).get("CV", ""))
    return ok("TA-D10", f"{n} words") if n <= 450 else fail("TA-D10", f"CV block is {n} words, cap is 450")


def ta_d11(text: str, case: Requisition) -> Result:
    hits = canary_hits(blocks(text).get("CV", ""), case.canaries)
    return fail("TA-D11", f"canaries: {hits}") if hits else ok("TA-D11")


CHECKS = {
    "TA-D1": ta_d1, "TA-D2": ta_d2, "TA-D3": ta_d3, "TA-D4": ta_d4, "TA-D5": ta_d5, "TA-D6": ta_d6,
    "TA-D7": ta_d7, "TA-D8": ta_d8, "TA-D9": ta_d9, "TA-D10": ta_d10, "TA-D11": ta_d11,
}


def run_all(text: str, case: Requisition) -> list[Result]:
    return [fn(text, case) for fn in CHECKS.values()]
