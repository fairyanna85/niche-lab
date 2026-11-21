# Rubric 07 — Requirement coding and reliability

Procedure per posting (prompt: `prompts/code-posting.md`):
- Code every core + module code 2 / 1 / 0 using the `posting_rule` of each code.
- `must_haves`: the 5 requirements a recruiter would screen on, paraphrased in ≤10 words each.
- `phrases`: up to 2 distinctive verbatim phrases ≤8 words (language chapter source).
- Count builder verbs (build, launch, create, scale, design, establish, grow, drive) and maintain verbs (manage, maintain, support, coordinate, oversee, assist).

Reliability (mandatory):
- A second coder (fresh subagent, blind to coder A, prompt `prompts/second-coder.md`) codes 20% of postings, minimum 8, chosen at random with a fixed seed.
- `analyze.py --kappa` computes Cohen's kappa per code and pooled.
- kappa ≥0.6: normal. 0.4–0.6: findings on the code labeled "weak reliability". <0.4: code excluded from fit, ranking and headline findings.
Reference run: pooled kappa 0.79 on 18 codes; src and infl at 0.0, pc at 0.5 — these rules exist because of that.
