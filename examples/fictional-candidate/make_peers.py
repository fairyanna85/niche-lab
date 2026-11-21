#!/usr/bin/env python3
"""Fictional peer set for the example (plan §3.5: the showcase never shows act 3 as a stub).

The postings in the example are real; these people are not. Each is generated from the niche's own requirement rates so
the aggregates behave like a real peer search, and every record is marked source_type "fictional".
usage: make_peers.py RUN
"""
import hashlib, json, random, sys
from pathlib import Path

PATHS = {
    "n02": ["partner manager at a martech platform", "alliances lead at a data warehouse vendor", "agency partnerships director",
            "channel sales manager at a SaaS scale-up", "solutions consultant turned partner lead"],
    "n01": ["alliances manager at an AI model provider", "cloud marketplace partner manager", "developer relations lead",
            "partner manager at a martech platform", "business development at an AI start-up"],
}
ETYPES = ["SaaS vendor", "cloud provider", "agency or consultancy", "start-up", "systems integrator"]


def main(run):
    run = Path(run); rnd = random.Random(7)
    for nid, paths in PATHS.items():
        an = json.loads((run / "niches" / nid / "analysis.json").read_text())
        rates = {r["code"]: r["present"] for r in an["prevalence"]}
        med = an["years"]["median"] or 8
        rows = []
        for i in range(10 if nid == "n02" else 9):
            path = paths[min(int(rnd.random() ** 1.6 * len(paths)), len(paths) - 1)]
            codes = {k: int(rnd.random() < min(.92, v * (1.05 if "ai" not in k else .7))) for k, v in rates.items()}
            r = dict(id=f"{nid}-p{i + 1:02d}", niche_id=nid, name_hash=hashlib.sha1(f"fictional-{nid}-{i}".encode()).hexdigest()[:12],
                     source_type="fictional", source_url="", title=rnd.choice(["Head of Partnerships", "VP Partnerships", "Head of Alliances", "Director, Strategic Partnerships"]),
                     employer="(fictional)", years=max(4, round(rnd.gauss(med + 3, 3))), prior_role_type=path, prior_employer_type=rnd.choice(ETYPES), codes=codes)
            if i % 3 == 0:
                sc = dict(codes); flip = rnd.choice(sorted(sc)); sc[flip] = 1 - sc[flip]; r["second_coder"] = sc
            rows.append(r)
        (run / "niches" / nid / "peers.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        print(nid, len(rows))


if __name__ == "__main__":
    main(sys.argv[1])
