"""The baseline file the runner writes, its summary rows and the regression rule (spec section 7).

Pure Python with no model library, tested in continuous integration on canned answers. The runner
in evals/run.py calls `build()` and `write()` after a run on the user's own key. The repository
commits no baseline for v1.0 (REQ-090, DEV-018).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__, checks, inputs, judge

FORMAT = "prompts-on-trial baseline 1"
SAME, DIFFERENT = "same model as generator", "different model from generator"


@dataclass
class Run:
    """One model output of one case, with every check result on it."""

    part: str
    case: str
    run: int
    output_path: str
    deterministic: dict[str, bool]
    judged: dict[str, judge.Answer] = field(default_factory=dict)


def relation(generator: str, judge_model: str) -> str:
    """REQ-002: whether the judge is a different model from the generator."""
    return SAME if generator == judge_model else DIFFERENT


def _gates(gate_answers: dict[str, dict[str, list[judge.Answer]]]) -> dict[str, judge.Gate]:
    return {cid: judge.gate(cid, gate_answers.get(cid, {})) for cid in judge.JUDGED}


def build(
    generator: str,
    judge_model: str,
    date: str,
    gate_answers: dict[str, dict[str, list[judge.Answer]]],
    runs: list[Run],
) -> dict:
    """Assemble the baseline of REQ-090 and its summary rows (REQ-091)."""
    gates = _gates(gate_answers)
    by_case: dict[tuple[str, str], list[Run]] = {}
    for r in runs:
        by_case.setdefault((r.part, r.case), []).append(r)
    case_rows = []
    for part, case in inputs.all_cases():
        rs = sorted(by_case.get((part, case), []), key=lambda r: r.run)
        judged_results = {}
        for jc in judge.for_case(part, case):
            answers = [r.judged[jc.id] for r in rs if jc.id in r.judged]
            judged_results[jc.id] = judge.result(answers, gates[jc.id])
        case_rows.append(
            {
                "part": part,
                "case": case,
                "runs": [
                    {
                        "run": r.run,
                        "output": r.output_path,
                        "deterministic": dict(r.deterministic),
                        "judged": {k: a.to_dict() for k, a in r.judged.items()},
                    }
                    for r in rs
                ],
                "judged_results": judged_results,
            }
        )
    b = {
        "format": FORMAT,
        "runner": {"name": "prompts-on-trial evals/run.py", "version": __version__},
        "generator_model": generator,
        "judge_model": judge_model,
        "judge_relation": relation(generator, judge_model),
        "date": date,
        "gate": {
            cid: {
                "open": g.open,
                "reasons": list(g.reasons),
                "answers": {fid: [a.to_dict() for a in ans] for fid, ans in sorted(gate_answers.get(cid, {}).items())},
            }
            for cid, g in gates.items()
        },
        "cases": case_rows,
    }
    b["summary"] = summary(b)
    return b


def summary(b: dict) -> dict[str, int]:
    """REQ-091. Counted over (case, check) pairs."""
    s = {
        "deterministic_3_of_3": 0,
        "deterministic_1_or_2_of_3": 0,
        "deterministic_0_of_3": 0,
        "judged_2_of_3_or_better": 0,
        "judged_below_2_of_3": 0,
        "judged_not_verified_gate_closed": 0,
    }
    for c in b["cases"]:
        ids = sorted({k for r in c["runs"] for k in r["deterministic"]})
        for cid in ids:
            n = sum(bool(r["deterministic"].get(cid)) for r in c["runs"])
            key = "deterministic_3_of_3" if n == 3 else "deterministic_0_of_3" if n == 0 else "deterministic_1_or_2_of_3"
            s[key] += 1
        for res in c["judged_results"].values():
            key = {
                judge.PASS: "judged_2_of_3_or_better",
                judge.FAIL: "judged_below_2_of_3",
                judge.NOT_VERIFIED: "judged_not_verified_gate_closed",
            }[res]
            s[key] += 1
    return s


_KEYS = ("format", "runner", "generator_model", "judge_model", "judge_relation", "date", "gate", "cases", "summary")


def validate(b: dict) -> list[str]:
    """Every way a baseline can break REQ-002, 005, 090 or 091. An empty list means valid."""
    errors = [f"missing key {k}" for k in _KEYS if k not in b]
    if errors:
        return errors
    if b["format"] != FORMAT:
        errors.append(f"format is {b['format']!r}")
    if b["judge_relation"] != relation(b["generator_model"], b["judge_model"]):
        errors.append("judge_relation does not match the two model ids (REQ-002)")
    if set(b["gate"]) != set(judge.JUDGED):
        errors.append("gate does not cover every judged check (REQ-080)")
    seen = {(c["part"], c["case"]) for c in b["cases"]}
    for pc in inputs.all_cases():
        if pc not in seen:
            errors.append(f"input {pc[1]} missing (REQ-090)")
    for c in b["cases"]:
        name = c["case"]
        if sorted(r["run"] for r in c["runs"]) != [1, 2, 3]:
            errors.append(f"{name}: runs are not 1, 2, 3 (REQ-005)")
        want_det = set(checks.PARTS[c["part"]][0])
        want_jud = {j.id for j in judge.for_case(c["part"], c["case"])}
        for r in c["runs"]:
            if not r.get("output"):
                errors.append(f"{name} run {r['run']}: no output path")
            if set(r["deterministic"]) != want_det:
                errors.append(f"{name} run {r['run']}: deterministic checks incomplete (REQ-005)")
            if set(r["judged"]) != want_jud:
                errors.append(f"{name} run {r['run']}: judged answers incomplete")
            for cid, a in r["judged"].items():
                if "quote" not in a:
                    errors.append(f"{name} run {r['run']} {cid}: answer has no quote field (REQ-090)")
        if set(c["judged_results"]) != want_jud:
            errors.append(f"{name}: judged results incomplete")
        for cid, res in c["judged_results"].items():
            if not b["gate"].get(cid, {}).get("open") and res != judge.NOT_VERIFIED:
                errors.append(f"{name} {cid}: reported {res} while its gate is closed (REQ-080)")
    if b["summary"] != summary(b):
        errors.append("summary rows do not match the cases (REQ-091)")
    return errors


def regressions(old: dict, new: dict) -> list[str]:
    """REQ-006: what regressed in `new` against the earlier baseline `old`."""
    found = []
    old_cases = {(c["part"], c["case"]): c for c in old["cases"]}
    flips = []
    for c in new["cases"]:
        before = old_cases.get((c["part"], c["case"]))
        if before is None:
            continue
        ids = {k for r in before["runs"] for k in r["deterministic"]}
        for cid in sorted(ids):
            was_3_of_3 = len(before["runs"]) == 3 and all(r["deterministic"].get(cid) for r in before["runs"])
            fails_now = any(r["deterministic"].get(cid) is False for r in c["runs"])
            if was_3_of_3 and fails_now:
                found.append(f"{c['case']} {cid}: passed 3 of 3, now fails in a run")
        for cid, res in c["judged_results"].items():
            if before["judged_results"].get(cid) == judge.PASS and res == judge.FAIL:
                flips.append(f"{c['case']} {cid}")
    if len(flips) >= 2:
        found.append("judged checks flipped from pass to fail: " + ", ".join(flips))
    return found


def write(b: dict, out_dir: Path) -> Path:
    """Write the baseline as out_dir/eval-baseline-YYYY-MM-DD.json, refusing an invalid one."""
    errors = validate(b)
    if errors:
        raise ValueError("invalid baseline: " + "; ".join(errors[:5]))
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"eval-baseline-{b['date']}.json"
    path.write_text(json.dumps(b, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def recheck(path: Path) -> list[str]:
    """REQ-092: re-run the deterministic checks on the saved outputs beside a baseline.

    Returns each result that differs from the one the baseline records.
    """
    b = json.loads(path.read_text(encoding="utf-8"))
    diffs = []
    for c in b["cases"]:
        for r in c["runs"]:
            text = (path.parent / r["output"]).read_text(encoding="utf-8")
            now = {x.check: x.passed for x in checks.run(c["part"], text, c["case"])}
            for cid, was in r["deterministic"].items():
                if now.get(cid) != was:
                    diffs.append(f"{c['case']} run {r['run']} {cid}: baseline {was}, now {now.get(cid)}")
    return diffs
