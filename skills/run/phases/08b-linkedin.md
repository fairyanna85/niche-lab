# Phase 8b — LinkedIn rewrite

**Inputs:** ledger, resumes.json, the rank-1 niche (headline, language chapter, pitch), `rulebook/linkedin_limits.yml`.
**Output:** `linkedin.json` (schema `schemas/linkedin.schema.json`), `out/linkedin.md`.
**Why it matters:** recruiters search LinkedIn by title and keywords. Current job titles carry heavy search weight, and the About section shows only about 300 characters before "See more".

Write:
1. **Headline** (≤220): niche title words, one proof number, two or three proven capabilities, one edge. No "Seeking opportunities".
2. **About** (≤2,600): the first 300 characters carry the role, the proof number and what you do for an employer in this niche. Then short paragraphs: what you built, what you did before, what you bring. First person, plain words, no stock phrases. Do not state preferences the person did not state (relocation, target cities).
3. **Experience descriptions** (≤2,000 each): lead with the strongest metric in the first 80 characters, then 2–5 short lines. Titles and dates exactly as on the resumes. Never rename a past title to the niche title.
4. **Skills:** 10–30, niche vocabulary first; the first three are the ones to pin.
5. **Open to work titles:** 1–5 titles from the niche's title queries.
6. **Featured:** what to pin, as placeholders when nothing public exists.
7. **Alternates:** one headline per other active niche.
8. **Connection note** (≤300) for warm approaches, with `[name]`.

Every number must appear in the ledger. Run `python3 scripts/gates.py --run RUN --linkedin` (limits, consistency with every resume, traceability, stock phrases, hook); fix every fail. Then `python3 scripts/render_linkedin.py --run RUN`.
