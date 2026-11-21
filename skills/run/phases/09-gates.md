# Phase 9 — Quality gates and review loops

**Outputs:** `gates.json`, `reviews/<resume_id>.json`, rendered PDFs.
**Rubrics:** 17–21. **Prompts:** `advocate.md`, `reviewer-recruiter.md`, `reviewer-hiring-manager.md`, `reviewer-ceo.md`.

Loop (max 3):
1. `python3 scripts/gates.py --run RUN --pdf` → traceability, consistency, authenticity, bullet score, keyword coverage (on codes the candidate can prove), six-second zone, length (rendered pages), disclosure, placeholders, ATS parse of the rendered PDF.
2. Fix every `fail`. Fix `warn` where a fix needs no new fact.
3. Advocate test: fresh subagent, top third only, one sentence per version. Pass = role family + a top-3 proof point + the niche segment.
4. Reviewer panel: three fresh subagents (recruiter, hiring manager, adversarial CEO) per version, each with the niche's top-10 must-haves. Apply fixes raised by ≥2 reviewers or by the CEO. A fix that needs a fact the ledger lacks becomes a placeholder + Confirm line. A fix that breaks a hard rule is declined and logged.
5. Write `reviews/<id>.json`: `{"advocate":{"status":"pass|warn|fail","sentence":"…"},"panel":{"loops":n,"ceo":"Good job|Not yet …","recruiter":"…","hiring_manager":"…"}}`.
6. Re-run step 1. Stop at no `fail` and CEO "Good job", or after loop 3 with the remaining issues reported.

Example run trajectory: loop 1 CEO "Not yet" ×3, "Good job" ×1; loop 2 "Good job" ×1 more; loop-2 fixes applied to the last two and not re-reviewed (reported as warn).

**Gate:** no `fail` in gates.json.

## Blind old-vs-new panel (2.1)

For the "run now" niches only (at most three): `python3 scripts/blind_panel.py prepare --run RUN` writes each packet with the original and the new resume as A and B at random. Run `prompts/blind-panel.md` on each packet with a reviewer that never sees the `.key.json` files, save `reviews/blind-<niche>.result.json`, then `blind_panel.py unblind`. Report the result as it is, including a loss: readers penalise unfilled blanks, which is itself the finding to act on.
