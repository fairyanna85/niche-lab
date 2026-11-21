# Rubric 02 — Field confidence (phase 1)

Every inferred field in `profile.json` carries one grade.

| Grade | Definition | May drive | Shown as |
|---|---|---|---|
| `stated` | the resume or LinkedIn says it in words | niche generation, ranking, resume text | plain |
| `inferred2` | ≥2 independent ledger lines imply it | niche generation, ranking | "inferred" chip |
| `inferred1` | 1 ledger line implies it | ranking only at half weight; never resume text | "inferred" chip + Confirm list |
| `absent` | nothing supports it | nothing; resume gets a `[placeholder]` | Confirm list |

Rules
- Evidence = ledger ids (`R12`, `L4`). A field graded `inferred2` with one id is a schema error.
- Reliable from a resume in the three-resume test: role family, industry, seniority band, city. Unreliable: target role, reporting line, span, side of market, own role, clearance to publish figures. Default those to `inferred1` unless explicit.
- `current_pay_band_est` is always at most `inferred2`: derive from title + level map + city from the niche pay data, never from a guess.
