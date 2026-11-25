"""The runner for the model path (spec sections 1.2, 6 and 7). Runs only on the user's own key.

    uv sync --group evals
    uv run python evals/run.py --generator anthropic/<model id> --judge openai/<model id> \\
        --out evals/runs/<date> [--compare <earlier eval-baseline-*.json>]

Order of work:
1. The known-bad gate: every known-bad output goes to the judge 3 times (REQ-080).
2. The three parts: every input goes to the generator 3 times; each output is scored by the
   deterministic checks and by every judged check that applies (REQ-001, REQ-005).
3. Every output is saved under <out>/outputs/, and <out>/eval-baseline-YYYY-MM-DD.json is written
   with its summary rows (REQ-090 to 092). A judged check whose gate is closed is NOT VERIFIED.
4. With --compare, the regression rule of REQ-006 is applied against the earlier baseline.

No model was run for v1.0 and no baseline is committed. evals/runs/ is ignored by git.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from inspect_ai import eval as inspect_eval
from inspect_ai.model import Model

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tasks  # noqa: E402

from prompts_on_trial import baseline, checks, judge  # noqa: E402


def _name(model: str | Model) -> str:
    return str(model)


def _ok(log):
    if log.status != "success":
        raise RuntimeError(f"{log.eval.task}: {log.error.message if log.error else log.status}")
    return log


def run(
    generator: str | Model,
    judge_model: str | Model,
    out_dir: Path,
    date: str | None = None,
    compare: Path | None = None,
    display: str = "none",
) -> tuple[Path, dict, list[str]]:
    """Run the gate and the three parts, write the baseline, return (path, baseline, regressions)."""
    date = date or datetime.date.today().isoformat()
    logs_dir = str(out_dir / "logs")
    fixtures = judge.known_bad()

    gate_log = _ok(inspect_eval(tasks.judge_gate(), model=judge_model, display=display, log_dir=logs_dir)[0])
    by_epoch: dict[str, dict[str, list[tuple[int, judge.Answer]]]] = {}
    for s in gate_log.samples or []:
        fid, cid = s.metadata["fixture"], s.metadata["check"]
        answer = judge.read_answer(s.output.completion, fixtures[fid].text())
        by_epoch.setdefault(cid, {}).setdefault(fid, []).append((s.epoch, answer))
    gate_answers = {cid: {fid: [a for _, a in sorted(v, key=lambda x: x[0])] for fid, v in f.items()} for cid, f in by_epoch.items()}

    logs = inspect_eval(
        [tasks.cognitive_profile(), tasks.travel_method(), tasks.tailoring_doctrine()],
        model=generator,
        model_roles={"grader": judge_model},
        display=display,
        log_dir=logs_dir,
    )
    runs = []
    for log in map(_ok, logs):
        for s in log.samples or []:
            part, case, text = s.metadata["part"], s.metadata["case"], s.output.completion
            rel = f"outputs/{part}/{case}-run{s.epoch}.md"
            (out_dir / rel).parent.mkdir(parents=True, exist_ok=True)
            (out_dir / rel).write_text(text, encoding="utf-8")
            det = {r.check: r.passed for r in checks.run(part, text, case)}
            replies = s.scores["judged_checks"].metadata["judged"]
            jud = {cid: judge.read_answer(a["raw"], text) for cid, a in replies.items()}
            runs.append(baseline.Run(part, case, s.epoch, rel, det, jud))

    b = baseline.build(_name(generator), _name(judge_model), date, gate_answers, runs)
    path = baseline.write(b, out_dir)
    regressions = baseline.regressions(json.loads(compare.read_text(encoding="utf-8")), b) if compare else []
    return path, b, regressions


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--generator", required=True, help="Inspect AI model id of the model under test")
    ap.add_argument("--judge", help="Inspect AI model id of the judge (default: the generator)")
    ap.add_argument("--out", type=Path, required=True, help="folder for the baseline and the outputs")
    ap.add_argument("--compare", type=Path, help="an earlier eval-baseline-*.json (REQ-006)")
    args = ap.parse_args(argv)
    path, b, regressions = run(args.generator, args.judge or args.generator, args.out, compare=args.compare, display="full")
    print(f"baseline: {path}")
    print(f"judge: {b['judge_relation']}")
    for k, v in b["summary"].items():
        print(f"{k}: {v}")
    closed = sorted(c for c, g in b["gate"].items() if not g["open"])
    print("gate closed (NOT VERIFIED): " + (", ".join(closed) or "none"))
    for r in regressions:
        print(f"REGRESSION: {r}")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
