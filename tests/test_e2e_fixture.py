"""Cycle 10: three distant professions run every phase offline, from recorded (synthetic) postings."""
import json, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
from common import load, validate


@pytest.mark.parametrize("field", ["nursing", "civil", "restaurant"])
def test_e2e(tmp_path, field):
    run = tmp_path / field
    r = subprocess.run([sys.executable, ROOT / "tests" / "fixtures" / "e2e_driver.py", "--field", field, "--run", run], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    res = load(run / "results.json")
    assert validate(res, "results") == []
    assert 1 <= len(res["niches"]) <= 10 and len(res["resumes"]) == len(res["niches"])
    assert validate(load(run / "linkedin.json"), "linkedin") == []
    assert all(g["status"] != "fail" for g in res["gates"]), [g for g in res["gates"] if g["status"] == "fail"]
    assert all(g["status"] != "fail" for g in res["gates_linkedin"])
    assert (run / "out" / "report.html").stat().st_size > 100_000
    mod = next((run / "codebooks").glob("induced-*.yml"))
    assert subprocess.run([sys.executable, ROOT / "skills/run/scripts/induce_codebook.py", "validate", mod], capture_output=True).returncode == 0
    assert "partner" not in json.dumps([n["label"] for n in res["niches"]]).lower()
    for n in res["niches"]: assert n["demand"]["rows"][0]["module"] in ("core", mod.stem)
