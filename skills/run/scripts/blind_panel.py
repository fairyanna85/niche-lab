#!/usr/bin/env python3
"""Phase 9 — blind old-vs-new panel for the "run now" niches (plan cycle 8).

prepare: for each run-now niche, write RUN/reviews/blind-<niche>.json with the original and the rewritten resume as
         plain text under the labels A and B, assigned at random (seeded by niche id). The key stays in a separate file
         the reviewer never reads (blind-<niche>.key.json).
unblind: read RUN/reviews/blind-<niche>.result.json  {"reviewers": [{"reviewer", "A": score 1-10, "B": score 1-10, "chose": "A"|"B", "why"}]}
         and write RUN/reviews/blind-<niche>.panel.json with scores mapped back to old/new.
usage: blind_panel.py prepare|unblind --run RUN
"""
import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, save


def as_text(r):
    out = [r["header"]["name"], r["header"]["headline"], "", r.get("profile") or ""]
    for e in r["experience"]:
        out += ["", f"{e['title']}, {e['employer']} ({e['dates']})"] + ([e["context"]] if e.get("context") else []) + ([e["scope"]] if e.get("scope") else []) + [f"- {b['text']}" for b in e["bullets"]]
    out += ["", "Skills: " + ", ".join(r.get("skills", []))]
    return "\n".join(out)


def prepare(run):
    rk = load(run / "ranking.json"); base = load(run / "baseline.json")["resume"]; res = {r["niche_id"]: r for r in load(run / "resumes.json")}
    niches = {n["id"]: n for n in load(run / "niches.json")["niches"]}
    for nid in rk.get("run_now", rk["order"][:2])[:3]:
        flip = int(hashlib.sha1(nid.encode()).hexdigest(), 16) % 2 == 1
        a, b = (res[nid], base) if flip else (base, res[nid])
        save(run / "reviews" / f"blind-{nid}.json", dict(niche=niches[nid]["label"], A=as_text(a), B=as_text(b)))
        save(run / "reviews" / f"blind-{nid}.key.json", dict(A="new" if flip else "old", B="old" if flip else "new"))
        print("prepared", nid)


def unblind(run):
    for f in sorted((run / "reviews").glob("blind-*.result.json")):
        nid = f.name.split("-")[1].split(".")[0]; key = load(run / "reviews" / f"blind-{nid}.key.json"); res = load(f)
        panel = [dict(reviewer=r["reviewer"], old=r[[k for k, v in key.items() if v == "old"][0]], new=r[[k for k, v in key.items() if v == "new"][0]],
                      chose=key[r["chose"]], why=r.get("why", "")) for r in res["reviewers"]]
        save(run / "reviews" / f"blind-{nid}.panel.json", dict(niche_id=nid, panel=panel, independent=res.get("independent", True), note=res.get("note", "")))
        print("unblinded", nid, [p["chose"] for p in panel])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prepare", "unblind"]); ap.add_argument("--run", required=True); a = ap.parse_args()
    (prepare if a.cmd == "prepare" else unblind)(Path(a.run))
