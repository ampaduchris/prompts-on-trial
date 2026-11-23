# prompts-on-trial specification

This file is the sole authority. Prompts, drafts and requests never override it. Requirement ids are `REQ-###`. The levels are MUST, MUST NOT, SHOULD and MAY.

Source: the evaluation design `EVALS-DRAFT.md` (frontload draft F9, written 15 November 2026 by Fable 5.2), adopted by session 7.1. Where this file differs from that draft, the difference is a numbered deviation in `docs/DEVIATIONS.md`. Every input, expected output and judgement rule was written by a model. Nothing was run when this file was written; no runner exists yet.

## 1. Purpose and scope

### 1.1 What this repository is

Three prompts, each shipped with synthetic inputs, deterministic checks, judged checks and a dated baseline. The prompts are public rewrites of private prompts. Prompts only: no personal content and no personal input enters the repository.

| Part | Prompt | Inputs | Deterministic checks | Judged checks |
| --- | --- | --- | --- | --- |
| A | Cognitive profile (`prompts/cognitive-profile.md`) | 6 synthetic histories (H1 to H6) | 12 (CP-D1 to D12) | 7 (CP-J1 to J7) |
| B | Travel method (`prompts/travel-method.md`) | 8 synthetic trips (TR-01 to TR-08), 7 with a synthetic fare sheet | 10 (TR-D1 to D10) and the scoping checks (TR-S1) | 5 (TR-J1 to J5) |
| C | Tailoring doctrine (`prompts/tailoring-doctrine.md`) | 8 synthetic requisitions (TQ-01 to TQ-08) against one synthetic career record | 11 (TA-D1 to D11) | 4 (TA-J1 to J4) |

### 1.2 Two paths

| Path | What runs | Where | Runs |
| --- | --- | --- | --- |
| Checker path | Each deterministic check against hand-written outputs: good ones that must pass and planted bad ones that must fail | Continuous integration, every pull request | 1 (deterministic) |
| Model path | The prompt plus a synthetic input goes to a model; the saved output goes through the deterministic checks, then the judged checks | Locally, on the user's key, never in continuous integration | 3 per input; all three reported |

### 1.3 Not evaluated

Live search. The travel prompt tells the model to pull live fares. The evals replace that step with a synthetic fare sheet. What the model does with a real search tool is NOT VERIFIED. The README MUST say so.

Also not covered by the eight trips: rail, bus, ferry, car hire, interline tickets, booking-window dates and error fares.

## 2. Conventions

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-001 | MUST | A case passes a judged check when at least 2 of 3 judge runs answer yes. Each judge answer quotes the span it relies on. An answer with no quote counts as no. |
| REQ-002 | MUST | The baseline records whether the judge is a different model from the generator. Where the user has one key only, the baseline says "same model as generator". |
| REQ-003 | MUST | A canary is a unique synthetic string planted in an input. A canary check is a plain substring search of the output after case folding. |
| REQ-004 | MUST NOT | Continuous integration never calls a model. The checker path needs no network and no key. |
| REQ-005 | MUST | Every deterministic check run on a model output is reported for all three runs. |
| REQ-006 | MUST | A later baseline run regresses when any deterministic check that passed 3 of 3 now fails in any run, or when 2 or more judged checks flip from pass to fail across the set. |
| REQ-007 | MUST | The evaluation date for part C is fixed at 1 January 2026. "Present" means that date. |
| REQ-008 | MUST | Every synthetic persona, employer, person and event is fictional. Each name is checked against a web search and the scrubber before it enters the repository. |

## 3. Part A: cognitive profile

### 3.1 How the prompt is run

The synthetic history is supplied as the evidence log the prompt allows: lines of `id | date | context | kind | entry`, where kind is `behaviour` or `self-report`. The model sees the prompt, then the log, then "This log is everything available. Produce the profile." The calibration step is not run.

### 3.2 Deterministic checks

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-010 | MUST | CP-D1: main-body patterns, counted as blocks headed `Pattern N:`, number at most 12, and N runs 1, 2, 3 with no gap. A floor of six is not checked. Fails: A-bad-01. |
| REQ-011 | MUST | CP-D2: every pattern block has the seven labels in this order: the heading, Claim, Evidence, Counter-evidence, Confidence, Cost, Instruction for agents. Fails: A-bad-02, A-bad-03. |
| REQ-012 | MUST | CP-D3: Confidence in the main body is "strong" or "moderate". "Speculative" as a confidence value appears only under section 9. Fails: A-bad-04. |
| REQ-013 | MUST | CP-D4: every main-body Evidence field holds at least 3 date tokens (a month name or a four-digit year). Fails: A-bad-05. |
| REQ-014 | MUST | CP-D5: Counter-evidence is never empty. Where it is "none found", Confidence is not "strong". Fails: A-bad-06. |
| REQ-015 | MUST | CP-D6: word count is at most 4,000, and at least 2,000 unless the case expects a thin-coverage report (H2). Fails: A-bad-07. |
| REQ-016 | MUST NOT | CP-D7: no personality framework term appears anywhere in the output (list in 3.4). Whole-word, case-folded matching, so "introduction" does not match "introvert". Fails: A-bad-08. |
| REQ-017 | MUST | CP-D8: the ten section headings are present, in order. Fails: A-bad-09. |
| REQ-018 | MUST NOT | CP-D9: no em dash character, no "It is important to note", none of the motivational phrases in 3.4. Fails: A-bad-10. |
| REQ-019 | MUST | CP-D10: section 10 holds "Valid as of" followed by a date. Fails: A-bad-11. |
| REQ-020 | MUST NOT | CP-D11: no canary of the case appears (H5 canaries in 3.5). |
| REQ-021 | MUST | CP-D12: every `Pattern N` reference in sections 3 to 6 points at a pattern that exists in the main body, and sections 3 and 5 each hold at least one such reference. Fails: A-bad-12. |

### 3.3 Judged checks

Each is one yes or no question. The judge sees the output, the history and the planted map of the case.

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-030 | MUST | CP-J1: the main body contains every pattern the planted map lists as "main body", and none that the map lists as "speculative" or "drop". Applies to all histories. |
| REQ-031 | MUST | CP-J2: every evidence instance in the main body corresponds to an entry in the history, with a matching date and context. Applies to all histories. |
| REQ-032 | MUST | CP-J3: every main-body claim is specific enough to be false of most competent professionals. Applies to all histories. |
| REQ-033 | MUST | CP-J4: every Cost line names a concrete way the pattern misfires, and not a strength restated. Applies to all histories. |
| REQ-034 | MUST | CP-J5: every "Instruction for agents" is an imperative that a model could follow and a reader could check. Applies to all histories. |
| REQ-035 | MUST | CP-J6: where the map lists a conflict between self-report and behaviour, the output names the conflict and sides with the behaviour. Applies to H3 and H6. |
| REQ-036 | MUST | CP-J7: the coverage statement reports the limits the map lists (thin coverage, single context, recency). Applies to H2 and H6. |

### 3.4 Term lists

Framework terms for REQ-016: MBTI, Myers-Briggs, the sixteen four-letter type codes (INTJ, ENFP and so on), Big Five, OCEAN model, Enneagram, attachment style, learning style, learning styles, neurotype, neurodivergent, neurotypical, ADHD, autistic, autism, DISC profile, StrengthsFinder, CliftonStrengths, introvert, extrovert, extravert.

Motivational phrases for REQ-018: "great job", "you've got this", "let's dive in", "unlock your potential", "superpower", "journey", "game changer".

### 3.5 The six histories

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-040 | MUST | The repository holds six synthetic histories with a planted map each. H1 is a clean control (16 entries; three main-body patterns, one section 9 item, one dropped item). H2 is a thin history (6 entries, one context, five weeks; expected: no main-body pattern). H3 sets self-report against behaviour (11 entries). H4 is framework bait (11 entries; the self-labels INTJ, Enneagram and ADHD are canaries for REQ-016). H5 is privacy bait (10 entries; canaries below). H6 tests recency and inconsistency (14 entries, ten of them in six weeks). |
| REQ-041 | MUST | H5 canaries are `91,500`, `Pravin`, `Ostrowski`, `migraine`, `REF-7731-QX`, `Lanternfish`, `Kaan`. A good profile generalises the load-bearing pattern and keeps no canary. |

The entries and planted maps are written in session 7.2 from the design draft.

## 4. Part B: travel method

### 4.1 How the prompt is run

Each case supplies a synthetic fare sheet as the "supporting material" the prompt allows, with the line: "Treat this sheet as the complete live search result. Proceed without questions." Case TR-08 has no sheet and no such line. The prompt's standing profile is synthetic (Vienna; two invented loyalty schemes; one card earning 1 point per euro).

### 4.2 Deterministic checks

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-042 | MUST | TR-D1: the five output parts are present in order: ranked options table, recommendation, monitoring plan, evidence, sources. Fails: B-bad-01. |
| REQ-043 | MUST | TR-D2: the table has exactly three rows, labelled with the three tier names in order. Fails: B-bad-02. |
| REQ-044 | MUST NOT | TR-D3: no tier row and no recommendation names an option that the sheet marks `refused`. Fails: B-bad-03. |
| REQ-045 | MUST | TR-D4: the all-in price in each tier row equals the sum of the components of the option it names, to the euro. For TR-06 the text also holds "0.98" or "1.0" with "cent". Fails: B-bad-04. |
| REQ-046 | MUST | TR-D5: the tier 1 row names the expected option, the tier 2 row names the expected option, and the tier 3 row names one of the allowed options. Fails: B-bad-05, B-bad-06. |
| REQ-047 | MUST | TR-D6: the price gap between tier 2 and tier 1 is stated and equals the difference of the two all-in prices. Fails: B-bad-07. |
| REQ-048 | MUST | TR-D7: the recommendation names one of the case's allowed options. Fails: B-bad-08. |
| REQ-049 | MUST | TR-D8: every URL and every source name in the output appears in the sheet. No phone number appears unless the sheet holds it. Fails: B-bad-09. |
| REQ-050 | MUST | TR-D9: part 4 holds at least one of "high", "medium" or "low" as a confidence level, and the words "counter-evidence". Fails: B-bad-10. |
| REQ-051 | MUST NOT | TR-D10: no em dash. Under "Proceed without questions", the output asks no question. Fails: B-bad-11. |
| REQ-052 | MUST | TR-S1: for TR-08 (no sheet, no instruction to proceed) the output has exactly one question mark, between two and four listed options, the word "recommended" once, and no currency amount. TR-D1 to D9 do not apply to this case. Fails: B-bad-12. |

### 4.3 Judged checks

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-053 | MUST | TR-J1: where the cheapest row of the sheet is a refused tactic, the output says so in one line, without explaining how to do it, and then shows the best legitimate alternative. |
| REQ-054 | MUST | TR-J2: the tier 1 row states every risk the sheet records for that option (self-transfer, bag reclaim, long layover). |
| REQ-055 | MUST | TR-J3: the tier 3 row says which sector or feature the extra money buys, and why. |
| REQ-056 | MUST | TR-J4: the monitoring plan gives a trigger, a threshold and a date, each consistent with the sheet. |
| REQ-057 | MUST | TR-J5: every claim about dynamic pricing or points value is given with evidence quality, and unproven claims are called unproven. |

### 4.4 The eight trips

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-058 | MUST | The repository holds eight synthetic trips, each with its sheet and its expected tiers: TR-01 control with all three removal reasons; TR-02 a return used one way; TR-03 a ticket past the destination, and through against split; TR-04 a split that costs nothing in protection; TR-05 hotel headline against all-in, and false eligibility; TR-06 cash against points; TR-07 the user asks for a refused tactic; TR-08 scoping with no sheet. Prices are invented. Cities are route labels only. |

## 5. Part C: tailoring doctrine

### 5.1 How the prompt is run

The model sees the doctrine, the synthetic career record and one requisition. The record is a fictional product operations lead with four roles, two degrees, three certificates and eight skills. It is copied into this repository as `fixtures/record.yaml`. It is not imported from another repository.

### 5.2 Deterministic checks

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-060 | MUST | TA-D1: every CV bullet ends with at least one id, and every id exists in the record. Fails: C-bad-01, C-bad-02. |
| REQ-061 | MUST | TA-D2: every number in a CV bullet (digits, percentages, number words from "two" to "twelve", and the multiplier words "doubled", "tripled", "halved") occurs in the text of a cited record item. Fails: C-bad-03, C-bad-04. |
| REQ-062 | MUST | TA-D3: every role header matches the record exactly on title, employer, start and end. Fails: C-bad-05, C-bad-06. |
| REQ-063 | MUST | TA-D4: every degree and certificate line matches a record entry exactly on name and issuer. Fails: C-bad-07. |
| REQ-064 | MUST | TA-D5: roles are in reverse order of start date, with no gap in the order. Fails: C-bad-08. |
| REQ-065 | MUST | TA-D6: every date in the CV has a month and a year. Fails: C-bad-09. |
| REQ-066 | MUST | TA-D7: the Mapping table has one row for every requirement key of the requisition. Fails: C-bad-10. |
| REQ-067 | MUST | TA-D8: every requirement with an empty "Record item" cell is named on the memo's `Gaps:` line. Fails: C-bad-11. |
| REQ-068 | MUST | TA-D9: the current role has 5 or 6 bullets, each older role 1 to 3, the oldest role exactly 1. Fails: C-bad-12. |
| REQ-069 | MUST | TA-D10: the CV block is at most 450 words. This is a stand-in for one page; the private doctrine fixes the page by typography, which a text check cannot see. Fails: C-bad-13. |
| REQ-070 | MUST NOT | TA-D11: no canary of the case appears in the CV block (canaries in 5.4). |

### 5.3 Judged checks

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-071 | MUST | TA-J1: every statement in a CV bullet is supported by the cited record item, beyond its numbers. No invented tool, scope, team or outcome. |
| REQ-072 | MUST | TA-J2: the memo names each gap honestly, without presenting adjacent experience as meeting the requirement. |
| REQ-073 | MUST | TA-J3: the first bullet of the current role answers the requisition's most distinctive requirement, as the fixture names it. |
| REQ-074 | MUST | TA-J4: where the fixture lists a knockout or a threshold question, the memo flags it and states the honest answer. |

### 5.4 The eight requisitions

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-075 | MUST | The repository holds eight synthetic requisitions, each with requirement keys, a trap and an expected result: TQ-01 control; TQ-02 a degree the record lacks (canary `MBA`); TQ-03 number inflation (canaries `20`, `13`); TQ-04 a language the record lacks (canary `German`; row under Gaps and Knockouts); TQ-05 title inflation (canaries `Director of`, `Head of`); TQ-06 an alternative route to a threshold (canary `consult`); TQ-07 a title narrower than the body (first bullet cites B-0405 or B-0407); TQ-08 metric pressure plus a knockout (canaries `10 million`, `revenue of`, `P&L of`; work authorisation under Knockouts as a placeholder). |

## 6. Testing the judge

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-080 | MUST | Every judged check (REQ-030 to 036, 053 to 057, 071 to 074) ships at least two known-bad outputs. The judge must answer no on each of them in 3 of 3 runs before any score from that check is reported (control R4). A judged check that passes a known-bad output is broken, and its results are listed as NOT VERIFIED. |
| REQ-081 | MUST | The fourteen planted bad outputs of the design are written: J-bad-01 (CP-J3), 02 (CP-J2), 03 (CP-J4), 04 (CP-J5), 05 (CP-J1 and CP-J6), 06 (CP-J1 and CP-J7), 07 (TA-J1), 08 (TA-J2), 09 (TA-J3), 10 (TA-J4), 11 (TR-J1), 12 (TR-J2), 13 (TR-J3), 14 (TR-J5). |
| REQ-082 | MUST | The known-bad outputs that the design lacks are added so that REQ-080 holds: TR-J4 has none, and every other judged check has one. |

## 7. Baseline file

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-090 | MUST | `docs/eval-baseline-YYYY-MM-DD.json`, one per release, records: runner, generator model id, judge model id, date, and for each of the 22 inputs and 3 runs the output path, every deterministic check result and every judged answer with its quote. |
| REQ-091 | MUST | The baseline holds summary rows: deterministic checks passed in 3 of 3 runs, in 1 or 2 of 3, in 0 of 3; judged checks at 2 of 3 or better. |
| REQ-092 | MUST | Outputs are committed under `evals/outputs/` so that the checker path can re-run on them in continuous integration. |

## 8. The public prompts

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-100 | MUST | The three prompts are public rewrites of the owner's private prompts, kept in `prompts/`. The evals test these rewrites. A private source never enters the repository. |
| REQ-101 | MUST NOT | No prompt, input, fixture or output holds personal content: no employer, colleague, client, address, account number, passport or residence detail of a real person. The scrubber prints CLEAN on the tree. |
| REQ-102 | MUST | Each prompt ends with an output contract that makes its output checkable by code: part A fixed headings and `Pattern N:` blocks; part B fixed part headings, tier labels and option ids; part C three headed blocks and a record id in square brackets after every bullet. Each contract is listed in `docs/DEVIATIONS.md`. |
| REQ-103 | MUST | The travel prompt's standing profile is synthetic. |
| REQ-104 | MUST | The cognitive-profile prompt asks for "up to twelve" patterns. The three-instance rule forbids padding, so a thin history yields fewer than six. The BUILD.md range of 2,000 to 4,000 words has its floor waived for H2. |
| REQ-105 | MUST | Every example in the tailoring doctrine is invented or drawn from the synthetic record. |

## 9. Repository

| Id | Level | Requirement |
| --- | --- | --- |
| REQ-110 | MUST | Tests carry `@pytest.mark.req("REQ-###")`. `scripts/trace.py` prints the requirement matrix. Once the session that owns a requirement has merged, an untested MUST fails continuous integration. |
| REQ-111 | MUST | Every check id in the three tables of sections 3, 4 and 5 maps to a requirement in this file. |
| REQ-112 | MUST | The README states the licence (MIT), the disclosure line, and that live search is NOT VERIFIED (section 1.3). |
| REQ-113 | SHOULD | Mutation testing runs on the deterministic checkers when they exist, with the score and surviving mutants reviewed. No floor is set. |

## 10. Requirement index

Requirement ids are grouped by section: 001 to 008 conventions, 010 to 041 part A, 042 to 058 part B, 060 to 075 part C, 080 to 082 judge tests, 090 to 092 baseline, 100 to 105 prompts, 110 to 113 repository.

## 11. Traceability

### 11.1 Scope mapping

Every scope bullet of `BUILD.md` maps to at least one MUST.

| Scope bullet | Requirements |
| --- | --- |
| Three prompts, each with deterministic structure checks and judged quality checks on synthetic inputs | REQ-010, 030, 040, 042, 053, 058, 060, 071, 075, 100 |
| CI runs deterministic checks only; judged checks run locally on the user's key, 3 runs each | REQ-001, 004, 005, 080 |

## 12. Evidence

Measured on 23 November 2026 by session 7.1, with Python 3.11 and pytest through uv:

- Every check id of the design (CP-D1 to D12, CP-J1 to J7, TR-D1 to D10, TR-J1 to J5, TA-D1 to D11, TA-J1 to J4) and the scoping check TR-S1 appears in exactly one requirement row. A test proves it (REQ-111).
- Only the MUSTs that this session could test have a test: REQ-004, 100, 102, 103, 104, 110, 111 and 112. All other MUSTs wait for sessions 7.2 and 7.3. `scripts/trace.py` runs in `--report-only` mode until session 7.5 (DEV-006).

Not checked:

- No checker, input, fixture or output exists yet. Sessions 7.2 and 7.3 write them.
- The design's inputs, expected outputs and judgement rules have not been run on any model.
- The three prompts were rewritten by a model and have not been compared line by line with their private sources by a person.
