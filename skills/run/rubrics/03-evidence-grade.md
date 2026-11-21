# Rubric 03 — Evidence grade (candidate × requirement code)

| Grade | Meaning | Example (code `prog`, partner program design) |
|---|---|---|
| 0 | nothing | — |
| 1 | keyword only (skills list, vague duty) | "Partner programs" in a skills line |
| 2 | duty with scope and own role clear | "Designed the agency partner tiering for 40 agencies" |
| 3 | outcome with a number or verifiable artifact | "Designed tiering for 40 agencies; tier-1 revenue +35% in a year" |

Only grades 2–3 count toward fit. Credit: grade 3 = 1.0, grade 2 = 0.75.
`fit.py` pre-fills grades from `resume_cues` regexes in the codebook (max grade 2 from a regex alone; 3 needs a number in the same ledger line). The agent must review every pre-filled grade ≥2 and every 0 on a code with prevalence ≥50%.
