# Rubric 01 — Parse quality (phase 0)

Purpose: make sure the text the pipeline reads is the text a recruiter and an ATS read.

| Check | Pass | Penalty |
|---|---|---|
| Reading order | `two_column_ratio` < 0.25 (share of lines with ≥2 text spans split by ≥8 spaces) | −30, re-extract column by column |
| Sections found | Experience and Education headers detected | −20 each missing |
| Dated roles | every role has a parseable start and end | −5 per undated role |
| Contact line | email or LinkedIn URL in first 8 lines | −10 |
| Length | ≤ 1 page per 10 years of experience, max 2 pages (Bock) | −10 per extra page |
| Encoding | no `�`, no ligature junk (`ﬁ`, `ﬂ`) left after normalization | −10 |

Score = 100 − penalties. **< 70 → the agent must read the PDF pages as images (Read tool) and fix the text by hand before phase 1.**
A two-column source is always reported as fix #1 candidate ("single column for ATS"), because both test resumes with two columns extracted out of order.
