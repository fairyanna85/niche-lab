# Rubric 05 — Niche screen (keep / merge / reject)

For each triaged niche, collect and quickly code 15 postings (core codes + module codes, coder A only).

| Verdict | Rule |
|---|---|
| keep | ≥15 live postings in the last 90 days from ≥8 distinct employers AND screen coverage ≥0.40 |
| merge | cosine similarity of required-code vectors with a kept niche ≥0.85 AND same role family → merge into the niche with more postings; keep both titles as queries |
| reject: volume | <15 postings or <8 employers after 3 query reformulations (log them) |
| reject: blocker | required credential, licence, language or work authorization the profile shows no signal for |
| reject: coverage | screen coverage <0.40 (share of codes present in ≥50% of postings where the candidate has grade ≥2) |

Ten kept niches is the ceiling. If fewer than 3 survive, do NOT pad: report "fewer than 3 viable niches" and list the closest rejects as Pivot candidates with what would make them viable.
Every reject stays in `results.json → portfolio.rejected` with its reason.
