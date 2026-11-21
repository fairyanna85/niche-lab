# Phase 3 — Demand: collect, code, dissect, diagnose

**Inputs:** kept niches. **Output:** `postings/` store, `niches/<id>/analysis.json`.
**Rubrics:** 06 inclusion, 07 coding, 08 liveness, 10 signal strength. **Prompts:** `code-posting.md`, `second-coder.md`.

Collection (per kept niche, target ≥30 "now" postings)
1. Search: exact title queries × city; employer careers pages; ATS boards; aggregators last. Record for each posting: URL, source type, first-seen date, any posted date, repost evidence.
2. Fetch the full text (WebFetch). Save to a temp file and run
   `python3 scripts/postings.py store --run RUN --text-file /tmp/p.txt --meta '{"niche_ids":["n01"],"company":"…","title":"…","city":"…","level":"Head","segment":"…","url":"…","source_type":"employer","era":"now","date_seen":"YYYY-MM-DD","date_evidence":"…"}'`
   The script refuses texts under 120 words and merges duplicates (keeps the employer copy).
3. Code each posting with `prompts/code-posting.md` (codebook = core + module), save the JSON, and run `postings.py code --run RUN --id pNNNN --codes-json /tmp/c.json`.
4. Reliability: `postings.py sample --run RUN` lists 20% (min 8). Spawn a fresh subagent with `prompts/second-coder.md` for those postings; save its outputs as `postings/second.jsonl` lines `{"id":…,"codes":{…}}`.
5. `postings.py liveness --run RUN --today <date>` and `postings.py validate --run RUN`.

Analysis
6. `python3 scripts/analyze.py --run RUN --niche <id>` for each kept niche. It produces prevalence with Wilson CIs, required shares, bundles (lift), archetype clusters, pay band with bootstrap CI, years, builder index, keyness against the other niches, kappa per code, and the change block (phase 5).
7. Read `reliability.per_code`. Codes with κ <0.4 are excluded automatically; for 0.4–0.6, add "weak reliability" wherever a finding uses the code.
8. Write the niche's `demand.insight` (one sentence: the 2–3 requirements in most postings, with "k of n") and 1–3 `do_this` items in `narrative.json` (phase 10 format).

**Gate:** each kept niche has analysis.json; pooled κ reported; any niche under 30 postings is labeled low confidence in the report.
