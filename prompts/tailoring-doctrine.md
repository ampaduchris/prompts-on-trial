# Tailoring doctrine

A method for tailoring one career record to one job requisition without inventing anything. Give a model this document, a career record and a requisition, then ask for a mapping, a CV and a memo.

This is a public rewrite of a private document. Every example is invented. The output contract at the end is an addition. Both are listed in `docs/DEVIATIONS.md`.

---

## 0. Record conventions

The record is a list of items, each with an id. Some items carry a status tag:

- `[WITHHELD]` or `[OFF]`: a settled decision to leave the item out. It is never a gap to report.
- `[HELD]`: the outcome is not yet known. Make no claim about its results.
- `[CONTESTED]`: two sources disagree. Use it only if the memo names it.
- `[CV-ONLY]`: no public source corroborates it.
- `[NEEDS INPUT]`: the candidate must supply a fact. Show a bracketed placeholder and list it in the memo.

## 1. Read the requisition, not just the description

Four lists before you write a word.

**Hard requirements**, with exact thresholds. "3+ years consulting experience in the relevant space required" is a number an application form will ask about.

**Alternative routes.** Descriptions often carry a second qualifying path: "in lieu of consulting experience, 4+ years minimum industry experience required." When the primary threshold is not met, the memo must name the alternative route and say how the form should be answered.

**The competency list in its given order.** The list of what the employer wants is its own priority ranking. Default to mirroring it.

**Knockouts.** Work authorisation, location, minimum years, language, clearance. These produce silent automated rejections that no amount of CV quality survives, and a referral does not override them.

**The requisition title.** It is often narrower than the body and it wins. A generic practice description arriving under the title "Digital and AI in the Retail Practice" is a brief for the AI topic inside that practice, and the CV should lead accordingly.

## 2. Map before writing

| Requirement | Record item | Strength |
|---|---|---|

Fill it completely, including empty rows. An empty row is a gap. Gaps go in the memo, never papered over with adjacent material.

Check the record conventions in section 0 before mapping. A `[WITHHELD]` or `[OFF]` item is a settled decision, never a gap to report.

This table is also the deliverable that tells the candidate whether to apply at all.

## 3. Selection

A bullet earns its place by answering a named requirement. Nothing else does.

Priority order when space is short:

1. Evidence for a hard requirement.
2. Evidence for a rare requirement, meaning one most applicants cannot answer.
3. Evidence for a preferred requirement.
4. Scale and seniority context: who the candidate works with, what size of business.
5. Everything else.

Within the current role, five to six bullets. Older roles, one to three, shrinking with age. The oldest role gets one.

**Category matters more than recency.** Planning cycles and database queries from an old role beat a recent bullet that answers nothing the description asked for.

## 4. Ordering

Default: mirror the description's own competency order.

Deviate when the requisition title signals a narrower brief. If the title names a topic the body treats as one requirement among several, lead with that topic.

Within the current role, the first bullet is the one that answers the description's most distinctive requirement, not the one that sounds most senior. For a knowledge or expert-track role, the reusable asset leads and the executive-exposure bullet sits third.

## 5. Phrasing

- Verb, object, mechanism, outcome. Cut everything else.
- Present tense for live work, past for completed. Never dress in-flight work as delivered.
- Name tools and platforms that the record names. "A forecasting model in a spreadsheet tool" indexes and demonstrates; "analytics tools" does neither. Never name a tool the record does not name.
- Expand every acronym at first use on the CV itself. It serves the human reader and it indexes both forms for the parser.
- One currency per employer, matched to how that business reports.
- Qualified pipeline is qualified pipeline. Never "potential revenue".
- Attribute programme-scale outcomes to the programme, then state the candidate's contribution separately.
- Never invent or adjust a number. Never add two figures from different bullets to make a larger one. Use a number only as the record states it.

## 6. Credibility rules

These are the defect classes found in real CVs. Each one costs a reader who is scoring the document as a writing sample.

| Defect | Rule |
|---|---|
| Broken reverse chronology | Never. Parsers build phantom gaps from it and humans read date manipulation |
| Year-only dates | Never. Month and year everywhere |
| Genuinely incoherent metrics | Check every metric pair, but understand the operating model before calling one impossible. See section 10 |
| Scale mismatch | A percentage and an absolute that imply a trivial base. Pick one |
| Ambiguous metrics | "Above 90%" without to-or-by. Resolve or cut |
| Mixed currency in one document | One convention |
| Mixed British and American spelling | One convention, chosen by the role's country |
| Unexpanded acronyms | Expand at first use |
| Initialisms as employer names | Full registered name |
| Untranslated grading scales | Explain in the same clause, or drop the number |
| Course providers dressed as universities | Name the actual provider |
| Inflated titles or credentials | The title and the degree are as the record states them. Never promote, never add a credential |
| Inconsistent bullet architecture | One structure across every entry |
| Overreach in the summary | "Global fintech leader" for a regional operating role. A reviewer notices and it contaminates everything after it |
| A number the candidate cannot discuss | If substantiating a figure in interview would breach confidentiality, it does not go on |

## 7. Divergence doctrine

**Contradiction is the defect.** Two sources asserting different values for the same field: two job titles for one employer, two employer names, two figures for one claim, an unsupported promotion. Modern hiring platforms build a single candidate profile from the CV and public data, so both values land on the recruiter's screen.

**Omission is not contradiction.** A CV routinely contains more than a public profile does.

**Where they conflict, the corroborated version wins,** even when it is less flattering. "Regional Marketing Lead" beats "Regional Lead, Sales and Marketing" if the second is the version a reference call will not support.

**Where a soft signal on a public profile could override a CV claim, neutralise it in the CV** rather than asking the candidate to change the profile.

## 8. Section architecture

The standard shape: Profile, Professional Experience, Education, Certifications and Skills.

Add a bespoke section only when the description names a competency that has real evidence sitting outside the employment history, and a reader scanning for it needs a header rather than a line buried in a skills list. A bespoke section costs three to five lines. Something else comes off. Say which, in the memo.

## 9. One page, and the cut order

Always one page. When it spills, cut in this order:

1. The oldest role's second bullet.
2. Any metric flagged `[CV-ONLY]` and ambiguous.
3. Skill list items already evidenced in a bullet.
4. The interests line.
5. Sub-lines under the oldest education entry.
6. Merge two bullets in the second-oldest role.

Never cut: month-precision dates, the right-to-work line, acronym expansions.

## 10. Precedent decisions

Reuse the reasoning, not the conclusion.

**Outcome does not gate the claim.** Two due diligences where neither target was acquired are still two due diligences. A no-go recommendation is the work succeeding.

**Short tenures need to answer their own question on the page or stay off it.** Four weeks in a role cannot demonstrate the thing the title implies. Off the CV, on the screening form, ready as a verbal story.

**A founder role is an asset or a liability depending entirely on the requirement.** For an internal delivery role it reads as retention risk. For a role whose core requirement is building products, it is direct evidence. Decide per requisition, and say why in the memo.

**Prefer the artefact a reviewer can inspect** over the credential they must take on trust.

**Understand the operating model before declaring a metric impossible.** An earnings uplift larger than a revenue uplift is ordinary in an operations advisory, where cost, contract terms and mix move earnings while revenue stays flat.

**Confidentiality decides some bullets, not credibility.** A real figure still stays off if substantiating it in an interview would require client specifics. Reference the work, drop the number.

**Short-course certificates dilute the credential they sit beside.** They belong in a cover letter at most.

## 11. Pre-flight checklist

Run every time.

- [ ] One page
- [ ] Reverse chronological, unbroken
- [ ] Month and year on every date; no unexplained gap over six months
- [ ] Every title and degree matches the record exactly
- [ ] Employer names in full
- [ ] Every metric pair arithmetically possible
- [ ] Every acronym expanded at first use
- [ ] One spelling convention, one currency convention
- [ ] Right-to-work line present for cross-border applications
- [ ] No `[CONTESTED]` item used without being named in the memo
- [ ] Every `[NEEDS INPUT]` visible as a bracketed placeholder and listed
- [ ] No claim about a `[HELD]` item's outcomes
- [ ] Present tense for in-flight work

## 12. Application mechanics for the memo

Flag these when the description or the record triggers them.

**Threshold questions.** When a hard requirement is not met by the primary route, name the alternative route and the honest answer. An unexplained "no" on a required field is an automated rejection that a referral will not survive. Count the alternative route's years from the record's own dates.

**Work authorisation.** State it unprompted on any cross-border application. If the record does not hold it, show a `[NEEDS INPUT]` placeholder.

**Verification timing.** Employment, education and criminal checks run after an offer, with written consent, through a separate vendor. They are never the cause of an application-stage rejection.

**CV versus screening form.** The CV is a summary and has never been an exhaustive record. The screening form asks for completeness and gets it. Anything held off the CV goes on the form.

**Referrals.** A referral that only enters the system is worth a fraction of one that reaches the hiring manager. The note should be three sentences, and the second should pre-empt the assumption the recruiter would otherwise make.

---

## Output contract (so that code can check the answer)

Evaluation date: when a task fixes a date, "present" means that date.

Write three blocks with these exact headings, in this order.

`## Mapping`: a table with the columns Requirement, Record item, Strength. One row for every requirement key of the requisition. An empty Record item cell marks a gap.

`## CV`: for each role, a header line `Title, Employer, start to end` with the title, employer and dates as the record states them and dates as month and year, then the bullets. Every bullet ends with one or more record ids in square brackets, for example `[B-0403]`. Use a number only if a cited record item states it. List roles newest first. Education and certification lines name the degree or certificate and the issuer exactly as the record does.

`## Memo`: a line starting `Gaps:` that names every requirement with an empty Record item cell (or `none`), and a line starting `Knockouts:` that names each knockout and the honest answer (or `none`). Then the rest of the memo.
