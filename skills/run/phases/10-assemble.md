# Phase 10 — Assemble and build the report

**Output:** `results.json`, `out/report.html`, `out/resume-*.{pdf,md,html}`.

1. Write `narrative.json`:
```
{ "summary": {"headline", "run_now": [ids], "fixes": [{text, why}] ×≤5, "gaps": [{text, why}] ×≤3, "narrative", "do_this": []},
  "profile_view": {"do_this": []}, "portfolio": {"do_this": []}, "funnel": {"do_this": []},
  "niches": {"n01": {"demand": {"insight", "do_this"}, "change": {"insight", "do_this"}, "peers": {"insight", "do_this"},
                     "language": {"use", "avoid", "do_this"}, "fit": {"fixes": {code: text}, "do_this"},
                     "employers": {"do_this"}, "access": {"do_this"}, "pitch": {"one_liner", "proof_points", "objections", "do_this"},
                     "pay": {"anchor", "walk_away", "script", "do_this"}, "plan30": [{week, actions}]}},
  "confirm_extra": [{item, why}], "method_steps": [], "limits": [], "sources": [{title, url}] }
```
   Blocks for hidden chapters may be omitted. Every number in the narrative must come from a script output; quote it with "k of n".
2. `python3 scripts/assemble.py --run RUN` (validates against the schema).
3. `python3 scripts/render_resume.py --run RUN --pdf`.
4. `python3 scripts/build_report.py --results RUN/results.json --out RUN/out/report.html` (fails on a missing do_this).
5. Open the report (screenshot with headless Chrome) and look at it: overlapping labels, empty charts, clipped tables. Fix and rebuild.
6. Deliver: the report, the per-niche resume PDFs, and a 3-line summary (niches to run now, top fix, number of items to confirm). If an artifact tool is available, publish the report HTML as an artifact.

## Journey text and findings (2.1)

Write `narrative.json → journey.acts[]` for cover, you, market, peers, verdict, course and method: the act's question (ending in "?"), a one-sentence answer, up to three "what we learned" lines and the hand-over sentence to the next act. Write `summary.findings`: exactly three cards (the stable core, the new demands, the rare proof). Every number in this text must appear in `results.json`; `build_report.py` fails otherwise. The verdict must not appear before act 4.
