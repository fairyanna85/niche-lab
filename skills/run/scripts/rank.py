#!/usr/bin/env python3
"""Phase 6/7 — rank qualified niches (rubric 13) and employers inside each niche (rubric 14).

usage: rank.py --run RUN [--draws 1000]

Reads  niches.json (kept niches + agent-filled `pref_checks`), qualification.json, profile.json,
       niches/<id>/analysis.json, fit.json, access.json (agent, rubric 15), postings.jsonl, evidence.json
Writes ranking.json, niches/<id>/employers.json
"""
import argparse, math, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save

WEIGHTS = dict(fit=35, pay=15, demand=15, momentum=10, preference=10, access=10, rarity=5)
GW = {"stated": 1.0, "inferred2": 0.75, "inferred1": 0.5, "absent": 0.0}


from fit import posting_fit


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); ap.add_argument("--draws", type=int, default=1000)
    a = ap.parse_args(); run = Path(a.run)
    doc = load(run / "niches.json"); q = load(run / "qualification.json"); prof = load(run / "profile.json")
    ev = load(run / "evidence.json"); posts = load(run / "postings" / "postings.jsonl")
    est = prof["fields"]["current_pay_band_est"]["value"] or {}
    edges = prof.get("edges", [])
    ids = [n["id"] for n in doc["niches"] if n["id"] in q and q[n["id"]]["verdict"] != "Rejected"]
    N = {n["id"]: n for n in doc["niches"]}
    an = {i: load(run / "niches" / i / "analysis.json") for i in ids}
    comp = {}
    maxd = max(an[i]["n_live_weighted"] for i in ids) if ids else 1
    meds = {i: (an[i].get("pay") or {}).get("median") for i in ids}
    for i in ids:
        A = an[i]; c = {}
        c["fit"] = q[i]["fit"]
        med = meds[i]
        if med and isinstance(est, dict) and est.get("mid") and A["pay"].get("currency") == est.get("currency"):
            c["pay"] = float(np.clip((med / est["mid"] - 0.7) / 0.6, 0, 1))
        elif med:
            vals = sorted(v for v in meds.values() if v); c["pay"] = vals.index(med) / max(1, len(vals) - 1) if len(vals) > 1 else 0.5
        else:
            c["pay"] = 0.5
        c["demand"] = math.log1p(A["n_live_weighted"]) / math.log1p(maxd) if maxd else 0
        if A.get("change"):
            rows = {r["code"]: r for r in A["change"]["rows"]}
            g = np.mean([rows[k]["delta"] for k in A["top_required"][:5] if k in rows]) if A["top_required"] else 0
            c["momentum"] = float(0.5 + 0.5 * math.tanh(3 * g))
        else:
            c["momentum"] = 0.5
        pc = N[i].get("pref_checks", [])
        c["preference"] = sum(GW[x["grade"]] for x in pc if x["matched"]) / sum(GW[x["grade"]] for x in pc) if pc and sum(GW[x["grade"]] for x in pc) else 0.5
        acc_f = run / "niches" / i / "access.json"
        acc = load(acc_f) if acc_f.exists() else []
        top = sorted(A["employers"])[:15] if A["employers"] else []
        strong = {x["company"] for x in acc if x["strength"] >= 2}
        c["access"] = len([e for e in A["employers"] if e in strong]) / min(15, len(A["employers"])) if A["employers"] else 0
        prev = {r["code"]: r["present"] for r in A["prevalence"]}
        rare = [e for e in edges if any(0.05 <= prev.get(k, 0) <= 0.30 for k in e.get("codes", []))]
        c["rarity"] = len(rare) / len(edges) if edges else 0
        comp[i] = {k: round(v, 3) for k, v in c.items()}
    W = np.array([WEIGHTS[k] for k in WEIGHTS], float)
    M = np.array([[comp[i][k] for k in WEIGHTS] for i in ids])
    score = M @ W / W.sum() * 100 if ids else np.array([])
    order = [ids[j] for j in np.argsort(-score)]
    # sensitivity
    rng = np.random.default_rng(11); K = len(ids)
    freq = {i: [0] * K for i in ids}; top3 = {i: 0 for i in ids}; same = 0
    base_top = set(order[:3])
    for _ in range(a.draws):
        w = rng.dirichlet(W / W.sum() * 50)
        s = M @ w; o = [ids[j] for j in np.argsort(-s)]
        for r, i in enumerate(o): freq[i][r] += 1
        for i in o[:3]: top3[i] += 1
        same += set(o[:3]) == base_top
    # overlaps
    allcodes = sorted({k for i in ids for k in [r["code"] for r in an[i]["prevalence"]]})
    def rv(i): d = {r["code"]: r["required"] for r in an[i]["prevalence"]}; return np.array([d.get(k, 0) for k in allcodes])
    def cosv(x, y): return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y))) if np.linalg.norm(x) and np.linalg.norm(y) else 0
    req = [[round(cosv(rv(x), rv(y)), 2) for y in order] for x in order]
    emp = [[round(len(set(an[x]["employers"]) & set(an[y]["employers"])) / max(1, len(set(an[x]["employers"]) | set(an[y]["employers"]))), 2) for y in order] for x in order]
    # sequence
    seq = []
    for r, i in enumerate(order):
        if r < 2 or (r == 2 and score[ids.index(i)] >= 0.9 * score[ids.index(order[1])] and q[i]["verdict"] != "Pivot" and top3[i] / a.draws >= 0.8):
            seq.append(dict(niche_id=i, phase="now", trigger="active from week 1"))
        elif r < 5:
            seq.append(dict(niche_id=i, phase="next", trigger="activate if an active niche gets no interview after 10 referral-led approaches, or by week 8"))
        else:
            seq.append(dict(niche_id=i, phase="parked", trigger="revisit at week 12 or if a strength-3 access path appears"))
    ranking = dict(weights=WEIGHTS, order=order,
                   niches=[dict(id=i, rank=r + 1, score=round(float(score[ids.index(i)]), 1), components=comp[i], verdict=q[i]["verdict"], flags=q[i]["flags"])
                           for r, i in enumerate(order)],
                   sensitivity=dict(draws=a.draws, rank_freq={i: [round(x / a.draws, 3) for x in freq[i]] for i in ids},
                                    p_top3={i: round(top3[i] / a.draws, 3) for i in ids}, stable=same / a.draws >= 0.8, same_top3_share=round(same / a.draws, 3)),
                   overlap=dict(ids=order, requirements=req, employers=emp), sequence=seq)
    save(run / "ranking.json", ranking)
    # employers per niche (rubric 14)
    prefseg = set(prof["revealed_preferences"].get("employer_types", {}).get("value") or [])
    for i in ids:
        acc_f = run / "niches" / i / "access.json"; acc = {x["company"]: x for x in (load(acc_f) if acc_f.exists() else [])}
        med = meds[i]; rows = []
        for co in an[i]["employers"]:
            ps = [p for p in posts if i in p["niche_ids"] and p["era"] == "now" and p["company"] == co]
            live = max(((p.get("liveness") or {}).get("score", 70) for p in ps), default=0)
            pf = max(posting_fit(p, ev) for p in ps)
            mids = [(p["pay"]["min"] + p["pay"]["max"]) / 2 for p in ps if p.get("pay") and p["pay"].get("min") and p["pay"].get("max")]
            payc = float(np.clip((max(mids) / med - 0.7) / 0.6, 0, 1)) if mids and med else 0.5
            st = acc.get(co, {}).get("strength", 0)
            segm = 1.0 if any(p.get("segment") in prefseg for p in ps) else 0.5 if not prefseg else 0.0
            s = 100 * (0.35 * pf + 0.20 * live / 100 + 0.20 * st / 3 + 0.15 * payc + 0.10 * segm)
            band = min(((p.get("liveness") or {}).get("band", "live") for p in ps), key=lambda b: ["likely_ghost", "doubtful", "live", "closed"].index(b))
            rows.append(dict(company=co, score=round(s, 1), posting_fit=round(pf, 2), liveness=live, band=band, access=st,
                             path=acc.get(co, {}).get("path"), pay_mid=max(mids) if mids else None, titles=[p["title"] for p in ps][:2],
                             urls=[p["url"] for p in ps][:2]))
        rows.sort(key=lambda r: (r["band"] == "likely_ghost", -r["score"]))
        save(run / "niches" / i / "employers.json", rows[:15])
    for n in ranking["niches"]:
        print(f"#{n['rank']} {n['id']} {n['score']:5.1f} {n['verdict']:8s} P(top3)={ranking['sensitivity']['p_top3'][n['id']]:.2f} {n['components']}")
    print("stable top-3:", ranking["sensitivity"]["stable"], ranking["sensitivity"]["same_top3_share"])


if __name__ == "__main__":
    main()
