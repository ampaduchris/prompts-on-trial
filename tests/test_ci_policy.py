"""CI never calls a model (REQ-004)."""

import re

import pytest

SDKS = re.compile(r"\b(anthropic|openai|inspect_ai|inspect-ai)\b")


@pytest.mark.req("REQ-004")
def test_no_model_sdk_in_the_runtime_package(root):
    for path in (root / "src").rglob("*.py"):
        assert not SDKS.search(path.read_text(encoding="utf-8")), path


@pytest.mark.req("REQ-004")
def test_workflow_holds_no_model_key(root):
    for path in (root / ".github" / "workflows").glob("*.yml"):
        body = path.read_text(encoding="utf-8")
        secrets = set(re.findall(r"secrets\.(\w+)", body))
        assert secrets <= {"GITHUB_TOKEN"}, (path.name, secrets)


@pytest.mark.req("REQ-080")
def test_ci_runs_the_judge_rules_on_the_mock_model(root):
    body = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "uv sync --locked --group evals" in body
    assert "pytest -q --tb=short -p no:logging tests/test_mock_runner.py" in body
