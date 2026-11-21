# Phase 8 — One resume per niche

**Inputs:** ledger, profile, niche blocks. **Output:** `resumes.json` (array of resume objects, schema in `results.schema.json → resumes`).
**Rubrics:** 16 fix priority, 17 bullet score, 18 authenticity, 21 disclosure. **Rulebook:** `rulebook/rules.md`. **Prompt:** `rewrite.md`.

Steps
1. Write the master selection: every role, its context line (placeholder if the resume lacks it), scope line, and the pool of bullets, each bullet citing ledger ids.
2. For each qualified niche (id `r-<niche>`), choose: headline (niche title words + 2–3 proven top requirements + one edge), a 2–3 line profile, bullet order by the niche's demand, skills ordered by the niche's top codes, the niche's "use" vocabulary. Dates, titles, employers, locations are identical across versions.
3. Missing numbers → `[short description]` placeholders. Never estimate. Methods (the Z in X-Y-Z) that the ledger doesn't state are placeholders too.
4. Apply disclosure defaults; strip stock phrases; vary bullet length.
5. Write the LinkedIn headline and About for the rank-1 niche as two `confirm_extra` items ("LinkedIn headline: …", "LinkedIn About: …"), so the candidate updates LinkedIn without contradicting the other versions.

**Gate:** one resume per qualified niche; `placeholders` counted.
