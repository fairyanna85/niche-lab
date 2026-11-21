# Phase 7 — Targeting

**Outputs:** `niches/<id>/access.json`, `niches/<id>/employers.json` (by rank.py), narrative blocks for employers, access, pitch, pay, plan30.
**Rubrics:** 14 employer opportunity, 15 access path, 08 liveness.

Steps
1. Access paths (inferred; the user gives no contacts). For each employer in the niche, look for public evidence: the candidate's past employers named as partners/customers/investors of the target; alumni of the candidate's past employers or schools on the target's team pages; shared ecosystems visible in the posting (e.g. the posting requires AWS co-sell and the candidate co-led an AWS Marketplace launch). Write `[{company, strength 0–3, path, evidence URL}]`. Never name a private individual.
2. Re-run `rank.py` (it writes employers.json with opportunity scores).
3. Narrative per niche:
   - `employers.do_this`: which 3–5 to approach first and why (score, liveness, access); which to watch, not apply.
   - `access.do_this`: the channel per strength (referral → warm intro → direct note + employer-site apply within 72 h → cold).
   - `pitch`: one-liner (role + proof + edge), 3 proof points from the ledger, 2–3 likely objections from the gaps with answers (placeholders where a fact is missing).
   - `pay` (only if the band exists): anchor = band p75 (or the posting's top if higher), walk-away = `[your floor]` placeholder (not inferable), a counter script; `do_this`.
   - `plan30`: four weeks, 1–3 actions each, ordered warm before cold, ending with a funnel review.
4. Funnel: keep the default benchmarks and diagnosis rules in `assemble.py`; add a `funnel.do_this` line about the tracker.

**Gate:** every qualified niche has employers, pitch, plan30 and either a pay block or a hidden reason.

## Added in 2.1

- **Golden formulas** (`narrative.json → niches.<id>.formulas`): for the niche's strongest requirement bundles (`analysis.json → bundles`, lift > 1.5), write one reusable sentence template with `[blanks]`, and an example built only from resume lines, with their ledger ids. Assemble rejects a formula whose bundle is not the niche's, whose ledger ids do not exist, or whose example states a number the cited lines do not contain.
- **12-week plan** (`narrative.json → plan12`): 6–10 items `{week: "1" | "3-6", track, action, target}`, tracks such as resume and profile, access, approaches, interviews, offers; extends the 30-day plan of the top niche. It is the course act's main figure.
