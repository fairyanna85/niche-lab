"""Cycle 4: any profession — induced codebook modules, neutral core."""
import json, re, subprocess, sys
from pathlib import Path
import pytest, yaml
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
CB = ROOT / "skills" / "run" / "codebooks"
FX = json.loads((ROOT / "tests" / "fixtures" / "postings_three_fields.json").read_text())
BANNED = re.compile(r"partner|saas|\barr\b|quota|\bapi|\bsql\b|\bisv|hyperscaler|pipeline|\bllm", re.I)


def run(*a):
    return subprocess.run([sys.executable, S / "induce_codebook.py", *map(str, a)], capture_output=True, text=True)


@pytest.mark.parametrize("field,expect", [("nursing", ["bls", "license"]), ("civil", ["pe", "autocad"]), ("restaurant", ["servsafe", "p&l"])])
def test_candidates_surface_field_requirements(tmp_path, field, expect):
    d = tmp_path / "raw"; d.mkdir()
    for i, p in enumerate(FX[field]): (d / f"{i}.txt").write_text(p["text"])
    r = run("candidates", "--raw-dir", d, "--min-docs", 3)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout); text = " ".join(c["phrase"].lower() for c in out)
    for e in expect: assert e in text, (e, text[:400])
    assert all(c["docs"] >= 3 for c in out)


def good_module(tmp_path, ids=None):
    ids = ids or [f"nu_{i}" for i in range(9)]
    m = dict(module="induced-nursing", version=1, status="UNTESTED", title_patterns=["nurse"],
             codes=[dict(id=i, label=f"Requirement {i}", posting_rule="2 if required; 1 if preferred", resume_cues=[r"\bbls\b"]) for i in ids])
    p = tmp_path / "induced-nursing.yml"; p.write_text(yaml.safe_dump(m)); return p


def test_validate_accepts_good_module(tmp_path):
    assert run("validate", good_module(tmp_path)).returncode == 0


def test_validate_rejects_core_id_collision(tmp_path):
    r = run("validate", good_module(tmp_path, ["mgr"] + [f"nu_{i}" for i in range(8)]))
    assert r.returncode == 1 and "core" in r.stdout


def test_validate_rejects_bad_size_and_regex(tmp_path):
    assert run("validate", good_module(tmp_path, ["nu_1", "nu_2"])).returncode == 1
    p = good_module(tmp_path); m = yaml.safe_load(p.read_text()); m["codes"][0]["resume_cues"] = ["(unclosed"]; p.write_text(yaml.safe_dump(m))
    assert run("validate", p).returncode == 1


def test_core_is_profession_neutral():
    core = yaml.safe_load((CB / "core.yml").read_text())
    for c in core["codes"]:
        assert not BANNED.search(c["label"] + " " + c["posting_rule"]), c["id"]
    ids = {c["id"] for c in core["codes"]}
    assert {"mgr", "budget", "cred", "shift", "safety", "cust", "data", "train"} <= ids


def test_reliability_flags_weak_codes(tmp_path):
    a = [dict(id=f"p{i}", codes={"x": 1 if i % 2 else 0, "y": 1 if i < 5 else 0}) for i in range(10)]
    b = [dict(id=f"p{i}", codes={"x": 1 if i % 2 else 0, "y": 1 if i % 3 == 0 else 0}) for i in range(10)]
    fa, fb = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    fa.write_text("".join(json.dumps(x) + "\n" for x in a)); fb.write_text("".join(json.dumps(x) + "\n" for x in b))
    r = run("reliability", "--a", fa, "--b", fb)
    out = json.loads(r.stdout)
    assert out["per_code"]["x"]["kappa"] == 1.0 and "y" in out["sharpen"] and "x" not in out["sharpen"]
