import copy, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples" / "fictional-candidate" / "run"
S = ROOT / "skills" / "run" / "scripts"
from common import load, validate


def test_example_results_valid():
    assert validate(load(EX / "results.json"), "results") == []


def test_example_profile_valid():
    assert validate(load(EX / "profile.json"), "profile") == []


def test_build_fails_without_do_this(tmp_path):
    r = copy.deepcopy(load(EX / "results.json"))
    r["niches"][0]["language"]["do_this"] = []
    f = tmp_path / "r.json"; f.write_text(json.dumps(r))
    p = subprocess.run([sys.executable, S / "build_report.py", "--results", f, "--out", tmp_path / "o.html"], capture_output=True, text=True)
    assert p.returncode == 1 and "BUILD FAILED" in p.stdout


def test_build_ok(tmp_path):
    p = subprocess.run([sys.executable, S / "build_report.py", "--results", EX / "results.json", "--out", tmp_path / "o.html"], capture_output=True, text=True)
    assert p.returncode == 0
    html = (tmp_path / "o.html").read_text()
    assert "/*__RESULTS__*/" not in html and "Jordan Avery" in html


def test_niche_count_bounds():
    r = load(EX / "results.json")
    assert 1 <= len(r["niches"]) <= 10 and len(r["resumes"]) == len(r["niches"])
