"""Build the exact text a model sees for each case on the model path (spec 3.1, 4.1, 5.1).

Pure Python with no model library, so continuous integration can test what the model would see.
"""

from __future__ import annotations

from . import cases

PROMPTS = cases.ROOT / "prompts"
PROMPT_FILE = {"A": "cognitive-profile.md", "B": "travel-method.md", "C": "tailoring-doctrine.md"}
PROFILE_CLOSE = "This log is everything available. Produce the profile."


def prompt(part: str) -> str:
    return (PROMPTS / PROMPT_FILE[part]).read_text(encoding="utf-8")


def build(part: str, case_id: str) -> str:
    """The single user message for one case: the prompt, then the case material."""
    if part == "A":
        h = cases.histories()[case_id]
        header = "Evidence log (id | date | context | kind | entry):"
        return f"{prompt('A')}\n\n---\n\n{header}\n{h.log.rstrip()}\n\n{PROFILE_CLOSE}"
    if part == "B":
        t = cases.trips()[case_id]
        if t.scoping:
            return f"{prompt('B')}\n\n---\n\n{t.brief}"
        return f"{prompt('B')}\n\n---\n\n{t.brief}\n\nFare sheet {t.id}:\n{t.sheet()}\n\n{cases.proceed_line()}"
    if part == "C":
        q = cases.requisitions()[case_id]
        record = cases.RECORD.read_text(encoding="utf-8")
        date = cases._load(cases.CASES / "tailoring.yaml")["evaluation_date"]
        return (
            f"{prompt('C')}\n\n---\n\nEvaluation date: {date}.\n\nCareer record:\n```yaml\n{record.rstrip()}\n```\n\n"
            f"{q.text()}"
        )
    raise KeyError(part)


def all_cases() -> list[tuple[str, str]]:
    """(part, case id) for all 22 inputs."""
    return (
        [("A", h) for h in cases.histories()]
        + [("B", t) for t in cases.trips()]
        + [("C", q) for q in cases.requisitions()]
    )
