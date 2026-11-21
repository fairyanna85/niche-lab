#!/usr/bin/env python3
"""Act 2 contrasts (plan §5.2): what rises with seniority, how two niches differ, how job titles and requirements
shifted between eras, and the per-posting pay ranges. Pure functions over coded postings; assemble.py calls them.

Small-sample rule: a within-niche contrast needs >= 10 postings on each side; otherwise the seniority contrast is
computed across all qualified niches and labelled so, and a niche-vs-niche contrast is withheld with the counts.
Fisher exact p < 0.05 marks a row significant; everything else is directional and drawn hollow.
"""
import math, re
from scipy.stats import fisher_exact

SENIOR = {"Head", "VP", "SVP", "executive", "C", "director_plus"}
JUNIOR = {"Mgr", "Dir", "SrDir", "manager", "lead", "experienced", "SrMgr"}
MIN_SIDE = 10
STOP = set("of and the for in to a an & - , / with at on senior sr jr i ii iii".split())


def wilson(k, n, z=1.96):
    if not n: return (None, None, None)
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, max(0.0, c - h), min(1.0, c + h))


def has(p, k): return 1 if (p.get("codes") or {}).get(k, 0) >= 1 else 0


def contrast(A, B, codes, labels, top=None):
    """Rows for every code: share in A and B, difference with Newcombe interval, Fisher exact p."""
    rows = []
    for k in codes:
        a, b = sum(has(p, k) for p in A), sum(has(p, k) for p in B)
        if a + b == 0: continue
        pa, la, ua = wilson(a, len(A)); pb, lb, ub = wilson(b, len(B))
        d = pa - pb
        lo = d - math.sqrt((pa - la) ** 2 + (ub - pb) ** 2); hi = d + math.sqrt((ua - pa) ** 2 + (pb - lb) ** 2)
        p = float(fisher_exact([[a, len(A) - a], [b, len(B) - b]])[1])
        rows.append(dict(code=k, label=labels.get(k, k), a=round(pa, 3), b=round(pb, 3), k_a=a, k_b=b, diff=round(d, 4), lo=round(lo, 3), hi=round(hi, 3), p=round(p, 4), significant=p < .05))
    rows.sort(key=lambda r: (r["p"], -abs(r["diff"]), r["code"]))
    return rows[:top] if top else rows


def seniority(posts_niche, posts_all, codes, labels):
    """Senior (Head/VP and above) against director and manager bands; within the niche when both sides reach 10."""
    for scope, P in (("niche", posts_niche), ("all niches", posts_all)):
        S = [p for p in P if p.get("level") in SENIOR]; D = [p for p in P if p.get("level") in JUNIOR]
        if len(S) >= MIN_SIDE and len(D) >= MIN_SIDE:
            return dict(scope=scope, n_senior=len(S), n_other=len(D), rows=contrast(S, D, codes, labels, top=12))
    S = [p for p in posts_all if p.get("level") in SENIOR]; D = [p for p in posts_all if p.get("level") in JUNIOR]
    return dict(scope=None, n_senior=len(S), n_other=len(D), rows=[], reason=f"{len(S)} senior and {len(D)} other postings across all niches (10 each needed)")


def versus(nid, other, by_niche, codes, labels):
    A, B = by_niche.get(nid, []), by_niche.get(other, [])
    if other is None: return dict(other=None, rows=[], reason="no other niche to compare")
    if len(A) < MIN_SIDE or len(B) < MIN_SIDE:
        return dict(other=other, n_a=len(A), n_b=len(B), rows=[], reason=f"{len(A)} and {len(B)} postings (10 each needed)")
    return dict(other=other, n_a=len(A), n_b=len(B), rows=contrast(A, B, codes, labels, top=12))


def title_terms(t):
    w = [x for x in re.findall(r"[a-zà-ÿ&]+", (t or "").lower()) if x not in STOP and len(x) > 1]
    return set(w)


def title_shift(then, now, min_count=3, top=10):
    """Words in job titles, then against now: share in each era, Fisher exact p."""
    T, N = [title_terms(t) for t in then], [title_terms(t) for t in now]
    vocab = {w for s in T + N for w in s}
    rows = []
    for w in vocab:
        a, b = sum(w in s for s in T), sum(w in s for s in N)
        if a + b < min_count: continue
        p = float(fisher_exact([[a, len(T) - a], [b, len(N) - b]])[1])
        rows.append(dict(term=w, share_then=round(a / len(T), 3), share_now=round(b / len(N), 3), n_then=len(T), n_now=len(N), k_then=a, k_now=b, p=round(p, 4)))
    rows.sort(key=lambda r: (-abs(r["share_now"] - r["share_then"]), r["p"], r["term"]))
    return rows[:top]


def pooled_change(then, now, codes, labels, top=10):
    """Then vs now across all niches of the role family: used where a niche's own archive is too small."""
    rows = []
    for k in codes:
        a, b = sum(has(p, k) for p in then), sum(has(p, k) for p in now)
        if a + b == 0: continue
        p = float(fisher_exact([[a, len(then) - a], [b, len(now) - b]])[1])
        d = b / len(now) - a / len(then)
        rows.append(dict(code=k, label=labels.get(k, k), then=round(a / len(then), 3), now=round(b / len(now), 3), delta=round(d, 3), p=round(p, 4),
                         signal="significant" if p < .05 else "directional"))
    rows.sort(key=lambda r: (-abs(r["delta"]), r["code"]))
    return rows[:top]


def pay_ranges(posts, currency):
    out = []
    for p in posts:
        pay = p.get("pay") or {}
        if pay.get("min") and pay.get("max") and (pay.get("currency") or currency) == currency:
            out.append(dict(posting_id=p["id"], company=p["company"], lo=pay["min"], hi=pay["max"], currency=currency,
                            source=p.get("source_type", "employer"), flagged=p.get("source_type") not in (None, "employer")))
    return sorted(out, key=lambda r: (r["lo"] + r["hi"]) / 2)
