# Prompt — phase 1 dissection

Inputs: `ledger.json` (every resume and LinkedIn line with an id), `parse_report.json`, `rubrics/02-field-confidence.md`, `codebooks/*.yml`.
Produce `profile.json` matching `schemas/profile.schema.json`.

For EVERY field: value, grade (stated / inferred2 / inferred1 / absent), evidence ids. Do not fill a field from general knowledge about the employer; use only ledger lines, except `level_map` and `current_pay_band_est`, which combine ledger lines with public level/pay data you cite in `note`.
Fields to infer:
- role_family (which codebook module fits; may be two), seniority_band (IC / Manager / Director / Head-VP / C), level_map (equivalent title at a 1,000-person tech company), industry, side_of_market (vendor / agency / platform / buyer / consultancy), span_people, span_budget_or_revenue, own_role (led / co-led / contributed per major claim), years_experience, current_pay_band_est, work_auth_signals (citizenships, locations worked, languages).
- revealed_preferences: employer_types, cities, median_tenure_years, company_stage, mobility (moves across cities/countries) — from the career history pattern, not from wishes.
- strengths: the 5–8 capabilities with the strongest evidence (grade them with rubric 03 against the closest code).
- edges: capabilities that are uncommon for the role family (e.g. builds software as a non-engineer, two-country career, both sides of a market).
- disclosure_risks: apply rubric 21.
Write a one-paragraph `positioning_hypothesis` in `profile.json → fields.positioning` as `inferred2` at best.
