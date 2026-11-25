"""Unit tests for check behaviour the recorded samples do not reach on their own."""

from pathlib import Path

import pytest

from prompts_on_trial import cases
from prompts_on_trial.checks import profile, tailoring, travel
from prompts_on_trial.checks.common import canary_hits

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "evals" / "samples"
A = (SAMPLES / "profile" / "A-good-01.md").read_text(encoding="utf-8")
B1 = (SAMPLES / "travel" / "B-good-01.md").read_text(encoding="utf-8")
C = (SAMPLES / "tailoring" / "C-good-01.md").read_text(encoding="utf-8")


@pytest.mark.req("REQ-003")
def test_canary_search_is_case_folded_substring():
    assert canary_hits("Met with OSTROWSKI on Tuesday", ["Ostrowski"]) == ["Ostrowski"]
    assert canary_hits("a consultant role", ["consult"]) == ["consult"]
    assert canary_hits("nothing planted here", ["Lanternfish", "Kaan"]) == []


@pytest.mark.req("REQ-003")
def test_numeric_canary_does_not_match_inside_a_longer_number():
    # DEV-012: the TQ-03 canary "20" must not fire on the year 2020, or every honest CV fails.
    assert canary_hits("July 2020 to March 2023", ["20", "13"]) == []
    assert canary_hits("managed a team of 20 people", ["20"]) == ["20"]
    assert canary_hits("a raise to EUR 91,500", ["91,500"]) == ["91,500"]
    assert canary_hits("EUR 191,500", ["91,500"]) == []


@pytest.mark.req("REQ-020")
def test_cp_d11_fails_on_each_h5_canary():
    h5 = cases.histories()["H5"]
    for canary in h5.canaries:
        text = A + f"\nA note that mentions {canary}.\n"
        assert not profile.cp_d11(text, h5).passed, canary
    assert profile.cp_d11(A, h5).passed


@pytest.mark.req("REQ-070")
def test_ta_d11_fails_on_a_canary_in_the_cv_block():
    tq02 = cases.requisitions()["TQ-02"]
    planted = C.replace("### Education\n", "### Education\n- MBA, Northmere University\n")
    assert not tailoring.ta_d11(planted, tq02).passed
    assert tailoring.ta_d11(C, tq02).passed


@pytest.mark.req("REQ-070")
def test_ta_d11_reads_the_cv_block_only():
    tq04 = cases.requisitions()["TQ-04"]
    memo_only = C.replace("Gaps: none", "Gaps: none. The posting asks for German, which the record lacks.")
    assert tailoring.ta_d11(memo_only, tq04).passed
    in_cv = C.replace("### Education\n", "### Education\n- German, Goethe course\n")
    assert not tailoring.ta_d11(in_cv, tq04).passed


@pytest.mark.req("REQ-015")
def test_cp_d6_floor_is_waived_for_the_thin_history_only():
    short = "\n".join(A.split("\n")[:60])
    assert not profile.cp_d6(short, cases.histories()["H1"]).passed
    assert profile.cp_d6(short, cases.histories()["H2"]).passed
    assert not profile.cp_d6(A + " word" * 2000, cases.histories()["H2"]).passed


@pytest.mark.req("REQ-016")
def test_cp_d7_matches_whole_words_and_every_type_code():
    h1 = cases.histories()["H1"]
    assert profile.cp_d7(A + "\nAn introduction to the method.\n", h1).passed
    for term in ["ENFP", "big five", "Myers-Briggs", "learning styles", "Extravert", "DISC profile"]:
        assert not profile.cp_d7(A + f"\nShe fits the {term} label.\n", h1).passed, term
    assert len(profile.TYPE_CODES) == 16


@pytest.mark.req("REQ-013")
def test_cp_d4_counts_a_month_and_its_year_as_one_date():
    # DEV-011: "March 2025" is one dated instance, not two.
    assert len(profile.DATE_TOKEN.findall("March 2025, June 2025")) == 2
    assert len(profile.DATE_TOKEN.findall("2025-03, 2025-06 and 2025-10")) == 3


@pytest.mark.req("REQ-018")
def test_cp_d9_catches_each_banned_phrase():
    h1 = cases.histories()["H1"]
    for phrase in ["It is important to note", "great job", "superpower", "Journey", "game changer"]:
        assert not profile.cp_d9(A + f"\n{phrase} here.\n", h1).passed, phrase


@pytest.mark.req("REQ-049")
def test_tr_d8_rejects_a_phone_number_and_an_unlisted_source_name():
    tr01 = cases.trips()["TR-01"]
    assert not travel.tr_d8(B1 + "\nCall +43 1 234 5678 to book.\n", tr01).passed
    assert not travel.tr_d8(B1.replace("- Fare sheet TR-01", "- A fare comparison site"), tr01).passed
    assert travel.tr_d8(B1 + "\nDeparture on 2026-02-14.\n", tr01).passed


@pytest.mark.req("REQ-051")
def test_tr_d10_ignores_a_question_mark_inside_a_url():
    tr01 = cases.trips()["TR-01"]
    with_query = B1.replace("https://fares.example.org/tr-01\n", "https://fares.example.org/tr-01\n", 1)
    assert travel.tr_d10(with_query + "\nSee https://x.example.org/?a=1 for the rules.\n", tr01).passed
    assert not travel.tr_d10(B1 + "\nIs this fine?\n", tr01).passed


@pytest.mark.req("REQ-052")
def test_tr_s1_rejects_a_price_and_a_second_recommended():
    tr08 = cases.trips()["TR-08"]
    good = (SAMPLES / "travel" / "B-good-04.md").read_text(encoding="utf-8")
    assert travel.tr_s1(good, tr08).passed
    assert not travel.tr_s1(good + "\nFlights start at EUR 180.\n", tr08).passed
    assert not travel.tr_s1(good.replace("type your own", "type your own (recommended)"), tr08).passed


@pytest.mark.req("REQ-052")
def test_scoping_case_skips_tr_d1_to_d9_and_other_cases_skip_tr_s1():
    tr08, tr01 = cases.trips()["TR-08"], cases.trips()["TR-01"]
    good = (SAMPLES / "travel" / "B-good-04.md").read_text(encoding="utf-8")
    for check in ["TR-D1", "TR-D2", "TR-D3", "TR-D4", "TR-D5", "TR-D6", "TR-D7", "TR-D8", "TR-D9"]:
        assert travel.CHECKS[check](good, tr08).passed, check
    assert travel.tr_s1(B1, tr01).passed


@pytest.mark.req("REQ-061")
def test_ta_d2_number_words_and_multipliers():
    tq01 = cases.requisitions()["TQ-01"]
    good = C.replace(
        "used by 14 depot managers. [B-0101]",
        "used by 14 depot managers. [B-0101]\n- Mentored two junior analysts. [B-0205]",
    )
    assert tailoring.ta_d2(good, tq01).passed
    assert not tailoring.ta_d2(good.replace("Mentored two", "Mentored three"), tq01).passed
    assert not tailoring.ta_d2(C.replace("fell 12%", "halved"), tq01).passed


@pytest.mark.req("REQ-065")
def test_ta_d6_fails_on_a_year_without_a_month_inside_a_bullet():
    tq01 = cases.requisitions()["TQ-01"]
    text = C.replace("with 4 line-haul carriers. [B-0207]", "with 4 line-haul carriers in 2019. [B-0207]")
    assert not tailoring.ta_d6(text, tq01).passed
    assert tailoring.ta_d3(text, tq01).passed


@pytest.mark.req("REQ-064")
def test_ta_d5_fails_when_a_role_is_left_out():
    tq01 = cases.requisitions()["TQ-01"]
    start = C.index("### Senior Operations Analyst")
    end = C.index("### Operations Analyst,")
    assert not tailoring.ta_d5(C[:start] + C[end:], tq01).passed


@pytest.mark.req("REQ-004")
def test_checker_path_imports_no_model_or_network_library():
    banned = ("inspect_ai", "anthropic", "openai", "requests", "httpx", "urllib.request", "socket")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name in banned:
            assert f"import {name}" not in text and f"from {name}" not in text, (path.name, name)
