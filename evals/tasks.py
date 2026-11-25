"""Inspect AI tasks for the model path (spec section 1.2). Runs locally on the user's key only.

    uv sync --group evals
    uv run inspect eval evals/tasks.py@travel_method --model anthropic/<model id>

Each task sends every case of one part to the model three times (epochs=3, REQ-005) and scores
each output with the deterministic checks. A score is "C" only when every check passes; the
metadata holds every check result, so all three runs are reported. The judged checks are added
in session 7.3. Continuous integration never runs this file (REQ-004).
"""

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState, generate

from prompts_on_trial import cases, checks, inputs

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


def _task(part: str) -> Task:
    return Task(dataset=_dataset(part), solver=[generate()], scorer=deterministic_checks(), epochs=EPOCHS)


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


__all__ = ["cases", "cognitive_profile", "tailoring_doctrine", "travel_method"]
