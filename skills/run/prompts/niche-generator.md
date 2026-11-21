# Prompt — phase 2 niche generation

Inputs: `profile.json`, `rubrics/04-niche-triage.md`, `rubrics/05-niche-screen.md`.
1. Write the current niche: role_family × seniority_band × segment × city from the profile.
2. Generate variants by changing ONE dimension at a time: adjacent role family (from the codebook modules and the candidate's strengths), adjacent segment, one band up, one band down, other city (only with a tie in the profile), other side of the market. Add observed moves: search public bios of people with the same past employers or titles and note where they went next.
3. Produce 8–15 candidates with `id` n01…, label in plain words ("Head of Partnerships, AI SaaS, New York"), `title_queries` (3–5 exact titles to search), `origin`.
4. Score triage (rubric 04) and record the notes. Screen in descending order (rubric 05).
Never invent a city, credential or language the ledger doesn't support.
