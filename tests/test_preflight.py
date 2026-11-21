"""Cycle 2: preflight and degraded modes."""
import json, os, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
PDF = ROOT / "examples" / "fictional-candidate" / "input" / "jordan-avery-resume.pdf"
SKILL_MD = (ROOT / "skills" / "run" / "SKILL.md").read_text()


def env_without(*tools):
    """PATH with the named executables hidden."""
    keep = []
    for d in os.environ["PATH"].split(":"):
        if not any((Path(d) / t).exists() for t in tools): keep.append(d)
    shim = Path("/tmp/np-shim"); shim.mkdir(exist_ok=True)
    for t in ("python3", "pandoc"):
        w = shutil.which(t)
        if w and t not in tools and not (shim / t).exists(): (shim / t).symlink_to(w)
    return dict(os.environ, PATH=":".join([str(shim)] + keep))


def test_preflight_json():
    r = subprocess.run([sys.executable, S / "preflight.py", "--json"], capture_output=True, text=True)
    d = json.loads(r.stdout)
    for k in ("python_packages", "pdf_reader", "chrome", "pandoc"):
        assert k in d and "status" in d[k]
    for k in ("web_search", "page_fetch", "subagents"):
        assert d[k]["status"] == "agent_must_check"


def test_skill_md_degraded_rules():
    assert "No web search or no page fetch" in SKILL_MD and "cannot run here" in SKILL_MD
    assert "not independent" in SKILL_MD
    assert "continue resume-only" in SKILL_MD


def test_ingest_without_pdftotext(tmp_path):
    env = env_without("pdftotext")
    r = subprocess.run([sys.executable, S / "ingest.py", "--resume", PDF, "--run", tmp_path], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rep = json.loads((tmp_path / "parse_report.json").read_text())
    assert rep["method"].startswith("pypdf")
    assert "Northwind Data" in (tmp_path / "resume.txt").read_text()


def test_gates_without_chrome(tmp_path):
    d = tmp_path / "run"; shutil.copytree(ROOT / "examples" / "fictional-candidate" / "run", d, ignore=shutil.ignore_patterns("out"))
    env = env_without("google-chrome", "chromium", "chromium-browser")
    subprocess.run([sys.executable, S / "gates.py", "--run", d, "--pdf"], env=env, capture_output=True, text=True)
    g = {x["name"]: x for x in json.loads((d / "gates.json").read_text())["summary"]}
    assert g["ats_parse"]["status"] == "not_run"


def test_reviews_inline_marked_not_independent(tmp_path):
    d = tmp_path / "run"; shutil.copytree(ROOT / "examples" / "fictional-candidate" / "run", d, ignore=shutil.ignore_patterns("out"))
    for f in (d / "reviews").glob("*.json"):
        r = json.loads(f.read_text()); r["independent"] = False; f.write_text(json.dumps(r))
    subprocess.run([sys.executable, S / "gates.py", "--run", d], capture_output=True, text=True)
    g = {x["name"]: x for x in json.loads((d / "gates.json").read_text())["summary"]}
    assert "not independent" in g["reviewer_panel"]["detail"]
