"""Requirement traceability (control R1).

Reads every table row in docs/spec.md that begins `| REQ-`, reads the
`@pytest.mark.req("REQ-###")` tags in tests/, prints the matrix and exits 1 if:

- a MUST or MUST NOT has no test (unless --report-only);
- a test is tagged with an id that is not in the spec (a typo would hide a gap);
- an id appears twice in the spec;
- a row of the scope table in section 11.1 names no MUST.

Withdrawn requirements (a row containing the word "withdrawn") are ignored.
Usage: python scripts/trace.py [--report-only] [--spec PATH] [--tests DIR]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROW = re.compile(r"^\|\s*(REQ-\d{3})\s*\|\s*(MUST NOT|MUST|SHOULD|MAY)\s*\|")
MARK = re.compile(r"mark\.req\(([^)]*)\)")
ID = re.compile(r"""["'](REQ-\d{3})["']""")
SCOPE_HEADING = re.compile(r"^###\s+11\.1\b")
ANY_HEADING = re.compile(r"^#{2,3}\s")


def read_spec(spec: Path) -> tuple[dict[str, str], list[str], list[tuple[str, list[str]]]]:
    """Return (id -> level, duplicate ids, scope rows as (text, referenced ids))."""
    levels: dict[str, str] = {}
    dupes: list[str] = []
    scope: list[tuple[str, list[str]]] = []
    in_scope = False
    for line in spec.read_text(encoding="utf-8").splitlines():
        if SCOPE_HEADING.match(line):
            in_scope = True
            continue
        if in_scope and ANY_HEADING.match(line):
            in_scope = False
        m = ROW.match(line)
        if m and "withdrawn" not in line.lower():
            if m.group(1) in levels:
                dupes.append(m.group(1))
            levels[m.group(1)] = m.group(2)
        if in_scope and line.startswith("|") and not re.match(r"^\|\s*(Scope bullet|-)", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                scope.append((cells[0], expand_ids(cells[1])))
    return levels, dupes, scope


def expand_ids(cell: str) -> list[str]:
    """`REQ-001, 030, 031` -> REQ-001, REQ-030, REQ-031 (bare numbers share the prefix)."""
    ids = []
    for token in re.findall(r"REQ-\d{3}|\b\d{3}\b", cell):
        ids.append(token if token.startswith("REQ-") else f"REQ-{token}")
    return ids


def read_tags(tests: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted(tests.rglob("*.py")):
        for mark in MARK.findall(path.read_text(encoding="utf-8")):
            for rid in ID.findall(mark):
                counts[rid] = counts.get(rid, 0) + 1
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report-only", action="store_true", help="do not fail on untested MUSTs")
    ap.add_argument("--spec", type=Path, default=ROOT / "docs" / "spec.md")
    ap.add_argument("--tests", type=Path, default=ROOT / "tests")
    args = ap.parse_args(argv)

    levels, dupes, scope = read_spec(args.spec)
    tags = read_tags(args.tests)

    untested = []
    for rid in sorted(levels):
        n = tags.get(rid, 0)
        print(f"{rid}  {levels[rid]:<8} {f'{n} test(s)' if n else 'NO TEST'}")
        if not n and levels[rid].startswith("MUST"):
            untested.append(rid)

    errors = []
    for rid in sorted(set(tags) - set(levels)):
        errors.append(f"tag for unknown requirement {rid}")
    for rid in sorted(set(dupes)):
        errors.append(f"requirement {rid} appears more than once in the spec")
    for text, ids in scope:
        musts = [i for i in ids if levels.get(i, "").startswith("MUST")]
        if not musts:
            errors.append(f"scope row maps to no MUST: {text[:60]}")
    for e in errors:
        print(f"ERROR {e}")

    print(
        f"{len(levels)} requirements, {len(untested)} untested MUST, "
        f"{len(scope)} scope rows, {len(errors)} errors"
    )
    if errors:
        return 1
    if untested and not args.report_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
