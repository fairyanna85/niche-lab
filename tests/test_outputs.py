"""Cycle 3: DOCX resumes and output in the resume's language."""
import json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
EX = ROOT / "examples" / "fictional-candidate" / "run"
FR = ROOT / "tests" / "fixtures" / "fr-resume.txt"
import render_resume


def test_docx_has_every_bullet_in_order(tmp_path):
    d = tmp_path / "run"; shutil.copytree(EX, d, ignore=shutil.ignore_patterns("out"))
    subprocess.run([sys.executable, S / "render_resume.py", "--run", d, "--docx"], check=True, capture_output=True)
    import docx
    r = json.loads((d / "resumes.json").read_text())[0]
    text = "\n".join(p.text for p in docx.Document(str(d / "out" / f"resume-{r['id']}.docx")).paragraphs)
    pos = [text.find(b["text"]) for e in r["experience"] for b in e["bullets"]]
    assert all(p >= 0 for p in pos) and pos == sorted(pos)


def test_language_detected_on_ingest(tmp_path):
    subprocess.run([sys.executable, S / "ingest.py", "--resume", FR, "--run", tmp_path], check=True, capture_output=True)
    assert json.loads((tmp_path / "parse_report.json").read_text())["language"] == "fr"
    led = json.loads((tmp_path / "ledger.json").read_text())
    assert any(l["section"].startswith("exp") for l in led["lines"])


def test_french_headers():
    r = json.loads((EX / "resumes.json").read_text())[0]; r["language"] = "fr"
    h = render_resume.to_html(r); m = render_resume.to_md(r)
    for t in ("Expérience professionnelle", "Formation", "Compétences"):
        assert t in h and t in m
    assert "Experience</h2>" not in h


def test_english_default():
    r = json.loads((EX / "resumes.json").read_text())[0]
    assert "Experience" in render_resume.to_md(r)
