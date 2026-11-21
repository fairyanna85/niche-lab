# Phase 0 — Ingest

**Inputs:** resume file (PDF, DOCX, TXT/MD); LinkedIn as PDF export, pasted text or URL.
**Output:** `resume.txt`, `linkedin.txt`, `parse_report.json`, `ledger.json` (skeleton).
**Rubric:** 01 parse quality.

Steps
1. LinkedIn URL only: try `WebFetch` once on the public profile. If it returns profile text, save it to `RUN/linkedin_input.txt` and pass that file. If it is blocked (the usual case), continue resume-only; `parse_report.linkedin_status = "blocked"` and every LinkedIn cross-check is reported `not_run`. Never retry through other tools.
2. Run `python3 scripts/ingest.py --resume <file> [--linkedin <file|url>] --run RUN`.
3. Read `parse_report.json`.
   - `score < 70` or `two_column_ratio ≥ 0.25`: open the PDF pages as images (Read tool), compare with `resume.txt`, fix reading order by hand, and re-run step 2 on the corrected text file (`--resume RUN/resume.fixed.txt`). Two-column layout is fix candidate #1 in the report.
   - `unfilled_placeholder` (e.g. "+X ppt", "X%"): the candidate's own resume has blanks. Keep them as `[placeholder]` in every version; add to Confirm.
   - `overlapping_roles`: decide whether it is a side role (board, advisory, teaching) and label it in the ledger; never delete it.
   - `resume_linkedin_conflict`: record in the ledger line's `conflict`; the resume wins for text, the report lists the conflict.
4. Review `ledger.json` line by line. The script guesses `employer`, `title`, `dates`, `claim_type`; correct every wrong one. Set `own_role` on each metric/duty line: `led` only if the line says led/built/owned/managed; `co-led` if it says co-/jointly/with; `contributed` for supported/helped/participated; else `unknown`.

**Gate:** parse score ≥70 after fixes; every experience line has employer, title and dates.
