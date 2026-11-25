"""Deterministic checks. Each takes an output text and its case and returns a Result.

No check calls a model or the network (REQ-004).
"""

from __future__ import annotations

from .. import cases
from . import profile, tailoring, travel
from .common import Result

PARTS = {
    "A": (profile.CHECKS, cases.histories),
    "B": (travel.CHECKS, cases.trips),
    "C": (tailoring.CHECKS, cases.requisitions),
}


def run(part: str, text: str, case_id: str) -> list[Result]:
    checks, load = PARTS[part]
    case = load()[case_id]
    return [fn(text, case) for fn in checks.values()]


__all__ = ["PARTS", "Result", "run"]
