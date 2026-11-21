# Phase 2b — Induce a codebook module for any profession

**When:** a kept niche's job family has no module in `codebooks/` (only `partnerships`, `program-management` and `support-operations` ship). Nursing, engineering, hospitality, law, teaching, trades: all go through this phase.
**Inputs:** the niche's 15–20 screen postings in `postings/raw/`. **Output:** `RUN/codebooks/induced-<family>.yml` (run-specific; it wins over shipped modules), `RUN/codebooks/induced-<family>.reliability.json`.

1. `python3 scripts/induce_codebook.py candidates --raw-dir RUN/postings/raw --min-docs 3 > RUN/candidates.json` lists recurring requirement sentences and terms (licences, tools, acronyms) with document counts; boilerplate is dropped.
2. Open-code: read 5 full postings, then the candidate list. Merge synonyms ("BLS", "Basic Life Support"). Drop anything already in `core.yml` (people management, budget, licence, shifts, safety, customers, data, training, tools, languages, AI use).
3. Write 8–20 codes: `id` (lowercase, ≤12 chars, prefixed with the family, e.g. `nu_icu`), `label`, `posting_rule` (what makes it 2, 1, 0), `resume_cues` (regexes), plus `title_patterns` and `status: UNTESTED`.
4. `python3 scripts/induce_codebook.py validate RUN/codebooks/induced-<family>.yml` must print `ok`.
5. Reliability: you code the 15 screen postings; a fresh `second-coder` agent codes the same 15 blind. Save both as JSONL `{"id","codes"}` and run `induce_codebook.py reliability --a A.jsonl --b B.jsonl`. Sharpen the rule of every code in `sharpen` (κ < 0.6) and re-code those codes once. Codes still under 0.4 are deleted.
6. Set the niche's `module` in `niches.json` to `induced-<family>`. Levels use the six generic bands (`scripts/ladder.py`); pay is annualized per currency (`scripts/pay.py`) and never pooled across currencies.

**Gate:** module validates; pooled κ ≥ 0.6 after sharpening, or the niche is labeled low confidence.
