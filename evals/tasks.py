"""Inspect AI tasks for the model path (spec section 1.2). Runs locally on the user's key only.

    uv sync --group evals
    uv run inspect eval evals/tasks.py@travel_method --model anthropic/<model id>

Each task sends every case of one part to the model three times (epochs=3, REQ-005) and scores
each output with the deterministic checks, then with every judged check that applies to the case.
The judge is the model bound to the `grader` role (`--model-role grader=<model id>`), or the
generator when no role is given. The metadata holds every check result and every judge reply, so
all three runs are reported. The Inspect AI score of a run is not the result: evals/run.py applies
the 2-of-3 rule and the known-bad gate (REQ-001, REQ-080) and writes the baseline (REQ-090).

`judge_gate` puts each known-bad output of evals/judge/ to the judge three times. Run it with the
judge as the model. evals/run.py runs it before the three parts.

No model was run for v1.0. Continuous integration runs this file only on Inspect AI's offline mock
model, with canned judge replies (tests/test_mock_runner.py); it never calls a model (REQ-004).
"""

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.model import get_model
from inspect_ai.solver import TaskState, generate

from prompts_on_trial import cases, checks, inputs, judge

EPOCHS = 3


def _dataset(part: str) -> MemoryDataset:
    ids = [c for p, c in inputs.all_cases() if p == part]
    return MemoryDataset(
        [Sample(id=c, input=inputs.build(part, c), metadata={"part": part, "case": c}) for c in ids],
        name=f"prompts-on-trial-{part}",
    )


@scorer(metrics=[accuracy(), stderr()])
def deterministic_checks():
    async def score(state: TaskState, target: Target) -> Score:
        part, case = state.metadata["part"], state.metadata["case"]
        results = checks.run(part, state.output.completion, case)
        failed = [r for r in results if not r.passed]
        return Score(
            value=INCORRECT if failed else CORRECT,
            answer=state.output.completion[:200],
            explanation="; ".join(str(r) for r in failed) or "all deterministic checks pass",
            metadata={r.check: r.passed for r in results},
        )

    return score


@scorer(metrics=[accuracy(), stderr()])
def judged_checks():
    """One judge call per judged check that applies to the case, in each run (spec 3.3, 4.3, 5.3).

    The value is the share of answers that count as yes in this run (REQ-001). It is a progress
    figure only; the reported result is computed by evals/run.py.
    """

    async def score(state: TaskState, target: Target) -> Score:
        part, case = state.metadata["part"], state.metadata["case"]
        output = state.output.completion
        grader = get_model(role="grader")
        answers = {}
        for jc in judge.for_case(part, case):
            reply = await grader.generate(judge.prompt(jc.id, case, output))
            answers[jc.id] = judge.read_answer(reply.completion, output).to_dict()
        yes = sum(a["counts_as_yes"] for a in answers.values())
        return Score(
            value=yes / len(answers) if answers else 1.0,
            explanation=", ".join(f"{k} {a['said']}" for k, a in answers.items()) or "no judged check applies",
            metadata={"judged": answers},
        )

    return score


def _task(part: str) -> Task:
    return Task(
        dataset=_dataset(part),
        solver=[generate()],
        scorer=[deterministic_checks(), judged_checks()],
        epochs=EPOCHS,
    )


@scorer(metrics=[accuracy()])
def gate_answer():
    """C when the judge says a clear no to a known-bad output (REQ-080)."""

    async def score(state: TaskState, target: Target) -> Score:
        kb = judge.known_bad()[state.metadata["fixture"]]
        a = judge.read_answer(state.output.completion, kb.text())
        return Score(value=CORRECT if a.said == judge.NO else INCORRECT, answer=a.said, metadata=a.to_dict())

    return score


@task
def judge_gate() -> Task:
    """Every known-bad output put to the judge for each judged check it is known-bad for."""
    samples = [
        Sample(
            id=f"{kb.id}:{cid}",
            input=judge.prompt(cid, kb.case, kb.text()),
            metadata={"fixture": kb.id, "check": cid, "case": kb.case},
        )
        for kb in judge.known_bad().values()
        for cid in kb.checks
    ]
    return Task(dataset=MemoryDataset(samples, name="prompts-on-trial-judge-gate"), solver=[generate()], scorer=gate_answer(), epochs=EPOCHS)


@task
def cognitive_profile() -> Task:
    """Part A: six synthetic histories (spec section 3)."""
    return _task("A")


@task
def travel_method() -> Task:
    """Part B: eight synthetic trips (spec section 4)."""
    return _task("B")


@task
def tailoring_doctrine() -> Task:
    """Part C: eight synthetic requisitions against one synthetic record (spec section 5)."""
    return _task("C")


__all__ = ["cases", "cognitive_profile", "judge_gate", "tailoring_doctrine", "travel_method"]
