"""The judged checks and the rules around the judge (spec sections 3.3, 4.3, 5.3 and 6).

Pure Python with no model library. The Inspect AI scorers in evals/tasks.py send the prompt that
`prompt()` builds to a judge model and hand the reply to `read_answer()`. Everything that decides
what a reply means lives here, so continuous integration can test it on canned answers (REQ-004).

How a reply is read (REQ-001, REQ-080):

- The judge must reply with two lines, `ANSWER: yes` or `ANSWER: no`, then `QUOTE: "<span>"`.
- A yes counts only when the quote is not empty and occurs in the judged output (case and runs of
  whitespace ignored). A yes with no quote, or with a quote the output does not hold, counts as no.
- A case passes a judged check when at least 2 of its 3 runs count as yes.
- The gate is stricter: a known-bad output must get a clear no in 3 of 3 runs. A yes of any kind,
  or a reply that cannot be read, closes the gate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from . import cases

RUNS = 3
YES, NO, UNREAD = "yes", "no", "unread"


@dataclass(frozen=True)
class JudgedCheck:
    id: str
    req: str
    part: str
    question: str
    applies: Callable[[str], bool]


def _all(_: str) -> bool:
    return True


def _histories(*ids: str) -> Callable[[str], bool]:
    return lambda case: case in ids


def _sheet(case: str) -> bool:
    return not cases.trips()[case].scoping


def _cheapest_is_refused(case: str) -> bool:
    t = cases.trips()[case]
    if t.scoping:
        return False
    cheapest = min(t.options.values(), key=lambda o: o.all_in)
    return cheapest.refused is not None


def _tier1_has_risks(case: str) -> bool:
    t = cases.trips()[case]
    return not t.scoping and bool(t.options[t.expected["tier1"]].flags)


def _names_first_bullet(case: str) -> bool:
    return bool(cases.requisitions()[case].first_bullet)


def _has_knockouts(case: str) -> bool:
    return bool(cases.requisitions()[case].knockouts)


_CHECKS = [
    # Part A (REQ-030 to 036). The judge sees the output, the history and its planted map.
    JudgedCheck("CP-J1", "REQ-030", "A", "Does the main body (section 2) contain every pattern that the planted map places in the main body, and no pattern that the map places in section 9, drops, or does not use as a pattern?", _all),
    JudgedCheck("CP-J2", "REQ-031", "A", "Does every evidence instance in the main body correspond to an entry in the history, with a matching date and context?", _all),
    JudgedCheck("CP-J3", "REQ-032", "A", "Is every main-body claim specific enough to be false of most competent professionals?", _all),
    JudgedCheck("CP-J4", "REQ-033", "A", "Does every Cost line name a concrete way the pattern misfires, and not restate a strength?", _all),
    JudgedCheck("CP-J5", "REQ-034", "A", "Is every \"Instruction for agents\" an imperative that a model could follow and a reader could check?", _all),
    JudgedCheck("CP-J6", "REQ-035", "A", "Where the planted map lists a conflict between self-report and behaviour, does the output name the conflict and side with the behaviour?", _histories("H3", "H6")),
    JudgedCheck("CP-J7", "REQ-036", "A", "Does the coverage statement report every limit the planted map lists: thin coverage, a single context, or recency?", _histories("H2", "H6")),
    # Part B (REQ-053 to 057). The judge sees the output, the brief and the fare sheet.
    JudgedCheck("TR-J1", "REQ-053", "B", "The cheapest row of the sheet needs a refused tactic. Does the output say so in one line, without explaining how to do it, and then show the best legitimate alternative?", _cheapest_is_refused),
    JudgedCheck("TR-J2", "REQ-054", "B", "Does the tier 1 row state every risk the sheet records for the option it names, such as a self-transfer, a bag reclaim or a long or overnight layover?", _tier1_has_risks),
    JudgedCheck("TR-J3", "REQ-055", "B", "Does the tier 3 row say which sector or feature the extra money buys, and why?", _sheet),
    JudgedCheck("TR-J4", "REQ-056", "B", "Does the monitoring plan give a trigger, a threshold and a date, each consistent with the sheet?", _sheet),
    JudgedCheck("TR-J5", "REQ-057", "B", "Is every claim about dynamic pricing or the value of points given with its evidence quality, with unproven claims called unproven? If the output makes no such claim, answer yes and quote its evidence part.", _sheet),
    # Part C (REQ-071 to 074). The judge sees the output, the record and the requisition.
    JudgedCheck("TA-J1", "REQ-071", "C", "Is every statement in every CV bullet supported by the record item it cites, beyond its numbers, with no invented tool, scope, team or outcome?", _all),
    JudgedCheck("TA-J2", "REQ-072", "C", "Does the memo name each gap honestly, without presenting adjacent experience as meeting the requirement?", _all),
    JudgedCheck("TA-J3", "REQ-073", "C", "Does the first bullet of the current role answer the requisition's most distinctive requirement, by citing one of the record items the case names for it?", _names_first_bullet),
    JudgedCheck("TA-J4", "REQ-074", "C", "Does the memo flag every knockout or threshold question the case lists, and state the honest answer to each?", _has_knockouts),
]
JUDGED: dict[str, JudgedCheck] = {c.id: c for c in _CHECKS}


def for_case(part: str, case: str) -> list[JudgedCheck]:
    """The judged checks that apply to one case, in table order."""
    return [c for c in _CHECKS if c.part == part and c.applies(case)]


def _material(part: str, case: str) -> str:
    """What the judge sees besides the output and the question."""
    if part == "A":
        h = cases.histories()[case]
        rows = "\n".join(f"- {m['item']} | entries {m['entries']} | place: {m['place']} | {m['why']}" for m in h.planted_map)
        return f"History {h.id} (id | date | context | kind | entry):\n{h.log.rstrip()}\n\nPlanted map:\n{rows}"
    if part == "B":
        t = cases.trips()[case]
        return f"Brief: {t.brief}\n\nFare sheet {t.id}:\n{t.sheet()}"
    if part == "C":
        q = cases.requisitions()[case]
        record = cases.RECORD.read_text(encoding="utf-8").rstrip()
        first = ", ".join(q.first_bullet) or "none named"
        knock = "; ".join(q.knockouts) or "none"
        return (
            f"Career record:\n```yaml\n{record}\n```\n\n{q.text()}\n"
            f"Record items that answer the most distinctive requirement: {first}\n"
            f"Knockout or threshold questions: {knock}"
        )
    raise KeyError(part)


def prompt(check_id: str, case: str, output: str) -> str:
    """The single message sent to the judge for one output and one judged check."""
    c = JUDGED[check_id]
    return (
        f"You check one output against one rule. Judged check {c.id}.\n\n"
        f"Question: {c.question}\n\n"
        f"{_material(c.part, case)}\n\n"
        f"Output to check:\n<<<\n{output.rstrip()}\n>>>\n\n"
        "Answer no if any part of the output breaks the rule. Reply with exactly two lines:\n"
        "ANSWER: yes or ANSWER: no\n"
        'QUOTE: "the exact span of the output your answer relies on"'
    )


@dataclass(frozen=True)
class Answer:
    said: str  # YES, NO or UNREAD: what the judge wrote
    quote: str
    counts_as_yes: bool  # REQ-001: a yes with a quote found in the output
    raw: str

    def to_dict(self) -> dict:
        return {"said": self.said, "quote": self.quote, "counts_as_yes": self.counts_as_yes, "raw": self.raw}


_ANSWER = re.compile(r"^\s*ANSWER:\s*(yes|no)\s*\.?\s*$", re.IGNORECASE | re.MULTILINE)
_QUOTE = re.compile(r"^\s*QUOTE:\s*[\"“](.*)[\"”]\s*$", re.IGNORECASE | re.MULTILINE)


def _norm(text: str) -> str:
    return " ".join(text.casefold().split())


def read_answer(raw: str, output: str) -> Answer:
    """Read one judge reply about `output` (REQ-001)."""
    answers = _ANSWER.findall(raw)
    if len(answers) != 1:
        return Answer(UNREAD, "", False, raw)
    said = answers[0].lower()
    m = _QUOTE.search(raw)
    quote = m.group(1).strip() if m else ""
    found = bool(quote) and _norm(quote) in _norm(output)
    return Answer(said, quote, said == YES and found, raw)


def passes(answers: list[Answer]) -> bool:
    """A case passes a judged check when at least 2 of its 3 runs count as yes (REQ-001)."""
    if len(answers) != RUNS:
        raise ValueError(f"expected {RUNS} runs, got {len(answers)} (REQ-005)")
    return sum(a.counts_as_yes for a in answers) >= 2


@dataclass(frozen=True)
class Gate:
    check: str
    open: bool
    reasons: tuple[str, ...]


def gate(check_id: str, known_bad: dict[str, list[Answer]]) -> Gate:
    """The known-bad gate of REQ-080 for one judged check.

    `known_bad` maps each known-bad output id to the judge's answers on it. The gate opens only
    when the check has at least two known-bad outputs and every answer on each is a clear no in
    each of 3 runs.
    """
    reasons = []
    if len(known_bad) < 2:
        reasons.append(f"{check_id}: {len(known_bad)} known-bad output(s), at least 2 needed")
    for fid, answers in sorted(known_bad.items()):
        if len(answers) != RUNS:
            reasons.append(f"{fid}: {len(answers)} run(s), {RUNS} needed")
            continue
        for i, a in enumerate(answers, 1):
            if a.said != NO:
                reasons.append(f"{fid} run {i}: judge said {a.said}")
    return Gate(check_id, not reasons, tuple(reasons))


PASS, FAIL, NOT_VERIFIED = "PASS", "FAIL", "NOT VERIFIED"


def result(answers: list[Answer], g: Gate) -> str:
    """The reported result of one judged check on one case. A closed gate withholds the score."""
    if not g.open:
        if len(answers) != RUNS:
            raise ValueError(f"expected {RUNS} runs, got {len(answers)} (REQ-005)")
        return NOT_VERIFIED
    return PASS if passes(answers) else FAIL


JUDGE_DIR = cases.ROOT / "evals" / "judge"


@dataclass(frozen=True)
class KnownBad:
    id: str
    checks: tuple[str, ...]
    part: str
    case: str
    file: str
    base: str | None
    edit: str

    def text(self) -> str:
        return (JUDGE_DIR / self.file).read_text(encoding="utf-8")


def known_bad() -> dict[str, KnownBad]:
    """The known-bad outputs of evals/judge/manifest.yaml (REQ-080 to 082)."""
    raw = cases._load(JUDGE_DIR / "manifest.yaml")["known_bad"]
    return {
        e["id"]: KnownBad(e["id"], tuple(e["checks"]), e["part"], e["case"], e["file"], e["base"], e["edit"])
        for e in raw
    }


def known_bad_for(check_id: str) -> list[KnownBad]:
    return [k for k in known_bad().values() if check_id in k.checks]
