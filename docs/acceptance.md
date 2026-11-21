# Acceptance on real data (cycle 10)

Outputs built from the three real test resumes stayed outside the repo. This file records results only, without names.

## (a) The reference report, figure by figure

The reference study's report (one real candidate, the same 42 current postings the example uses) was read figure by figure and every figure and block ticked against the new report, with all drawers open, for two niche selections (the top niche and the Paris niche).

| Reference figure or block | New report | Status |
|---|---|---|
| Eight phases, from niche to quality gates | `app-phases` + quality gates (method drawer) | present |
| Planned vs achieved sample | `mkt-sample` | present |
| Coding reliability per requirement | `app-kappa` | present |
| Demand map | `mkt-demand` | present (16 rows, 10 shown, 6 behind "show") |
| What rises with seniority | `mkt-seniority` | present; reproduces the reference's seniority gaps (diff and Fisher p, 25+ codes, `tests/test_contrasts.py`) |
| AI-native vs martech employers | `mkt-contrast` | present as "niche against its largest neighbour"; the segment pair appears when the AI-native niche is selected |
| NYC vs Paris | `mkt-contrast` | present when the Paris niche is selected (Paris against New York, 10 vs 10 postings, directional) |
| Requirements that travel together | `mkt-bundles` | present |
| Then vs now (three eras) | `mkt-change` | **partial**: two eras (older vs current), pooled across niches where a niche's archive is under 10; the reference showed three eras as small multiples |
| NYC pay: published base ranges | `mkt-pay` | present (ranges behind "show", midpoints visible) |
| Words hiring managers repeat | `mkt-words` | present |
| Builder index | `mkt-builder` | present |
| Distinctive vocabulary by audience | `mkt-keyness` | present per niche |
| Fit by segment | `vrd-fit` + ranking | present |
| Each posting: coverage vs pay | `vrd-scatter` | present where a niche has ≥ 3 postings with pay; the Paris niche has 2 and shows a stub saying so |
| The bridge | `vrd-bridge` | present |
| 12-week search plan | `crs-plan12` | present |
| Must-haves covered, old resume vs new | `crs-oldnew` | present (six-second zone and whole text) |
| Blind panel, old vs new | `crs-panel` | present; three readers in one session, labelled not independent |
| Mandatory before sending | `crs-confirm` | present |
| Hero tiles | `cover-tiles` | present (scale only; the verdict waits for act 4) |
| Three findings | `vrd-findings` | present |
| Statistical and linguistic toolkit | `app-toolkit` | present |
| Four target tiers | `vrd-verdict` + `crs-playbook` | present |
| Message rules by audience | `crs-rules` | present per niche |
| Golden formulas | `crs-formulas` | present, gated against the resume lines |
| Interview narrative | `vrd-narrative` | present (verdict drawer) |
| Rewritten resume and legend | `crs-resumes` | present |

Not run: a full rebuild with the reference candidate's own resume through every agent-written phase. The figure set does not depend on the candidate, and the example uses the same corpus, so the tick-off above was made on the example.

## (b) The other real resumes through the layout checks

Act 1 (career line, dissection, baseline) was rebuilt from each real ledger and audited at 320, 390, 768 and 1440 px: zero violations, zero script errors for all three.

Found and fixed: the career line came out wrong on real resumes. The parser put company names in the title field and locations in the employer field, and two-column layouts placed job titles after the bullets, so one resume produced one role instead of ten. `timeline.py` now groups roles by their date line. All three real resumes produce every role with correct dates (6, 10 and 8 roles). A synthetic test reproduces the pattern (`test_messy_two_column_ledger_is_grouped_by_date_line`).

Still imperfect: on one real resume the job titles sit away from their dates in the PDF, so the career line shows the company name in place of the title. Phase 0's ledger correction step (the agent fixing `employer` and `title` per role) is where that is fixed in a live run.

## (c) Live run with web search

Not done. A live run means collecting and coding 30+ real postings for a new profession through web search and page fetch. The any-profession claim still rests on the synthetic nursing, civil engineering and restaurant fixtures plus the reference corpus.
