#!/usr/bin/env python3
"""Stress fixture for the report: the example's results pushed to every layout edge the template must survive.

10 niches (the schema maximum), 70+ character niche labels, an unbroken 45-character employer name, a 60-character
requirement label, German compound words, a niche with no pay, no trend and no peers, a niche with 5 postings,
a niche with no actions, and 100 placeholders. Deterministic: no randomness beyond a fixed jitter.

usage: make_stress_results.py OUT.json
"""
import copy, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "examples" / "fictional-candidate" / "run" / "results.json"

LONG_LABELS = [
    "Senior Director of Global Strategic Alliances and Ecosystem Partnerships, enterprise AI infrastructure, San Francisco Bay Area",
    "Leiterin Partnerschaftsentwicklungsverantwortlichkeitsbereich, Datenplattformen und Unternehmenssoftware, München",
    "Head of Channel, Reseller and Distribution Partnerships for EMEA and APAC, cybersecurity platforms, London",
    "Vice President, Technology Alliances and Marketplace Go-To-Market, developer tools, Remote (United States)",
    "Directrice des partenariats stratégiques et de l'écosystème intégrateurs, logiciels industriels, Lyon",
    "Partner Development Lead, hyperscaler co-sell (AWS, Microsoft Azure, Google Cloud), fintech infrastructure, Toronto",
]
LONG_EMPLOYER = "Supercalifragilisticexpialidociouscorporation"  # 45 characters, no break opportunity
LONG_REQ = "Builds and runs partner enablement, certification and incentive programmes across regions"  # 89 chars


def main(out):
    r = json.loads(SRC.read_text())
    base = sorted(r["niches"], key=lambda n: n["rank"])
    pf = {p["id"]: p for p in r["portfolio"]["niches"]}
    clones = []
    for i in range(10 - len(base)):
        src = base[i % len(base)]
        nid = f"s{i + 5:02d}"
        n = copy.deepcopy(src); n["id"] = nid; n["rank"] = len(base) + i + 1; n["label"] = LONG_LABELS[i]; n["resume_id"] = "r-" + nid
        n["score"] = round(src["score"] - 3 - i, 1)
        n["fit_per_posting"]["niche"] = nid; n["fix_ladder"]["niche"] = nid
        for p in n["fit_per_posting"]["postings"]: p["id"] = p["id"] + nid
        clones.append((src, n))
        rs = copy.deepcopy(next(x for x in r["resumes"] if x["niche_id"] == src["id"])); rs.update(id="r-" + nid, niche_id=nid); r["resumes"].append(rs)
        if r.get("gates_per_resume", {}).get(src["resume_id"]): r["gates_per_resume"]["r-" + nid] = r["gates_per_resume"][src["resume_id"]]
        p = copy.deepcopy(pf[src["id"]]); p.update(id=nid, rank=n["rank"], label=n["label"], score=n["score"]); r["portfolio"]["niches"].append(p)
        r["portfolio"]["sequence"].append({"niche_id": nid, "phase": "parked", "trigger": "only if the first three niches stall after six weeks of referral-led approaches across every employer on the list"})
        for k in ("pay_points", "years", "levels"):
            if src["id"] in r["market"][k]: r["market"][k][nid] = copy.deepcopy(r["market"][k][src["id"]])
        r["market"]["closeness"][nid] = r["market"]["closeness"][src["id"]] * 0.9
        for j, pt in enumerate([pt for pt in r["market"]["points"] if pt["niche"] == src["id"]]):
            q = copy.deepcopy(pt); q.update(id=pt["id"] + nid, niche=nid, niches=[nid], x=min(1, max(0, pt["x"] * .8 + .1 + (i % 3) * .05)), y=min(1, max(0, pt["y"] * .8 + .1 + (j % 4) * .02)))
            r["market"]["points"].append(q)
        for d in r["market"]["dna"]:
            c = next((c for c in d["cells"] if c["niche"] == src["id"]), None)
            if c: d["cells"].append(dict(c, niche=nid))
        for a in [a for a in r["actions"] if a.get("niche_id") == src["id"]][:3]:
            r["actions"].append(dict(a, id=a["id"] + nid, niche_id=nid))
    r["niches"] = base + [c for _, c in clones]

    # edges on specific niches
    nopay = r["niches"][5]; nopay["pay"] = None; nopay["change"] = None; nopay["peers"] = None
    nopay["hidden_reason"] = {"pay": "no posted ranges in 12 postings", "change": "no archive postings", "peers": "peer search found 2 people (< 8 needed)"}
    nopay["size"]["pay_median"] = None
    small = r["niches"][6]; fp = small["fit_per_posting"]; fp["postings"] = fp["postings"][:5]; fp["n"] = len(fp["postings"]); fp["above_line"] = sum(p["fit"] >= fp["line"] for p in fp["postings"])
    small["size"]["n_postings"] = 5; small["size"]["n_employers"] = 4
    noact = r["niches"][7]["id"]; r["actions"] = [a for a in r["actions"] if a.get("niche_id") != noact]
    for n in r["niches"]:
        if n["employers"]["rows"]:
            n["employers"]["rows"][0]["company"] = LONG_EMPLOYER
            n["employers"]["rows"][0]["titles"] = ["Senior Director, Worldwide Strategic Partnerships and Alliances Ecosystem Development"]
        n["demand"]["rows"][0]["label"] = LONG_REQ
        if n["fix_ladder"]["steps"]: n["fix_ladder"]["steps"][0]["label"] = LONG_REQ
    r["market"]["dna"][0]["label"] = LONG_REQ

    # 100 placeholders across the first resume and the confirm list
    res0 = r["resumes"][0]
    res0["skills"] = res0["skills"] + [f"[Zertifizierungsnachweis {k:03d}]" for k in range(100)]
    r["confirm"] += [{"item": f"Fill [Zertifizierungsnachweis {k:03d}]", "why": "only you can supply it"} for k in range(100)]
    r["meta"]["candidate"] = "Maximiliane Alexandra Featherstonehaugh-Montgomery (fictional)"
    Path(out).write_text(json.dumps(r, ensure_ascii=False, indent=1))
    return r


if __name__ == "__main__":
    main(sys.argv[1])
