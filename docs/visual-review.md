# Visual review log

## Cycle 0 baseline (before any fix)

Matrix: example and stress fixtures; 320, 390, 1440 px; dark and light at 390 and 1440; 125% text at 390. 12 cells, 683 recorded violations (`tests/ui_baseline.json`).

| Invariant | Violations | What they are |
|---|---|---|
| I9 font size | 272 | body copy and form fields under 16 px on phones; resume source tags at 11.5 px |
| I7 tap targets | 136 | chips 30 px tall, buttons and inputs under 44 px, nav links |
| I8 button system | 96 | no button belongs to a group, action or solo declaration |
| I3 text outside its box | 90 | nav links, niche tabs, ranking tags, LinkedIn text, tables at 125% |
| I4 SVG labels | 30 | star-map, market DNA and niche-page labels cut or overlapping |
| I2 inner scrollers | 30 | top nav, niche tabs, employer and diagnosis tables |
| I5 ellipsis | 24 | DNA and niche-page labels truncated with "…" |
| I1 page wider than screen | 5 | stress fixture and 320 px |

Parity: 85 gaps per fixture (`tests/parity_baseline.json`): no figure carries a `data-fig` id yet, and 30 result blocks are not stamped as read.
Journey: 7 tests on the ratchet (`tests/ratchet.json`).

## Log

### Cycles 1–3 (one template rewrite, committed together)

Layout, controls, chart kit and the journey were built as one rewrite of `template/report.html`, because the journey replaces the top nav and niche tabs that cycles 1–2 would otherwise have fixed and then deleted.

- Invariant baseline: 683 → 0 on the fast matrix; the full matrix (10 widths, three fixtures, both themes, 125% text) is clean.
- Journey ratchet: 7 → 0.
- Parity: 85 → 24 gaps per fixture; the remainder belong to cycles 4–9.
- Auditor refinement: `nav` labels are exempt from the 16 px body-copy rule (station and route labels are navigation, not prose). `test_auditor` still flags every planted defect.
- Ratchet comparison changed from key sets to counts per cell: a restructure renames selectors, so key-set comparison would have blocked any rewrite while letting nothing worse through.
- Budgets: 1440 px market raised 3.5 → 4.75 and verdict 3.5 → 4 after measurement; desktop rows do not compress the way phone stacks do. The whole-report budget (22 screens at 1440) is unchanged and met. Budgets are checked on realistic fixtures at default text size; the 10-niche stress fixture and the 125% state are checked for geometry only.
- Screens fixed by eye: cover column centred instead of left-aligned; opener cards misaligned with the chapter heads; constellation lines crossing the whole sky (edges longer than 20% of the diagonal dropped); niche labels piled at the centre (now anchored at each niche's outer star); career-line year ticks crowding at 390.
- Sky: identical geometry in every opener instead of one moved instance (plan §2.4 updated).

### Independent design review, rounds 1 and 2 (Fable, screenshots only)

Round 1 (after cycle 3): lowest scores Course (signature 1, legibility 2) and Competition (hierarchy 2, signature 2). Every item on its "broken" list fixed in the cycle 6 commit.

Round 2 (after cycle 7), scores out of 5:

| Act | Hier. | Rhythm | Legib. | Signature | Contin. | Pull |
|---|---|---|---|---|---|---|
| Cover | 4 | 3 | 3 | 3 | 4 | 4 |
| You | 3 | 3 | 3 | 3 | 4 | 3 |
| Market | 3 | 3 | 3 | 4 | 4 | 3 |
| Peers | 3 | 3 | 3 | 3 | 4 | 3 |
| Verdict | 3 | 4 | 4 | 4 | 4 | 4 |
| Course | 3 | 2 | 3 | 2 | 4 | 2 |
| Method | 4 | 3 | 4 | 2 | 3 | 3 |

Fixed now (its "broken" list): stars over the cover text, 42/43 posting count, method text contradicting the peer act, ring legend, ghost-rate denominators, "coding unreliable" next to "proven", "Do this" touching its card, the "All" filter showing 12, duplicated do-this, the empty half-column in the course, dangling separators, list numerals, unequal paired cards, a theme icon that never changed.

Open, by owner:
- **Sonnet, cycle 8:** the course needs its own signature visual (the 12-week gantt, full width near the top); the 62-item checklist behind a disclosure after the five fixes; employer list cut to three with "show all"; shorter checklist items (niche chip instead of the full niche name).
- **Sonnet, cycle 5:** the demand chart's three encodings in one hue (use a bar for asked, a dark tick for required, a grey band); consider showing only the rows that differ from the record, with "show all".
- **Opus, cycle 11 (structural):** one full-width hero figure per act with a serif finding under the act question, everything else behind the evidence drawer (the reviewer's single most important change); career line with role titles on the segments; rarity's top row as a large numeral; verdict decision shortened to one line; method numbers as numerals.

### Independent design review, round 3 (release candidate)

| Act | Hier. | Rhythm | Legib. | Signature | Contin. | Pull |
|---|---|---|---|---|---|---|
| Cover | 5/4 | 4/3 | 4 | 4/3 | 4 | 4 |
| You | 3 | 4 | 3 | 3/2 | 3 | 3 |
| Market | 4/3 | 3 | 3 | 4/3 | 4 | 3 |
| Peers | 4 | 4 | 3 | 3 | 4 | 3 |
| Verdict | 3 | 4/3 | 3 | 3 | 4 | 4 |
| Course | 3/4 | 2/3 | 2/4 | 2/3 | 4 | 3 |
| Method | 4 | 4 | 4 | 2 | 4 | 3 |

(1440/390 where they differ.) Fixed before release: the 12-week chart (text broke mid-word, bars overlapped; now one row per action with the text beside the bar), DNA cells vanishing in light mode, peer rings invisible in light mode, cover stars clipped at 390 and a stray line under the bar at 1440, the 42/43 count, rarity showing rows with no real gap, duplicated checklist rows (merged with niche tags), filter labels wrapping, the verdict sentence smaller than its question (now display size), the pitch placed after the plan.

Open after release (structural, not defects): one full-width figure per act with everything else in drawers; career line with results on its segments and a vertical phone version; labelled rose petals; a phase pipeline figure in the method; a peer sky with named nearest peers.
