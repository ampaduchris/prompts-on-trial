"""The runner on Inspect AI's offline mock model, with canned judge replies (REQ-080, REQ-090).

Skipped where Inspect AI is not installed. Continuous integration installs the `evals` group for a
separate step that runs this file. The mock model makes no network call; no model is called.
"""

import importlib.util
import re
from pathlib import Path

import pytest

inspect_ai = pytest.importorskip("inspect_ai")
from inspect_ai.model import ModelOutput, get_model  # noqa: E402

from prompts_on_trial import baseline, inputs, judge  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = {
    "A": ROOT / "evals/samples/profile/A-good-01.md",
    "B": ROOT / "evals/samples/travel/B-good-01.md",
    "C": ROOT / "evals/samples/tailoring/C-good-01.md",
}
KNOWN_BAD = {kb.text().rstrip() for kb in judge.known_bad().values()}
OUTPUT = re.compile(r"Output to check:\n<<<\n(.*)\n>>>", re.DOTALL)


def _runner():
    spec = importlib.util.spec_from_file_location("run", ROOT / "evals" / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _text(messages) -> str:
    return "\n".join(m.text for m in messages)


def generator():
    """Answers every case with the reference output of its part."""

    def out(messages, *_):
        prompt = _text(messages)
        ref = next(p for part, p in REFERENCE.items() if prompt.startswith(inputs.prompt(part)))
        return ModelOutput.from_content("mockllm/model", ref.read_text(encoding="utf-8"))

    return get_model("mockllm/model", custom_outputs=out, memoize=False)


def canned_judge(yes_to_known_bad: bool):
    """Says no to every known-bad output (or yes, for a broken judge) and yes to anything else."""

    def out(messages, *_):
        output = OUTPUT.search(_text(messages)).group(1)
        quote = next(line for line in output.splitlines() if line.strip())
        said = "yes" if (output.rstrip() not in KNOWN_BAD or yes_to_known_bad) else "no"
        return ModelOutput.from_content("mockllm/model", f'ANSWER: {said}\nQUOTE: "{quote}"')

    return get_model("mockllm/model", custom_outputs=out, memoize=False)


@pytest.mark.req("REQ-080")
def test_runner_with_a_judge_that_fails_every_known_bad_output(tmp_path):
    path, b, regressions = _runner().run(generator(), canned_judge(False), tmp_path, date="2026-11-25")
    assert all(g["open"] for g in b["gate"].values())
    results = {r for c in b["cases"] for r in c["judged_results"].values()}
    assert results == {judge.PASS}
    assert baseline.validate(b) == [] and regressions == []


@pytest.mark.req("REQ-080")
def test_runner_withholds_every_score_of_a_judge_that_passes_known_bad_outputs(tmp_path):
    path, b, _ = _runner().run(generator(), canned_judge(True), tmp_path, date="2026-11-25")
    assert not any(g["open"] for g in b["gate"].values())
    results = {r for c in b["cases"] for r in c["judged_results"].values()}
    assert results == {judge.NOT_VERIFIED}
    assert b["summary"]["judged_2_of_3_or_better"] == 0
    assert b["summary"]["judged_not_verified_gate_closed"] == sum(len(c["judged_results"]) for c in b["cases"])


@pytest.mark.req("REQ-090")
def test_runner_saves_outputs_and_a_baseline_the_checker_path_can_rerun(tmp_path):
    path, b, _ = _runner().run(generator(), canned_judge(False), tmp_path, date="2026-11-25")
    assert path == tmp_path / "eval-baseline-2026-11-25.json"
    assert len(list((tmp_path / "outputs").rglob("*.md"))) == 66
    assert baseline.recheck(path) == []
    assert b["judge_relation"] == "same model as generator"


@pytest.mark.req("REQ-080")
def test_gate_task_scores_a_clear_no_as_correct(tmp_path):
    from inspect_ai import eval as inspect_eval

    tasks = _runner().tasks
    for broken, want in ((False, "C"), (True, "I")):
        log = inspect_eval(tasks.judge_gate(), model=canned_judge(broken), display="none", log_dir=str(tmp_path), limit=2)[0]
        assert log.status == "success"
        assert {s.scores["gate_answer"].value for s in log.samples} == {want}
