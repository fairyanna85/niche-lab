#!/usr/bin/env python3
"""Phase 3 — posting store, liveness scoring, second-coder sampling, merging coder output.

Layout inside a run:
  postings/raw/<sha256>.txt     full posting text (never edited)
  postings/postings.jsonl       one coded record per posting (schemas/posting.schema.json)
  postings/second.jsonl         coder-B codes for the reliability sample

Subcommands
  store   --run R --text-file F --meta '{"niche_ids":["n01"],"company":..,"title":..,"city":..,"url":..,"source_type":..,"era":"now","date_evidence":..}'
          → writes raw text, prints id; refuses texts under 120 words (rubric 06)
  code    --run R --id ID --codes-json FILE   merge coder-A JSON (prompts/code-posting.md output) into the record
  liveness --run R --today YYYY-MM-DD        score every 'now' posting (rubric 08)
  sample  --run R [--share 0.2 --min 8 --seed 7]  list ids for the blind second coder
  validate --run R
  import-reference --run R --niche-map JSON  convert reference/partnerships-2026 into postings.jsonl (raw_retained=false)
"""
import argparse, datetime as dt, json, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save, sha256, validate, REPO, die

EVERGREEN = re.compile(r"talent (pool|community|network)|future opportunit|always (accepting|looking)|general application|expression of interest", re.I)
PAY_LAW = re.compile(r"new york|nyc|california|\bca\b|colorado|washington|illinois|paris|france|berlin|madrid|amsterdam|dublin|\beu\b", re.I)


def P(run): return Path(run) / "postings"


def records(run):
    f = P(run) / "postings.jsonl"
    return load(f) if f.exists() else []


def cmd_store(a):
    text = Path(a.text_file).read_text(errors="replace")
    if len(text.split()) < 120:
        die(f"posting text has {len(text.split())} words (<120): excluded by rubric 06")
    meta = json.loads(a.meta)
    h = sha256(text)
    raw = P(a.run) / "raw"; raw.mkdir(parents=True, exist_ok=True)
    (raw / f"{h}.txt").write_text(text)
    recs = records(a.run)
    norm = lambda s: re.sub(r"\W+", " ", s.lower()).strip()
    for r in recs:  # dedupe: same company + normalized title + city (rubric 06)
        if norm(r["company"]) == norm(meta["company"]) and norm(r["title"]) == norm(meta["title"]) and r["city"] == meta["city"] and r["era"] == meta.get("era", "now"):
            pri = ["employer", "ats", "aggregator", "agency", "archive"]
            if pri.index(meta["source_type"]) < pri.index(r["source_type"]):
                r.update(url=meta["url"], source_type=meta["source_type"], text_sha256=h)
            r["niche_ids"] = sorted(set(r["niche_ids"]) | set(meta["niche_ids"]))
            r["reposts"] = r.get("reposts", 0) + (1 if meta.get("reposted") else 0)
            save(P(a.run) / "postings.jsonl", recs); print(r["id"], "(duplicate merged)"); return
    rid = f"p{len(recs) + 1:04d}"
    rec = dict(id=rid, niche_ids=meta["niche_ids"], company=meta["company"], title=meta["title"], city=meta["city"],
               level=meta.get("level", "Dir"), segment=meta.get("segment"), url=meta["url"], source_type=meta["source_type"],
               era=meta.get("era", "now"), date_posted=meta.get("date_posted"), date_seen=meta.get("date_seen"),
               date_evidence=meta.get("date_evidence", ""), reposts=meta.get("reposts", 0), removed=meta.get("removed", False),
               text_sha256=h, pay=None, years_required=None, codes={}, must_haves=[], phrases=[], builder_verbs=0,
               maintain_verbs=0, coder="A", liveness=None, raw_retained=True)
    recs.append(rec); save(P(a.run) / "postings.jsonl", recs); print(rid)


def cmd_code(a):
    recs = records(a.run); c = load(a.codes_json)
    for r in recs:
        if r["id"] == a.id:
            for k in ("pay", "years_required", "codes", "must_haves", "phrases", "builder_verbs", "maintain_verbs", "level"):
                if k in c: r[k] = c[k]
            if c.get("salary_min") is not None or c.get("salary_max") is not None:
                r["pay"] = dict(min=c.get("salary_min"), max=c.get("salary_max"), currency=c.get("currency"), unit=c.get("pay_unit", "year"))
            if r.get("pay") and r["pay"].get("unit") not in (None, "year") and not r["pay"].get("annualized"):
                from pay import annualize
                u = r["pay"]["unit"]
                r["pay"].update(min=annualize(r["pay"]["min"], u) if r["pay"].get("min") else None,
                                max=annualize(r["pay"]["max"], u) if r["pay"].get("max") else None, annualized=True)
            if r.get("level") not in (None, "") and c.get("title_band_override") is None:
                from ladder import band_for_title, LEGACY
                if r["level"] not in LEGACY: r["level"] = r["level"] if r["level"] in ("entry", "experienced", "lead", "manager", "director", "executive") else band_for_title(r["title"])
            save(P(a.run) / "postings.jsonl", recs); print("coded", a.id); return
    die(f"no posting {a.id}")


def liveness(r, today):
    if r["era"] != "now" or r.get("removed"):
        return dict(score=0, band="closed", flags=["archive" if r["era"] != "now" else "removed"])
    s, flags = 100, []
    seen = r.get("date_posted") or r.get("date_seen")
    if seen:
        age = (today - dt.date.fromisoformat(seen[:10])).days
        pen = 60 if age > 90 else 40 if age > 60 else 20 if age > 30 else 0
        if pen: s -= pen; flags.append(f"age {age}d")
    else:
        s -= 10; flags.append("no date")
    if r.get("reposts"): s -= min(30, 15 * r["reposts"]); flags.append(f"reposted x{r['reposts']}")
    if r["source_type"] == "aggregator": s -= 10; flags.append("aggregator only")
    if r["source_type"] == "agency" or "confidential" in r["company"].lower(): s -= 15; flags.append("agency/confidential")
    if PAY_LAW.search(r["city"]) and not (r.get("pay") and r["pay"].get("min")): s -= 10; flags.append("no pay where required")
    txt = ""
    if r.get("raw_retained", True):
        f = None
        for base in (Path(r.get("_run", ".")),):
            f = base / "postings" / "raw" / f"{r['text_sha256']}.txt"
        if f and f.exists(): txt = f.read_text()
    if txt and EVERGREEN.search(txt): s -= 30; flags.append("evergreen wording")
    if txt and len(txt.split()) < 150: s -= 10; flags.append("thin text")
    if r.get("layoff_news"): s -= 15; flags.append("layoff/freeze news")
    band = "live" if s >= 70 else "doubtful" if s >= 40 else "likely_ghost"
    return dict(score=max(0, s), band=band, flags=flags)


def cmd_liveness(a):
    today = dt.date.fromisoformat(a.today); recs = records(a.run)
    for r in recs:
        r["_run"] = a.run; r["liveness"] = liveness(r, today); r.pop("_run")
    save(P(a.run) / "postings.jsonl", recs)
    from collections import Counter
    print(Counter(r["liveness"]["band"] for r in recs))


def cmd_sample(a):
    recs = [r for r in records(a.run) if r["codes"]]
    k = max(a.min, round(len(recs) * a.share)); k = min(k, len(recs))
    ids = sorted(random.Random(a.seed).sample([r["id"] for r in recs], k))
    save(P(a.run) / "second_sample.json", ids); print(" ".join(ids))


def cmd_validate(a):
    bad = 0
    for r in records(a.run):
        errs = validate(r, "posting")
        if errs: bad += 1; print(r["id"], errs[:3])
    print("invalid records:", bad)
    if bad: sys.exit(1)


def cmd_import_reference(a):
    """Reference run → postings.jsonl. Raw text was not retained in the reference run; sha256 is of the coded summary."""
    sys.path.insert(0, str(REPO / "reference" / "partnerships-2026"))
    from data import R  # noqa
    from hist import H  # noqa
    rules = json.loads(a.niche_map)  # {"n01": {"city":["NYC"],"lvl":[..],"seg":[..]}, ...}
    out = []
    def niches_for(r):
        ids = []
        for nid, rule in rules.items():
            if all(r.get(k) in v for k, v in rule.items()): ids.append(nid)
        return ids
    city = {"NYC": "New York", "PAR": "Paris"}
    for era, rows in (("now", R), ("archive", H)):
        for r in rows:
            ids = niches_for(r)
            if not ids: continue
            summary = json.dumps(dict(co=r["co"], title=r["title"], must=r["must"], ph=r["ph"], url=r["url"]), sort_keys=True)
            e = "now" if era == "now" else r["era"]
            src = "archive" if era == "archive" else ("aggregator" if re.search(r"builtin|mediabistro|ziprecruiter|themuse|jobera|sonara|recruiter\.com|vaia|marketingmonk|edisonpartners|madrona|gusto", r["url"]) else "agency" if re.search(r"loxo|goodwin", r["url"]) else "employer")
            out.append(dict(id=f"p{len(out) + 1:04d}", niche_ids=ids, company=r["co"], title=r["title"], city=city.get(r["city"], r["city"]),
                            level=r["lvl"], segment=r["seg"], url=r["url"], source_type=src, era=e,
                            date_posted=None, date_seen="2026-11-10" if e == "now" else None,
                            date_evidence=r.get("date") or ("captured Nov 2026" if e == "now" else ""), reposts=0, removed=e != "now",
                            text_sha256=sha256(summary), pay=dict(min=r["bmin"], max=r["bmax"], currency=r.get("cur") or ("USD" if r["bmin"] and r["city"] == "NYC" else None)) if r.get("bmin") else None,
                            years_required=r["yrs"] if r["yrs"] and "unreliable" not in r.get("note", "") else None,
                            codes=r["c"], must_haves=r["must"][:5], phrases=r["ph"][:3], builder_verbs=r["vb"], maintain_verbs=r["vm"],
                            coder="A", liveness=None, raw_retained=False, note=r.get("note", "")))
    save(P(a.run) / "postings.jsonl", out)
    # second coding from the reference run
    from data import SECOND, SECOND_MAP, CODE_FOR  # noqa
    sec = []
    for key, (co, title) in SECOND_MAP.items():
        hit = [p for p in out if p["company"] == co and p["era"] == "now" and (title is None or p["title"] == title)]
        if hit:
            sec.append(dict(id=hit[0]["id"], codes={CODE_FOR[k]: v for k, v in SECOND[key].items()}, binary=True))
    save(P(a.run) / "second.jsonl", sec)
    print(f"imported {len(out)} postings, {len(sec)} second-coded")


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("store"); s.add_argument("--run", required=True); s.add_argument("--text-file", required=True); s.add_argument("--meta", required=True)
    s = sp.add_parser("code"); s.add_argument("--run", required=True); s.add_argument("--id", required=True); s.add_argument("--codes-json", required=True)
    s = sp.add_parser("liveness"); s.add_argument("--run", required=True); s.add_argument("--today", default=dt.date.today().isoformat())
    s = sp.add_parser("sample"); s.add_argument("--run", required=True); s.add_argument("--share", type=float, default=0.2); s.add_argument("--min", type=int, default=8); s.add_argument("--seed", type=int, default=7)
    s = sp.add_parser("validate"); s.add_argument("--run", required=True)
    s = sp.add_parser("import-reference"); s.add_argument("--run", required=True); s.add_argument("--niche-map", required=True)
    a = ap.parse_args()
    dict(store=cmd_store, code=cmd_code, liveness=cmd_liveness, sample=cmd_sample, validate=cmd_validate,
         **{"import-reference": cmd_import_reference})[a.cmd](a)


if __name__ == "__main__":
    main()
