#!/usr/bin/env python3
"""Phase 10 — validate results.json and inject it into template/report.html.

usage: build_report.py --results RUN/results.json --out RUN/out/report.html
Fails (exit 1) if the schema fails or any rendered section lacks a non-empty do_this.
"""
import argparse, base64, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, validate, REPO

SECTIONS_TOP = ["summary", "profile_view", "portfolio", "funnel"]
SECTIONS_NICHE = ["demand", "change", "peers", "language", "fit", "employers", "access", "pitch", "pay"]


def fontface(d: Path) -> str:
    """Embed the vendored OFL fonts so the report is one self-contained file that renders offline."""
    css = []
    for f in sorted(d.glob("*.woff2")):
        m = re.match(r"(marcellus|instrument-sans|eb-garamond)-latin-(\d+)-(normal|italic)", f.stem)
        if not m: continue
        fam = {"marcellus": "Marcellus", "instrument-sans": "Instrument Sans", "eb-garamond": "EB Garamond"}[m.group(1)]
        b64 = base64.b64encode(f.read_bytes()).decode()
        css.append(f'@font-face{{font-family:"{fam}";font-style:{m.group(3)};font-weight:{m.group(2)};font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
    return "\n".join(css)


def advice_errors(res):
    errs = []
    for s in SECTIONS_TOP:
        if not res.get(s, {}).get("do_this"): errs.append(f"{s}: missing do_this")
    for n in res["niches"]:
        for s in SECTIONS_NICHE:
            sec = n.get(s)
            if sec is None:
                if s not in n.get("hidden_reason", {}) and s not in ("access",):
                    errs.append(f"{n['id']}.{s}: null without hidden_reason")
                continue
            if not sec.get("do_this"): errs.append(f"{n['id']}.{s}: missing do_this")
        if not n.get("plan30"): errs.append(f"{n['id']}: missing plan30")
    for a in res.get("actions", []):
        for k in ("impact", "effort", "section"):
            if not a.get(k): errs.append(f"action {a.get('id')}: missing {k}")
    return errs


def allowed_numbers(res):
    """Every number the report may state: numeric leaves (raw, as %, in thousands) and list lengths."""
    ok = set()
    def walk(o):
        if isinstance(o, bool): return
        if isinstance(o, (int, float)):
            for v in (o, o * 100, o / 1000, o * 1000):
                ok.add(round(v, 2)); ok.add(round(v))
        elif isinstance(o, dict): [walk(v) for v in o.values()]
        elif isinstance(o, list): ok.add(len(o)); [walk(v) for v in o]
        elif isinstance(o, str):
            for m in re.findall(r"\d+(?:\.\d+)?", o.replace(",", "")): ok.add(round(float(m), 2))
    walk({k: (v if k != "summary" else {kk: vv for kk, vv in v.items() if kk != "findings"}) for k, v in res.items() if k != "journey"}); return ok


def journey_errors(res):
    """Gate on the connective text: a number in it that appears nowhere in the results is a manufactured finding."""
    ok, errs = allowed_numbers(res), []
    texts = [(a["act"], [a["question"], a["answer"], *a["learned"], a.get("handover") or ""]) for a in res.get("journey", {}).get("acts", [])]
    texts += [("findings", [f["title"] + " " + f["body"] for f in res.get("summary", {}).get("findings", [])])]
    for act, ts in texts:
        a = {"act": act}
        for t in ts:
            for m in re.findall(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)", t):
                v = float(m.replace(",", ""))
                if round(v, 2) not in ok and round(v) not in ok: errs.append(f"journey.{a['act']}: '{m}' not found in results ({t[:60]})")
    return errs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--results", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[1] / "template" / "report.html"))
    a = ap.parse_args()
    res = load(a.results)
    errs = validate(res, "results") + advice_errors(res) + journey_errors(res)
    if errs:
        print("BUILD FAILED", *errs[:30], sep="\n  "); sys.exit(1)
    tpl = Path(a.template).read_text()
    marker = "/*__RESULTS__*/null"
    if marker not in tpl: sys.exit("template marker not found")
    data = json.dumps(res, ensure_ascii=False).replace("</", "<\\/")
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.replace(marker, data).replace("/*__FONTFACE__*/", fontface(Path(a.template).parent / "fonts"))
                   .replace("__TITLE__", f"{res['meta']['candidate']}: niche report"))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
