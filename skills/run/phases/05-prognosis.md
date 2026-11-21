# Phase 5 — Prognosis: what is changing

**Inputs:** closed postings for the same niche from earlier years. **Output:** `change` block in `analysis.json` (computed by `analyze.py`).
**Rubric:** 10 signal strength.

Collection
1. Sources that keep removed postings: Built In (removal stamp "Sorry, this job was removed"; legacy URL scheme for 2020–21), employer careers pages that keep closed pages, aggregator archives. Wayback is often unreachable from the workspace; do not route around a block.
2. Date each with evidence: removal stamp, posted date, or an in-text anchor (funding round, award year, "in 2021").
3. Store with `era` = "2024-25", "2022-23" or "2020-21" and `source_type` = "archive". Code with the same prompt.
4. Target ≥15 archive postings over two eras per niche. If no 2020 postings exist, use the earliest era available and say so.

Analysis (automatic in `analyze.py`): Fisher exact per code (now vs archive), Cochran–Armitage trend across eras, Mantel–Haenszel odds ratio stratified by level (senior vs below, +0.5 correction), requirements per posting by era, years required then vs now.
Narrative: one insight sentence naming the 2–3 largest rises with their signal label; `do_this` items about which rising requirements to evidence first.

**Gate:** ≥15 archive postings, or `change` is null with the hidden reason.
