#!/usr/bin/env python3
"""Phase 2 + 6 — screen candidate niches (rubric 05) and qualify kept ones (rubric 12).

  niches.py screen --run R     uses screen postings tagged with each niche id; writes verdicts into RUN/niches.json
  niches.py qualify --run R    after analyze + fit on kept niches; writes RUN/qualification.json

Merge rule: cosine similarity of required-code vectors ≥0.85 and same role family → merge into the niche with more postings.
"""
import argparse, collections, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save, thresholds, codebook
from fit import score as fit_score


def vec(posts, ids):
    n = len(posts) or 1
    return [sum(1 for p in posts if p["codes"].get(k, 0) == 2) / n for k in ids]


def cos(a, b):
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def coverage_quick(posts, ev):
    if not posts: return 0.0
    keys = {k for p in posts for k in p["codes"]}
    core = [k for k in keys if sum(1 for p in posts if p["codes"].get(k, 0) >= 1) / len(posts) >= 0.5]
    return sum(1 for k in core if ev.get(k, {}).get("grade", 0) >= 2) / len(core) if core else 0.0


def screen(a):
    run = Path(a.run); th, relaxed = thresholds(run)
    doc = load(run / "niches.json"); ev = load(run / "evidence.json")
    posts = [p for p in load(run / "postings" / "postings.jsonl") if p["era"] == "now" and (p.get("liveness") or {}).get("band") != "likely_ghost"]
    by = {n["id"]: [p for p in posts if n["id"] in p["niche_ids"]] for n in doc["niches"]}
    for n in doc["niches"]:
        ps = by[n["id"]]
        n["screen"].update(n_postings=len(ps), n_employers=len({p["company"] for p in ps}),
                           posting_ids=[p["id"] for p in ps], coverage_est=round(coverage_quick(ps, ev), 2))
        if n["verdict"] == "not_screened":
            continue
        if n.get("blocker"):
            n["verdict"], n["reason"] = "reject", f"blocker: {n['blocker']}"
        elif len(ps) < th["min_postings"] or n["screen"]["n_employers"] < th["min_employers"]:
            n["verdict"], n["reason"] = "reject", f"volume: {len(ps)} postings / {n['screen']['n_employers']} employers (< {th['min_postings']} / {th['min_employers']})"
        elif n["screen"]["coverage_est"] < th["coverage_keep"]:
            n["verdict"], n["reason"] = "reject", f"coverage {n['screen']['coverage_est']:.2f} < {th['coverage_keep']}"
        else:
            n["verdict"], n["reason"] = "keep", f"{len(ps)} postings, {n['screen']['n_employers']} employers, coverage {n['screen']['coverage_est']:.2f}"
    kept = sorted([n for n in doc["niches"] if n["verdict"] == "keep"], key=lambda n: -n["screen"]["n_postings"])
    allcodes = sorted({k for p in posts for k in p["codes"]})
    for i, x in enumerate(kept):
        for y in kept[:i]:
            if y["verdict"] != "keep" or x["verdict"] != "keep": continue
            s = cos(vec(by[x["id"]], allcodes), vec(by[y["id"]], allcodes))
            if s >= 0.85 and x["role_family"] == y["role_family"] and x["seniority"] == y["seniority"] and x["city"] == y["city"]:
                x["verdict"], x["merged_into"], x["reason"] = "merge", y["id"], f"required-code cosine {s:.2f} with {y['id']}"
    doc["relaxed_thresholds"] = relaxed
    save(run / "niches.json", doc)
    for n in doc["niches"]:
        print(f"{n['id']} {n['verdict']:12s} {n['label'][:60]:60s} {n['reason']}")


def qualify(a):
    run = Path(a.run); th, _ = thresholds(run)
    doc = load(run / "niches.json"); prof = load(run / "profile.json")
    band_rank = ["IC", "Manager", "Director", "Head-VP", "C"]
    cand_band = prof["fields"]["seniority_band"]["value"]
    est = prof["fields"]["current_pay_band_est"]["value"] or {}
    out = {}
    for n in doc["niches"]:
        if n["verdict"] != "keep": continue
        an = load(run / "niches" / n["id"] / "analysis.json"); f = fit_score(run, n["id"])
        cov = f["coverage"]
        step = band_rank.index(n["seniority"]) - band_rank.index(cand_band) if n["seniority"] in band_rank and cand_band in band_rank else 0
        if n.get("blocker") or cov < 0.40: v = "Rejected"
        elif cov >= 0.75 and step == 0 and n["role_family"] == prof["fields"]["role_family"]["value"]: v = "Core"
        elif (0.60 <= cov < 0.75 and step in (0, 1)) or (step == 1 and cov >= 0.75): v = "Stretch"
        else: v = "Pivot"
        flags = []
        med = (an.get("pay") or {}).get("median"); cur_mid = est.get("mid") if isinstance(est, dict) else None
        if med and cur_mid and (an["pay"].get("currency") == est.get("currency")) and med < 0.85 * cur_mid:
            flags.append("pay step-down")
        if an["confidence"] == "low": flags.append("low confidence")
        out[n["id"]] = dict(verdict=v, coverage=cov, fit=f["fit"], band_step=step, flags=flags)
    save(run / "qualification.json", out)
    for k, v in out.items(): print(k, v)


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    for c in ("screen", "qualify"):
        s = sp.add_parser(c); s.add_argument("--run", required=True)
    a = ap.parse_args(); dict(screen=screen, qualify=qualify)[a.cmd](a)


if __name__ == "__main__":
    main()
