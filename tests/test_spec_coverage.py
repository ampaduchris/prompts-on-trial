"""Every check of the evaluation design maps to exactly one requirement (REQ-111)."""

import re

import pytest

CHECK_IDS = (
    [f"CP-D{i}" for i in range(1, 13)]
    + [f"CP-J{i}" for i in range(1, 8)]
    + [f"TR-D{i}" for i in range(1, 11)]
    + ["TR-S1"]
    + [f"TR-J{i}" for i in range(1, 6)]
    + [f"TA-D{i}" for i in range(1, 12)]
    + [f"TA-J{i}" for i in range(1, 5)]
)

ROW = re.compile(r"^\|\s*(REQ-\d{3})\s*\|\s*(MUST NOT|MUST|SHOULD|MAY)\s*\|\s*([A-Z]{2}-[DJS]\d+):")


def rows(root):
    found = []
    for line in (root / "docs" / "spec.md").read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            found.append((m.group(1), m.group(2), m.group(3)))
    return found


def test_check_id_count_is_50():
    assert len(CHECK_IDS) == 50 and len(set(CHECK_IDS)) == 50


@pytest.mark.req("REQ-111")
@pytest.mark.parametrize("check", CHECK_IDS)
def test_check_has_exactly_one_must_row(root, check):
    hits = [r for r in rows(root) if r[2] == check]
    assert len(hits) == 1, f"{check}: {len(hits)} rows"
    assert hits[0][1].startswith("MUST")


@pytest.mark.req("REQ-111")
def test_no_row_for_an_unknown_check(root):
    assert {r[2] for r in rows(root)} <= set(CHECK_IDS)
