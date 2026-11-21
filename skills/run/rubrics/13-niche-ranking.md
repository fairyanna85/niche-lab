# Rubric 13 — Niche ranking (opportunity score, 0–100)

Components, each normalized 0–1:
| Component | Weight | Formula |
|---|---|---|
| Fit | 35 | rubric 11 fit |
| Pay | 15 | clip((niche median / est. current pay − 0.7) / 0.6, 0, 1); if current pay unknown, rank niche medians and scale 0–1 |
| Demand | 15 | log(1 + live-weighted postings) / log(1 + max across niches) |
| Momentum | 10 | 0.5 + 0.5·tanh(3·growth), growth = (now share − archive share) of the niche's top-5 required codes, or posting-count growth when archives allow; 0.5 if unknown |
| Revealed-preference fit | 10 | share of matched revealed preferences (city, company stage, employer type, international scope), each weighted by its grade (stated 1, inferred2 0.75, inferred1 0.5) |
| Access | 10 | share of the niche's top-15 employers with an access path of strength ≥2 (rubric 15) |
| Rarity | 5 | share of the candidate's edges that match a code demanded in 5–30% of postings (rare and wanted) |

Weights are fixed because the user gives no input; they are printed in the report.
Sensitivity: 1,000 Dirichlet draws centred on the weights (concentration 50). Report each niche's rank frequency and P(top 3). The order is "stable" if the top-3 set is unchanged in ≥80% of draws; otherwise the report says which niches swap.
Sequence: run the top 2 now, plus the third if it scores ≥90% of the second, is not a Pivot and lands in the top 3 in ≥80% of weight draws (the search evidence favors 2–3 role types at once); next = rank 4–5; parked = rest, each with a trigger (e.g. "no interview after 10 referral-led approaches in the active niches").
