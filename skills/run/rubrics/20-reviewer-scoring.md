# Rubric 20 — Reviewer panel

Three fresh subagents, prompts in `prompts/reviewer-*.md`, each sees the niche resume and the niche's top-10 must-haves only:
- Recruiter: keywords /10, scope clarity /10, red flags list.
- Hiring manager: relevance /10, proof /10, level fit /10.
- Adversarial CEO: verdict "Good job" or "Not yet" + at most 8 fixes.
Loop at most 3 times. Apply fixes raised by ≥2 reviewers or by the CEO. Decline any fix that breaks a hard rule (traceability, disclosure, placeholder rule) and log it in `gates` with the reason.
Reference run trajectory: CEO "Not yet" (8 fixes) → "Not yet" (5) → "Good job".
