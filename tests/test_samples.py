"""The checker path (spec section 1.2): every deterministic check against recorded sample outputs.

Each planted-bad sample in evals/samples/manifest.yaml is one edit to a good sample and must fail
exactly the checks it names. Each good sample must pass every check. A check that no planted-bad
sample fails is reported as a gap by `test_every_check_has_a_failing_sample`.
"""

from pathlib import Path

import pytest
import yaml

from prompts_on_trial.checks import PARTS, run

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "evals" / "samples"
MANIFEST = yaml.safe_load((SAMPLES / "manifest.yaml").read_text(encoding="utf-8"))["samples"]
BY_ID = {e["id"]: e for e in MANIFEST}


def _failed(entry: dict) -> list[str]:
    text = (SAMPLES / entry["file"]).read_text(encoding="utf-8")
    return sorted(r.check for r in run(entry["part"], text, entry["case"]) if not r.passed)


@pytest.mark.parametrize("entry", MANIFEST, ids=[e["id"] for e in MANIFEST])
def test_sample_fails_exactly_its_named_checks(entry):
    assert _failed(entry) == sorted(entry["must_fail"])


@pytest.mark.parametrize("entry", [e for e in MANIFEST if e["must_fail"]], ids=lambda e: e["id"])
def test_bad_sample_is_one_edit_to_its_base(entry):
    base = BY_ID[entry["base"]]
    assert not base["must_fail"], "a planted-bad sample is made from a good one"
    bad = (SAMPLES / entry["file"]).read_text(encoding="utf-8")
    good = (SAMPLES / base["file"]).read_text(encoding="utf-8")
    if entry["case"] == base["case"]:
        assert bad != good


def test_every_check_has_a_failing_sample():
    failed_somewhere = {c for e in MANIFEST for c in e["must_fail"]}
    every_check = {c for checks, _ in PARTS.values() for c in checks}
    # TA-D11 (canary in the CV block) is proved by unit tests in test_checks.py.
    assert every_check - failed_somewhere == {"TA-D11"}


def _check_is_proved(check: str) -> None:
    """The check passes every good sample of its part and fails at least one planted-bad one."""
    part = next(p for p, (checks, _) in PARTS.items() if check in checks)
    goods = [e for e in MANIFEST if e["part"] == part and not e["must_fail"]]
    bads = [e for e in MANIFEST if check in e["must_fail"]]
    assert goods and bads
    for e in goods:
        assert check not in _failed(e), e["id"]
    for e in bads:
        assert check in _failed(e), e["id"]


@pytest.mark.req("REQ-010")
def test_cp_d1():
    _check_is_proved("CP-D1")


@pytest.mark.req("REQ-011")
def test_cp_d2():
    _check_is_proved("CP-D2")


@pytest.mark.req("REQ-012")
def test_cp_d3():
    _check_is_proved("CP-D3")


@pytest.mark.req("REQ-013")
def test_cp_d4():
    _check_is_proved("CP-D4")


@pytest.mark.req("REQ-014")
def test_cp_d5():
    _check_is_proved("CP-D5")


@pytest.mark.req("REQ-015")
def test_cp_d6():
    _check_is_proved("CP-D6")


@pytest.mark.req("REQ-016")
def test_cp_d7():
    _check_is_proved("CP-D7")


@pytest.mark.req("REQ-017")
def test_cp_d8():
    _check_is_proved("CP-D8")


@pytest.mark.req("REQ-018")
def test_cp_d9():
    _check_is_proved("CP-D9")


@pytest.mark.req("REQ-019")
def test_cp_d10():
    _check_is_proved("CP-D10")


@pytest.mark.req("REQ-020")
def test_cp_d11():
    _check_is_proved("CP-D11")


@pytest.mark.req("REQ-021")
def test_cp_d12():
    _check_is_proved("CP-D12")


@pytest.mark.req("REQ-042")
def test_tr_d1():
    _check_is_proved("TR-D1")


@pytest.mark.req("REQ-043")
def test_tr_d2():
    _check_is_proved("TR-D2")


@pytest.mark.req("REQ-044")
def test_tr_d3():
    _check_is_proved("TR-D3")


@pytest.mark.req("REQ-045")
def test_tr_d4():
    _check_is_proved("TR-D4")


@pytest.mark.req("REQ-046")
def test_tr_d5():
    _check_is_proved("TR-D5")


@pytest.mark.req("REQ-047")
def test_tr_d6():
    _check_is_proved("TR-D6")


@pytest.mark.req("REQ-048")
def test_tr_d7():
    _check_is_proved("TR-D7")


@pytest.mark.req("REQ-049")
def test_tr_d8():
    _check_is_proved("TR-D8")


@pytest.mark.req("REQ-050")
def test_tr_d9():
    _check_is_proved("TR-D9")


@pytest.mark.req("REQ-051")
def test_tr_d10():
    _check_is_proved("TR-D10")


@pytest.mark.req("REQ-052")
def test_tr_s1():
    _check_is_proved("TR-S1")


@pytest.mark.req("REQ-060")
def test_ta_d1():
    _check_is_proved("TA-D1")


@pytest.mark.req("REQ-061")
def test_ta_d2():
    _check_is_proved("TA-D2")


@pytest.mark.req("REQ-062")
def test_ta_d3():
    _check_is_proved("TA-D3")


@pytest.mark.req("REQ-063")
def test_ta_d4():
    _check_is_proved("TA-D4")


@pytest.mark.req("REQ-064")
def test_ta_d5():
    _check_is_proved("TA-D5")


@pytest.mark.req("REQ-065")
def test_ta_d6():
    _check_is_proved("TA-D6")


@pytest.mark.req("REQ-066")
def test_ta_d7():
    _check_is_proved("TA-D7")


@pytest.mark.req("REQ-067")
def test_ta_d8():
    _check_is_proved("TA-D8")


@pytest.mark.req("REQ-068")
def test_ta_d9():
    _check_is_proved("TA-D9")


@pytest.mark.req("REQ-069")
def test_ta_d10():
    _check_is_proved("TA-D10")
