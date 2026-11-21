#!/usr/bin/env python3
"""Render linkedin.json as a copy-ready Markdown file: RUN/out/linkedin.md (field by field, with character counts)."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load


def to_md(li):
    m = ["# LinkedIn rewrite", "", f"_Written for niche {li['niche_id']}. Every title, date and number matches your resume versions._", "",
         f"## Headline ({len(li['headline'])}/220)", li["headline"], "", f"## About ({len(li['about'])}/2600)", li["about"], "", "## Experience"]
    for e in li["experience"]:
        m += [f"### {e['title']}, {e['employer']} — {e['dates']} ({len(e['description'])}/2000)", e["description"], ""]
    m += ["## Skills (pin the first three)", ", ".join(li["skills"]), "", "## Open to work: job titles", ", ".join(li["open_to_titles"]), ""]
    if li.get("featured"): m += ["## Featured"] + [f"- {f['title']} — {f['why']}" for f in li["featured"]] + [""]
    if li.get("alternates"): m += ["## Alternate headlines for your other niches"] + [f"- {a['niche_id']}: {a['headline']}" for a in li["alternates"]] + [""]
    if li.get("connection_note"): m += [f"## Connection note ({len(li['connection_note'])}/300)", li["connection_note"], ""]
    return "\n".join(m)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); a = ap.parse_args(); run = Path(a.run)
    (run / "out").mkdir(exist_ok=True); (run / "out" / "linkedin.md").write_text(to_md(load(run / "linkedin.json"))); print("wrote out/linkedin.md")
