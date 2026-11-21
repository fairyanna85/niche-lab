# Prompt — code one posting (coder A)

You are coding a job posting for a labor-market study. Read the FULL text below. Output exactly one JSON object on one line, no prose, matching `schemas/posting.schema.json` fields `company, title, city, level, date_evidence, pay, years_required, codes, must_haves, phrases, builder_verbs, maintain_verbs`.

Codebook: {{CODEBOOK}}   ← core.yml + the niche module, each code with its `posting_rule`.

Rules
- codes: 2 = required / core responsibility; 1 = preferred or mentioned; 0 = absent. Apply each `posting_rule` literally. When unsure between 1 and 2, choose 1.
- level: one of entry, experienced, lead, manager, director, executive (scripts/ladder.py gives the default from the title; override only when the posting states the ladder).
- pay: only a stated range, as salary_min, salary_max, currency and pay_unit (hour, day, week, month or year). The script annualizes. Never infer pay.
- years_required: the smallest number stated, else null.
- must_haves: the 5 things a recruiter would screen on, ≤10 words each, paraphrased.
- phrases: up to 2 distinctive verbatim phrases, ≤8 words each.
- builder_verbs = count of build/launch/create/scale/design/establish/grow/drive (any inflection); maintain_verbs = count of manage/maintain/support/coordinate/oversee/assist.
- date_evidence: every date signal visible (posted, "x days ago" + today's date, removal stamp, funding round year, award year).
- If the text has no job description, output {"empty": true}.

POSTING TEXT:
{{TEXT}}
