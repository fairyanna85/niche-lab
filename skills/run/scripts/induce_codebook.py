#!/usr/bin/env python3
"""Phase 2b — induce a job-family codebook module for ANY profession from the screen postings.

  candidates  --raw-dir DIR [--min-docs 3]   recurring requirement sentences and terms (acronyms, tools, licences),
                                             with document counts; boilerplate (in ≥90% of postings) dropped. The agent
                                             merges synonyms and writes 8–20 codes from this list.
  validate    MODULE.yml                     size 8–20, unique ids, no clash with core ids, rules present, cue regexes compile
  reliability --a A.jsonl --b B.jsonl        Cohen's kappa per code from two blind codings; codes under 0.6 listed in `sharpen`
"""
import argparse, collections, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import yaml
from common import CODEBOOKS

ACRO = re.compile(r"\b[A-Z][A-Z0-9&/+.-]{1,9}\b|\b[A-Z][a-z]+[A-Z][A-Za-z0-9]*\b")   # BLS, P&L, PE, AutoCAD, ServSafe
STOPCAPS = {"I", "A", "We", "The", "Our", "You", "This", "In", "Pay", "OR", "AND"}


def sentences(t): return [s.strip() for s in re.split(r"(?<=[.;!?])\s+|\n+", t) if len(s.split()) >= 3]


def norm(s): return re.sub(r"\s+", " ", re.sub(r"[^\w&/+ -]", " ", s.lower())).strip()


def candidates(a):
    docs = [p.read_text(errors="ignore") for p in sorted(Path(a.raw_dir).glob("*.txt"))]
    n = len(docs); sent_df = collections.Counter(); term_df = collections.Counter(); example = {}
    for d in docs:
        ss = {norm(s): s for s in sentences(d)}
        for k, v in ss.items(): sent_df[k] += 1; example.setdefault(k, v)
        terms = {m.group(0) for m in ACRO.finditer(d)} - STOPCAPS
        for t in terms: term_df[t] += 1
    out = []
    for k, c in sent_df.items():
        if a.min_docs <= c < 0.9 * n: out.append(dict(kind="sentence", phrase=example[k], docs=c))
    for t, c in term_df.items():
        if a.min_docs <= c < 0.9 * n: out.append(dict(kind="term", phrase=t, docs=c))
    out.sort(key=lambda x: (-x["docs"], x["kind"], x["phrase"]))
    print(json.dumps(out, indent=1, ensure_ascii=False))


def validate_module(path):
    errs = []
    m = yaml.safe_load(Path(path).read_text())
    core = {c["id"] for c in yaml.safe_load((CODEBOOKS / "core.yml").read_text())["codes"]}
    codes = m.get("codes", [])
    if not 8 <= len(codes) <= 20: errs.append(f"module has {len(codes)} codes; needs 8–20")
    if not m.get("title_patterns"): errs.append("title_patterns missing")
    ids = [c.get("id") for c in codes]
    for i in {i for i in ids if ids.count(i) > 1}: errs.append(f"duplicate id {i}")
    for i in set(ids) & core: errs.append(f"id {i} collides with a core code")
    for c in codes:
        for k in ("id", "label", "posting_rule", "resume_cues"):
            if not c.get(k): errs.append(f"{c.get('id')}: missing {k}")
        if c.get("id") and not re.fullmatch(r"[a-z][a-z0-9_]{1,11}", c["id"]): errs.append(f"{c['id']}: id must be lowercase, ≤12 chars")
        for rx in c.get("resume_cues", []) or []:
            try: re.compile(rx)
            except re.error as e: errs.append(f"{c.get('id')}: bad regex {rx!r} ({e})")
    return errs


def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(v) / n) * (b.count(v) / n) for v in set(a) | set(b))
    return 1.0 if pe == 1 else round((po - pe) / (1 - pe), 3)


def reliability(a):
    A = {r["id"]: r["codes"] for r in map(json.loads, Path(a.a).read_text().splitlines()) if r}
    B = {r["id"]: r["codes"] for r in map(json.loads, Path(a.b).read_text().splitlines()) if r}
    ids = sorted(set(A) & set(B)); per = {}
    for k in sorted({k for i in ids for k in A[i]} & {k for i in ids for k in B[i]}):
        x = [1 if A[i].get(k, 0) >= 1 else 0 for i in ids]; y = [1 if B[i].get(k, 0) >= 1 else 0 for i in ids]
        per[k] = dict(n=len(ids), kappa=kappa(x, y), agree=round(sum(p == q for p, q in zip(x, y)) / len(ids), 3))
    print(json.dumps(dict(per_code=per, sharpen=[k for k, v in per.items() if v["kappa"] < 0.6]), indent=1))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("candidates"); c.add_argument("--raw-dir", required=True); c.add_argument("--min-docs", type=int, default=3)
    v = sp.add_parser("validate"); v.add_argument("module")
    r = sp.add_parser("reliability"); r.add_argument("--a", required=True); r.add_argument("--b", required=True)
    a = ap.parse_args()
    if a.cmd == "candidates": candidates(a)
    elif a.cmd == "reliability": reliability(a)
    else:
        errs = validate_module(a.module)
        print("\n".join(errs) if errs else "ok"); sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
