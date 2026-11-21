#!/usr/bin/env python3
"""Phase 10 — assemble results.json from script outputs (numbers) and narrative.json (agent prose and advice).

usage: assemble.py --run RUN
Numbers come ONLY from script outputs. narrative.json carries claims, advice ("do_this"), pitch, scripts and plans.
Every section the template renders needs a non-empty do_this; build_report.py refuses to build otherwise.
"""
import argparse, datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from timeline import build_timeline
import contrasts as CT
from common import codebook, load, save, validate, thresholds, REPO

FUNNEL_BENCH = [
    dict(stage="Cold application → offer", rate="0.5%", source="Gem 2026 Recruiting Benchmarks (165M applications)", url="https://app.gem.com/blog/key-takeaways-from-the-2026-recruiting-benchmarks-report"),
    dict(stage="Referral vs inbound conversion", rate="11×", source="Gem 2026 Recruiting Benchmarks", url="https://app.gem.com/blog/key-takeaways-from-the-2026-recruiting-benchmarks-report"),
    dict(stage="Referred candidates passing first screen", rate="52% (vs 35% overall)", source="Ashby 2026 benchmarks via Noon", url="https://www.noon.ai/blog/articles/360-employee-referral-statistics-2026"),
    dict(stage="Postings not actively being filled", rate="18–22% per quarter", source="Greenhouse via Apollo Technical", url="https://www.apollotechnical.com/?p=60303"),
    dict(stage="Gain from negotiating an offer", rate="+18.8% average; 55% don't try", source="Interview Guys review of 2024–25 studies", url="https://blog.theinterviewguys.com/?p=4616"),
]
DIAG = [
    dict(symptom="No replies after 10 approaches in a niche", cause="Channel (cold) or top third of the resume", fix="Switch to access paths of strength ≥2; re-run the advocate test on the niche resume"),
    dict(symptom="Screens but no second interviews", cause="Level or proof mismatch", fix="Re-check level mapping; lead with the niche's top-3 proof points in the first 2 minutes"),
    dict(symptom="Final rounds, no offers", cause="Interview performance or references", fix="Rehearse the 3 likely objections in the pitch section; line up 2 references per niche"),
    dict(symptom="Offers below the niche band", cause="Anchoring or negotiation", fix="Use the niche pay script; counter once with the band's 75th percentile and the walk-away number ready"),
]


def fmt_val(v):
    if isinstance(v, dict) and "mid" in v:
        if v["mid"] is None: return "not estimable from the record"
        sym = {"EUR": "€", "GBP": "£"}.get(v.get("currency"), "$")
        return f"{sym}{round(v['mid'] / 1000)}K midpoint ({v.get('currency', '')})"
    if isinstance(v, dict): return ", ".join(f"{a}: {b}" for a, b in v.items())
    if isinstance(v, list): return ", ".join(map(str, v))
    return v


def market_block(run, niches_out, ev):
    """Whole-market view across qualified niches: 2-D map of postings (classical MDS on Jaccard distance of
    requirement profiles, candidate included as a point), requirement DNA matrix, pay and years distributions."""
    import numpy as np
    posts = [p for p in load(run / "postings" / "postings.jsonl") if p["era"] == "now" and (p.get("liveness") or {}).get("band") != "likely_ghost"]
    order = [n["id"] for n in niches_out]
    P = [p for p in posts if any(i in order for i in p["niche_ids"])]
    if len(P) < 3: return None
    codes = sorted({k for p in P for k, v in p["codes"].items() if v})
    X = np.array([[1 if p["codes"].get(k, 0) >= 1 else 0 for k in codes] for p in P] + [[1 if ev.get(k, {}).get("grade", 0) >= 2 else 0 for k in codes]], bool)
    inter = (X[:, None, :] & X[None, :, :]).sum(-1); union = (X[:, None, :] | X[None, :, :]).sum(-1)
    D = 1 - np.divide(inter, union, out=np.zeros_like(inter, float), where=union > 0)
    n = len(D); J = np.eye(n) - 1 / n; B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B); idx = np.argsort(w)[::-1][:2]
    Y = V[:, idx] * np.sqrt(np.maximum(w[idx], 1e-9))
    Y = (Y - Y.min(0)) / np.maximum(Y.max(0) - Y.min(0), 1e-9)
    pts = []
    for i, p in enumerate(P):
        prim = next(nid for nid in order if nid in p["niche_ids"])
        mid = (p["pay"]["min"] + p["pay"]["max"]) / 2 if p.get("pay") and p["pay"].get("min") and p["pay"].get("max") else None
        pts.append(dict(id=p["id"], company=p["company"], title=p["title"], url=p.get("url"), niche=prim, niches=[x for x in order if x in p["niche_ids"]],
                        x=round(float(Y[i, 0]), 4), y=round(float(Y[i, 1]), 4), band=(p.get("liveness") or {}).get("band", "live"),
                        level=p["level"], pay_mid=mid, currency=(p.get("pay") or {}).get("currency")))
    cand = dict(x=round(float(Y[-1, 0]), 4), y=round(float(Y[-1, 1]), 4))
    close = {}
    for nid in order:
        sims = [1 - D[-1, i] for i, p in enumerate(P) if nid in p["niche_ids"]]
        close[nid] = round(float(np.mean(sims)), 3) if sims else None
    dna_codes = []
    prev = {nid: {r["code"]: r for r in nn["demand"]["rows"]} for nid, nn in zip(order, niches_out)}
    for k in codes:
        vals = [prev[nid].get(k, {}).get("present", 0) for nid in order]
        if max(vals) >= 0.3: dna_codes.append((k, float(np.mean(vals))))
    dna_codes.sort(key=lambda t: -t[1])
    dna = [dict(code=k, label=next((prev[nid][k]["label"] for nid in order if k in prev[nid]), k),
                cells=[dict(niche=nid, present=prev[nid].get(k, {}).get("present", 0), required=prev[nid].get(k, {}).get("required", 0)) for nid in order],
                grade=ev.get(k, {}).get("grade", 0)) for k, _ in dna_codes[:22]]
    pay = {}; yrs = {}; lv = {}
    for nn in niches_out:
        nid = nn["id"]; cur = nn["size"]["currency"]
        pay[nid] = sorted((p["pay"]["min"] + p["pay"]["max"]) / 2 for p in P if nid in p["niche_ids"] and p.get("pay") and p["pay"].get("min") and p["pay"].get("max") and p["pay"]["max"] != p["pay"]["min"] and p["pay"].get("currency") == cur)
        yrs[nid] = sorted(p["years_required"] for p in P if nid in p["niche_ids"] and p.get("years_required"))
        lv[nid] = nn["size"]["levels"]
    # competing supply: peers placed among the postings they resemble (mean of the 5 nearest by Jaccard distance)
    peer_pts, peers_sum, peer_rows = [], [], []
    for nn in niches_out:
        nid = nn["id"]; f = run / "niches" / nid / "peers.jsonl"; sec = nn.get("peers")
        rows = load(f) if (f.exists() and sec) else []
        peer_rows += rows
        for r in rows:
            v = np.array([1 if r["codes"].get(k) else 0 for k in codes], bool)
            d = 1 - np.array([((v & X[i]).sum() / max(1, (v | X[i]).sum())) for i in range(len(P))])
            nb = np.argsort(d)[:5]
            peer_pts.append(dict(id=r["id"], niche=nid, x=round(float(Y[nb, 0].mean()), 4), y=round(float(Y[nb, 1].mean()), 4)))
        peers_sum.append(dict(niche_id=nid, n=sec["n"], sources=sec["sources"], years=sec["years"], paths=sec["paths"], kappa=sec.get("kappa"))
                         if sec else dict(niche_id=nid, n=0, reason=nn["hidden_reason"].get("peers", "peer search not run")))
    # rarity: each requirement the record proves, how often postings ask for it and how often peers show it
    label = {k: next((prev[nid][k]["label"] for nid in order if k in prev[nid]), k) for k in codes}
    rarity = []
    for k in codes:
        g = ev.get(k, {}).get("grade", 0)
        if g < 2: continue
        asked = sum(1 for p in P if p["codes"].get(k, 0) >= 1)
        shown = sum(1 for r in peer_rows if r["codes"].get(k))
        rarity.append(dict(code=k, label=label[k], grade=g, asked_share=round(asked / len(P), 3), asked_n=len(P),
                           peer_share=round(shown / len(peer_rows), 3) if peer_rows else None, peer_n=len(peer_rows)))
    rarity.sort(key=lambda r: ((r["peer_share"] if r["peer_share"] is not None else 1) - r["asked_share"]))
    return_bridge = bridge_links(ev, rarity, label)
    return dict(points=pts, candidate=cand, closeness=close, dna=dna, pay_points=pay, years=yrs, levels=lv,
                peers=peers_sum, peer_points=peer_pts, rarity=rarity, bridge=return_bridge,
                method="classical MDS on Jaccard distance between requirement profiles; the candidate is placed with the same distance using evidence grade 2–3; peers at the mean position of their 5 nearest postings")


def formula_errors(niches, ledger):
    """Gate on golden formulas: each cites a real bundle of its niche and real resume lines, and its example states no
    number those lines do not contain."""
    import re as _re
    L = {l["id"]: l["text"] for l in ledger}; errs = []
    for n in niches:
        pairs = {frozenset((b["a"], b["b"])) for b in n["demand"]["bundles"]}
        for i, f in enumerate(n.get("formulas", [])):
            if frozenset(f["bundle"]) not in pairs: errs.append(f"{n['id']} formula {i}: bundle {f['bundle']} is not a bundle of this niche")
            miss = [x for x in f["ledger_ids"] if x not in L]
            if miss: errs.append(f"{n['id']} formula {i}: unknown ledger ids {miss}")
            src = " ".join(L.get(x, "") for x in f["ledger_ids"]).replace(",", "")
            for num in _re.findall(r"\d+(?:\.\d+)?", f["example"].replace(",", "")):
                if num not in _re.findall(r"\d+(?:\.\d+)?", src): errs.append(f"{n['id']} formula {i}: '{num}' is not in the cited lines")
    return errs


def zone_text(r):
    """The six-second zone: headline, profile and the first role's first three bullets."""
    ex = r["experience"][0]["bullets"][:3] if r.get("experience") else []
    return "\n".join([r["header"]["headline"], r.get("profile") or ""] + [b["text"] for b in ex])


def zone_coverage(run, results):
    """Must-haves visible in the six-second zone and in the whole text, original against the niche's version (cycle 4)."""
    import re as _re
    from gates import all_text
    ev = load(run / "evidence.json"); base = load(run / "baseline.json")["resume"]; nmods = {n["id"]: n["module"] for n in load(run / "niches.json")["niches"]}
    out = {}
    for n in results["niches"]:
        an = load(run / "niches" / n["id"] / "analysis.json"); _, byid = codebook([nmods[n["id"]]], run)
        top = [k for k in an["top_required"] if k in byid and ev.get(k, {}).get("grade", 0) >= 2][:10]
        cov = lambda t: sum(1 for k in top if any(_re.search(rx, t, _re.I) for rx in byid[k].get("resume_cues", [])))
        new = next((r for r in results["resumes"] if r["niche_id"] == n["id"]), None)
        out[n["id"]] = dict(total=len(top), original=dict(zone=cov(zone_text(base)), whole=cov(all_text(base, extra=True))),
                            rewritten=dict(zone=cov(zone_text(new)), whole=cov(all_text(new, extra=True))) if new else None)
    results["baseline"]["zone_coverage"] = out


def act2_extras(run, results):
    """Contrasts, title shift, pooled trend, pay ranges and the sample achieved (cycle 5; plan §5.2)."""
    th, relaxed = thresholds(run)
    allp = [p for p in load(run / "postings" / "postings.jsonl")]
    order = [n["id"] for n in results["niches"]]
    now = [p for p in allp if p["era"] == "now" and (p.get("liveness") or {}).get("band") != "likely_ghost" and any(i in order for i in p["niche_ids"])]
    then = [p for p in allp if p["era"] != "now" and any(i in order for i in p["niche_ids"])]
    labels = {}
    for n in results["niches"]:
        for r in n["demand"]["rows"]: labels.setdefault(r["code"], r["label"])
    codes = sorted({k for p in now + then for k, v in (p.get("codes") or {}).items()})
    by = {nid: [p for p in now if nid in p["niche_ids"]] for nid in order}
    for n in results["niches"]:
        others = sorted([o for o in order if o != n["id"]], key=lambda o: -len(by[o]))
        n["demand"]["contrasts"] = dict(seniority=CT.seniority(by[n["id"]], now, codes, labels), versus=CT.versus(n["id"], others[0] if others else None, by, codes, labels))
        if n.get("pay"): n["pay"]["ranges"] = CT.pay_ranges(by[n["id"]], n["size"]["currency"])
    if results.get("market") is not None:
        results["market"]["title_shift"] = CT.title_shift([p["title"] for p in then], [p["title"] for p in now]) if len(then) >= th["archive_n"] else []
        results["market"]["change"] = dict(n_then=len(then), n_now=len(now), rows=CT.pooled_change(then, now, codes, labels)) if len(then) >= th["archive_n"] else None
    results["method"]["sample"] = [dict(niche_id=n["id"], planned=th["stats_n"], achieved=len(by[n["id"]]), archive_planned=th["archive_n"],
                                        archive_achieved=sum(1 for p in then if n["id"] in p["niche_ids"]),
                                        reason="relaxed thresholds: example corpus" if relaxed else None) for n in results["niches"]]


def bridge_links(ev, rarity, label, strengths=None):
    """The bridge: each strength on the record, linked to the requirements it proves (codes graded 2–3 whose evidence
    shares a resume line with the strength). Filled with the strengths in assemble(); reads_as defaults to the
    requirement as employers phrase it and can be overridden in narrative.json → bridge_reads_as.{code}."""
    if strengths is None: return []
    asked = {r["code"]: r["asked_share"] for r in rarity}
    out = []
    for i, s in enumerate(strengths):
        lines = set(s.get("evidence") or [])
        codes = [k for k, v in ev.items() if v.get("grade", 0) >= 2 and lines & set(v.get("evidence") or []) and k in asked]
        for k in sorted(codes, key=lambda k: -asked[k])[:3]:
            out.append(dict(strength_id=f"s{i + 1}", asset=s["label"], code=k, reads_as=label.get(k, k), asked_share=asked[k],
                            ledger_ids=sorted(lines & set(ev[k].get("evidence") or []))))
    return out


RANK = {"high": 3, "medium": 2, "low": 1}


def build_actions(res):
    """One ranked checklist from every source of advice. Impact/effort rules:
    fixes → high impact; fix-ladder steps → impact by coverage gain, effort by surface (low) vs build (high);
    failed or warned gates → high/medium; blanks to fill → high impact, low effort; every do_this → medium/medium."""
    import re as _re
    acts, seen = [], set()
    def add(text, impact, effort, section, niche=None):
        key = _re.sub(r"\W+", " ", text.lower()).strip()
        if not text or key in seen: return
        seen.add(key); acts.append(dict(text=text, impact=impact, effort=effort, section=section, niche_id=niche))
    S = res["summary"]
    for f in S["fixes"]: add(f["text"], "high", "medium" if "[" in f["text"] else "low", "summary")
    blanks = [c for c in res["confirm"] if c["item"].startswith("Fill [")]
    if blanks: add(f"Fill the {len(blanks)} blanks the resume versions leave open (numbers and context only you know).", "high", "low", "confirm")
    for n in res["niches"]:
        for st in n["fix_ladder"]["steps"][:3]:
            if st["coverage_gain"] <= 0 and st["fit_gain"] <= 0: continue
            imp = "high" if st["coverage_gain"] >= 0.08 else "medium" if st["coverage_gain"] >= 0.04 or st["fit_gain"] >= 0.04 else "low"
            verb = "Surface evidence of" if st["kind"] == "surface" else "Build evidence of"
            add(f"{verb} '{st['label']}' for {n['label']} (+{round(st['coverage_gain']*100)} pts coverage).", imp, "low" if st["kind"] == "surface" else "high", "fit", n["id"])
    for g in res["gates"]:
        if g["status"] in ("fail", "warn") and g["name"] not in ("placeholders", "reviewer_panel"):
            add(f"Fix the '{g['name'].replace('_', ' ')}' check: {g['detail']}", "high" if g["status"] == "fail" else "medium", "medium", "gates")
    for x in res.get("gates_linkedin", []):
        if x["status"] == "fail": add(f"LinkedIn: {x['detail']}", "high", "low", "linkedin")
    add("Paste the LinkedIn rewrite: headline, About, experience descriptions, pinned skills.", "high", "low", "linkedin")
    for sec in ("summary", "profile_view", "portfolio", "funnel"):
        for d in res[sec].get("do_this", []): add(d, "medium", "medium", sec)
    for n in res["niches"]:
        for sec in ("demand", "change", "language", "fit", "employers", "access", "pitch", "pay"):
            if n.get(sec):
                for d in n[sec].get("do_this", []): add(d, "medium", "medium", sec, n["id"])
    acts.sort(key=lambda a: -(RANK[a["impact"]] * 2 - RANK[a["effort"]]))
    for k, a in enumerate(acts): a["id"] = f"a{k + 1:03d}"
    return acts


def need(d, key, where):
    if key not in d: sys.exit(f"narrative.json missing {where}.{key}")
    return d[key]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); a = ap.parse_args(); run = Path(a.run)
    cfg = load(run / "run_config.json"); prof = load(run / "profile.json"); nar = load(run / "narrative.json")
    rk = load(run / "ranking.json"); doc = load(run / "niches.json"); parse = load(run / "parse_report.json")
    ledger = load(run / "ledger.json")["lines"]; resumes = load(run / "resumes.json")
    gates = load(run / "gates.json") if (run / "gates.json").exists() else dict(summary=[])
    th, relaxed = thresholds(run)
    N = {n["id"]: n for n in doc["niches"]}
    niches_out = []
    for r in rk["niches"]:
        i = r["id"]; an = load(run / "niches" / i / "analysis.json"); fit = load(run / "niches" / i / "fit.json")
        emp = load(run / "niches" / i / "employers.json"); accf = run / "niches" / i / "access.json"
        acc = load(accf) if accf.exists() else []
        pf = run / "niches" / i / "peers.json"; peers = load(pf) if pf.exists() else dict(hidden="peer search not run")
        tn = need(nar["niches"], i, "niches")
        hidden = {}
        change = None
        if an.get("change"):
            change = dict(eras=an["change"]["eras"], rows=an["change"]["rows"], codes_per_posting=an["change"]["codes_per_posting"],
                          years_then=an["change"]["years_then"], years_now=an["years"]["median"], **need(tn, "change", i))
        else:
            hidden["change"] = an.get("change_hidden_reason", "no archive postings")
        peers_sec = None
        if "hidden" in peers: hidden["peers"] = peers["hidden"]
        else: peers_sec = dict(**peers, **need(tn, "peers", i))
        pay_sec = None
        if an["pay"].get("median"):
            pay_sec = dict(band=an["pay"], **need(tn, "pay", i))
        else:
            hidden["pay"] = an["pay"].get("note", "no posted pay ranges")
        acc_sec = dict(paths=acc, **need(tn, "access", i)) if acc else None
        if not acc: hidden["access"] = "no public access path found"
        resume_id = next((x["id"] for x in resumes if x["niche_id"] == i), None)
        if not resume_id: sys.exit(f"no resume for niche {i}")
        niches_out.append(dict(
            id=i, label=N[i]["label"], verdict=r["verdict"], rank=r["rank"], score=r["score"], components=r["components"], flags=r["flags"],
            confidence=an["confidence"], segment=N[i]["segment"], city=N[i]["city"], seniority=N[i]["seniority"],
            size=dict(n_postings=an["n_now"], n_live_weighted=an["n_live_weighted"], n_employers=an["n_employers"], n_archive=an["n_archive"],
                      liveness=an["liveness"], levels=an["levels"], pay_median=an["pay"].get("median"), currency=an["pay"].get("currency"),
                      peer_pool=None if "hidden" in peers else peers["n"]),
            demand=dict(rows=an["prevalence"], top_required=an["top_required"], bundles=an["bundles"], clusters=an["clusters"],
                        years=an["years"], builder=an["builder_index"], reliability=an["reliability"], **need(tn, "demand", i)),
            change=change, peers=peers_sec,
            language=dict(keyness=an["language"]["keyness"], contrast=an["language"]["contrast"], phrases=an["language"]["phrases"][:12], **need(tn, "language", i)),
            fit=dict(score=fit["fit"], coverage=fit["coverage"], rows=fit["rows"], gaps=[dict(**g, fix=tn["fit"].get("fixes", {}).get(g["code"], "")) for g in fit["gaps"]],
                     **{k: v for k, v in need(tn, "fit", i).items() if k != "fixes"}),
            employers=dict(rows=emp, **need(tn, "employers", i)), access=acc_sec,
            pitch=need(tn, "pitch", i), formulas=tn.get("formulas", []), pay=pay_sec, plan30=need(tn, "plan30", i), resume_id=resume_id, hidden_reason=hidden,
            fit_per_posting=load(run / "niches" / i / "fit_per_posting.json"), fix_ladder=load(run / "niches" / i / "fix_ladder.json"),
            liveness_summary=an["liveness_summary"]))
    seq = rk["sequence"]
    rejected = [dict(label=n["label"], reason=n["reason"], verdict=n["verdict"]) for n in doc["niches"] if n["verdict"] in ("reject", "merge", "not_screened")]
    qual_rej = [dict(label=N[i]["label"], reason="qualification: coverage below 0.40 or blocker", verdict="Rejected") for i, v in load(run / "qualification.json").items() if v["verdict"] == "Rejected"]
    G = {"stated": "stated", "inferred2": "inferred2", "inferred1": "inferred1", "absent": "absent"}
    fields = [dict(name=k, value=fmt_val(v["value"]), grade=v["grade"], evidence=v["evidence"])
              for k, v in prof["fields"].items()]
    confirm = []
    for k, v in list(prof["fields"].items()) + list(prof["revealed_preferences"].items()):
        if v["grade"] in ("inferred1", "absent"):
            confirm.append(dict(item=f"{k.replace('_', ' ')}: {v['value'] if v['value'] not in (None, '') else '—'}", why=f"{v['grade']}: " + (v.get("note") or "one line of evidence or none")))
    for d in prof.get("disclosure_risks", []):
        confirm.append(dict(item=f"Line {d['line']}: {d['type'].replace('_', ' ')}", why=f"defaulted to '{d['action']}' (rubric 21)"))
    import re as _re
    texts = [t for x in resumes for t in ([x["header"]["headline"], x["profile"]] + [(e.get("context") or "") for e in x["experience"]]
                                          + [(e.get("scope") or "") for e in x["experience"]] + [b["text"] for e in x["experience"] for b in e["bullets"]])]
    phs = sorted({p for t in texts for p in _re.findall(r"\[[^\]]+\]", t)})
    for p in phs: confirm.append(dict(item=f"Fill {p}", why="fact not in the resume or LinkedIn; left blank rather than estimated"))
    for iss in parse["issues"]:
        if iss["kind"] in ("unfilled_placeholder", "overlapping_roles", "resume_linkedin_conflict"):
            confirm.append(dict(item=f"{iss['kind'].replace('_', ' ')} {iss.get('line') or ''}: {iss['detail']}", why="found in the source documents"))
    confirm += nar.get("confirm_extra", [])
    orig_lines = [l for l in ledger if l["source"] == "resume"]
    results = dict(
        meta=dict(candidate=prof["candidate"]["display_name"], generated=dt.date.today().isoformat(), skill_version=cfg.get("skill_version", "0.1.0"),
                  fictional=cfg.get("fictional", False), data_window=cfg.get("data_window", ""), banner=cfg.get("banner"),
                  relaxed_thresholds=relaxed, thresholds=th, linkedin_status=prof["candidate"].get("linkedin_status", "absent")),
        summary=need(nar, "summary", "root"),
        profile_view=dict(fields=fields, strengths=prof["strengths"], edges=prof["edges"], parse=dict(score=parse["score"], method=parse["method"], two_column_ratio=parse["two_column_ratio"], issues=parse["issues"]),
                          positioning=prof["fields"].get("positioning", {}).get("value"), timeline=build_timeline(ledger, resumes), **need(nar, "profile_view", "root")),
        portfolio=dict(niches=[dict(id=n["id"], label=n["label"], verdict=n["verdict"], score=n["score"], rank=n["rank"], components=n["components"],
                                    fit=n["fit"]["score"], pay_median=n["size"]["pay_median"], currency=n["size"]["currency"], demand=n["size"]["n_live_weighted"],
                                    n_postings=n["size"]["n_postings"], confidence=n["confidence"], flags=n["flags"]) for n in niches_out],
                       weights=rk["weights"], sensitivity=dict(rank_freq=rk["sensitivity"]["rank_freq"], p_top3=rk["sensitivity"]["p_top3"], stable=rk["sensitivity"]["stable"], same_top3_share=rk["sensitivity"]["same_top3_share"], draws=rk["sensitivity"]["draws"]),
                       overlap=rk["overlap"], sequence=seq, rejected=rejected + qual_rej, **need(nar, "portfolio", "root")),
        niches=niches_out, resumes=resumes,
        original=dict(headline=next((l["text"] for l in orig_lines[1:4] if l["claim_type"] == "header"), ""), bullets=[l["text"] for l in orig_lines if l["claim_type"] in ("metric", "duty") and l.get("employer")],
                      ledger_ids=[l["id"] for l in orig_lines if l["claim_type"] in ("metric", "duty") and l.get("employer")]),
        gates=gates["summary"],
        funnel=dict(benchmarks=FUNNEL_BENCH, diagnosis=DIAG, **nar.get("funnel", dict(do_this=["Log every approach in the tracker: niche, employer, channel, date, outcome. Review weekly against the diagnosis table."]))),
        method=dict(steps=nar.get("method_steps", []), limits=nar.get("limits", []), sources=nar.get("sources", []),
                    n_postings=sum(n["size"]["n_postings"] for n in niches_out), n_archive=sum(n["size"]["n_archive"] for n in niches_out)),
        confirm=confirm)
    results["journey"] = need(nar, "journey", "root")
    results["plan12"] = need(nar, "plan12", "root")
    results["market"] = market_block(run, niches_out, load(run / "evidence.json"))
    act2_extras(run, results)
    if results["market"]:
        ev = load(run / "evidence.json"); lab = {r["code"]: r["label"] for r in results["market"]["rarity"]}
        br = bridge_links(ev, results["market"]["rarity"], lab, results["profile_view"]["strengths"])
        for b in br: b["reads_as"] = nar.get("bridge_reads_as", {}).get(b["code"], b["reads_as"])
        results["market"]["bridge"] = br
    for r in results["resumes"]:
        rv = run / "reviews" / f"{r['id']}.json"; bp = run / "reviews" / f"blind-{r['niche_id']}.panel.json"
        rounds = load(rv).get("panel", {}) if rv.exists() else {}
        panel = load(bp) if bp.exists() else None
        r["review"] = dict(panel=panel["panel"] if panel else [], independent=panel["independent"] if panel else None, note=panel.get("note", "") if panel else "",
                           rounds=[dict(reader=k, verdict=str(v)) for k, v in rounds.items()])
    fe = formula_errors(results["niches"], ledger)
    if fe: sys.exit("formula gate failed:\n  " + "\n  ".join(fe))
    results["baseline"] = load(run / "baseline.json")
    zone_coverage(run, results)
    results["linkedin"] = load(run / "linkedin.json")
    results["gates_linkedin"] = gates.get("linkedin", [])
    results["gates_per_resume"] = gates.get("per_resume", {})
    results["actions"] = build_actions(results)
    est = prof["fields"]["current_pay_band_est"]["value"]
    results["meta"]["candidate_pay_est"] = est if isinstance(est, dict) else None
    results["meta"]["candidate_years"] = prof["fields"]["years_experience"]["value"]
    errs = validate(results, "results")
    save(run / "results.json", results)
    if errs:
        print("results.json schema errors:", *errs[:20], sep="\n  "); sys.exit(1)
    print(f"results.json ok: {len(niches_out)} niches, {len(resumes)} resumes, {len(confirm)} items to confirm")


if __name__ == "__main__":
    main()
