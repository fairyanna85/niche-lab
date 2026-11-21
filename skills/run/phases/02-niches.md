# Phase 2 — Generate, triage and screen niches

**Definition:** a niche = role family × seniority band × employer segment × city, with its own demand signature (≥15 live postings from ≥8 employers, a required-skills profile that differs from its siblings, its own pay band and peer pool).
**Inputs:** `profile.json`, `evidence.json`.
**Output:** `niches.json` (schema `niche.schema.json`).
**Rubrics:** 04 triage, 05 screen, 06 inclusion. **Prompt:** `prompts/niche-generator.md`.

Steps
1. Write 8–15 candidates (ids n01…). Start from the current niche; vary one dimension at a time; add observed moves from public bios. Cities only where the profile shows a tie.
2. For each candidate add `pref_checks`: 2–4 revealed-preference checks (city, employer type/stage, international scope), each `{pref, matched, grade}` with the grade of the underlying profile field.
3. Triage (rubric 04). Candidates scoring <5 → `verdict: "not_screened"` with the reason.
4. Screen: for each remaining candidate, search 3–5 exact title queries (WebSearch; employer careers pages and ATS boards first: Greenhouse, Lever, Ashby, Workday; then Built In, Indeed, Welcome to the Jungle for Paris). Store and quickly code ~15 postings per niche (phase 3 commands). A posting may belong to several niches — store once, list all niche ids.
5. Run `python3 scripts/postings.py liveness --run RUN --today <date>` then `python3 scripts/niches.py screen --run RUN`.
6. Read the verdicts. If fewer than 3 are kept, do not lower thresholds: say so in the report and list the closest rejects as Pivot candidates with what would make them viable. `--relaxed` (run_config) exists only for the example run and must print a banner.

**Gate:** every candidate has a verdict and a reason; 1–10 kept.
