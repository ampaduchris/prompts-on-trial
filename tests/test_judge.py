"""The judged checks and the rules around the judge, on canned judge answers (spec sections 2, 3.3,
4.3, 5.3, 6 and 7). No model is called: every judge reply here is a string written in this file.

How well any real judge judges is NOT VERIFIED. These tests prove the rules, not the judge.
"""

import json
from pathlib import Path

import pytest
import yaml

from prompts_on_trial import baseline, checks, inputs, judge

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "evals" / "samples"
REFERENCE = {"A": "profile/A-good-01.md", "B": "travel/B-good-01.md", "C": "tailoring/C-good-01.md"}

H = [f"H{i}" for i in range(1, 7)]
TR = [f"TR-0{i}" for i in range(1, 8)]
TQ = [f"TQ-0{i}" for i in range(1, 9)]
APPLIES = {
    "CP-J1": H, "CP-J2": H, "CP-J3": H, "CP-J4": H, "CP-J5": H,
    "CP-J6": ["H3", "H6"], "CP-J7": ["H2", "H6"],
    "TR-J1": ["TR-02", "TR-03", "TR-05", "TR-07"],
    "TR-J2": ["TR-01", "TR-03", "TR-04", "TR-05", "TR-06"],
    "TR-J3": TR, "TR-J4": TR, "TR-J5": TR,
    "TA-J1": TQ, "TA-J2": TQ, "TA-J3": ["TQ-01", "TQ-07"], "TA-J4": ["TQ-03", "TQ-04", "TQ-06", "TQ-08"],
}


def reply(said: str, quote: str | None) -> str:
    return f"ANSWER: {said}" + (f'\nQUOTE: "{quote}"' if quote is not None else "")


def first_line(text: str) -> str:
    return next(line for line in text.splitlines() if line.strip())


def answers(output: str, *said: str) -> list[judge.Answer]:
    return [judge.read_answer(reply(s, first_line(output)), output) for s in said]


def _judged_check_is_proved(check_id: str, req: str) -> None:
    """The check exists, applies where the spec says, has two known-bad outputs, and the gate and
    the 2-of-3 rule give the right result on canned answers."""
    jc = judge.JUDGED[check_id]
    assert jc.req == req and "?" in jc.question
    part_cases = [c for p, c in inputs.all_cases() if p == jc.part]
    assert [c for c in part_cases if jc.applies(c)] == APPLIES[check_id]

    bads = judge.known_bad_for(check_id)
    assert len(bads) >= 2, "REQ-080: at least two known-bad outputs"
    for kb in bads:
        assert kb.part == jc.part and jc.applies(kb.case), kb.id
        text = kb.text()
        p = judge.prompt(check_id, kb.case, text)
        assert jc.question in p and text.rstrip() in p and "ANSWER: yes or ANSWER: no" in p

    # A judge that says a clear no on every known-bad output, 3 of 3: the gate opens.
    gate_answers = {kb.id: answers(kb.text(), "no", "no", "no") for kb in bads}
    g = judge.gate(check_id, gate_answers)
    assert g.open, g.reasons
    good = (SAMPLES / REFERENCE[jc.part]).read_text(encoding="utf-8")
    assert judge.result(answers(good, "yes", "yes", "no"), g) == judge.PASS
    assert judge.result(answers(good, "yes", "no", "no"), g) == judge.FAIL

    # The same judge passes one known-bad output in one run: the gate closes, the score is withheld.
    first = bads[0]
    gate_answers[first.id] = answers(first.text(), "no", "yes", "no")
    g = judge.gate(check_id, gate_answers)
    assert not g.open and any(first.id in r for r in g.reasons)
    assert judge.result(answers(good, "yes", "yes", "yes"), g) == judge.NOT_VERIFIED


@pytest.mark.req("REQ-030")
def test_cp_j1():
    _judged_check_is_proved("CP-J1", "REQ-030")


@pytest.mark.req("REQ-031")
def test_cp_j2():
    _judged_check_is_proved("CP-J2", "REQ-031")


@pytest.mark.req("REQ-032")
def test_cp_j3():
    _judged_check_is_proved("CP-J3", "REQ-032")


@pytest.mark.req("REQ-033")
def test_cp_j4():
    _judged_check_is_proved("CP-J4", "REQ-033")


@pytest.mark.req("REQ-034")
def test_cp_j5():
    _judged_check_is_proved("CP-J5", "REQ-034")


@pytest.mark.req("REQ-035")
def test_cp_j6():
    _judged_check_is_proved("CP-J6", "REQ-035")


@pytest.mark.req("REQ-036")
def test_cp_j7():
    _judged_check_is_proved("CP-J7", "REQ-036")


@pytest.mark.req("REQ-053")
def test_tr_j1():
    _judged_check_is_proved("TR-J1", "REQ-053")


@pytest.mark.req("REQ-054")
def test_tr_j2():
    _judged_check_is_proved("TR-J2", "REQ-054")


@pytest.mark.req("REQ-055")
def test_tr_j3():
    _judged_check_is_proved("TR-J3", "REQ-055")


@pytest.mark.req("REQ-056")
def test_tr_j4():
    _judged_check_is_proved("TR-J4", "REQ-056")


@pytest.mark.req("REQ-057")
def test_tr_j5():
    _judged_check_is_proved("TR-J5", "REQ-057")


@pytest.mark.req("REQ-071")
def test_ta_j1():
    _judged_check_is_proved("TA-J1", "REQ-071")


@pytest.mark.req("REQ-072")
def test_ta_j2():
    _judged_check_is_proved("TA-J2", "REQ-072")


@pytest.mark.req("REQ-073")
def test_ta_j3():
    _judged_check_is_proved("TA-J3", "REQ-073")


@pytest.mark.req("REQ-074")
def test_ta_j4():
    _judged_check_is_proved("TA-J4", "REQ-074")


@pytest.mark.req("REQ-111")
def test_every_judged_check_id_of_the_spec_is_defined():
    spec = (ROOT / "docs" / "spec.md").read_text(encoding="utf-8")
    for cid, jc in judge.JUDGED.items():
        row = next(line for line in spec.splitlines() if line.startswith(f"| {jc.req} |"))
        assert f"{cid}:" in row
    assert len(judge.JUDGED) == 16


# REQ-001: the 2-of-3 rule and the quote.

OUT = "Pattern 1: Sorts before acting\nShe scored 14 flats   on 6 criteria."


@pytest.mark.req("REQ-001")
def test_a_yes_counts_only_with_a_quote_the_output_holds():
    assert judge.read_answer(reply("yes", "scored 14 FLATS on 6 criteria"), OUT).counts_as_yes
    no_quote = judge.read_answer(reply("yes", None), OUT)
    assert no_quote.said == judge.YES and not no_quote.counts_as_yes
    assert not judge.read_answer(reply("yes", ""), OUT).counts_as_yes
    assert not judge.read_answer(reply("yes", "scored 15 flats"), OUT).counts_as_yes
    assert not judge.read_answer(reply("no", "scored 14 flats"), OUT).counts_as_yes


@pytest.mark.req("REQ-001")
def test_a_reply_that_cannot_be_read_counts_as_no():
    for raw in ["Yes, it does.", "ANSWER: maybe", "ANSWER: yes\nANSWER: no\nQUOTE: \"Pattern 1\"", ""]:
        a = judge.read_answer(raw, OUT)
        assert a.said == judge.UNREAD and not a.counts_as_yes, raw
    assert judge.read_answer('answer: Yes.\nquote: "Pattern 1"', OUT).counts_as_yes


@pytest.mark.req("REQ-001")
def test_a_case_passes_on_two_of_three():
    assert judge.passes(answers(OUT, "yes", "yes", "no"))
    assert judge.passes(answers(OUT, "yes", "yes", "yes"))
    assert not judge.passes(answers(OUT, "yes", "no", "no"))
    unquoted = [judge.read_answer(reply("yes", None), OUT)] * 2 + answers(OUT, "yes")
    assert not judge.passes(unquoted)


@pytest.mark.req("REQ-005")
def test_every_judged_result_needs_all_three_runs():
    g = judge.Gate("CP-J1", True, ())
    for n in (2, 4):
        with pytest.raises(ValueError):
            judge.result(answers(OUT, *["yes"] * n), g)
    with pytest.raises(ValueError):
        judge.result(answers(OUT, "no", "no"), judge.Gate("CP-J1", False, ("closed",)))


# REQ-080 to 082: the gate and the known-bad outputs.


@pytest.mark.req("REQ-080")
def test_the_gate_refuses_the_scores_of_a_judge_that_passes_a_known_bad_output():
    """The exit test of session 7.3: a judge that says yes to a known-bad output, with a valid
    quote, in one run of three, has its scores withheld for that check on every case."""
    bads = judge.known_bad_for("TR-J2")
    gate_answers = {kb.id: answers(kb.text(), "no", "no", "no") for kb in bads}
    gate_answers[bads[0].id] = answers(bads[0].text(), "no", "no", "yes")
    assert all(a.counts_as_yes is False for a in gate_answers[bads[0].id][:2])
    assert gate_answers[bads[0].id][2].counts_as_yes
    g = judge.gate("TR-J2", gate_answers)
    assert not g.open
    assert g.reasons == (f"{bads[0].id} run 3: judge said yes",)
    good = (SAMPLES / REFERENCE["B"]).read_text(encoding="utf-8")
    assert judge.result(answers(good, "yes", "yes", "yes"), g) == judge.NOT_VERIFIED

    b = _canned_baseline(gate_override={"TR-J2": gate_answers})
    assert not b["gate"]["TR-J2"]["open"]
    results = [c["judged_results"]["TR-J2"] for c in b["cases"] if "TR-J2" in c["judged_results"]]
    assert results and set(results) == {judge.NOT_VERIFIED}
    assert b["summary"]["judged_not_verified_gate_closed"] == len(results)
    assert not baseline.validate(b)


@pytest.mark.req("REQ-080")
def test_the_gate_closes_on_any_answer_that_is_not_a_clear_no():
    bads = judge.known_bad_for("CP-J3")
    text = bads[0].text()
    clean = {kb.id: answers(kb.text(), "no", "no", "no") for kb in bads}
    assert judge.gate("CP-J3", clean).open
    for bad_reply in [reply("yes", None), reply("yes", "not in the output at all"), "I think it is fine.", ""]:
        g = judge.gate("CP-J3", {**clean, bads[0].id: answers(text, "no", "no") + [judge.read_answer(bad_reply, text)]})
        assert not g.open, bad_reply
    assert not judge.gate("CP-J3", {bads[0].id: clean[bads[0].id]}).open  # one known-bad only
    assert not judge.gate("CP-J3", {**clean, bads[0].id: answers(text, "no", "no")}).open  # two runs
    assert not judge.gate("CP-J3", {}).open


DRAFT = {
    "J-bad-01": ["CP-J3"], "J-bad-02": ["CP-J2"], "J-bad-03": ["CP-J4"], "J-bad-04": ["CP-J5"],
    "J-bad-05": ["CP-J1", "CP-J6"], "J-bad-06": ["CP-J1", "CP-J7"], "J-bad-07": ["TA-J1"],
    "J-bad-08": ["TA-J2"], "J-bad-09": ["TA-J3"], "J-bad-10": ["TA-J4"], "J-bad-11": ["TR-J1"],
    "J-bad-12": ["TR-J2"], "J-bad-13": ["TR-J3"], "J-bad-14": ["TR-J5"],
}


@pytest.mark.req("REQ-081")
def test_the_fourteen_design_fixtures_are_written():
    kb = judge.known_bad()
    for fid, cids in DRAFT.items():
        assert list(kb[fid].checks) == cids, fid
        assert kb[fid].text().strip()
    assert kb["J-bad-05"].case == "H3" and kb["J-bad-06"].case == "H6" and kb["J-bad-11"].case == "TR-03"
    assert "Strong at execution" in kb["J-bad-05"].text()
    assert "Dutch is close to German" in kb["J-bad-08"].text()
    assert "private browser window" in kb["J-bad-14"].text()


@pytest.mark.req("REQ-082")
def test_every_judged_check_has_two_known_bad_outputs():
    counts = {cid: len(judge.known_bad_for(cid)) for cid in judge.JUDGED}
    assert min(counts.values()) >= 2, counts
    assert counts["TR-J4"] >= 2


@pytest.mark.req("REQ-082")
def test_each_known_bad_output_is_an_edit_of_its_base_or_stands_alone():
    manifest = yaml.safe_load((judge.JUDGE_DIR / "manifest.yaml").read_text(encoding="utf-8"))["known_bad"]
    files = sorted(p.name for p in (judge.JUDGE_DIR / "known-bad").glob("*.md"))
    assert files == sorted(Path(e["file"]).name for e in manifest)
    sample_files = {e["id"]: e["file"] for e in yaml.safe_load((SAMPLES / "manifest.yaml").read_text())["samples"]}
    for e in manifest:
        text = (judge.JUDGE_DIR / e["file"]).read_text(encoding="utf-8")
        assert e["edit"].strip()
        if e["base"]:
            assert text != (SAMPLES / sample_files[e["base"]]).read_text(encoding="utf-8"), e["id"]


# REQ-002, 005, 006, 090, 091, 092: the baseline the runner writes.


def _canned_baseline(generator="g/model-1", judge_model="j/model-2", gate_override=None, said="yes", out_dir=None):
    gate_answers = {cid: {kb.id: answers(kb.text(), "no", "no", "no") for kb in judge.known_bad_for(cid)} for cid in judge.JUDGED}
    gate_answers.update(gate_override or {})
    runs = []
    for part, case in inputs.all_cases():
        text = (SAMPLES / REFERENCE[part]).read_text(encoding="utf-8")
        det = {r.check: r.passed for r in checks.run(part, text, case)}
        for n in (1, 2, 3):
            rel = f"outputs/{part}/{case}-run{n}.md"
            if out_dir is not None:
                (out_dir / rel).parent.mkdir(parents=True, exist_ok=True)
                (out_dir / rel).write_text(text, encoding="utf-8")
            jud = {jc.id: answers(text, said)[0] for jc in judge.for_case(part, case)}
            runs.append(baseline.Run(part, case, n, rel, det, jud))
    return baseline.build(generator, judge_model, "2026-11-25", gate_answers, runs)


@pytest.mark.req("REQ-002")
def test_the_baseline_says_whether_the_judge_is_the_generator():
    assert _canned_baseline("a/x", "a/x")["judge_relation"] == "same model as generator"
    b = _canned_baseline("a/x", "b/y")
    assert b["judge_relation"] == "different model from generator"
    b["judge_relation"] = "same model as generator"
    assert any("REQ-002" in e for e in baseline.validate(b))


@pytest.mark.req("REQ-005")
def test_a_baseline_missing_a_run_or_a_check_is_invalid():
    b = _canned_baseline()
    b["cases"][0]["runs"].pop()
    b["summary"] = baseline.summary(b)
    assert any("REQ-005" in e for e in baseline.validate(b))
    b = _canned_baseline()
    b["cases"][5]["runs"][1]["deterministic"].popitem()
    assert any("deterministic checks incomplete" in e for e in baseline.validate(b))


@pytest.mark.req("REQ-006")
def test_regression_rule():
    old = _canned_baseline()
    assert baseline.regressions(old, _canned_baseline()) == []

    new = _canned_baseline()
    case = next(c for c in new["cases"] if c["case"] == "TR-01")
    cid = next(k for k, v in case["runs"][0]["deterministic"].items() if v)
    case["runs"][2]["deterministic"][cid] = False
    assert baseline.regressions(old, new) == [f"TR-01 {cid}: passed 3 of 3, now fails in a run"]

    one_flip = _canned_baseline()
    one_flip["cases"][0]["judged_results"]["CP-J1"] = judge.FAIL
    assert baseline.regressions(old, one_flip) == []
    one_flip["cases"][1]["judged_results"]["CP-J2"] = judge.FAIL
    assert len(baseline.regressions(old, one_flip)) == 1

    closed = _canned_baseline(said="no", gate_override={cid: {} for cid in judge.JUDGED})
    assert baseline.regressions(old, closed) == [], "a closed gate is not compared"


@pytest.mark.req("REQ-090")
def test_the_runner_writes_a_complete_baseline(tmp_path):
    b = _canned_baseline(out_dir=tmp_path)
    assert baseline.validate(b) == []
    path = baseline.write(b, tmp_path)
    assert path.name == "eval-baseline-2026-11-25.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["runner"]["name"] == "prompts-on-trial evals/run.py"
    assert data["generator_model"] == "g/model-1" and data["judge_model"] == "j/model-2"
    assert len(data["cases"]) == 22 and all(len(c["runs"]) == 3 for c in data["cases"])
    a = data["cases"][0]["runs"][0]["judged"]["CP-J1"]
    assert a["said"] == "yes" and a["quote"] and a["counts_as_yes"]
    assert set(data["gate"]) == set(judge.JUDGED)
    assert len(data["gate"]["TR-J4"]["answers"]) >= 2


@pytest.mark.req("REQ-090")
def test_write_refuses_an_invalid_baseline(tmp_path):
    b = _canned_baseline()
    b["cases"][0]["judged_results"]["CP-J1"] = judge.PASS
    b["gate"]["CP-J1"]["open"] = False
    with pytest.raises(ValueError):
        baseline.write(b, tmp_path)
    assert not list(tmp_path.glob("*.json"))


@pytest.mark.req("REQ-090")
def test_no_baseline_or_model_output_is_committed(root):
    found = [p for p in root.rglob("eval-baseline-*.json") if ".venv" not in p.parts]
    assert found == []
    assert not (root / "evals" / "outputs").exists()
    assert "evals/runs/" in (root / ".gitignore").read_text(encoding="utf-8").splitlines()


@pytest.mark.req("REQ-091")
def test_summary_rows():
    b = _canned_baseline()
    s = b["summary"]
    pairs = sum(len(c["runs"][0]["deterministic"]) for c in b["cases"])
    judged = sum(len(c["judged_results"]) for c in b["cases"])
    assert s["deterministic_3_of_3"] + s["deterministic_1_or_2_of_3"] + s["deterministic_0_of_3"] == pairs
    assert s["deterministic_1_or_2_of_3"] == 0
    assert s["judged_2_of_3_or_better"] == judged and judged == sum(len(judge.for_case(p, c)) for p, c in inputs.all_cases())

    case = b["cases"][0]
    cid = next(iter(case["runs"][0]["deterministic"]))
    flipped = not case["runs"][0]["deterministic"][cid]
    case["runs"][0]["deterministic"][cid] = flipped
    s2 = baseline.summary(b)
    assert s2["deterministic_1_or_2_of_3"] == 1
    assert any("REQ-091" in e for e in baseline.validate(b))

    closed = _canned_baseline(gate_override={"CP-J1": {}})
    assert closed["summary"]["judged_not_verified_gate_closed"] == 6


@pytest.mark.req("REQ-092")
def test_the_checker_path_reruns_on_saved_outputs(tmp_path):
    b = _canned_baseline(out_dir=tmp_path)
    path = baseline.write(b, tmp_path)
    assert baseline.recheck(path) == []
    target = tmp_path / "outputs" / "B" / "TR-01-run2.md"
    target.write_text(target.read_text(encoding="utf-8").replace("## 3. Monitoring plan", "## 3. Plan"), encoding="utf-8")
    diffs = baseline.recheck(path)
    assert diffs and all(d.startswith("TR-01 run 2") for d in diffs)
