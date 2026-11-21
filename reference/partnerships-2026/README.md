# Reference run — Partnerships / Alliances, New York and Paris, 2026

The study this skill was extracted from. Kept unchanged except for path fixes, so the generalized scripts can be checked against it (`tests/test_reference.py`). Candidate-specific files from that study are not included.

| File | What it is |
|---|---|
| `data.py` | 42 coded 2026 postings (32 New York, 10 Paris); `SECOND` = blind second coding of 8 postings on 18 codes |
| `hist.py` | 17 closed postings (2020–21 n=5, 2024–25 n=12), dated by Built In removal stamps or in-text anchors |
| `analyze.py` | prevalence, gaps, lift, clustering, pay bootstrap, keyness, Cohen's kappa → `results.json` |
| `then_now.py` | Fisher exact, Cochran–Armitage, AI composites, builder index, pay, term shifts → `then_now.json` |
| `mh_adjusted.py` | seniority-adjusted Mantel–Haenszel odds ratios (rebuilt from the original thread) |
| `titles.py` | 2020 vs 2026 title vocabulary |
| `prompt.txt` | the original coding prompt (now `skills/run/prompts/code-posting.md`) |
| `sources.md` | every posting URL |

Headline numbers it reproduces: build-from-zero 24% → 62% (OR_MH 4.29); reports to C-level 0% → 31% (OR_MH 7.46); candidate AI fluency 0% → 28% (OR_MH 7.16); requirements per posting 11.7 → 14.0 (Mann–Whitney p = 0.05); pooled kappa 0.79 (agreement 0.91).

Known weaknesses that shaped the skill: raw posting text was not stored (now mandatory); kappa covered 18 of 35 codes and was 0.0 on `src` and `infl` (now: every code is second-coded and κ < 0.4 excludes a code); the codebook was written before reading postings (now: modules are written from 15 screen postings).
