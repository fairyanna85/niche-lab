#!/usr/bin/env python3
"""Phase 1/6 — candidate evidence per requirement code, and fit to a niche (rubrics 03 and 11).

  fit.py prefill --run R --modules partnerships,program-management
      → RUN/evidence.json  {code: {grade, evidence:[ledger ids], source:"regex", reviewed:false}}
        Regex alone can give at most grade 2; grade 3 needs a digit-bearing number on the same ledger line.
        THE AGENT MUST REVIEW: every grade ≥2 and every 0 on a code that any niche demands at ≥50%.
        Set "reviewed": true and correct "grade"/"evidence" in place.
  fit.py score --run R --niche n01
      → RUN/niches/<id>/fit.json  fit, coverage, per-code status, gaps
"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save, codebook

CREDIT = {3: 1.0, 2: 0.75}


def prefill(a):
    run = Path(a.run)
    ledger = load(run / "ledger.json")["lines"]
    codes, _ = codebook(a.modules.split(","), run)
    prev = load(run / "evidence.json") if (run / "evidence.json").exists() else {}
    ev = {}
    for c in codes:
        if prev.get(c["id"], {}).get("reviewed"):
            ev[c["id"]] = prev[c["id"]]; continue
        best, ids = 0, []
        for l in ledger:
            if l["claim_type"] in ("contact",): continue
            if any(re.search(rx, l["text"], re.I) for rx in c.get("resume_cues", [])):
                g = 1 if l["claim_type"] in ("skill", "header") or l["section"] in ("summary", "profile", "about") else 2
                if g == 2 and l["claim_type"] == "metric" and any(re.search(r"\d", x) for x in l["numbers"]):
                    g = 3
                if g >= best:
                    ids = ([l["id"]] + ids if g > best else ids + [l["id"]]); best = g
        ev[c["id"]] = dict(label=c["label"], grade=best, evidence=ids[:4], source="regex", reviewed=False)
    save(run / "evidence.json", ev)
    print(f"prefilled {len(ev)} codes; grades: " + ", ".join(f"{k}={v['grade']}" for k, v in ev.items()))


def posting_fit(p, ev):
    num = den = 0.0
    for k, v in p["codes"].items():
        if v == 0: continue
        w = 1.0 if v == 2 else 0.5; den += w
        num += w * CREDIT.get(ev.get(k, {}).get("grade", 0), 0)
    return num / den if den else 0.0


def per_posting(run: Path, niche_id: str, line=0.6):
    ev = load(run / "evidence.json")
    W = {"live": 1.0, "doubtful": 0.5, "likely_ghost": 0.0, "closed": 0.0, None: 1.0}
    ps = [p for p in load(run / "postings" / "postings.jsonl") if niche_id in p["niche_ids"] and p["era"] == "now" and W[(p.get("liveness") or {}).get("band")] > 0]
    rows = sorted((dict(id=p["id"], company=p["company"], title=p["title"], fit=round(posting_fit(p, ev), 3), band=(p.get("liveness") or {}).get("band"))
                   for p in ps), key=lambda r: -r["fit"])
    out = dict(niche=niche_id, line=line, n=len(rows), above_line=sum(r["fit"] >= line for r in rows), postings=rows)
    save(run / "niches" / niche_id / "fit_per_posting.json", out)
    return out


def ladder(run: Path, niche_id: str):
    """Coverage and fit gained by proving each unproven requirement (grade → 3), one at a time, by re-scoring."""
    base = score(run, niche_id, write=False); ev = load(run / "evidence.json"); steps = []
    for r in base["rows"]:
        if r["grade"] >= 3: continue
        e2 = {k: dict(v) for k, v in ev.items()}; e2.setdefault(r["code"], {"grade": 0})["grade"] = 3
        a = score(run, niche_id, write=False, ev=e2)
        steps.append(dict(code=r["code"], label=r["label"], from_grade=r["grade"], demand=r["demand"],
                          coverage_gain=round(a["coverage"] - base["coverage"], 3), fit_gain=round(a["fit"] - base["fit"], 3),
                          kind="surface" if r["grade"] >= 1 else "build"))
    steps.sort(key=lambda s: (-s["coverage_gain"], -s["fit_gain"]))
    out = dict(niche=niche_id, base=dict(fit=base["fit"], coverage=base["coverage"]), steps=steps)
    save(run / "niches" / niche_id / "fix_ladder.json", out)
    return out


def score(run: Path, niche_id: str, write=True, ev=None):
    an = load(run / "niches" / niche_id / "analysis.json")
    ev = ev if ev is not None else load(run / "evidence.json")
    num = den = 0.0; rows = []; gaps = []
    for r in an["prevalence"]:
        k = r["code"]
        if r["present"] < 0.20 or r["reliability"] == "excluded": continue
        g = ev.get(k, {}).get("grade", 0)
        w = r["required"] + 0.5 * (r["present"] - r["required"])
        num += w * CREDIT.get(g, 0); den += w
        status = "proven" if g == 3 else "partial" if g == 2 else ("gap" if r["present"] >= 0.5 else "minor")
        rows.append(dict(code=k, label=r["label"], demand=r["present"], required=r["required"], grade=g,
                         evidence=ev.get(k, {}).get("evidence", []), status=status, reviewed=ev.get(k, {}).get("reviewed", False)))
        if status == "gap":
            gaps.append(dict(code=k, label=r["label"], demand=r["present"]))
    core = [x for x in rows if x["demand"] >= 0.5]
    cov = sum(1 for x in core if x["grade"] >= 2) / len(core) if core else 0.0
    out = dict(niche=niche_id, fit=round(num / den, 3) if den else 0.0, coverage=round(cov, 3), n_core=len(core), rows=rows,
               gaps=sorted(gaps, key=lambda g: -g["demand"]), unreviewed=[x["code"] for x in rows if not x["reviewed"] and (x["grade"] >= 2 or x["status"] == "gap")])
    if write: save(run / "niches" / niche_id / "fit.json", out)
    return out


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("prefill"); s.add_argument("--run", required=True); s.add_argument("--modules", required=True)
    s = sp.add_parser("score"); s.add_argument("--run", required=True); s.add_argument("--niche", required=True)
    s = sp.add_parser("per-posting"); s.add_argument("--run", required=True); s.add_argument("--niche", required=True)
    s = sp.add_parser("ladder"); s.add_argument("--run", required=True); s.add_argument("--niche", required=True)
    a = ap.parse_args()
    if a.cmd == "prefill": prefill(a)
    elif a.cmd == "per-posting":
        o = per_posting(Path(a.run), a.niche); print(f"{a.niche}: {o['above_line']} of {o['n']} postings at fit ≥ {o['line']}")
    elif a.cmd == "ladder":
        o = ladder(Path(a.run), a.niche); print(f"{a.niche}: " + ", ".join(f"{x['code']} +{x['coverage_gain']}" for x in o["steps"][:5]))
    else:
        o = score(Path(a.run), a.niche)
        print(f"{a.niche}: fit {o['fit']} coverage {o['coverage']} gaps {[g['code'] for g in o['gaps']]} unreviewed {o['unreviewed']}")


if __name__ == "__main__":
    main()
