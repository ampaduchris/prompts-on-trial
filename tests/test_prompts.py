"""The three public prompts (REQ-100, REQ-102, REQ-103, REQ-104)."""

import pytest

PROMPTS = ["cognitive-profile", "travel-method", "tailoring-doctrine"]

CONTRACT = {
    "cognitive-profile": ["Output contract", "## 10. Validity", "`Pattern N: label`", "Valid as of"],
    "travel-method": ["OUTPUT CONTRACT", "## 1. Ranked options", "## 5. Sources", "`OPT-A`"],
    "tailoring-doctrine": ["Output contract", "## Mapping", "## CV", "## Memo", "`Gaps:`", "`Knockouts:`"],
}


def text(root, name):
    return (root / "prompts" / f"{name}.md").read_text(encoding="utf-8")


@pytest.mark.req("REQ-100")
@pytest.mark.parametrize("name", PROMPTS)
def test_prompt_exists_and_names_itself_a_rewrite(root, name):
    body = text(root, name)
    assert len(body.split()) > 800
    assert "public rewrite" in body


@pytest.mark.req("REQ-102")
@pytest.mark.parametrize("name", PROMPTS)
def test_prompt_ends_with_its_contract(root, name):
    body = text(root, name)
    for marker in CONTRACT[name]:
        assert marker in body, marker


@pytest.mark.req("REQ-103")
def test_travel_profile_is_synthetic(root):
    body = text(root, "travel-method")
    assert "STANDING PROFILE (synthetic" in body
    assert "Alpine Miles" in body and "Harbour Points" in body


@pytest.mark.req("REQ-104")
def test_cognitive_profile_asks_for_up_to_twelve(root):
    body = text(root, "cognitive-profile")
    assert "Up to twelve" in body
    assert "Six to twelve" not in body
