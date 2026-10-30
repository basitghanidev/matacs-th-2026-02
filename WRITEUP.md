# AI Proposal Triage Design — Write-up

Category: Commercial Solar Installation. Project: 150 kW rooftop system, Windsor, Ontario. Budget ceiling: $260,000 CAD. Deadline: complete within 16 weeks of award.

## Flow in brief

Admin defines a category and criteria in admin screens; criteria are stored, versioned, and never hard-coded. A reviewer uploads PDFs and selects a category. The system extracts text, AI extracts structured facts, rules apply mandatory gates and maths, AI scores weighted criteria, a human reviews flags and evidence, and only then is a ranked list shown with a reason per position. See `diagram/process-flow.png`.

## 1. AI vs. rules

AI is used only where language varies: reading a PDF and turning it into structured fields (licence holder, WSIB and insurance confirmation, relevant installs, price, weeks, warranty years, named lead, crew, safety and monitoring plan). AI also drafts an evidence-linked score for experience, and team and approach.

Rules do everything exact and auditable: mandatory gates, budget and 16-week checks, price and timeline bands, weighted totals, sorting, versioning, and the audit log. AI never decides eligibility, adds up scores, or changes criteria. In short: AI interprets messy text; code decides, calculates, and records.

## 2. Consistency and explainability

Scores are repeatable because AI does not invent the maths. Extraction and scoring use a fixed prompt, temperature 0, and a fixed JSON schema. The same criteria version is used for every proposal in a run, and totals are calculated by code, not AI.

Ranking the same proposals twice under the same version should give the same result. Wording may differ slightly; totals must not, because totals come from code. Every score shows its criterion, weight, extracted value, and one-line reason, plus whether it was AI-extracted, rule-calculated, or human-overridden. Low-confidence or missing fields stay missing, never filled in.

## 3. Human in the loop

A person reviews at three points: when a proposal is flagged (failed gate, missing field, or suspicious content); before the ranked list is finalised, to check evidence and scores; and at award, where only a human can choose, override a rank, or ask for clarification.

An override must include a reason and keeps the original scores beside it, so the change is visible. The audit log records: proposal letter, criteria version, extracted values, mandatory results, each score, total, rank, flags, reviewer, override reason, and timestamps. No result is final without a named reviewer.

## 4. Changing criteria

Criteria are versioned. Editing criteria or weights creates a new version; it never rewrites old scores. Already-scored proposals keep their old version and rank, clearly labelled. The reviewer can re-run the set under the new version, producing a new list and audit record. The system shows what changed and which ranks moved, so no silent re-ranking happens after a decision has started.

## 5. Risks and safeguards

- **Wrong extraction or made-up facts:** require a value per scored field, return null when not stated, show confidence, and block award on any null mandatory field. A second check compares output numbers with extracted text.
- **Bias:** score only the admin's criteria, hide bidder names during scoring where possible, and use the same bands for every proposal.
- **Manipulation:** proposal text is data, never instructions. Any instruction or attempt to change ranking inside a proposal is ignored, flagged for a human, and logged.
- **Missing data:** missing weighted data scores 0 and is flagged, not averaged or guessed. Missing mandatory data fails that gate.
- **Cost and failure:** use AI only for extraction and qualitative scoring, cache results per proposal and criteria version, and fall back to manual review if AI fails. No proposal is ranked on a failed AI run.

## Ranking of the sample set

Scoring bands used for all proposals: Experience — 12+ relevant installs 95, 9–11 installs 75–85, 6–8 installs 70; Price — $231,000 or less 90, up to $240,000 80, $240,000–$245,000 70; Timeline — 10–12 weeks 90, 13 weeks 85, 14 weeks 75, not stated 0; Warranty — 12 years workmanship 100, 10 years 85; Team — named lead, crew, safety and monitoring 95, named lead and crew with no safety or monitoring stated 75, named lead with safety but no crew size stated 80. Totals are weighted: Experience 30%, Price 25%, Timeline 15%, Warranty 15%, Team 15%.

- **A — Rank 1, 89:** passes both mandatory gates, strongest experience, 12 weeks, 10-year workmanship warranty, named senior lead with a six-person crew, safety plan and monitoring.
- **E — Rank 2, 81:** passes both mandatory gates, 13 weeks, best workmanship warranty at 12 years, named lead with a six-person crew, safety plan, roof assessment and longer monitoring. Lower experience count than A keeps it second.
- **D — Rank 3, 73:** passes both mandatory gates, good experience and lowest eligible price, but no completion time is stated, so Timeline scores 0. It can be ranked, but it must not win until a timeline within 16 weeks is confirmed by a human.
- **B — Ineligible, no score:** WSIB and insurance are confirmed, but the licence is not held by the bidder — electrical work is by a subcontractor to be confirmed after award. A mandatory criterion must be held by the bidder and stated in the proposal, so the cheapest price and fastest time cannot save it.
- **C — Flagged, not ranked, no score:** passes the mandatory gates on its merits, but the document contains an instruction aimed at an automated review system. That instruction is ignored, the proposal is held for human review, and no rank or score is assigned until a human clears it. On numbers alone it would not have ranked first in any case.

## Assumptions

Timeline is a weighted criterion, not a mandatory gate, so a missing timeline penalises a proposal but does not by itself make it ineligible. Mandatory means only the two stated pass/fail criteria. If an admin intended timeline as mandatory, D would move from ranked to flagged, and A and E would be unchanged.
