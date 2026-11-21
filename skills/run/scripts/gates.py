#!/usr/bin/env python3
"""Phase 9 — deterministic quality gates on every niche resume (rubrics 16–21 + Bock rules).

usage: gates.py --run RUN [--pdf]
Reads  resumes.json, ledger.json, profile.json, resume.txt, niches/<id>/analysis.json, reviews/<resume_id>.json (agent)
Writes gates.json  → {"per_resume": {id: [gate...]}, "summary": [gate...]}
Exit code 1 if any gate fails (the agent must fix and re-run; max 3 loops, then report the failure).
"""
import argparse, re, statistics, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save, numbers_in, codebook, HEADERS
import render_resume

STOCK = [l.strip().lower() for l in (Path(__file__).parent / "stock_phrases.txt").read_text().splitlines() if l.strip()]
WEAK_START = {"responsible", "helped", "worked", "assisted", "involved", "participated", "tasked", "duties"}
PH = re.compile(r"\[[^\]]+\]")


def norm_num(s):
    return re.sub(r"[\s,]", "", s.lower()).rstrip(".")


def all_text(r, extra=False):
    parts = [r["header"]["headline"], r["profile"]] + [b["text"] for e in r["experience"] for b in e["bullets"]]
    if extra:
        parts += [x for e in r["experience"] for x in ((e.get("context") or ""), (e.get("scope") or ""))] + list(r.get("skills", []))
    return "\n".join(parts)


def g(name, status, detail, **kw): return dict(name=name, status=status, detail=detail, **kw)


def check(r, ledger, prof, orig, run, versions, pdf):
    L = {l["id"]: l for l in ledger}
    out = []
    # 1 traceability
    bad, missing_ids = [], []
    led_nums_all = {norm_num(n) for l in ledger for n in l["numbers"]}
    for e in r["experience"]:
        for b in e["bullets"]:
            if not b["ledger"]: missing_ids.append(b["text"][:50]); continue
            unknown = [i for i in b["ledger"] if i not in L]
            if unknown: missing_ids.append(f"unknown ids {unknown}")
            src_nums = {norm_num(n) for i in b["ledger"] if i in L for n in L[i]["numbers"]}
            for n in numbers_in(PH.sub("", b["text"])):
                if re.search(r"\d", n) and norm_num(n) not in src_nums:
                    bad.append(f"'{n}' in: {b['text'][:60]}")
    tops = r["header"]["headline"] + " " + r["profile"] + " " + " ".join((e.get("scope") or "") + " " + (e.get("context") or "") for e in r["experience"])
    for n in numbers_in(PH.sub("", tops)):
        if re.search(r"\d", n) and norm_num(n) not in led_nums_all:
            bad.append(f"'{n}' in headline/profile/scope/context")
    out.append(g("traceability", "fail" if bad or missing_ids else "pass",
                 "every number and bullet resolves to a ledger line" if not (bad or missing_ids) else "; ".join((bad + missing_ids)[:6])))
    # 2 consistency across versions
    inc = []
    for other in versions:
        if other["id"] == r["id"]: continue
        om = {e["employer"]: e for e in other["experience"]}
        for e in r["experience"]:
            o = om.get(e["employer"])
            if o and (o["title"] != e["title"] or o["dates"] != e["dates"]):
                inc.append(f"{e['employer']}: '{e['title']} {e['dates']}' vs '{o['title']} {o['dates']}' in {other['id']}")
    out.append(g("consistency", "fail" if inc else "pass", "titles and dates identical across versions" if not inc else "; ".join(inc[:4])))
    # 3 authenticity
    txt = all_text(r).lower()
    head = (r["header"]["headline"] + " " + r["profile"]).lower()
    stock_all = [s for s in STOCK if re.search(r"\b" + re.escape(s) + r"\b", txt)]
    stock_head = [s for s in STOCK if re.search(r"\b" + re.escape(s) + r"\b", head)]
    bullets = [b["text"] for e in r["experience"] for b in e["bullets"]]
    starts = [re.findall(r"[A-Za-z]+", b)[0].lower() for b in bullets if re.findall(r"[A-Za-z]+", b)]
    rep = [w for w in set(starts) if starts.count(w) > 2]
    sd = statistics.pstdev([len(b.split()) for b in bullets]) if len(bullets) > 2 else 99
    probs = ([f"stock phrases {stock_all}"] if len(stock_all) >= 2 or stock_head else []) + ([f"verb repeated >2: {rep}"] if rep else []) + ([f"uniform bullet length (sd {sd:.1f})"] if sd < 3 else [])
    out.append(g("authenticity", "fail" if probs else "pass", "; ".join(probs) or f"no stock phrases in headline/profile, bullet length sd {sd:.1f}"))
    # 4 bullet score (rubric 17, heuristic; reviewers refine)
    scores = []
    for b in bullets:
        w = re.findall(r"[A-Za-z]+", b); s = 0
        s += 1 if w and w[0].lower() not in WEAK_START else 0
        s += 1 if re.search(r"\d", PH.sub("", b)) else (0.5 if PH.search(b) else 0)
        s += 1 if re.search(r"\b(by|through|via|using|with|across|after)\b", b, re.I) else 0
        s += 1 if len(b.split()) >= 12 else 0
        s += 1 if re.search(r"\b(of|for|across|in)\b .*\b(market|team|partners?|clients?|countries|regions?|org|revenue|users|creators)\b", b, re.I) else 0
        scores.append(s)
    avg = sum(scores) / len(scores) if scores else 0
    out.append(g("bullet_score", "pass" if avg >= 4 and min(scores) >= 3 else "warn", f"average {avg:.1f}/5, min {min(scores) if scores else 0}/5 (target ≥4.0, none <3)", value=round(avg, 2)))
    # 5 keyword coverage before/after on the niche's top required codes
    an = load(run / "niches" / r["niche_id"] / "analysis.json")
    niche = next(n for n in load(run / "niches.json")["niches"] if n["id"] == r["niche_id"])
    _, byid = codebook([niche["module"]], run)
    ev = load(run / "evidence.json")
    top = [k for k in an["top_required"] if k in byid and ev.get(k, {}).get("grade", 0) >= 2][:10]   # only what the candidate can prove
    def cov(text): return sum(1 for k in top if any(re.search(rx, text, re.I) for rx in byid[k].get("resume_cues", [])))
    before, after = cov(orig), cov(all_text(r, extra=True))
    missing = [k for k in top if not any(re.search(rx, all_text(r, extra=True), re.I) for rx in byid[k].get("resume_cues", []))]
    out.append(g("keyword_coverage", "pass" if after >= before and after >= 0.8 * len(top) else "warn",
                 f"{after}/{len(top)} provable top-required codes visible (original resume: {before}/{len(top)})" + (f"; missing {missing}" if missing else ""),
                 before=before, after=after, total=len(top)))
    # 6 six-second zone
    first = r["experience"][0] if r["experience"] else {"title": "", "bullets": []}
    zone = " ".join([r["header"]["headline"], r["profile"], first["title"]] + [b["text"] for b in first["bullets"][:2]])
    words = [w for w in re.findall(r"[a-z]+", niche["label"].lower()) if len(w) > 3 and w not in ("head", "senior", "york", "paris", "london")]
    hits = [w for w in words if w in zone.lower()]
    has_num = bool(re.search(r"\d", PH.sub("", zone)))
    out.append(g("six_second_zone", "pass" if hits and has_num else "fail", f"niche words in top third: {hits or 'none'}; proof number: {'yes' if has_num else 'no'}"))
    # 7 length
    yrs = prof["fields"]["years_experience"]["value"] or 10
    words_n = len(all_text(r).split()) + 60 * len(r["experience"])
    pages = words_n / 560; limit = max(1, min(2, round(yrs / 10 + 0.49)))
    out.append(g("length", "pass" if pages <= limit + 0.15 else "fail", f"~{pages:.1f} pages estimated; limit {limit} (1 page per 10 years, max 2)"))
    # 8 disclosure
    leaks = []
    for d in prof.get("disclosure_risks", []):
        if d["action"] in ("remove", "generalize") and d["line"] in L:
            frag = L[d["line"]]["text"][:40].lower()
            if frag and frag in txt: leaks.append(d["line"])
        for nm in d.get("names", []):
            if nm.lower() in txt: leaks.append(nm)
    out.append(g("disclosure", "fail" if leaks else "pass", "no flagged line or name reused" if not leaks else f"flagged content reused: {leaks}"))
    # 9 placeholders
    ph = PH.findall(all_text(r, extra=True))
    out.append(g("placeholders", "warn" if ph else "pass", f"{len(ph)} placeholders for the candidate to fill: {sorted(set(ph))[:6]}" if ph else "none", count=len(ph)))
    # 10 ATS parse on the rendered PDF
    if pdf:
        o = run / "out"; o.mkdir(exist_ok=True)
        hp = o / f"resume-{r['id']}.html"; hp.write_text(render_resume.to_html(r)); pp = o / f"resume-{r['id']}.pdf"
        if render_resume.to_pdf(hp, pp):
            t = subprocess.run(["pdftotext", str(pp), "-"], capture_output=True, text=True).stdout
            pages_real = t.count("\f")
            tl = re.sub(r"\s+", " ", t).lower()
            def hdr(x):
                m = re.search(rf"^\s*{x}\s*$", t, re.I | re.M)
                return m.start() if m else -1
            Lh = HEADERS.get(r.get("language", "en"), HEADERS["en"])
            order = [hdr(re.escape(Lh[x])) for x in ("profile", "experience", "education")]
            firsts = [tl.find(re.sub(r"\s+", " ", e["bullets"][0]["text"][:22]).lower()) for e in r["experience"]]
            ok = all(x >= 0 for x in order) and order == sorted(order) and all(x >= 0 for x in firsts) and firsts == sorted(firsts)
            out.append(g("ats_parse", "pass" if ok else "fail", f"PDF text extracts in reading order; {pages_real} page(s)" if ok else "section or bullet order broken in extracted PDF text"))
            out[6] = g("length", "pass" if pages_real <= limit else "fail", f"{pages_real} rendered page(s); limit {limit}")
        else:
            out.append(g("ats_parse", "not_run", "no headless Chrome/Chromium available"))
    else:
        out.append(g("ats_parse", "not_run", "run with --pdf"))
    # 11–12 agent-run gates (advocate test, reviewer panel)
    rv = run / "reviews" / f"{r['id']}.json"
    if rv.exists():
        R = load(rv)
        out.append(g("advocate_test", R["advocate"]["status"], R["advocate"]["sentence"]))
        ind = R.get("independent", True)
        out.append(g("reviewer_panel", "pass" if R["panel"]["ceo"] == "Good job" and ind else "warn",
                     f"loops {R['panel']['loops']}; recruiter {R['panel'].get('recruiter')}; hiring manager {R['panel'].get('hiring_manager')}; CEO '{R['panel']['ceo']}'"
                     + ("" if ind else "; reviews run inline, not independent (no subagents available)")))
    else:
        out.append(g("advocate_test", "not_run", "reviews/<id>.json missing"))
        out.append(g("reviewer_panel", "not_run", "reviews/<id>.json missing"))
    return out


def check_linkedin(li, ledger, resumes):
    import yaml
    lim = yaml.safe_load((Path(__file__).resolve().parents[1] / "rulebook" / "linkedin_limits.yml").read_text())
    out, over = [], []
    if len(li["headline"]) > lim["headline"]: over.append(f"headline {len(li['headline'])}/{lim['headline']}")
    if len(li["about"]) > lim["about"]: over.append(f"about {len(li['about'])}/{lim['about']}")
    for e in li["experience"]:
        if len(e["title"]) > lim["experience_title"]: over.append(f"title '{e['title'][:30]}'")
        if len(e["description"]) > lim["experience_description"]: over.append(f"{e['employer']} description {len(e['description'])}/{lim['experience_description']}")
    over += [f"skill '{k[:30]}'" for k in li["skills"] if len(k) > lim["skill"]]
    if li.get("connection_note") and len(li["connection_note"]) > lim["connection_note"]: over.append("connection note")
    for a in li.get("alternates", []):
        if len(a["headline"]) > lim["headline"]: over.append(f"alternate headline {a['niche_id']}")
    out.append(g("li_limits", "fail" if over else "pass", "; ".join(over) or "every field within LinkedIn limits"))
    # consistency with resumes: same employer → same title and dates
    roles = {(e["employer"]): (e["title"], e["dates"]) for r in resumes for e in r["experience"]}
    drift = [f"{e['employer']}: '{e['title']} {e['dates']}' vs resume '{' '.join(roles[e['employer']])}'" for e in li["experience"]
             if e["employer"] in roles and (e["title"], e["dates"]) != roles[e["employer"]]]
    missing = [e["employer"] for e in li["experience"] if e["employer"] not in roles]
    out.append(g("li_consistency", "fail" if drift or missing else "pass", "; ".join(drift + [f"{m} not in any resume" for m in missing]) or "titles and dates match every resume version"))
    led = {norm_num(n) for l in ledger for n in l["numbers"]}
    bad = [n for t in [li["headline"], li["about"]] + [e["description"] for e in li["experience"]] for n in numbers_in(PH.sub("", t)) if re.search(r"\d", n) and norm_num(n) not in led]
    out.append(g("li_traceability", "fail" if bad else "pass", f"numbers not in the ledger: {sorted(set(bad))}" if bad else "every number resolves to a ledger line"))
    txt = (li["headline"] + " " + li["about"] + " " + " ".join(e["description"] for e in li["experience"])).lower()
    st = [x for x in STOCK if re.search(r"\b" + re.escape(x) + r"\b", txt)]
    out.append(g("li_authenticity", "fail" if st else "pass", f"stock phrases {st}" if st else "no stock phrases"))
    hook = li["about"][:lim["about_visible"]]
    ok = bool(re.search(r"\d", hook)) and len(set(re.findall(r"[a-z]{5,}", hook.lower()))) >= 8
    out.append(g("li_hook", "pass" if ok else "fail", f"first {lim['about_visible']} characters " + ("carry a proof number and the core message" if ok else "lack a proof number or say too little")))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); ap.add_argument("--pdf", action="store_true"); ap.add_argument("--linkedin", action="store_true")
    a = ap.parse_args(); run = Path(a.run)
    if a.linkedin:
        li = load(run / "linkedin.json")
        res = check_linkedin(li, load(run / "ledger.json")["lines"], load(run / "resumes.json"))
        prev = load(run / "gates.json") if (run / "gates.json").exists() else {}
        prev["linkedin"] = res; save(run / "gates.json", prev)
        for x in res: print(f"{x['status']:8s} {x['name']:16s} {x['detail'][:100]}")
        sys.exit(1 if any(x["status"] == "fail" for x in res) else 0)
    resumes = load(run / "resumes.json"); ledger = load(run / "ledger.json")["lines"]; prof = load(run / "profile.json")
    orig = (run / "resume.txt").read_text()
    per = {r["id"]: check(r, ledger, prof, orig, run, resumes, a.pdf) for r in resumes}
    order = [x["name"] for x in next(iter(per.values()))]
    rank = dict(fail=3, warn=2, not_run=1, pass_=0)
    summary = []
    for nm in order:
        gs = [next(x for x in per[i] if x["name"] == nm) for i in per]
        worst = max(gs, key=lambda x: rank.get(x["status"] if x["status"] != "pass" else "pass_", 0))
        detail = worst["detail"] if worst["status"] != "pass" else gs[0]["detail"]
        if nm == "keyword_coverage":
            detail = "; ".join(f"{i}: {x['after']}/{x['total']} (original {x['before']})" for i, x in zip(per, gs))
        if nm == "placeholders":
            detail = f"{sum(x.get('count', 0) for x in gs)} placeholders across {len(gs)} versions"
        summary.append(dict(name=nm, status=worst["status"], detail=detail))
    prev = load(run / "gates.json") if (run / "gates.json").exists() else {}
    save(run / "gates.json", dict(per_resume=per, summary=summary, **({"linkedin": prev["linkedin"]} if "linkedin" in prev else {})))
    for s in summary: print(f"{s['status']:8s} {s['name']:18s} {s['detail'][:110]}")
    sys.exit(1 if any(s["status"] == "fail" for s in summary) else 0)


if __name__ == "__main__":
    main()
