# Rubric 18 — Authenticity (anti-sameness)

Why: in a 2026 survey of 1,000 hiring managers, 80% said they can spot an AI-written resume; recruiters report AI resumes look nearly identical. This skill is itself an AI writing resumes, so this gate is mandatory.
Fail if any:
- A bullet has no candidate-specific detail from the ledger (named product, partner, market, number, team, tool).
- Stock phrases: ≥1 in headline/profile or ≥2 in the whole resume from `scripts/stock_phrases.txt`.
- One verb starts more than 2 bullets.
- Bullet length standard deviation <3 words (uniform machine rhythm).
- The profile paragraph could describe a different candidate in the same niche (test: swap the name; if nothing else breaks, rewrite).
