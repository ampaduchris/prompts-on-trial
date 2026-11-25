"""README claims (REQ-112)."""

import pytest


@pytest.mark.req("REQ-112")
def test_readme_states_licence_disclosure_and_the_live_search_limit(root):
    body = (root / "README.md").read_text(encoding="utf-8")
    assert "MIT" in body
    assert "Built by directing Claude Code. No hand-written code." in body
    assert "NOT VERIFIED" in body and "live search" in body.lower()


@pytest.mark.req("REQ-112")
def test_readme_says_no_model_was_run_and_how_to_run_one(root):
    body = (root / "README.md").read_text(encoding="utf-8")
    assert "No model was run for v1.0" in body
    assert "own key" in body and "uv run python evals/run.py --generator" in body
