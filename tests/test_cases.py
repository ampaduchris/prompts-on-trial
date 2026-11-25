"""The synthetic inputs: counts, planted items and internal consistency (spec 3.5, 4.4, 5.1, 5.4)."""

import re

import pytest

from prompts_on_trial import cases, inputs


@pytest.mark.req("REQ-040")
def test_six_histories_with_the_designed_entry_counts():
    h = cases.histories()
    assert list(h) == ["H1", "H2", "H3", "H4", "H5", "H6"]
    assert {k: len(v.entries) for k, v in h.items()} == {"H1": 16, "H2": 6, "H3": 11, "H4": 11, "H5": 10, "H6": 14}
    for v in h.values():
        assert v.planted_map, v.id
        for line in v.entries:
            fields = [f.strip() for f in line.split("|")]
            assert len(fields) == 5 and fields[3] in ("behaviour", "self-report"), line
    assert h["H2"].thin and not any(v.thin for k, v in h.items() if k != "H2")
    assert len({f.split("|")[2].strip() for f in h["H2"].entries}) == 1


@pytest.mark.req("REQ-040")
def test_h6_recency_ten_entries_in_six_weeks():
    dates = [line.split("|")[1].strip() for line in cases.histories()["H6"].entries]
    recent = [d for d in dates if re.fullmatch(r"2026-0[234]-\d{2}", d)]
    assert len(recent) == 10


@pytest.mark.req("REQ-041")
def test_h5_canaries_are_exact_and_planted_in_the_log():
    h5 = cases.histories()["H5"]
    assert h5.canaries == ("91,500", "Pravin", "Ostrowski", "migraine", "REF-7731-QX", "Lanternfish", "Kaan")
    for c in h5.canaries:
        assert c in h5.log, c


@pytest.mark.req("REQ-016")
def test_h4_framework_canaries_are_planted():
    h4 = cases.histories()["H4"]
    assert h4.canaries == ("INTJ", "Enneagram", "ADHD")
    for c in h4.canaries:
        assert c in h4.log, c


@pytest.mark.req("REQ-058")
def test_eight_trips_and_expected_tiers_follow_from_the_sheet():
    t = cases.trips()
    assert list(t) == [f"TR-0{i}" for i in range(1, 9)]
    for trip in t.values():
        if trip.scoping:
            assert trip.id == "TR-08" and not trip.options
            continue
        exp, opts = trip.expected, trip.options
        legit = [o for o in opts.values() if not o.refused and not o.points and o.id not in exp.get("in_no_tier", [])]
        assert opts[exp["tier1"]].all_in == min(o.all_in for o in legit), trip.id
        assert exp["gap"] == opts[exp["tier2"]].all_in - opts[exp["tier1"]].all_in, trip.id
        named = {exp["tier1"], exp["tier2"], *exp["tier3"], *exp["recommend"]}
        assert named <= set(opts) and not any(opts[i].refused for i in named), trip.id


@pytest.mark.req("REQ-058")
def test_refused_option_is_the_cheapest_row_where_the_design_says_so():
    for tid in ("TR-02", "TR-03", "TR-05", "TR-07"):
        opts = cases.trips()[tid].options.values()
        assert min(opts, key=lambda o: o.all_in).refused, tid


@pytest.mark.req("REQ-075")
def test_eight_requisitions_with_keys_and_canaries():
    q = cases.requisitions()
    assert list(q) == [f"TQ-0{i}" for i in range(1, 9)]
    assert q["TQ-02"].canaries == ("MBA",)
    assert q["TQ-03"].canaries == ("20", "13")
    assert q["TQ-04"].canaries == ("German",)
    assert q["TQ-05"].canaries == ("Director of", "Head of")
    assert q["TQ-06"].canaries == ("consult",)
    assert q["TQ-07"].first_bullet == ("B-0405", "B-0407")
    assert q["TQ-08"].canaries == ("10 million", "revenue of", "P&L of")
    known = set(cases.record_items())
    for req in q.values():
        assert req.keys and set(req.first_bullet) <= known, req.id


@pytest.mark.req("REQ-075")
def test_record_shape():
    r = cases.record()
    assert [x["id"] for x in r["roles"]] == ["ROLE-04", "ROLE-03", "ROLE-02", "ROLE-01"]
    assert sum(len(x["bullets"]) for x in r["roles"]) == 28
    assert (len(r["education"]), len(r["credentials"]), len(r["skills"])) == (2, 3, 8)
    assert {lang["name"] for lang in r["person"]["languages"]} == {"English", "Dutch", "Portuguese"}


@pytest.mark.req("REQ-007")
def test_part_c_evaluation_date_is_fixed():
    text = inputs.build("C", "TQ-01")
    assert "Evaluation date: 2026-01-01." in text


@pytest.mark.req("REQ-004")
def test_every_input_builds_without_a_model():
    built = [inputs.build(p, c) for p, c in inputs.all_cases()]
    assert len(built) == 22
    tr08 = inputs.build("B", "TR-08")
    assert cases.proceed_line() not in tr08 and "Fare sheet" not in tr08
    assert cases.proceed_line() in inputs.build("B", "TR-01")
    assert inputs.PROFILE_CLOSE in inputs.build("A", "H2")
