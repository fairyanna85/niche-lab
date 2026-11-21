"""No real candidate data in the repo (the three test resumes stay outside it).

The terms this scan looks for are private, so they are never committed.
List them, one per line, in a local file named .private-blocklist.txt in
the repository root (it is gitignored), or pass them comma-separated in
the NICHE_LAB_BLOCKLIST environment variable. With no terms configured,
the test scans for nothing and passes.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _terms():
    terms = []
    local = ROOT / ".private-blocklist.txt"
    if local.exists():
        terms += [line.strip() for line in local.read_text().splitlines()
                  if line.strip() and not line.startswith("#")]
    env = os.environ.get("NICHE_LAB_BLOCKLIST", "")
    terms += [t.strip() for t in env.split(",") if t.strip()]
    return terms


_TERMS = _terms()
BLOCK = re.compile("|".join(re.escape(t) for t in _TERMS), re.I) if _TERMS else None


def test_no_real_candidate_data():
    if BLOCK is None:
        return
    hits = []
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in {".py", ".md", ".json", ".jsonl", ".html", ".yml", ".txt", ".svg"} and "test_privacy" not in p.name:
            if BLOCK.search(p.read_text(errors="ignore")):
                hits.append(str(p.relative_to(ROOT)))
    assert hits == []
