#!/usr/bin/env python3
"""Phase 4 — competing supply: the people who hold the niche's jobs now, coded from public text.

usage: peers.py --run RUN --niche n01
Reads  RUN/niches/<id>/peers.jsonl   one line per person (prompts/peer-score.md output):
       {"id", "niche_id", "name_hash", "source_type", "source_url", "title", "employer", "years",
        "prior_role_type", "prior_employer_type", "codes": {code: 0|1}, "second_coder": {code: 0|1} | absent}
Writes RUN/niches/<id>/peers.json    aggregate below, or {"hidden": reason, "n": k, "sources": {...}} under the threshold.

Sources (plan §5.1): hire and promotion announcements, company leadership and team pages, conference speaker bios.
LinkedIn profiles are not read. Names are stored only as hashes; the report shows role paths and aggregates.
"""
import argparse, collections, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save, thresholds

W = dict(scope=0.25, employer=0.20, trajectory=0.20, impact=0.20, external=0.15)


def kappa(pairs):
    """Cohen's kappa over (a, b) binary pairs; None when undefined."""
    if not pairs: return None
    a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
    po = float((a == b).mean()); pa = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return None if pa >= 1 else round((po - pa) / (1 - pa), 2)


def aggregate(rows, min_n):
    src = dict(collections.Counter(r.get("source_type", "other") for r in rows))
    if len(rows) < min_n:
        return dict(hidden=f"{len(rows)} people found in public announcements, team pages and speaker bios (< {min_n} needed)", n=len(rows), sources=src)
    codes = sorted({k for r in rows for k in r.get("codes", {})})
    share = {k: round(sum(1 for r in rows if r["codes"].get(k)) / len(rows), 3) for k in codes}
    yrs = sorted(r["years"] for r in rows if r.get("years") is not None)
    paths = collections.Counter(r["prior_role_type"] for r in rows if r.get("prior_role_type"))
    etypes = collections.Counter(r["prior_employer_type"] for r in rows if r.get("prior_employer_type"))
    pairs = [(r["codes"].get(k, 0), r["second_coder"].get(k, 0)) for r in rows if r.get("second_coder") for k in codes]
    out = dict(n=len(rows), sources=src, codes=share,
               years=dict(n=len(yrs), median=float(np.median(yrs)) if yrs else None, top_quartile=float(np.percentile(yrs, 75)) if yrs else None, values=yrs),
               paths=[dict(path=p, n=k) for p, k in paths.most_common(8)], employer_types=[dict(type=t, n=k) for t, k in etypes.most_common(6)],
               second_coded=sum(1 for r in rows if r.get("second_coder")), kappa=kappa(pairs))
    if all("scores" in r for r in rows):  # v2 rubric-09 scores, kept when present
        for r in rows: r["total"] = sum(W[k] * r["scores"][k] for k in W)
        rows = sorted(rows, key=lambda r: -r["total"]); q = max(2, len(rows) // 4)
        out["diffs"] = [dict(criterion=k, median=float(np.median([r["scores"][k] for r in rows])), top=float(np.median([r["scores"][k] for r in rows[:q]]))) for k in W]
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); ap.add_argument("--niche", required=True)
    a = ap.parse_args(); run = Path(a.run); th, _ = thresholds(run)
    f = run / "niches" / a.niche / "peers.jsonl"
    if not f.exists():
        out = dict(hidden="peer search not run for this niche", n=0, sources={})
    else:
        out = aggregate(load(f), th["peers_n"])
    save(run / "niches" / a.niche / "peers.json", out)
    print(f"{a.niche}: " + (out["hidden"] if "hidden" in out else f"{out['n']} peers, median {out['years']['median']} years, kappa {out['kappa']}"))


if __name__ == "__main__":
    main()
