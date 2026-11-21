import copy, json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples" / "fictional-candidate" / "run"
S = ROOT / "skills" / "run" / "scripts"


def gates(run):
    subprocess.run([sys.executable, S / "gates.py", "--run", run], capture_output=True, text=True)
    return {g["name"]: g for g in json.loads((run / "gates.json").read_text())["summary"]}


def clone(tmp_path):
    d = tmp_path / "run"; shutil.copytree(EX, d, ignore=shutil.ignore_patterns("out")); return d


def test_example_gates_have_no_fail(tmp_path):
    g = gates(clone(tmp_path))
    assert all(x["status"] != "fail" for x in g.values()), {k: v for k, v in g.items() if v["status"] == "fail"}


def test_invented_number_fails_traceability(tmp_path):
    d = clone(tmp_path); rs = json.loads((d / "resumes.json").read_text())
    rs[0]["experience"][0]["bullets"][0]["text"] += ", lifting win rate 37%"
    (d / "resumes.json").write_text(json.dumps(rs))
    assert gates(d)["traceability"]["status"] == "fail"


def test_title_drift_fails_consistency(tmp_path):
    d = clone(tmp_path); rs = json.loads((d / "resumes.json").read_text())
    rs[1]["experience"][0]["title"] = "VP, Strategic Partnerships"
    (d / "resumes.json").write_text(json.dumps(rs))
    assert gates(d)["consistency"]["status"] == "fail"


def test_stock_phrase_fails_authenticity(tmp_path):
    d = clone(tmp_path); rs = json.loads((d / "resumes.json").read_text())
    rs[0]["profile"] = "Results-driven, passionate leader. " + rs[0]["profile"]
    (d / "resumes.json").write_text(json.dumps(rs))
    assert gates(d)["authenticity"]["status"] == "fail"
