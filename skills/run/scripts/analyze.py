#!/usr/bin/env python3
"""Phase 3 + 5 — demand dissection, diagnosis and prognosis for ONE niche.

usage: analyze.py --run RUN --niche n01

Reads  RUN/niches.json, RUN/postings/postings.jsonl, RUN/postings/second.jsonl (optional)
Writes RUN/niches/<id>/analysis.json

Methods (each one maps to a report visual):
  prevalence + Wilson 95% CI, required share       → demand bar chart with CI whiskers
  co-occurrence lift on codes ≥20%                 → "bundles" list
  Jaccard + average-linkage clusters (n≥12)        → posting archetypes
  pay midpoints, bootstrap CI of the median        → pay band box
  years required, builder index                    → stat tiles
  log-odds keyness with informative Dirichlet prior vs contrast corpus → language chart
  Cohen's kappa per code on the blind second coding → reliability table, code exclusion
  then vs now: Fisher exact, Cochran–Armitage trend across eras, Mantel–Haenszel OR by level band → change dumbbell
Statistical tests run only when each compared group has n ≥ stats threshold (rubric 10); otherwise counts only.
"""
import argparse, collections, itertools, math, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save, wilson, codebook, thresholds

STOP = set("""a an the and or of to in for with on at by from as is are be your you our we will this that it its into across
including within years year experience strong proven ability track record deep excellent skills knowledge 5 7 8 10 plus +""".split())
WEIGHT = {"live": 1.0, "doubtful": 0.5, "likely_ghost": 0.0, "closed": 0.0, None: 1.0}


def present(r, k): return 1 if r["codes"].get(k, 0) >= 1 else 0
def required(r, k): return 1 if r["codes"].get(k, 0) == 2 else 0


def toks(s):
    s = s.lower().replace("-", " ").replace("/", " ")
    return [w for w in re.findall(r"[a-z\$\+0-9é]+", s) if w not in STOP and len(w) > 1]


def text_of(r): return " ".join(r.get("must_haves", []) + r.get("phrases", []))


def keyness(target, contrast, top=15):
    """Monroe et al. log-odds ratio with informative Dirichlet prior; returns z-scores."""
    ca, cb = collections.Counter(), collections.Counter()
    for r in target: ca.update(set(toks(text_of(r))))
    for r in contrast: cb.update(set(toks(text_of(r))))
    call = ca + cb
    if not call: return []
    a0 = sum(call.values()); na, nb = sum(ca.values()), sum(cb.values())
    res = []
    for w, cw in call.items():
        aw = cw
        ya, yb = ca[w], cb[w]
        la = math.log((ya + aw) / (na + a0 - ya - aw)); lb = math.log((yb + aw) / (nb + a0 - yb - aw))
        var = 1 / (ya + aw) + 1 / (yb + aw)
        res.append(dict(term=w, z=round((la - lb) / math.sqrt(var), 2), n_in=ya, n_out=yb))
    res.sort(key=lambda x: -x["z"])
    return [x for x in res if x["n_in"] >= 2][:top]


def kappa(a, b):
    a, b = np.array(a), np.array(b)
    po = (a == b).mean()
    pe = sum((a == v).mean() * (b == v).mean() for v in set(a) | set(b))
    return None if pe == 1 else float((po - pe) / (1 - pe))


def cochran_armitage(groups, k):
    from scipy.stats import norm
    ns = np.array([len(g) for g in groups]); xs = np.array([sum(present(r, k) for r in g) for g in groups]); t = np.arange(len(groups))
    N = ns.sum(); Pp = xs.sum() / N if N else 0
    if Pp in (0, 1): return 0.0, 1.0
    T = np.sum(t * (xs - ns * Pp)); V = Pp * (1 - Pp) * (np.sum(ns * t * t) - np.sum(ns * t) ** 2 / N)
    if V <= 0: return 0.0, 1.0
    z = T / math.sqrt(V); return float(z), float(2 * (1 - norm.cdf(abs(z))))


def mh(now, base, k):
    from statsmodels.stats.contingency_tables import StratifiedTable
    tabs = []
    # two strata, as in the reference run: senior (Head/VP/SVP/C) vs everything below
    sb = lambda r: "senior" if r["level"] in ("Head", "VP", "SVP", "C", "director", "executive") else "below"
    for band in ("senior", "below"):
        a = [r for r in now if sb(r) == band]; c = [r for r in base if sb(r) == band]
        if not a or not c: continue
        x = sum(present(r, k) for r in a); y = sum(present(r, k) for r in c)
        tabs.append(np.array([[x, len(a) - x], [y, len(c) - y]], float) + 0.5)
    if not tabs: return None, None
    st = StratifiedTable(tabs)
    return float(st.oddsratio_pooled), float(st.test_null_odds(correction=True).pvalue)


def signal(n_now, n_base, ci_w, p, kap, th):
    if n_now >= th["stats_n"] and n_base >= th["stats_n"] and ci_w <= 0.30 and p is not None and p < 0.05 and (kap is None or kap >= 0.6):
        return "strong"
    if n_now >= 15 and n_base >= 15 and p is not None and p < 0.10:
        return "moderate"
    return "directional"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); ap.add_argument("--niche", required=True)
    a = ap.parse_args(); run = Path(a.run)
    th, relaxed = thresholds(run)
    niches = {n["id"]: n for n in load(run / "niches.json")["niches"]}
    niche = niches[a.niche]
    codes, byid = codebook([niche["module"]], run)
    allp = load(run / "postings" / "postings.jsonl")
    def w(r): return WEIGHT[(r.get("liveness") or {}).get("band")]
    now = [r for r in allp if a.niche in r["niche_ids"] and r["era"] == "now" and w(r) > 0]
    arch = [r for r in allp if a.niche in r["niche_ids"] and r["era"] != "now"]
    others = [r for r in allp if a.niche not in r["niche_ids"] and r["era"] == "now" and w(r) > 0]
    n = len(now)
    out = dict(niche=a.niche, n_now=n, n_live_weighted=round(sum(w(r) for r in now), 1),
               n_employers=len({r["company"] for r in now}), n_archive=len(arch),
               liveness=dict(collections.Counter((r.get("liveness") or {}).get("band", "unscored") for r in allp if a.niche in r["niche_ids"] and r["era"] == "now")),
               confidence="normal" if n >= th["stats_n"] else "low", relaxed_thresholds=relaxed)

    # liveness summary (ghost-job risk) for the niche, against the Greenhouse benchmark
    allnow = [r for r in allp if a.niche in r["niche_ids"] and r["era"] == "now"]
    buckets = {"0-30": 0, "31-60": 0, "61-90": 0, "90+": 0, "unknown": 0}
    for r in allnow:
        lv = r.get("liveness") or {}; age = next((int(f.split()[1][:-1]) for f in lv.get("flags", []) if f.startswith("age ")), None)
        if age is None: buckets["unknown" if not (r.get("date_posted") or r.get("date_seen")) else "0-30"] += 1
        else: buckets["90+" if age > 90 else "61-90" if age > 60 else "31-60" if age > 30 else "0-30"] += 1
    bands = collections.Counter((r.get("liveness") or {}).get("band", "unscored") for r in allnow)
    out["liveness_summary"] = dict(n=len(allnow), bands=dict(bands), age_buckets=buckets,
                                   doubtful_share=round((bands["doubtful"] + bands["likely_ghost"]) / len(allnow), 3) if allnow else 0.0,
                                   benchmark=dict(low=0.18, high=0.22, source="Greenhouse share of postings not actively being filled, per quarter (via Apollo Technical)"))

    # reliability
    sec_f = run / "postings" / "second.jsonl"
    kap = {}
    if sec_f.exists():
        sec = {s["id"]: s for s in load(sec_f)}
        ids = [r for r in allp if r["id"] in sec]
        pooled_a, pooled_b = [], []
        for c in codes:
            k = c["id"]; pairs = [(present(r, k), 1 if sec[r["id"]]["codes"].get(k, 0) >= 1 else 0) for r in ids if k in sec[r["id"]]["codes"]]
            if len(pairs) >= 5:
                x, y = zip(*pairs); pooled_a += x; pooled_b += y
                kap[k] = dict(n=len(pairs), agree=round(float(np.mean(np.array(x) == np.array(y))), 2), kappa=None if kappa(x, y) is None else round(kappa(x, y), 2))
        out["reliability"] = dict(n_postings=len(ids), pooled_kappa=round(kappa(pooled_a, pooled_b), 2) if pooled_a else None,
                                  pooled_agree=round(float(np.mean(np.array(pooled_a) == np.array(pooled_b))), 2) if pooled_a else None, per_code=kap)
    else:
        out["reliability"] = None
    excluded = {k for k, v in kap.items() if v["kappa"] is not None and v["kappa"] < 0.4}
    weak = {k for k, v in kap.items() if v["kappa"] is not None and 0.4 <= v["kappa"] < 0.6}

    # prevalence
    rows = []
    for c in codes:
        k = c["id"]; kp = sum(present(r, k) for r in now); kr = sum(required(r, k) for r in now)
        p, lo, hi = wilson(kp, n)
        rows.append(dict(code=k, label=c["label"], module=c["module"], present=round(p, 3), lo=round(lo, 3), hi=round(hi, 3),
                         required=round(kr / n, 3) if n else 0, k=kp, n=n,
                         reliability="excluded" if k in excluded else "weak" if k in weak else "ok" if k in kap else "unchecked"))
    rows.sort(key=lambda r: (-r["present"], -r["required"]))
    out["prevalence"] = rows
    out["top_required"] = [r["code"] for r in sorted(rows, key=lambda r: -r["required"]) if r["required"] > 0 and r["code"] not in excluded][:10]

    # lift pairs
    common = [r["code"] for r in rows if r["present"] >= 0.2]
    pairs = []
    for x, y in itertools.combinations(common, 2):
        px = np.mean([present(r, x) for r in now]); py = np.mean([present(r, y) for r in now])
        pxy = np.mean([present(r, x) * present(r, y) for r in now])
        if px and py and pxy >= 0.15:
            pairs.append(dict(a=x, b=y, both=round(float(pxy), 2), lift=round(float(pxy / (px * py)), 2)))
    out["bundles"] = sorted(pairs, key=lambda p: -p["lift"])[:8]

    # clusters
    if n >= 12 and common:
        from scipy.cluster.hierarchy import linkage, fcluster
        from scipy.spatial.distance import pdist
        X = np.array([[present(r, k) for k in common] for r in now], bool)
        lab = fcluster(linkage(pdist(X, "jaccard"), "average"), 3, "maxclust")
        cl = []
        for g in sorted(set(lab)):
            idx = [i for i in range(n) if lab[i] == g]
            share = {k: np.mean([present(now[i], k) for i in idx]) for k in common}
            base = {k: np.mean([present(r, k) for r in now]) for k in common}
            dist = sorted(common, key=lambda k: -(share[k] - base[k]))[:4]
            cl.append(dict(size=len(idx), signature=dist, examples=[f"{now[i]['company']} — {now[i]['title']}" for i in idx[:4]]))
        out["clusters"] = sorted(cl, key=lambda c: -c["size"])
    else:
        out["clusters"] = None

    # pay
    cur = collections.Counter((r.get("pay") or {}).get("currency") for r in now if r.get("pay") and r["pay"].get("min"))
    main_cur = cur.most_common(1)[0][0] if cur else None
    mids = np.array([(r["pay"]["min"] + r["pay"]["max"]) / 2 for r in now if r.get("pay") and r["pay"].get("min") and r["pay"].get("max")
                     and r["pay"]["max"] != r["pay"]["min"] and r["pay"].get("currency") == main_cur and "pay flagged" not in r.get("note", "") and "looks low" not in r.get("note", "")])
    if len(mids) >= 3:
        rng = np.random.default_rng(3); bs = [np.median(rng.choice(mids, len(mids))) for _ in range(4000)]
        out["pay"] = dict(currency=main_cur, n=int(len(mids)), median=float(np.median(mids)), p25=float(np.percentile(mids, 25)),
                          p75=float(np.percentile(mids, 75)), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                          by_level={lv: float(np.median([(r["pay"]["min"] + r["pay"]["max"]) / 2 for r in now if r["level"] == lv and r.get("pay") and r["pay"].get("min") and r["pay"].get("max") and r["pay"]["max"] != r["pay"]["min"] and r["pay"].get("currency") == main_cur]))
                                    for lv in sorted({r["level"] for r in now}) if sum(1 for r in now if r["level"] == lv and r.get("pay") and r["pay"].get("min") and r["pay"].get("max") and r["pay"]["max"] != r["pay"]["min"] and r["pay"].get("currency") == main_cur) >= 2})
    else:
        out["pay"] = dict(currency=main_cur, n=int(len(mids)), median=None, median_low_n=float(np.median(mids)) if len(mids) else None,
                          note=f"{len(mids)} posted pay range(s); a band needs at least 3")

    yrs = [r["years_required"] for r in now if r.get("years_required")]
    out["years"] = dict(n=len(yrs), median=float(np.median(yrs)) if yrs else None)
    vb = sum(r["builder_verbs"] for r in now); vm = sum(r["maintain_verbs"] for r in now)
    out["builder_index"] = dict(ratio=round(vb / (vb + vm), 2) if vb + vm else None, build=vb, maintain=vm)
    out["levels"] = dict(collections.Counter(r["level"] for r in now))
    out["employers"] = sorted({r["company"] for r in now})

    # language
    contrast = others if len(others) >= 10 else arch   # keyness needs a contrast set; with none it returns []
    out["language"] = dict(contrast="other niches" if contrast is others else "archive postings", contrast_n=len(contrast),
                           keyness=keyness(now, contrast) if len(contrast) >= 5 else [],
                           phrases=[p for r in now for p in r.get("phrases", [])][:40],
                           top_terms=collections.Counter(w for r in now for w in set(toks(text_of(r)))).most_common(25))

    # change (prognosis)
    if len(arch) >= th["archive_n"]:
        eras = sorted({r["era"] for r in arch}) + ["now"]
        groups = [[r for r in arch if r["era"] == e] for e in eras[:-1]] + [now]
        from scipy.stats import fisher_exact
        crow = []
        for c in codes:
            k = c["id"]; b = sum(present(r, k) for r in arch); x = sum(present(r, k) for r in now)
            pb = wilson(b, len(arch)); pn = wilson(x, n)
            p = float(fisher_exact([[x, n - x], [b, len(arch) - b]])[1])
            orr, pmh = mh(now, arch, k)
            z, pt = cochran_armitage(groups, k) if len(groups) >= 3 else (None, None)
            kv = kap.get(k, {}).get("kappa")
            crow.append(dict(code=k, label=c["label"], then=round(pb[0], 3), now=round(pn[0], 3), delta=round(pn[0] - pb[0], 3),
                             by_era={e: round(np.mean([present(r, k) for r in g]), 3) if g else None for e, g in zip(eras, groups)},
                             fisher_p=round(p, 4), or_mh=None if orr is None else round(orr, 2), p_mh=None if pmh is None else round(pmh, 4),
                             trend_z=None if z is None else round(z, 2), trend_p=None if pt is None else round(pt, 4),
                             signal=signal(n, len(arch), pn[2] - pn[1], p, kv, th)))
        crow.sort(key=lambda r: -r["delta"])
        def cpp(g): return float(np.mean([sum(present(r, c["id"]) for c in codes) for r in g])) if g else None
        out["change"] = dict(eras={e: len(g) for e, g in zip(eras, groups)}, rows=crow,
                             codes_per_posting={e: cpp(g) for e, g in zip(eras, groups)},
                             years_then=float(np.median([r["years_required"] for r in arch if r.get("years_required")])) if any(r.get("years_required") for r in arch) else None)
    else:
        out["change"] = None
        out["change_hidden_reason"] = f"{len(arch)} archive postings (< {th['archive_n']} needed)"
    save(run / "niches" / a.niche / "analysis.json", out)
    print(f"{a.niche}: n={n} employers={out['n_employers']} archive={len(arch)} confidence={out['confidence']} "
          f"top_required={out['top_required'][:5]} pay_median={out['pay'].get('median')}")


if __name__ == "__main__":
    main()
