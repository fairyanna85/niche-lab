# Handoff to Sonnet: cycles 4, 5, 8, 9

Read `docs/CORRECTIVE-PLAN-v2.1.md` first (sections 2.2, 3, 4, 5). This file says what is already done, what is left, and how to work in this repo without breaking what the Opus cycles built.

## 1. State at handoff

| Cycle | Status |
|---|---|
| 0 Harness | Done. Tested auditor (`tests/ui/auditor.js`, `tests/test_auditor.py`), matrix (`tests/test_ui_invariants.py`), parity (`tests/test_parity.py`, `tests/parity_manifest.yml`), journey tests, ratchets, stress fixture, `tools/shoot.py`, `docs/design-rubric.md` |
| 1–3 Layout, controls, chart kit, journey | Done as one template rewrite. Full matrix clean (10 widths × 3 fixtures × both themes × 125% text). Journey ratchet empty |
| 3b Checkpoint | Published (artifact `10670917-cea7-4dc3-a618-0ac4c42df9fb`) |
| 4 Act 1 | **Partly done by Opus** (needed for the checkpoint): timeline (`scripts/timeline.py`, multilingual date parser, tests), dissection, strengths, edges, baseline summary. **Left for you: see 3.1** |
| 5 Act 2 | Sky, DNA, demand map, pay midpoints, ghost-job risk, niche list, per-niche trend, vocabulary are rendered. **Left: see 3.2** |
| 6 Act 3 | Done (peers, paths, rarity, odds, fictional peer set) |
| 7 Act 4 | Done (findings, bridge, fit strip, fit × pay scatter, plates, ranking, ladder, robustness, sequence) |
| 8 Act 5 | Actions, playbook, rules, resumes, LinkedIn, tracker, confirm are rendered. **Left: see 3.3** |
| 9 Appendix | Phases, limits, sources, gates rendered. **Left: see 3.4** |
| 10–11 | Opus, after you |

Suite: 166 passing. Parity gaps: 17 per fixture, every one of them yours (`tests/parity_baseline.json`).

Also read `docs/visual-review.md` → "Open, by owner": the independent design review assigned specific fixes to cycles 5 and 8.

## 2. How to work here

**The loop for every cycle**
1. Write the failing tests (unit tests for new computations; the parity rows already exist and are on the ratchet).
2. Implement: script → schema → assemble → example narrative (if authored text is needed) → `tests/fixtures/e2e_driver.py` (if the schema requires a new authored field) → template.
3. Rebuild the example: `bash examples/fictional-candidate/rebuild.sh` (runs the whole pipeline; ~1 minute).
4. Remove the closed gaps from the ratchet: `NL_UPDATE_BASELINE=1 python3 -m pytest -q tests/test_parity.py -k "test_parity["`. The file may only shrink; `test_parity_baseline_only_shrinks` compares against HEAD.
5. `make test` (fast matrix, ~2 min), then **`make test-full`** before every commit (full matrix; required from cycle 3 on). Both must be green.
6. `python3 tools/shoot.py /tmp/shots --fixtures example,stress` and look at every image of the act you changed, at 390 and 1440, dark and light. Fix what you see. Log it in `docs/visual-review.md`.
7. Commit with the attribution lines in the system prompt; one commit per cycle.

**Never**
- Add `data-audit-ignore`, more than 3 `data-btn-solo`, or more than 4 `data-decor`; a test counts them.
- Grow `tests/ui_baseline.json` (it is empty: the template has zero known violations) or `tests/parity_baseline.json`.
- Use `text-overflow: ellipsis`, truncate a label with "…", or let a container scroll sideways.
- Put real candidate data in the repo. The privacy test scans for the three real test candidates.
- Put more than five `[data-fig]` figures outside expanders in one act, or exceed the length budgets in `tests/ui_invariants.py` (`BUDGETS`). New figures usually belong in the act's `evidence(...)` drawer.

**Template conventions** (`skills/run/template/report.html`, one file, no network)
- `fig(id, src, node)` stamps `data-fig` (the manifest id) and `data-src` (the `results.json` keys it truly reads; space-separated; per-niche keys as `niches.<key>`). `test_every_result_block_rendered` uses `data-src`.
- `stub(id, src, what, why)` when data is missing: it must say why. The example may have **no** stubs; the stress fixture may, for manifest rows of kind `stub-ok`.
- `forNiche(n => node)` re-renders on niche selection. Read the selected niche only through it.
- `panel(title, desc, body, foot)`, `evidence(title, [nodes], note)`, `act(list)` for "Do this", `phHTML(text)` for any authored text (it renders `[placeholders]` and turns internal niche ids into names).
- Charts: never hand-draw SVG text. Compose the kit, which keeps labels in HTML where they wrap and draws at the container's real width: `barRows(rows, o)` (bars or dots; `lo/hi` interval, `req` line, `m2` ring, `band` benchmark box), `dotStrip`, `stripRows` (one strip per row, shared axis), `scatter`, `linkDiagram`. Wrap them in `chart(draw)`. Every data mark carries `data-mark`; the parity test compares mark counts with the rows in `results.json` where a `rows:` function is declared in `tests/test_parity.py`.
- Numbers in authored text (journey, findings) must exist in `results.json`; `build_report.py` fails otherwise.
- Colours: `HUE(nicheId)`, `var(--gold)` for the candidate, `var(--ink*)` for text. Never put the series colour on text.

## 3. What is left

### 3.1 Cycle 4: Act 1 (You)
- `you-rare` (block): the candidate's top rare proofs from `market.rarity` (highest asked share minus peer share), as one sentence each. Small; place it with `you-edges` or as a strip under it.
- `baseline.zone_coverage` (contract §5): for each niche, must-haves covered in the six-second zone (headline, summary, first role's first three bullets) and in the whole text, for the original and the rewritten version. Compute in `scripts/baseline.py` (zone) and `gates.py` (rewritten). It feeds `you-baseline` (original) and `crs-oldnew` (cycle 8).
- Tests: zone extraction on the example and the French fixture; schema.

### 3.2 Cycle 5: Act 2 (The market)
Data exists for three of these; the rest need computation in `scripts/analyze.py`.
- `mkt-bundles` from `niches[].demand.bundles` (lift, support). Chart: `barRows` of pair labels by lift.
- `mkt-builder` from `niches[].demand.builder`.
- `mkt-words` from `niches[].language.phrases` (the phrases employers repeat, with counts).
- `mkt-seniority`, `mkt-contrast`: `analyze.contrasts` under the small-sample rule in plan §5.2 (within-niche only when each side has ≥ 10 postings; Fisher p < 0.05 solid, otherwise hollow and labelled directional; Wilson intervals). Use `barRows` with `lo/hi` or a diverging layout built from it. **Reference test:** reproduce `reference/partnerships-2026/results.json → gaps` (segment contrast) and the NYC (32) vs Paris (10) comparison from `prev`.
- `mkt-titles`: `market.title_shift[]` from live and archive titles, Fisher p. **Reference test:** `reference/partnerships-2026/titles.py` output.
- `market.change` pooled across niches for any niche whose archive is under 10 (the example's archives are 4, 0, 0, 13). This removes the `mkt-change: stub` gap. **Reference test:** `reference/partnerships-2026/then_now.json`.
- `mkt-pay` ranges: `niches[].pay.ranges[]` per posting (`lo`, `hi`, `currency`, `source`, `flagged` for aggregator-estimated ranges). Render as range rows; keep the midpoint strip.
- `mkt-sample`: `method.sample[]` planned vs achieved per niche.
- Keep act 2 at five headline figures: sky, DNA, demand map, pay, plus one. Everything else goes in the evidence drawer.

### 3.3 Cycle 8: Act 5 (The course)
- `crs-formulas`: phase 7 prompt and gate. Each formula turns a requirement bundle into a sentence template with a filled example from the ledger; the gate checks every formula cites a bundle and ledger ids and contains no number absent from the ledger. Copy buttons (`copyBtn`).
- `crs-plan12`: 12-week plan as a gantt (`plan12[]`: `week`, `track`, `action`, `target`). Extend `plan30`; add a `gantt` primitive to the kit (HTML labels, rows per track, narrow mode as a week-by-week list). This is the act's signature visual (the review asked for one); give it the full width near the top.
- `crs-oldnew`: must-haves covered old vs new, whole text and six-second zone, per niche (from 3.1).
- `crs-bullets`: bullets written as result + measure + method, complete vs waiting on a placeholder (from `gates`).
- `crs-panel`: blind old-vs-new panel for "run now" niches only (labels randomised; the reviewer is never told which is the original), plus the review rounds already in `RUN/reviews/` copied into `resumes[].review`. Render scores and rounds.

### 3.4 Cycle 9: Appendix
- `app-kappa`: agreement per code from `niches[].demand.reliability.per_code`.
- `app-toolkit`: method table (test, what it answers, where it is used).
- `app-postings`: every posting with URL, niche, liveness band and codes, filterable by niche; a stacked-card table on phones. Inside an expander.
- `app-phases` already renders `method.steps`; add status per phase (done / reduced sample / not run) if you add it to the contract.

## 4. Definition of done for your part
- `tests/parity_baseline.json` is `{"example": [], "stress": [...only stub-ok rows...]}`.
- `make test-full` green; `tests/ui_baseline.json` still `{}`.
- Example rebuilt; every act read in screenshots at 390 and 1440, both themes; `docs/visual-review.md` updated.
- Nothing in section 2's "Never" list.

Then hand back to Opus for cycle 10 (real-data acceptance: the reference candidate rebuilt and ticked figure by figure against the original report, the other two real resumes through the matrix, one live run) and cycle 11 (visual pass, design review round 3, release 2.1.0).
