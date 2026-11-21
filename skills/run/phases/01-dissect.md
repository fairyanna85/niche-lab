# Phase 1 — Dissect the candidate

**Start with the end in mind.** Later phases need, from this phase: role family (picks the codebook module and the niche seeds), seniority band and level map (niche level, pay estimate, Stretch vs Core), segment and side of market (niche segment), city ties and languages (which cities may be niches), span and own role (scope lines, bullet credibility), strengths and edges (fit and rarity), disclosure risks (rewrite), revealed preferences (ranking component).

**Inputs:** `ledger.json`, `parse_report.json`, codebooks.
**Output:** `profile.json` (schema `profile.schema.json`), `evidence.json`.
**Rubrics:** 02 field confidence, 03 evidence grade, 21 disclosure.
**Prompt:** `prompts/dissect.md`.

Steps
1. Pick the codebook module(s): compare the ledger's titles and duty lines with each module's `title_patterns` and codes. A versatile profile may get two modules (e.g. partnerships + program-management). If no module fits, write a new module first (see `codebooks/README.md`), from 15 screen postings, before coding anything.
2. Fill `profile.json` following `prompts/dissect.md`. Every field carries grade + ledger ids. Fields the three-resume test showed are usually NOT on a resume — target role, reporting line, span, side of market, own role, clearance to publish figures — default to `inferred1` or `absent` unless a line states them.
3. `current_pay_band_est`: leave `{"mid": null}` now; fill it in phase 6 from the run's own posting data for the candidate's current title/level/city, grade `inferred2`, with the note naming the niche and n.
4. Run `python3 scripts/fit.py prefill --run RUN --modules <m1,m2>`. Review `evidence.json`: confirm or correct every grade ≥2, and check every grade 0 on codes that are core to the role family. Regex cues mis-fire (in the example run, "board" matched "onboarding"); you are the check. Set `"reviewed": true` on every code.
5. Validate: `python3 -c "import sys; sys.path.insert(0,'scripts'); from common import *; print(validate(load('RUN/profile.json'),'profile'))"` must print `[]`.

**Gate:** schema valid; no unreviewed evidence; disclosure risks listed with default actions.
