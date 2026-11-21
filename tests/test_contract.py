"""Cycle 7: results.json carries everything the atlas and workbench need."""
import copy, json, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
EX = ROOT / "examples" / "fictional-candidate" / "run"
from common import load, validate

R = load(EX / "results.json")


@pytest.mark.parametrize("key", ["market", "baseline", "linkedin", "actions"])
def test_required_top_level(key):
    r = copy.deepcopy(R); r.pop(key)
    assert any(key in e for e in validate(r, "results"))


@pytest.mark.parametrize("key", ["fit_per_posting", "fix_ladder", "liveness_summary"])
def test_required_per_niche(key):
    r = copy.deepcopy(R); r["niches"][0].pop(key)
    assert validate(r, "results")


def test_actions_complete_and_ranked():
    acts = R["actions"]
    assert len(acts) >= 10
    sections = {"summary", "fit", "gates", "confirm", "demand", "language", "employers", "access", "pitch", "pay", "change", "portfolio", "profile_view", "funnel", "linkedin"}
    for a in acts:
        assert a["impact"] in ("high", "medium", "low") and a["effort"] in ("low", "medium", "high")
        assert a["section"] in sections and a["text"] and a["id"]
    rank = {"high": 3, "medium": 2, "low": 1}
    keys = [rank[a["impact"]] * 2 - rank[a["effort"]] for a in acts]
    assert keys == sorted(keys, reverse=True)
    assert len({a["text"] for a in acts}) == len(acts)


def test_build_fails_on_action_without_impact(tmp_path):
    r = copy.deepcopy(R); r["actions"][0].pop("impact")
    f = tmp_path / "r.json"; f.write_text(json.dumps(r))
    p = subprocess.run([sys.executable, S / "build_report.py", "--results", f, "--out", tmp_path / "o.html"], capture_output=True, text=True)
    assert p.returncode == 1
