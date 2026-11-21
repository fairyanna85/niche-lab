#!/usr/bin/env python3
"""Phase 9 — score the ORIGINAL resume on the same gates as the rewrites, so the report can show before → after.

usage: baseline.py --run RUN      → RUN/baseline.json  {gates: [...], coverage_by_niche: {...}, resume: {...}}
The original is rebuilt from the ledger as a resume object (same shape as resumes.json entries)."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save
import gates


def original_resume(ledger):
    R = [l for l in ledger if l["source"] == "resume"]
    hdr = [l for l in R if l["claim_type"] in ("header", "contact") and not l.get("employer")]
    name = hdr[0]["text"] if hdr else ""
    headline = next((l["text"] for l in hdr[1:] if l["claim_type"] == "header"), "")
    contact = " · ".join(l["text"] for l in hdr if l["claim_type"] == "contact")
    profile = " ".join(l["text"] for l in R if l["section"] in ("summary", "profile", "about", "profil", "perfil") and l["claim_type"] in ("duty", "metric"))
    roles, order = {}, []
    for l in R:
        if not l.get("employer"): continue
        k = (l["employer"], l["title"], l["dates"])
        if k not in roles: roles[k] = []; order.append(k)
        if l["claim_type"] in ("duty", "metric"): roles[k].append(dict(text=l["text"], ledger=[l["id"]]))
    exp = [dict(employer=e, title=t or "", dates=d or "", context="", bullets=roles[(e, t, d)] or [dict(text="", ledger=[])]) for e, t, d in order]
    edu = [l["text"] for l in R if l["claim_type"] == "education"]
    skills = [l["text"] for l in R if l["claim_type"] == "skill"]
    return dict(id="original", niche_id=None, header=dict(name=name, headline=headline, contact=contact), profile=profile,
                skills=skills, experience=exp, education=edu, placeholders=0)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); a = ap.parse_args(); run = Path(a.run)
    ledger = load(run / "ledger.json")["lines"]; prof = load(run / "profile.json"); orig_txt = (run / "resume.txt").read_text()
    rk = load(run / "ranking.json"); top = rk["order"][0]
    r = original_resume(ledger); r["niche_id"] = top
    gs = [x for x in gates.check(r, ledger, prof, orig_txt, run, [r], pdf=False) if x["name"] not in ("advocate_test", "reviewer_panel", "ats_parse", "consistency")]
    cov = {}
    for nid in rk["order"]:
        r2 = dict(r, niche_id=nid)
        g = next(x for x in gates.check(r2, ledger, prof, orig_txt, run, [r2], pdf=False) if x["name"] == "keyword_coverage")
        cov[nid] = dict(before=g["before"], total=g["total"])
    save(run / "baseline.json", dict(gates=gs, coverage_by_niche=cov, resume=r, scored_against=top))
    for x in gs: print(f"{x['status']:8s} {x['name']:18s} {x['detail'][:90]}")


if __name__ == "__main__":
    main()
