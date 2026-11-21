# Rubric 08 — Posting liveness (ghost-job risk)

Why: Greenhouse classifies 18–22% of postings on its platform in a typical quarter as not actively being filled; agencies post 3% of listings but 10.8% of likely ghosts. Stale postings distort demand size and waste applications.

Start at 100 and subtract:
| Signal | Penalty |
|---|---|
| Age since first seen >30 days / >60 / >90 | −20 / −40 / −60 |
| Reposted (same company+title re-listed with new id, ≥10 days apart), per repost | −15 (max −30) |
| Only found on an aggregator, not on the employer site / ATS | −10 |
| Posted by an agency or "confidential" employer | −15 |
| No pay range where the law requires one (NYC, CA, CO, WA, IL; EU employers from June 2026) | −10 |
| Evergreen wording ("talent pool", "future opportunities", "always accepting") | −30 |
| Thin text (<150 words) and no team or manager named | −10 |
| Public layoff or hiring-freeze news at the employer in the last 90 days | −15 |

Bands: ≥70 `live`, 40–69 `doubtful`, <40 `likely_ghost`; removal stamp or 404 → `closed`.
Use: demand size counts live = 1, doubtful = 0.5, likely ghost = 0. Coding and language use all non-ghost postings. Employer ranking uses the score directly. Archive postings are `closed` by definition and are only used for then-vs-now.
