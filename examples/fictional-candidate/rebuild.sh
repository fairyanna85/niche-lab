#!/usr/bin/env bash
# Re-runs every deterministic step of the example. Agent-written files (profile.json, evidence.json after review,
# niches.json candidates, access.json, resumes.json, narrative.json, reviews/) are kept as committed.
set -euo pipefail
cd "$(dirname "$0")"
S=../../skills/run/scripts
python3 $S/postings.py import-reference --run run --niche-map '{"n01":{"city":["NYC"],"lvl":["Head","VP","SVP"],"seg":["A"]},"n02":{"city":["NYC"],"lvl":["Head","VP","SVP","SrDir"],"seg":["B","C","D"]},"n03":{"city":["NYC"],"lvl":["Dir","SrDir","Mgr"]},"n04":{"city":["PAR"]},"n05":{"city":["NYC"],"lvl":["Dir","Mgr"],"seg":["A"]},"n06":{"city":["NYC"],"seg":["D"]}}'
python3 $S/postings.py liveness --run run --today 2026-11-12
for n in n01 n02 n03 n04 n05 n06; do python3 $S/analyze.py --run run --niche $n; done
python3 $S/niches.py screen --run run
for n in n01 n02 n03 n04; do python3 $S/fit.py score --run run --niche $n; done
python3 $S/niches.py qualify --run run
for n in n01 n02 n03 n04; do python3 $S/fit.py per-posting --run run --niche $n; python3 $S/fit.py ladder --run run --niche $n; done
python3 $S/rank.py --run run
python3 $S/gates.py --run run --pdf || true
python3 $S/baseline.py --run run
python3 $S/gates.py --run run --linkedin || true
python3 $S/render_linkedin.py --run run
python3 $S/render_resume.py --run run --pdf --docx
# phase 4: fictional peers for the two run-now niches (the postings are real, these people are not)
python3 make_peers.py run
for n in $(ls run/niches); do python3 $S/peers.py --run run --niche $n; done
# phase 9: blind old-vs-new panel (reviewer results are stored in run/reviews; unblind maps them back)
python3 $S/blind_panel.py unblind --run run
python3 $S/assemble.py --run run
python3 $S/build_report.py --results run/results.json --out report.html
