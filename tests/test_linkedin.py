"""Cycle 6: LinkedIn rewrite — schema, limits, traceability, anti-sameness."""
import copy, json, shutil, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
EX = ROOT / "examples" / "fictional-candidate" / "run"
from common import load, validate


@pytest.fixture()
def run(tmp_path):
    d = tmp_path / "run"; shutil.copytree(EX, d, ignore=shutil.ignore_patterns("out")); return d


def gate(run):
    r = subprocess.run([sys.executable, S / "gates.py", "--run", run, "--linkedin"], capture_output=True, text=True)
    return r.returncode, {x["name"]: x for x in json.loads((run / "gates.json").read_text())["linkedin"]}


def edit(run, f):
    li = json.loads((run / "linkedin.json").read_text()); f(li); (run / "linkedin.json").write_text(json.dumps(li))


def test_example_linkedin_valid_and_passes(run):
    assert validate(load(run / "linkedin.json"), "linkedin") == []
    rc, g = gate(run)
    assert all(x["status"] != "fail" for x in g.values()), g


def test_headline_over_limit_fails(run):
    edit(run, lambda li: li.__setitem__("headline", "x" * 221))
    assert gate(run)[1]["li_limits"]["status"] == "fail"


def test_title_drift_fails(run):
    edit(run, lambda li: li["experience"][0].__setitem__("title", "VP, Strategic Partnerships"))
    assert gate(run)[1]["li_consistency"]["status"] == "fail"


def test_invented_number_fails(run):
    edit(run, lambda li: li.__setitem__("about", li["about"] + " Grew revenue 47%."))
    assert gate(run)[1]["li_traceability"]["status"] == "fail"


def test_stock_phrase_fails(run):
    edit(run, lambda li: li.__setitem__("about", "Passionate, results-driven leader. " + li["about"]))
    assert gate(run)[1]["li_authenticity"]["status"] == "fail"


def test_hook_in_visible_part(run):
    edit(run, lambda li: li.__setitem__("about", "Hello. " * 60 + li["about"]))
    assert gate(run)[1]["li_hook"]["status"] == "fail"
