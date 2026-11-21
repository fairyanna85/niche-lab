# Prompt — phase 8 rewrite for one niche

Inputs: `ledger.json`, `profile.json`, the niche object from `results.json` (demand, language, fit, pitch), `rulebook/rules.md`, rubrics 16–18, 21.
Output: one resume object matching `results.schema.json → resumes[]`.
Hard rules
- Every bullet lists the ledger ids it draws from. Numbers, titles, employers and dates must appear verbatim in those ledger lines. A number the candidate did not give → `[X]` placeholder; count them in `placeholders`.
- Same facts across all versions of this candidate: only selection, order, emphasis and vocabulary change between niches.
- Headline: niche role title | 2–3 top required capabilities the candidate proves | one edge.
- Profile: 3 lines max; first line names the niche role and segment; one proof number; one edge.
- Each role: company context line (what the company is, size or stage), title, dates, scope line (people / budget / revenue), 2–5 X-Y-Z bullets ordered by niche demand.
- Use the niche's "use" vocabulary (language chapter); never the stock phrases.
- Apply disclosure defaults (rubric 21).
