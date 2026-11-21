# Phase 4 — Supply: who the candidate competes with

**Inputs:** kept niches. **Output:** `niches/<id>/peers.jsonl`, `niches/<id>/peers.json`; the report's act 3.
**Prompt:** `peer-score.md`. **Threshold:** 8 people per niche (`peers_n`).

LinkedIn profiles are not read: they block automated access. The people who hold these jobs are findable elsewhere.

Steps
1. For each niche, collect 8–20 people who currently hold one of the niche's titles, from public text only:
   - hire and promotion announcements (company blogs, press releases, trade press: search "<title>" joins / appointed / promoted, with the niche's segment and city);
   - company leadership and team pages of the niche's employers;
   - conference and podcast speaker bios.
   Run the "run now" niches first; stop at 20 per niche.
2. Code each person with `prompts/peer-score.md` on the niche's codebook (same codes as postings: 1 = the text shows it), plus years in the field, prior role type and prior employer type. Store the name only as a hash and keep the source URL.
3. Second coder: re-code every fifth person with `prompts/second-coder.md`, written to `second_coder`; κ is reported in the report.
4. `python3 scripts/peers.py --run RUN --niche <id>` → shares per code, years (median, top quarter), prior-role paths. Under 8 people the niche's peer block is hidden with the count found and where it looked.
5. Narrative (`narrative.json → niches.<id>.peers`): one insight about what the people in these jobs have in common, and `do_this` items that turn the candidate's edge or gap into a resume or search action.

What the report shows: peers as open circles on the sky (placed at the mean position of their five nearest postings), years against the candidate, the paths they took, and the "rarity" view: for each requirement the candidate proves, how often postings ask for it against how often peers show it.

**Gate:** ≥ 8 people, or the niche's peer block is hidden with the count found; act 3 then rests on rarity against postings, years asked, level mix and hiring benchmarks.
