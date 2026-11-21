# Phase 6 — Fit, qualify, rank

**Inputs:** analysis.json per niche, evidence.json, profile.json. **Outputs:** `fit.json`, `qualification.json`, `ranking.json`.
**Rubrics:** 11 fit, 12 qualification, 13 ranking.

Steps
1. Fill `profile.fields.current_pay_band_est.value` = `{"mid": <median posted midpoint for the candidate's current title/level/city>, "currency": "USD"}` from the niche that matches today's job; grade `inferred2`; note the niche and n. If no niche matches, leave `mid: null` (pay then ranks niches relative to each other).
2. `python3 scripts/fit.py score --run RUN --niche <id>` for each kept niche.
3. `python3 scripts/niches.py qualify --run RUN` → Core / Stretch / Pivot / Rejected, plus "pay step-down" and "low confidence" flags.
4. Write `niches/<id>/access.json` (phase 7 step 1) before ranking, because access is a ranking component.
5. `python3 scripts/rank.py --run RUN` → scores, 1,000-draw sensitivity, overlap matrices, sequence.
6. If fewer than 3 niches qualify, the summary headline must say so.

**Gate:** ranking.json exists; sequence has 2–3 "now" niches (or fewer with the reason).
