import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples" / "fictional-candidate" / "run"
from common import load, SKILL


def test_market_block_shape():
    m = load(EX / "results.json")["market"]
    assert m["points"] and all(0 <= p["x"] <= 1 and 0 <= p["y"] <= 1 for p in m["points"])
    assert 0 <= m["candidate"]["x"] <= 1
    ids = [n["id"] for n in load(EX / "results.json")["niches"]]
    assert set(m["closeness"]) == set(ids)


def test_market_block_deterministic(tmp_path):
    import shutil
    d = tmp_path / "run"; shutil.copytree(EX, d, ignore=shutil.ignore_patterns("out"))
    a = SKILL / "scripts" / "assemble.py"
    subprocess.run([sys.executable, a, "--run", d], check=True, capture_output=True)
    m1 = json.loads((d / "results.json").read_text())["market"]
    subprocess.run([sys.executable, a, "--run", d], check=True, capture_output=True)
    m2 = json.loads((d / "results.json").read_text())["market"]
    assert m1 == m2


def test_schema_declares_market():
    s = load(SKILL / "schemas" / "results.schema.json")
    assert "market" in s["properties"]
