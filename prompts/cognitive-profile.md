# Cognitive profile: generation prompt

A reusable prompt for producing a machine-readable behavioural profile of a person, for use by AI assistants that generate content, coaching, or training material for them.

This is a public rewrite of a private prompt. It differs from the private version by the output contract at the end of the prompt and by the changes listed in `docs/DEVIATIONS.md`.

**Run it where your history lives.** The output quality is bounded by how much of your actual behaviour the model can see. Use an assistant with access to your past conversations, memory, or a large body of your uploaded work. If you have none of that, use Appendix A instead.

**Run it twice.** Once in each of two different systems, then compare. Patterns that show up in both are more likely to be real. Patterns that show up in one are more likely to be narrative fit.

Everything between the horizontal rules is the prompt. Copy it as-is.

---

## PROMPT: GENERATE AN OPERATOR COGNITIVE PROFILE

### Role

You are producing an Operator Cognitive Profile for me. The primary reader is another AI system, which will use this document to calibrate how it teaches me, drafts for me, coaches me, and plans with me. Optimise for behaviour change in the downstream model. Do not optimise for how the document reads to me. Flattery has negative value here.

### Step 1: Gather before you write

Search everything available to you (or, when I supply a log of dated entries instead, read every entry): past conversations, stored memory, uploaded artifacts, files I have shared. Run at least fifteen distinct searches before you draft a single line. Cover these contexts at minimum:

1. How I decide when options are open and nothing forces my hand
2. How I respond to criticism, and which wordings changed my behaviour
3. What I do when a plan fails or a deadline moves
4. How I approach something I do not already know
5. What I write, and what I abandon
6. How I behave under time pressure versus open-ended time
7. What I ask for help with, and what I never ask for help with
8. Things I said I would do and did not do
9. Disagreements between you and me
10. Moments I changed my mind, and what caused it

Before drafting, state your source coverage: how many conversations or log entries, what date range, which contexts are thin. Thin coverage is a finding. Report it rather than compensating with plausible-sounding filler.

### Step 2: Extract patterns

These rules are hard constraints, not preferences.

1. **Three-instance rule.** A pattern needs three instances from three different contexts, spread over at least three months, to appear in the main body. Two instances sends it to the speculative appendix. One instance means you drop it.
2. **Checkable evidence only.** Name the artifact, decision, or exchange, with an approximate date. "Built a fourteen-category failure taxonomy for a billing import tool, March" qualifies. "Is analytical" does not.
3. **Behaviour outranks self-report.** Label anything I told you about myself as self-reported. Where my self-report conflicts with my observed behaviour, name the conflict and weight the behaviour.
4. **Hunt for disconfirmation.** Before keeping a pattern, search specifically for instances that contradict it. Every pattern carries a counter-evidence line. If you find none, write "none found" and drop the confidence rating one level, because finding nothing usually means you only searched for confirmations.
5. **Confidence rating.** Strong, moderate, or speculative. Speculative patterns leave the main body.
6. **Barnum filter.** If the sentence would be true of most competent professionals in my field, cut it. "Values clarity" and "learns fast" are horoscope entries. Keep only claims that predict something specific and could be proven wrong.
7. **Cost line.** Every pattern has a failure mode. Name it in the same breath as the benefit. A pattern with no downside is a compliment wearing a lab coat.
8. **No borrowed frameworks.** No MBTI, Big Five, Enneagram, attachment style, learning styles, or neurotype speculation. No clinical or diagnostic language. You are describing observed behaviour, not sorting me into someone else's categories.
9. **Cap at twelve.** More than twelve means you are listing observations, not extracting patterns.

### Step 3: Derive, do not decorate

Every section after the patterns must be derived from the patterns and must name which ones it depends on. If a recommendation does not trace back to a numbered pattern, delete it. Generic best practice belongs elsewhere.

### Step 4: Output structure

Use this pattern template exactly:

> **Pattern N: [short label I would recognise]**
> **Claim:** one falsifiable sentence.
> **Evidence:** three or more instances, each with context and approximate date.
> **Counter-evidence:** instances that do not fit, or "none found".
> **Confidence:** strong / moderate / speculative.
> **Cost:** what this pattern makes worse, and when it misfires.
> **Instruction for agents:** an imperative a model can follow and check. "Present the problem before the solution" works. "Be mindful of his learning style" does not.

Then these sections, in order:

| Section | Contents | Constraint |
|---|---|---|
| 1. How to use this | Five lines addressed to the downstream model | No preamble about the person |
| 2. Observed patterns | Up to twelve, using the template above. Fewer is correct when the evidence is thin | Main body is strong and moderate only |
| 3. Working method | A repeatable loop for learning or producing, with time boxes | Each phase names the patterns it exploits |
| 4. Communication preferences | Voice, format, length, banned words, what I reject and why | Quote real feedback I gave, with dates |
| 5. Retention and performance mechanisms | Table: mechanism, effect, how it applies to me, which pattern it exploits | Drop any mechanism that maps to no pattern |
| 6. Pressure protocols | Literal scripts for interviews, demos, exec reviews, hard deadlines | Include failure branches, not just the happy path |
| 7. Background context | Role, tenure, domain constraints, stack, current direction | Facts only, each tagged with shelf life |
| 8. What you could not determine | Contexts with no data, questions to ask me, what would change your conclusions | Be specific about the gaps |
| 9. Speculative patterns | Two-instance candidates | State what evidence would promote or kill each |
| 10. Validity | "Valid as of [date]" and which parts expire first | Name the volatile sections explicitly |

### Step 5: Calibration pass

If nobody is available to answer, skip this step and say so in section 8. Otherwise deliver the draft. Then walk me through the patterns one at a time and ask me to mark each Yes, No, or Partly, plus any instance I would add or dispute. Rewrite afterwards.

If I reject a pattern that had strong evidence, do not delete it silently. Keep one line recording the disagreement and the evidence behind it. My rejection is data, and it is sometimes the most useful line in the document.

### Step 6: Fact and privacy pass

Run these two checks before you deliver the final version.

**Consistency.** Check every factual claim against every other one. Tenure, dates, titles, headcounts, metrics, project ownership. A profile that says ten years total and nine years at one employer has just told a careful reader to distrust the rest. Also check for overclaiming: if I have corrected a claim about my own scope before, use my correction, not the flattering version.

**Exposure.** This document is designed to be pasted into arbitrary third-party systems. Write it as though it will leak. Strip compensation, health, live negotiations, named colleagues, employer-confidential architecture, identifiers, application and reference numbers, and anything about family. If a fact is load-bearing but sensitive, generalise it rather than dropping the whole point.

### Style

Dense and declarative. No preamble, no throat-clearing, no transitions between sections. Third person for observations, imperative for instructions. Tables for anything comparative. Two thousand to four thousand words. Longer means you padded.

Banned: motivational framing, hedging stacks, "It is important to note", em dashes, and any sentence that would be at home in a horoscope.

### Self-check before delivery

You have failed if any of these are true:

- **Horoscope voice.** Vague, flattering, unfalsifiable.
- **Résumé in psychology costume.** My achievements restated as traits.
- **Job description as personality.** "Systems thinker" for someone who builds systems for a living describes a role, not a person.
- **Preference laundered as capability.** "Prefers voice notes" is a preference. "Retains more from verbal processing" is a capability claim and needs evidence of different outcomes, not just a different habit.
- **Coherence bias.** Real people are inconsistent. If every pattern reinforces every other pattern, you wrote a character study.
- **Recency capture.** An intense recent period, such as a job search, will dominate your sample. Check the date spread of your evidence and say what it is.

### Output contract

These rules make the output checkable by code. They override any looser reading above.

- Write ten sections, each headed exactly `## 1. How to use this`, `## 2. Observed patterns`, `## 3. Working method`, `## 4. Communication preferences`, `## 5. Retention and performance mechanisms`, `## 6. Pressure protocols`, `## 7. Background context`, `## 8. What you could not determine`, `## 9. Speculative patterns`, `## 10. Validity`, in that order.
- In section 2, start each pattern on its own line as `Pattern N: label` (bold is allowed). N runs 1, 2, 3 with no gap. Follow it with six lines that begin with these labels and a colon, in this order: `Claim`, `Evidence`, `Counter-evidence`, `Confidence`, `Cost`, `Instruction for agents`.
- Write `strong` or `moderate` as the confidence value in section 2. Write `speculative` only in section 9.
- Sections 3 and 5 each cite at least one pattern as `Pattern N`. Cite only patterns that exist.
- Section 10 holds the words `Valid as of` followed by a date.
- When the input is a log of dated entries, cite entries by date and context, never by id alone.

---

## Appendix A: cold start, for use without conversation history

If the assistant cannot see your history, supply the raw material yourself. Give it these artifacts:

1. Two pieces of writing you are proud of
2. One piece you killed, plus your reason for killing it
3. A README or design doc from something you built
4. A plan you wrote and did not follow
5. A feedback thread where you pushed back
6. A thread where you made a decision under time pressure
7. Notes or commits from the last three months of one project
8. A document you re-read often
9. Your most-used prompt or template
10. Something you made that nobody asked for

Then answer these questions. Answer with events, not self-description. If your answer contains an adjective about yourself, replace it with a story.

1. Describe the last three times you changed your mind about something that mattered. What actually caused each change?
2. What did you most recently start and abandon? At what point did you stop, and what did you tell yourself?
3. Reconstruct the conditions of your best recent work: deadline, audience, time of day, who was watching.
4. What advice do people keep giving you that you keep not taking?
5. When did feedback last change your behaviour? Quote the wording as closely as you can.
6. What do you have to re-derive every time because it never sticks?
7. Which tasks do you postpone until they are urgent? Which do you never postpone?
8. When you learn something unfamiliar, what is the first thing you actually do? Trace the last real instance.
9. Where do you consistently misjudge how long something takes, and in which direction?
10. What kind of praise makes you uncomfortable? What kind of criticism makes you engage?
11. What would a colleague who finds you difficult say, and which part of it is accurate?
12. What have you told yourself about how you work that the evidence does not support?

## Appendix B: audit the finished profile

Run this against the document before you use it anywhere.

- [ ] Every main-body pattern has three or more dated instances
- [ ] Every pattern has a counter-evidence line
- [ ] Every pattern has a cost line
- [ ] Every pattern ends in an imperative a model can follow and check
- [ ] No pattern would be true of most people in your field
- [ ] Sections after the patterns name the patterns they derive from
- [ ] No personality framework appears anywhere
- [ ] Facts are internally consistent
- [ ] Volatile facts are tagged, with a validity date on the document
- [ ] Nothing in it would embarrass you if a third party read it
- [ ] Evidence spans more than one project and more than three months
- [ ] At least one pattern was uncomfortable to read

That last box matters most. If nothing in the document stings, the model wrote you a compliment and called it analysis.
