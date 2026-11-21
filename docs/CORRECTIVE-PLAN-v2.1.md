# niche-lab v2.1 corrective plan (TDD)

Author: Fable. Builder: Opus. Scope: the report (template, assemble, the phases that feed it). The pipeline, plugin packaging and gates stay as they are unless a cycle below names them.

"The reference report" below means the original single-candidate partnerships study the skill was extracted from. Its content is real-person data and never enters the repo; parity is by figure and block type, fed from `results.json`.

## 1. What is wrong, measured

Audit run on `examples/fictional-candidate/report.html` at 320, 390, 768, 1024 and 1440 px.

| Feedback | Finding | Evidence |
|---|---|---|
| Horizontal scroll | The page itself scrolls sideways at 320 px | document width 348 in a 320 viewport |
| Horizontal scroll | Four inner scrollers | top nav: 835 px of links in a 53 px slot at 390 (only "Atlas" visible); niche tabs: 990 px wide, scroll at every width under 1440; employer table; tracker diagnosis table |
| Text exceeds containers | Chart labels leave their SVG | market DNA row labels cut by up to 53 px at 320–390; niche-page requirement and fix-ladder labels cut at 320, 390, 768, 1024 and 1440 |
| Text exceeds containers | Labels truncated with "…" | every DNA row on mobile ("Owns partner-sourced pi…") |
| Text exceeds containers | Tag escapes its cell | "low confidence" in the ranking table, by 35 px (390) and 61 px (320) |
| Buttons | No shared geometry | filter chips 42–215 px wide on three ragged rows; niche tabs 227–249 px; `.btn` 54–250 px; resume version buttons 62 vs 41 px tall |
| Buttons | Small tap targets | 30–31 buttons under 44 px in one dimension (chips are 30 px tall) |
| Flow | Conclusion first, no "you" chapter | order is Atlas → Verdict → Next moves → DNA → You vs market → Ranking → Niches → Resumes → LinkedIn → Plan → Quality → Confirm; 12 flat nav links |
| Flow | The dissection is computed and never shown | `profile_view` (12 fields, strengths, edges) is in `results.json`; the template never reads it |
| Parity | Data computed, not rendered | `demand.bundles`, `demand.builder`, `demand.years`, `language.phrases`, `profile_view`, `reviews/*` (in the run folder, never copied into `results.json`). Corrected in cycle 0: `summary.narrative`, `fixes` and `gaps` are rendered (verdict section); the first draft's text search missed them |
| Parity | Not computed at all | seniority contrast, niche-vs-niche contrast, posted pay ranges per posting, planned-vs-achieved sample, asset-to-requirement bridge, 12-week plan, golden formulas, old-vs-new blind panel, six-second-zone coverage split |

### Root cause

1. **Tests asserted features, not geometry.** `test_mobile_legible_and_no_overflow` checks one width and only the document's scroll width. Nothing tested inner scrollers, text leaving its box, SVG labels, truncation or button sizes.
2. **One fixture with short labels.** The example has four niches and short employer names. No stress case.
3. **The atlas rewrite (cycle 8) replaced the v1 template instead of extending it,** and the contract test only checks that `results.json` validates, not that every block of it is rendered. Seven computed blocks were dropped silently.
4. **The section order was organised by artefact** (map, verdict, tables) rather than by the reader's question.

## 2. Target design

### 2.1 The journey: five acts, one question each

| Act | Station label | Question it answers | Ends by handing over |
|---|---|---|---|
| Cover | — | "What can the market do with a record like yours?" | the five stations as a route map; "Skip to the verdict" link |
| 1 | You | What do you bring, on the evidence? | "This is your supply. Now, who is asking for it?" |
| 2 | The market | What do employers ask for, where, at what pay, and how is that changing? | "This is the demand. Who else is answering it?" |
| 3 | The competition (station: Peers) | Who else supplies this, and what is rare about you? | "Supply, demand, competition. Here is what they add up to." |
| 4 | The verdict | Where do you fit, which niches win, and why? | "The decision is made. Here is how to run it." |
| 5 | The course | What exactly do you do, send and say, in what order? | tracker and confirm list |
| Appendix | Method | How was this measured, and what are its limits? | — |

Rules:
- The cover poses the question and shows scale (postings read, employers, niches found). It does **not** state the verdict. One "Skip to the verdict" link serves the reader in a hurry.
- Each act opens with a chapter head: number, station name, the question as the headline, a one-sentence answer. Numbering is legitimate here: it is a sequence.
- Each act closes with a "what we learned" strip of at most three sentences computed from data, then the hand-over sentence and a Next button.
- Advice ("Do this") stays attached to the evidence it follows from in acts 1–4; act 5 gathers every action into the ranked list.
- **Depth on demand.** Each act shows at most five headline figures; the remaining evidence sits in "See the evidence" expanders, closed by default. Without this, 48 figures turn the journey into a data dump.
- **Length budget, calibrated on today's report.** Today's example is 40.3 screens at 390 px and 21.7 at 1440 with fewer figures than planned; the niche pages alone are 8.3 screens on a phone and the workbench sections (actions, resumes, LinkedIn, plan, confirm) 16.3. Budgets with expanders closed, in screens at 390 / 1440: cover 1.5 / 1; acts 1–4 ≤ 7 / 3.5 each, sky opener included; act 5 ≤ 12 / 6, because it is a workbench (resume versions, LinkedIn fields and tracker open as tool panels, one at a time); appendix ≤ 3 / 1.5. Whole report ≤ 45 / 22.
- **Navigation without the bar.** Each act has a URL anchor (`#you`, `#market`, `#peers`, `#verdict`, `#course`, `#method`) so a link can open on any act, and the browser's back button returns to the previous act.
- **The connective text is written, not templated.** The act answers, learned strips and hand-overs are authored in the narrative step of phase 10 into `journey.acts[]`, and gated like resume text: every number in them must match `results.json`.
- One niche selector, sticky under the station bar from act 2 onward. The selected niche persists across acts and in storage. It replaces the 990 px tab strip.

### 2.2 Where everything goes (parity manifest)

Status: **R** rendered today (move it), **D** data exists, render it, **N** new data and new figure.

| Act | Block or figure (`data-fig` id) | Reference-report equivalent | Status |
|---|---|---|---|
| Cover | `cover-tiles` postings, employers, coder agreement, must-haves covered, new demands | five hero tiles | N (assemble from existing numbers) |
| 1 | `you-dissection` 12 fields with confidence grade and ledger lines | — (v2 gain) | D |
| 1 | `you-timeline` roles on a time axis with scope markers | — | N (from ledger) |
| 1 | `you-strengths`, `you-edges`, `you-rare` | "rare proof" finding card | D |
| 1 | `you-baseline` how the current resume reads: gates, six-second zone, parse | old-resume half of chapter 4 | R + N (zone split) |
| 2 | `mkt-atlas` star map, four encodings | — | R |
| 2 | `mkt-niches` found and screened out, with reasons | niche definition and segments | R |
| 2 | `mkt-sample` planned vs achieved per niche | planned vs achieved sample | N |
| 2 | `mkt-dna` requirement × niche matrix | — | R (rebuild responsive) |
| 2 | `mkt-demand` demand map with 95% intervals, required share, your proof | demand map | R |
| 2 | `mkt-seniority` what rises with seniority (diverging, significant bars solid) | what rises with seniority | N |
| 2 | `mkt-contrast` selected niche vs another (dumbbell, sorted by gap) | AI-native vs martech; NYC vs Paris | N |
| 2 | `mkt-bundles` requirements that travel together (lift) | requirement bundles | D |
| 2 | `mkt-change` then vs now small multiples, test results, stat tiles (requirements per posting, years asked, build-verb share, pay midpoint) | then vs now | R per niche; pooled `market.change` when a niche's archive is < 10 |
| 2 | `mkt-titles` title vocabulary then vs now (terms gaining and losing share in job titles, with Fisher p) | "titles containing Channel: 21% → 0%" | N (archive titles; title-only archive counts) |
| 2 | `mkt-pay` posted ranges per posting, median line, aggregator ranges flagged | NYC pay ranges | N (ranges) + R (dots) |
| 2 | `mkt-words` phrases employers repeat | words hiring managers repeat | D |
| 2 | `mkt-builder` builder index | builder index | D |
| 2 | `mkt-keyness` distinctive vocabulary | keyness | R |
| 2 | `mkt-live` ghost-job share vs benchmark | — | R |
| 3 | `cmp-peers` peer median vs top quartile vs you | peer benchmark (blocked in the reference) | R (stub only below 8 peers per niche; see 5.1) |
| 3 | `cmp-paths` how the people now in these jobs got there: prior role type → current role, most common paths first | "precedents ran through a hyperscaler alliance role" | N |
| 3 | `cmp-asks` years asked and level mix vs you | — | R (from "you vs market") |
| 3 | `cmp-rarity` each of your proofs: share of postings asking, share of peers showing | "0 of 42 ask for it" | N |
| 3 | `cmp-odds` applicant-to-offer and referral benchmarks, sourced | 2026 search evidence | D (rulebook) |
| 4 | `vrd-findings` three finding cards: stable core, new demands, your rare proof | three finding cards | N (from existing numbers) |
| 4 | `vrd-bridge` your assets mapped to what employers ask (two-column link diagram) | the bridge | N |
| 4 | `vrd-fit` fit by niche, must-haves proved / partly / not shown | fit by segment | R |
| 4 | `vrd-scatter` each posting: fit × pay, apply line | coverage vs pay scatter | D |
| 4 | `vrd-ladder` fix ladder | — | R |
| 4 | `vrd-ranking`, `vrd-robust` score table, 1,000-weighting robustness | — | R |
| 4 | `vrd-verdict` plates with roses, run now / hold | four target tiers | R |
| 4 | `vrd-narrative` the story to tell | interview narrative | R |
| 5 | `crs-playbook` per niche: employers, access, pitch, objections, pay script | tier cards, corpus examples | R |
| 5 | `crs-rules` message rules: use, avoid, lead with | message rules by audience | R + D |
| 5 | `crs-formulas` bundles turned into sentence templates | golden formulas | N |
| 5 | `crs-resumes` versions, source tags, requirement tags, placeholders | rewritten resume and legend | R |
| 5 | `crs-oldnew` must-haves covered, old vs new, whole text and six-second zone | old vs new coverage | N (zone) |
| 5 | `crs-bullets` bullets written as result, measure, method: complete vs waiting on a placeholder | "bullets with a so-what: 6 complete, 10 pending" | D (gates) |
| 5 | `crs-panel` blind panel scores old vs new; review rounds | blind panel; CEO rounds | D + N (blind A/B) |
| 5 | `crs-linkedin` | — | R |
| 5 | `crs-plan12` 12-week plan as a gantt with weekly targets | 12-week search plan | N |
| 5 | `crs-actions`, `crs-tracker`, `crs-confirm` | mandatory before sending | R |
| App. | `app-phases` phase status; `app-kappa` agreement per code; `app-toolkit` method table; `app-limits`; `app-sources`; `app-postings` every posting with URL, niche, liveness band and codes, filterable by niche | chapter 1; "every posting URL and the coding" | R + D |

Any block whose data is missing renders a stub that names the reason and what would fill it. A stub counts as rendered; an absent block does not.

### 2.3 Layout system

- **Breakpoints:** 320–479 (one column), 480–859 (one column, wider charts), 860–1279 (two columns), 1280+ (max content width 1200).
- **Station bar:** five equal columns (`grid-template-columns: repeat(5, 1fr)`), all visible at every width, never scrolls. Labels are short so they fit a 64 px column at 320: **You · Market · Peers · Verdict · Course**, each over its act number; the full act names live in the chapter heads. Top on desktop; fixed to the bottom edge under 860 px, 56 px plus `env(safe-area-inset-bottom)`. Hidden while a text field has focus (the on-screen keyboard otherwise pushes it over the field being typed in). Active station follows scroll; a thin progress line shows position within the act.
- **Theme toggle and the candidate's name** move out of the bar into the cover and a small fixed corner control; the bar carries stations only.
- **Buttons:** one component, three sizes (36 / 44 / 52 px tall; mobile uses 44 minimum). Every set of sibling buttons sits in a `data-btn-group` grid with equal columns and stretched rows, so widths and heights match by construction. Labels wrap to two lines; nothing truncates. Row actions of the same kind (every "Copy", every "Export") share one fixed width and one right edge.
- **Niche selector:** equal-width segmented grid for up to 5 niches on desktop; a single full-width picker button opening a sheet on mobile or above 5 niches. Short labels ("1 · Martech & data, NYC") with the full label in the sheet.
- **Forms:** inputs, selects and textareas are 16 px under 860 px. At 14 px (today's size) iOS zooms the page on focus, which produces sideways scroll the geometry tests will not see.
- **Text:** `min-width: 0` on every grid and flex child; `overflow-wrap: anywhere` on labels, employer names and URLs; tags wrap under their text instead of sitting beside it under 480 px.
- **Tables:** under 640 px each row becomes a stacked card with label–value pairs. No table scrolls sideways at any width.
- **Charts:** drawn at the container's pixel width (existing rule). Under 560 px, category labels move out of the SVG into an HTML row above each bar, where they wrap. The DNA matrix becomes an HTML grid with sticky wrapped row headers; under 560 px it shows the selected niche plus "you" as two columns, with a toggle for all niches as small multiples. No "…" anywhere.
- **Kept from v2:** dark default and light toggle, validated palette, embedded fonts, 12 px minimum, reduced-motion static plates, storage wrapper, offline single file, build failure on missing advice.

### 2.4 Art direction per act

Geometry tests make the report correct, not beautiful. Each act gets one signature visual, given the full width and the first screen; everything else in the act stays quiet.

| Act | Signature visual | Register |
|---|---|---|
| Cover | the night sky before any star is named: all postings as unlabelled points, the candidate in gold | still, one line of type |
| 1 You | the career as a single gold line through time, widening with scope | warm, close |
| 2 The market | the constellations resolve: stars group into niches, then recolour by liveness, then by pay (three of today's four encodings) | wide, cool |
| 3 The competition | the same sky with peers added as dim points around the gold one; what is rare glows. Without peers: the candidate's rare proofs as glowing points against the share of postings that ask for them | crowded, then one point isolated |
| 4 The verdict | the sky recoloured by fit (today's fourth encoding), apply line drawn, then the bridge: assets on the left, asks on the right, links in gold | decisive, largest type in the report |
| 5 The course | the route: 12 weeks as a path leaving the map | practical, checklist density |

The sky has identical geometry in every opener (one instance per opener rather than one moved between them: each act's marks stay countable and nothing has to be re-parented on scroll), so the reader stays in one place while the story moves. It appears full-bleed only in each act's opener (sticky for that opener's scroll distance, about 1.5 screens), then gives way to content on opaque panels. It never sits behind body text: a sky behind text fails contrast unpredictably and repaints on every scroll on phones. Fit is a verdict, so the fit encoding moves from the market chapter to act 4. Reduced motion shows each state as a static plate.

## 3. Test harness (write first; everything starts red)

### 3.1 `tests/ui_invariants.py`

One function `audit(page) -> dict` running in the page, and one `assert_clean(audit)`. Invariants:

| Id | Invariant | Tolerance |
|---|---|---|
| I1 | `documentElement.scrollWidth == clientWidth` | 0 |
| I2 | No element with `overflow-x: auto/scroll` has `scrollWidth > clientWidth` | 1 px, empty allow-list |
| I3 | No visible text-bearing element's box leaves its parent's box when the parent's overflow is visible; no element is cut by a parent with `overflow: hidden` (`scrollWidth > clientWidth`) | 1.5 px |
| I4 | Every SVG `<text>` box lies inside its SVG's box. Within `[data-chart]`, no two axis or category labels intersect (star-map labels and `[data-decor]` are exempt from the intersection rule, not from the bounds rule) | 2 px |
| I5 | No label, heading, button, tab or table cell ends in "…"; no element has `text-overflow: ellipsis`. Prose and quoted scripts are exempt | — |
| I6 | In every `[data-btn-group]`, visible children have equal width and equal height per row, and equal left/top alignment per column/row | 1 px |
| I7 | Every `button`, `[role=tab]`, `summary`, form control, and `a` that is not inside running prose is at least 44 × 44 px under 860 px, 36 px tall above | — |
| I8 | Every `button` passes one of: (a) inside a `[data-btn-group]`; (b) carries `data-action`, and all buttons with the same action value have the same width and, within one list, the same right edge (covers every Copy, Export and Next); (c) carries `data-btn-solo` (capped below) | 1 px |
| I9 | Computed font size ≥ 12 px everywhere (SVG text after scale); body copy and form controls ≥ 16 px under 860 px | — |
| I10 | Zero console errors, zero network requests (existing) | — |
| I10b | No interactive element is hidden under the fixed station bar or the corner control: for each, `elementFromPoint` at its centre after scrolling it into view returns the element or a descendant | — |
| I11 | Act heights within the budgets in 2.1 with expanders closed; at most five figures outside expanders per act | — |
| I12 | Every chart's mark count equals its data row count. `data-rows` is computed by the test from `results.json` using the filter declared for that figure in the parity manifest (for example "top 15 by share"), not read from what the renderer stamps; a renderer that drops rows cannot also lower the expected count | 0 |

**Escape hatches are capped.** `data-btn-solo`, `data-decor` and `data-audit-ignore` exist so the auditor can skip true exceptions. A test counts them: at most 3 solo buttons (theme toggle, mobile niche picker, skip link), 4 decor elements and 0 audit-ignores per report. Raising a cap needs a line in `docs/visual-review.md` saying why. Otherwise the cheapest way to turn a test green is to exempt the element.

**The auditor is tested first.** `tests/test_auditor.py` feeds it ten tiny HTML pages, each with one planted defect (clipped label, ragged buttons, inner scroller, overlapping axis labels) and two clean pages. It must flag exactly the planted ones. An auditor with false positives gets switched off; one with false negatives is how v2 shipped.

### 3.2 Matrix

- Widths: 320, 360, 390, 430, 600, 768, 1024, 1280, 1440, 1920. Heights 800.
- Themes: dark, light at 390 and 1440; dark only elsewhere.
- Fixtures: (a) the fictional example; (b) the nursing e2e output; (c) **new `stress` fixture** built by `tests/fixtures/make_stress_results.py`: 10 niches, labels of 70+ characters, an unbroken 45-character employer name, a 60-character requirement label, German compound words, `change: null`, `peers: null`, pay unknown for one niche, a niche with 5 postings, zero actions for one niche, 100 placeholders.
- States: whole-page audit with expanders closed, then with every expander open; repeat with the first, the last and the longest-label niche selected; open the mobile niche sheet and audit it; at 390, once more with the root font size at 125% (Android font scaling and browser text zoom), which catches fixed heights that only hold at default text size.
- Tiers, to keep the loop fast: `make test` runs widths 320, 390, 1440 on the example and stress fixtures (target under 2 minutes); `make test-full` runs the whole matrix and is required before every commit from cycle 3 on and at release.

### 3.3 Red without a red suite: the ratchet

The draft said both "everything starts red" and "the suite is never red between cycles". Both hold only with a ratchet. `tests/ui_baseline.json` records every invariant violation found in cycle 0 as `{invariant, fixture, width, selector}`. The invariant tests fail on any violation **not** in the baseline, and on any baseline entry that no longer occurs but is still listed (so fixed items must be deleted). Each cycle's commit must shrink the file; release requires it empty. The parity and journey tests use the same mechanism with `tests/parity_baseline.json`.

### 3.4 Existing UI tests

None is deleted silently. `test_no_errors_no_network`, `test_star_per_posting_and_you`, and the five workbench tests (placeholder fill and export, actions persist, storage errors, copy, tracker) are kept unchanged and must stay green in every cycle. `test_four_chapters_change_encoding` is rewritten as `test_sky_states` (cover, three market states, peers or rarity, fit) in the journey cycle. `test_reduced_motion_static_plates` is rewritten to expect one static plate per opener. `test_mobile_legible_and_no_overflow` is removed only in the commit where the invariant matrix replaces it, and that commit says so.

### 3.5 Structure and parity tests

- `tests/parity_manifest.yml`: every row of the table in 2.2 as `{fig, act, source: <json path>, kind: chart|block|table}`.
- `test_parity`: for each row, `[data-fig=<id>]` exists inside `[data-act=<act>]` in the example and stress reports; it passes I12 (marks equal data rows) or holds non-empty text for blocks, **or** is a `[data-stub]` with a reason. With the fictional example, the test also lists which figures are stubs and fails on any stub. The example therefore needs a fictional peer set (`examples/fictional-candidate/run/peers.json`, labelled fictional in the banner) so the showcase never shows act 3 as a stub.
- The R / D / N statuses in 2.2 come from a text search of the template and are not all verified. Cycle 0 runs `test_parity` against the current report and corrects the table from the result before any code changes.
- `test_every_result_block_rendered`: walk the top-level and per-niche keys of `results.schema.json`; each must be read by the template (assert via a `data-src` attribute the renderer stamps on each figure). This is the guard against a rewrite dropping blocks again.
- `test_journey_order`: `data-act` values appear in DOM order `cover, you, market, competition, verdict, course, method`; each act has one chapter head with a question, a learned strip and (except the last) a Next control whose target is the following act; the verdict headline string from `summary.headline` does not occur before `[data-act=verdict]`; the cover has a skip link to it.
- `test_station_bar`: five stations, all inside the viewport at every width; active station changes when each act is scrolled into view; keyboard Tab reaches all five; selected niche survives reload.

### 3.6 Eyes

Automated geometry cannot judge beauty. `tools/shoot.py` writes one screenshot per act at 390 and 1440, dark and light (28 images) for all three fixtures. Each cycle from 3 onward ends with the builder reading every changed screenshot and fixing what it sees before committing. Findings and fixes are logged in `docs/visual-review.md`.

The builder does not grade its own design. At the end of cycles 3, 7 and 11, a fresh subagent that has not seen the code receives only the screenshots and `docs/design-rubric.md` and scores each act 1–5 on: hierarchy (is the one important thing obvious), rhythm (spacing and alignment consistent), legibility, signature visual lands, continuity between acts, and "would I keep reading". Any score under 4 comes back as a fix list; at most three rounds. The rubric is written in cycle 0.

## 4. Cycles

Each cycle: write the listed tests, see them fail, implement, see them pass, run the whole suite, commit. A cycle that adds a schema field also updates `e2e_driver.py`, the stress generator and the example run in the same commit, so the suite is never red between cycles.

| # | Cycle | Red tests | Implementation | Done when |
|---|---|---|---|---|
| 0 | Harness | 3.1–3.5 written; `test_auditor` green; stress fixture; matrix; both ratchet baselines generated; design rubric | No product code. Parity table in 2.2 corrected from the first `test_parity` run | Auditor flags exactly the planted defects; baselines committed; suite green with the ratchet |
| 1 | Layout and controls | I1, I3 (HTML), I6–I9, I10b | Breakpoints, container, `min-width: 0`, wrapping, tag wrapping, stacked tables under 640, 16 px forms; button component and sizes; `data-btn-group` grids; aligned row actions; resume-version list; filter chips as an equal grid. The top nav and the niche tab strip are **not** fixed here: both are replaced in cycle 3 and stay on the ratchet until then | Those invariants' baseline entries gone except nav and niche tabs |
| 2 | Chart kit | I2, I4, I5, I12; one unit page per primitive at the stress widths | Eight shared primitives: labelled bar rows, diverging bars, dumbbell, dot strip, range bars, small multiples, gantt, link diagram. Each handles wrapping, narrow mode and `data-rows` once. Existing charts ported; every later figure must compose them. Labels move out of SVG under 560 px; DNA becomes an HTML grid with a mobile mode; fix-ladder and requirement charts fixed | Chart entries gone from the baseline; no "…" in any fixture |
| 3 | Journey skeleton | `test_journey_order`, `test_station_bar`, `test_sky_states`, I11 | Five acts, anchors, chapter heads, learned strips, hand-overs, station bar, niche selector and sheet, cover without verdict, skip link, sky openers. Existing sections move into acts; no new figures yet. Nav and niche-tab baseline entries disappear here | `ui_baseline.json` empty; design review round 1 scores ≥ 4 or its fixes applied |
| 3b | **Checkpoint** | — | Publish the restructured example and send it. Continue to cycle 4 without waiting; a redirect lands before the new figures are built rather than after | Artifact sent with the design-review scores |
| 4 | Act 1: You | parity rows `you-*`; schema tests for `profile_view.timeline`, `baseline.zone_coverage`; date parser unit tests ("Mar 2022 – Present", "2019–21", "03/2018", French and German month names) | Timeline from the ledger's existing `employer`, `title`, `dates`; scope from ledger numbers; dissection with confidence grades and ledger lines; strengths, edges, rare proof; baseline read of the current resume | Act 1 parity green; stress clean |
| 5 | Act 2: The market | parity rows `mkt-*`; unit tests for `analyze.contrasts` and `title_shift` reproducing the reference study's seniority, segment and title-word figures; `pay.ranges` | Seniority contrast, niche-vs-niche contrast and title shift under the rule in 5.2; per-posting pay lo–hi with source flag; `method.sample`; pooled `market.change`. Render with the chart kit | Reference numbers reproduce; parity green |
| 6 | Act 3: The competition | parity rows `cmp-*`; unit tests for `rarity` and `paths`; peer coding test (bios coded on the same codebook, κ with the second coder reported) | Phase 4 per 5.1; peers placed on the sky by the candidate's projection method; rarity, paths, odds benchmarks with source links; fictional peer set for the example | Parity green with peers present (example, stress) and below threshold (nursing) |
| 7 | Act 4: The verdict | parity rows `vrd-*`; bridge unit test (each link has a strength id, a code, ledger ids) | Bridge, finding cards, fit × pay scatter, narrative; ranking, robustness, ladder, plates moved here; sky fit state | Parity green; verdict text first appears in act 4; design review round 2 |
| 8 | Act 5: The course | parity rows `crs-*`; schema tests for `formulas`, `plan12`, `resumes[].review`; gate: every formula cites a bundle and ledger ids, no number absent from the ledger | Phase 7 formulas and 12-week plan; phase 9 blind old-vs-new panel for "run now" niches only (labels randomised, reviewer never told which is original); review rounds saved. Render formulas with copy buttons, gantt, old vs new, bullets tile, panel and rounds | Parity green; `make example` rebuilds; e2e fixtures pass |
| 9 | Appendix | parity rows `app-*` | Phase status, agreement per code, toolkit table, limits, sources, posting list | Parity green; `parity_baseline.json` empty |
| 10 | Real-data acceptance (outputs stay outside the repo) | — | (a) Rebuild the reference study's candidate on the reference corpus (the corpus is already in the repo; only the candidate's ledger is private) and tick every figure and block of the original report against the new one in `docs/visual-review.md`, without names. (b) Run the full invariant matrix on act 1 built from the other two real resumes' ledgers: real two-column parses and long titles are what the synthetic fixtures miss. (c) One live run with web search for one of those two resumes in its own profession, at reduced volume (2 niches × 15 postings, labelled), to test the any-profession claim on real postings | Every original figure ticked or its gap fixed; matrix clean on the real ledgers; live run report delivered to the user |
| 11 | Visual pass and release | full matrix; `test_release` | Read all screenshots, fix, log; design review round 3. Print stylesheet opens every expander and hides the bar. New README screenshots (one per act, plus mobile). Version 2.1.0. `SKILL.md` phase table updated. Republish the example. Privacy scan | Whole suite green; visual log has no open item |

## 5. Contract changes

`results.schema.json` additions (all required; `null` allowed only with a sibling `*_reason`):

- `profile_view.timeline[]`: `{employer, title, start, end, scope, ledger_ids}`
- `baseline.zone_coverage`: `{zone: {covered, total}, whole: {covered, total}}` per niche, for original and rewritten
- `method.sample[]`: `{niche_id, planned, achieved, archive_planned, archive_achieved, reason}`
- `niches[].demand.contrasts`: `{seniority: [{code, diff, p, significant}], versus: {niche_id, rows: [{code, a, b, gap}]}}`
- `niches[].pay.ranges[]`: `{posting_id, lo, hi, currency, source, flagged}`
- `market.rarity[]`: `{strength_id, label, asked_share, asked_n, peer_share, peer_n}`
- `market.bridge[]`: `{strength_id, asset, reads_as, code, ledger_ids}`
- `summary.findings[3]`: `{title, body, numbers}`
- `niches[].formulas[]`: `{bundle, template, example, ledger_ids}`
- `plan12[]`: `{week, track, action, target}`
- `resumes[].review`: `{panel: [{reviewer, old, new, chose}], rounds: [{n, verdict, fixes, applied}], independent}`

- `journey.acts[]`: `{act, question, answer, learned[], handover}`
- `market.change`: then vs now pooled across the niches of one role family, used for any niche whose archive is under 10 postings. The example's archives are 4, 0, 0 and 13 postings, so without this three of four niches render the then-vs-now figure as a stub.
- `market.title_shift[]`: `{term, share_then, share_now, n_then, n_now, p}` from live and archive titles (a title-only archive counts here)
- `market.peers`: `{niche_id, n, sources[], median, top_quartile, paths[]}` per niche, or `n` below threshold with `reason`

### 5.1 Act 3 needs obtainable data

The user asked for competing supply as its own step. An act that is usually a stub does not deliver that, and the draft accepted it. LinkedIn profiles cannot be read, but the people who hold these jobs are findable elsewhere. Phase 4 collects, per "run now" niche, at least 8 and up to 20 people currently in the niche's titles from: hire and promotion announcements (company blogs, press releases, trade press), company leadership and team pages, and conference speaker bios. Each is coded on the niche's codebook from the public text, with years, prior role type and prior employer type; a second coder re-codes 20%. The report shows role paths and aggregates; names appear only as source links in the appendix. Below 8 per niche, act 3 runs on rarity, years asked, level mix and benchmarks, and the stub says how many were found and where it looked.

### 5.2 Small-sample rule

- Seniority contrast: within a niche only if each band has ≥ 10 postings; otherwise across the role family, labelled "all niches".
- Niche-vs-niche contrast: drawn when both niches have ≥ 10 postings (the reference study's NYC 32 vs Paris 10 qualifies). Bars are solid only where Fisher p < 0.05; everything else is drawn hollow and labelled directional, with Wilson intervals.
- Below those floors the figure is a stub that states the counts. A Fisher test on a 10-posting niche split in two is noise, and drawing it would be a manufactured finding.

Four of the new blocks are written by the model at run time (`formulas`, `plan12`, `bridge.reads_as`, `journey`). Offline tests can check their shape and that their numbers trace to the ledger; they cannot check that the writing is good. Each gets a prompt, a rubric and a place in the reviewer loop.

Phases touched: 03 (ranges, titles), 04 (peers per 5.1), 05 (contrasts, title shift), 07 (formulas, plan12), 09 (blind A/B), 10 (assemble, template). `SKILL.md` phase table and rubric 16 updated to match.

## 6. Constraints carried over

- Works for any profession: every new figure is driven by codes and niches, never by a named segment or city. The stress and nursing fixtures enforce it.
- No real candidate data in the repo; the privacy test stays.
- One question to the user; everything else inferred, with stubs and the confirm list for what cannot be.
- Single offline HTML file, fonts embedded, no network.
- Workbench behaviour unchanged: checklist, placeholder fill, copy, tracker, export.

## 7. Decisions taken, and their cost

- **Verdict moves from first to fourth.** This is the requested journey. The skip link on the cover is the concession to a reader who wants the answer immediately.
- **Blind old-vs-new panel only for "run now" niches.** Running it for every niche would add up to 30 reviewer calls per run.
- **No horizontal scrolling at all,** including tables and tabs. Wide tables therefore stack on phones, which makes them longer.
- **Act 3 depends on public announcements and team pages.** In professions that rarely announce hires (nursing, restaurant management) it will often fall below 8 peers and run on rarity and benchmarks. Finding peers adds roughly 20–60 page reads per run.

- **Most evidence is behind expanders.** The journey stays short enough to finish; the cost is that a figure from the reference report may be one tap away rather than on the page.
- **Scope is large:** 52 figures, 16 contract additions, six phases. If it has to be cut, the order to drop is: `crs-panel` blind A/B (most run-time cost), `mkt-titles`, `you-timeline`, `mkt-sample`, `app-toolkit`, the live run in cycle 10(c). Cycles 0–3, acts 1 and 4, and cycle 10(a) are not cuttable: they are the five asks and the parity proof.

## 8. Not verifiable in the build environment

- Rendering inside the Claude mobile app's viewer.
- Fresh-session plugin install, skill upload, raw-zip flow.
- A live run producing the new blocks from real web postings.
- Whether the result is "stunning". The independent design review and the checkpoint reduce the risk; only the reader settles it.

## 9. Review log

**Builder's review (Opus).** Each item was checked against the code and the current report before changing the plan.

| # | Problem in the previous draft | Evidence | Change |
|---|---|---|---|
| 1 | "Starts red" and "never red between cycles" contradict each other | section 3 vs section 4 preamble | Ratchet baselines (3.3) |
| 2 | Cycles 1–3 would fix the nav and niche tabs that cycle 4 deletes | both replaced by the station bar and selector | Left on the ratchet until the journey cycle; layout and controls merged, journey moved to cycle 3, checkpoint earlier |
| 3 | Length budget unachievable for the workbench and not calibrated | today: 40.3 screens at 390; workbench sections 16.3 | Per-act budgets (2.1) |
| 4 | "The competition" does not fit a 64 px station at 320 | 11 characters at 12 px ≈ 72 px | Short station labels |
| 5 | Fixed bottom bar: unaddressed safe area, keyboard overlap, content hidden under it | standard iOS behaviour | Safe-area inset, hidden on input focus, I10b |
| 6 | 14 px form fields make iOS zoom on focus, causing sideways scroll the tests cannot see | `.ph-field input`, `.trk input` at 14 px | 16 px forms (2.3, I9) |
| 7 | A sky behind body text fails contrast and repaints on scroll | the draft put one persistent canvas behind everything | Sky in act openers only |
| 8 | Fit encoding placed in the market act, before the verdict | 2.4 table | Moved to act 4 |
| 9 | I12 trusted the renderer's own row count | `data-rows` stamped by the renderer | Expected count computed by the test from `results.json` |
| 10 | Solo-button cap of 6 contradicted five Next buttons plus toggles | I8 as written | I8 accepts shared `data-action`; solo cap 3 |
| 11 | Small-sample rule would suppress the reference study's own NYC-vs-Paris figure and made "pooled niche-vs-niche" meaningless | n ≥ 30 per niche; Paris n = 10 | Rule rewritten (5.2) |
| 12 | Wrong fact: "4 archive postings each" | archives are 4, 0, 0, 13 | Corrected |
| 13 | Act 3 accepted as a stub in most runs; the example would show it as a stub | `peers: null` in every example niche | Obtainable peer sources (5.1); fictional peer set for the example |
| 14 | Parity gaps against the reference report | title-word shift, bullets-with-a-so-what tile, posting list with URLs, precedent paths were not in the manifest | `mkt-titles`, `crs-bullets`, `app-postings`, `cmp-paths` |
| 15 | Existing UI tests' fate unstated | 10 tests in `test_report_ui.py`, two tied to the old atlas | 3.4 |
| 16 | Real-data acceptance assumed studies that do not exist | only the reference candidate has a study; the other two real resumes have phase 0 output only | Cycle 10 split into rebuild, act-1 matrix and one live run |
| 17 | Timeline assumed dates the ledger may not parse | ledger stores `dates` as raw strings | Date parser with multilingual unit tests in cycle 4 |
| 18 | No check for larger text settings or printing | — | 125% text state; print stylesheet |

**Fit for purpose, by ask:**
- **Equal, aligned buttons:** yes; I6–I8 enforce it by construction and by test.
- **No text outside containers:** yes; I3–I5 and I12, with a tested auditor.
- **No sideways scroll:** yes; I1, I2, and 16 px forms for the iOS case the geometry tests cannot see.
- **Fully responsive:** yes, from 320 to 1920 px, at 125% text and in both themes.
- **The journey:** structurally yes, through the act order, station bar, hand-overs and journey test. Whether it *feels* intuitive is judged by the design review and the checkpoint, not by a test.
- **All of the reference report:** yes; the manifest covers every figure and block, cycle 10(a) ticks them off one by one, and act 3 no longer depends on a stub.
- **Stunning:** not provable by tests; the checkpoint after cycle 3 is where the user judges it.
