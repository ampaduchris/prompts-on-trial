"""Part B deterministic checks: TR-D1 to TR-D10 and TR-S1 (spec section 4.2, REQ-042 to REQ-052)."""

from __future__ import annotations

import re

from ..cases import Trip
from .common import EM_DASH, URL, Result, clean, fail, ok, strip_urls, table_rows, whole_word

PARTS = ["1. Ranked options", "2. Recommendation", "3. Monitoring plan", "4. Evidence", "5. Sources"]
TIERS = ["1. Absolute lowest", "2. Lowest within sane limits", "3. Best price per comfort"]

HEADING = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
OPTION_ID = re.compile(r"\bOPT-[A-Z]\b")
# A euro amount: "EUR 195", "€195", "195 EUR", "195 euros".
EURO = re.compile(r"(?:EUR|€)\s?(\d[\d,]*)|(\d[\d,]*)\s?(?:EUR\b|euros?\b|€)")
GAP = re.compile(r"\bgap\b[^|\d]*?(?:EUR|€)?\s?(\d[\d,]*)", re.IGNORECASE)
PHONE = re.compile(r"\+?\(?\d[\d\s().\-/]{7,}\d")
CURRENCY = re.compile(r"(?:EUR|€|\$|£|USD|GBP)\s?\d|\d[\d,.]*\s?(?:EUR\b|euros?\b|€|dollars?\b|pounds?\b)", re.IGNORECASE)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)]|[A-Da-d][.)])\s+\S")


def parts(text: str) -> dict[int, str]:
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


def _amount(m: re.Match[str]) -> int:
    return int((m.group(1) or m.group(2)).replace(",", ""))


def tier_rows(text: str) -> list[dict]:
    """The tier table of part 1: label, option ids named, first euro amount, stated gap."""
    rows = []
    for cells in table_rows(parts(text).get(1, "")):
        row = " | ".join(cells)
        euro = EURO.search(row)
        gap = GAP.search(row)
        rows.append({
            "label": clean(cells[0]),
            "ids": OPTION_ID.findall(row),
            "price": _amount(euro) if euro else None,
            "gap": int(gap.group(1).replace(",", "")) if gap else None,
        })
    return rows


def _not_applicable(check: str, trip: Trip) -> Result | None:
    return ok(check, "not applicable to a scoping case") if trip.scoping else None


def tr_d1(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D1", trip):
        return r
    got = [f"{m.group(1)}. {m.group(2)}" for line in text.splitlines() if (m := HEADING.match(line.strip()))]
    return ok("TR-D1") if got == PARTS else fail("TR-D1", f"parts {got}")


def tr_d2(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D2", trip):
        return r
    labels = [r["label"] for r in tier_rows(text)]
    return ok("TR-D2") if labels == TIERS else fail("TR-D2", f"tier rows {labels}")


def tr_d3(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D3", trip):
        return r
    refused = {oid for oid, o in trip.options.items() if o.refused}
    named = [i for r in tier_rows(text) for i in r["ids"]]
    named += OPTION_ID.findall(parts(text).get(2, ""))
    bad = sorted(refused.intersection(named))
    return fail("TR-D3", f"refused options named: {bad}") if bad else ok("TR-D3")


def tr_d4(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D4", trip):
        return r
    rows = tier_rows(text)
    if not rows:
        return fail("TR-D4", "no tier rows")
    for row in rows:
        if not row["ids"] or row["ids"][0] not in trip.options:
            return fail("TR-D4", f"{row['label']}: no option from the sheet")
        want = trip.options[row["ids"][0]].all_in
        if row["price"] != want:
            return fail("TR-D4", f"{row['label']}: {row['ids'][0]} priced {row['price']}, all-in is {want}")
    if trip.expected.get("cents_per_point"):
        if not (re.search(r"\b(?:0\.98|1\.0)\b", text) and re.search(r"\bcents?\b", text, re.IGNORECASE)):
            return fail("TR-D4", "no cents-per-point value (0.98 or 1.0 with 'cent')")
    return ok("TR-D4")


def tr_d5(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D5", trip):
        return r
    rows = tier_rows(text)
    first = [r["ids"][0] if r["ids"] else None for r in rows]
    exp = trip.expected
    if len(first) != 3:
        return fail("TR-D5", f"{len(first)} tier rows")
    if first[0] != exp["tier1"]:
        return fail("TR-D5", f"tier 1 names {first[0]}, expected {exp['tier1']}")
    if first[1] != exp["tier2"]:
        return fail("TR-D5", f"tier 2 names {first[1]}, expected {exp['tier2']}")
    if first[2] not in exp["tier3"]:
        return fail("TR-D5", f"tier 3 names {first[2]}, allowed {exp['tier3']}")
    return ok("TR-D5")


def tr_d6(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D6", trip):
        return r
    rows = tier_rows(text)
    if len(rows) < 2 or not rows[0]["ids"] or not rows[1]["ids"]:
        return fail("TR-D6", "tier 1 or tier 2 row missing")
    if rows[1]["gap"] is None:
        return fail("TR-D6", "no gap stated in the tier 2 row")
    try:
        want = trip.options[rows[1]["ids"][0]].all_in - trip.options[rows[0]["ids"][0]].all_in
    except KeyError as e:
        return fail("TR-D6", f"option {e} is not on the sheet")
    return ok("TR-D6") if rows[1]["gap"] == want else fail("TR-D6", f"gap {rows[1]['gap']}, expected {want}")


def tr_d7(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D7", trip):
        return r
    named = sorted(set(OPTION_ID.findall(parts(text).get(2, ""))))
    if len(named) != 1:
        return fail("TR-D7", f"recommendation names {named or 'no option'}")
    allowed = trip.expected["recommend"]
    return ok("TR-D7") if named[0] in allowed else fail("TR-D7", f"recommends {named[0]}, allowed {allowed}")


def tr_d8(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D8", trip):
        return r
    sources = set(trip.sources)
    for url in URL.findall(text):
        url = url.rstrip(".,;:")
        if url not in sources:
            return fail("TR-D8", f"URL not on the sheet: {url}")
    for line in parts(text).get(5, "").splitlines():
        if LIST_ITEM.match(line):
            item = clean(re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)).rstrip(".")
            if item not in sources:
                return fail("TR-D8", f"source not on the sheet: {item}")
    for m in PHONE.finditer(strip_urls(text)):
        if len(re.sub(r"\D", "", m.group(0))) >= 9:
            return fail("TR-D8", "phone number not on the sheet")
    return ok("TR-D8")


def tr_d9(text: str, trip: Trip) -> Result:
    if r := _not_applicable("TR-D9", trip):
        return r
    body = parts(text).get(4, "")
    level = any(whole_word(w).search(body) for w in ("high", "medium", "low"))
    counter = re.search(r"counter-evidence", body, re.IGNORECASE)
    if not level:
        return fail("TR-D9", "part 4 has no confidence level")
    return ok("TR-D9") if counter else fail("TR-D9", "part 4 does not say counter-evidence")


def tr_d10(text: str, trip: Trip) -> Result:
    if EM_DASH in text:
        return fail("TR-D10", "em dash")
    if not trip.scoping and "?" in strip_urls(text):
        return fail("TR-D10", "asks a question under 'Proceed without questions'")
    return ok("TR-D10")


def tr_s1(text: str, trip: Trip) -> Result:
    if not trip.scoping:
        return ok("TR-S1", "applies to the scoping case only")
    prose = strip_urls(text)
    q = prose.count("?")
    if q != 1:
        return fail("TR-S1", f"{q} question marks")
    items = [line for line in prose.splitlines() if LIST_ITEM.match(line)]
    if not 2 <= len(items) <= 4:
        return fail("TR-S1", f"{len(items)} listed options")
    rec = len(whole_word("recommended").findall(prose))
    if rec != 1:
        return fail("TR-S1", f"'recommended' appears {rec} times")
    if CURRENCY.search(prose):
        return fail("TR-S1", "a currency amount")
    return ok("TR-S1")


CHECKS = {
    "TR-D1": tr_d1, "TR-D2": tr_d2, "TR-D3": tr_d3, "TR-D4": tr_d4, "TR-D5": tr_d5, "TR-D6": tr_d6,
    "TR-D7": tr_d7, "TR-D8": tr_d8, "TR-D9": tr_d9, "TR-D10": tr_d10, "TR-S1": tr_s1,
}


def run_all(text: str, trip: Trip) -> list[Result]:
    return [fn(text, trip) for fn in CHECKS.values()]
