"""Cycle 1: the repo is a Claude plugin and its own marketplace; the standalone skill zip still builds."""
import json, re, shutil, subprocess, zipfile
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
AGENTS = {"second-coder", "advocate", "reviewer-recruiter", "reviewer-hiring-manager", "reviewer-ceo"}


def front(p):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", p.read_text(), re.S)
    assert m, f"{p} has no frontmatter"
    meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
    return {k.strip(): v.strip() for k, v in meta.items()}, m.group(2)


def test_manifest():
    m = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert m["name"] == "niche-lab" and re.match(r"^\d+\.\d+\.\d+$", m["version"])


def test_marketplace():
    mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert len(mk["plugins"]) == 1 and mk["plugins"][0]["source"] == "./" and mk["plugins"][0]["name"] == "niche-lab"


def test_skill_entry():
    meta, body = front(ROOT / "skills" / "run" / "SKILL.md")
    assert meta["name"] == "run" and meta["description"]
    assert "resume" in body.lower() and "linkedin" in body.lower()
    for d in ("resume per niche", "LinkedIn rewrite", "report"):
        assert d.lower() in body.lower()
    assert "Ask exactly one question" in body


def test_agents_match_prompts():
    files = {p.stem: p for p in (ROOT / "agents").glob("*.md")}
    assert set(files) == AGENTS
    for name, p in files.items():
        meta, body = front(p)
        assert meta["name"] == name and meta["description"]
        prompt = (ROOT / "skills" / "run" / "prompts" / f"{name}.md").read_text().strip()
        assert prompt in body, f"agents/{name}.md is out of sync with its prompt; run tools/build_agents.py"


def test_no_root_claude_md():
    assert not (ROOT / "CLAUDE.md").exists()


def test_start_here_points_to_skill():
    t = (ROOT / "START_HERE.md").read_text()
    assert "skills/run/SKILL.md" in t


def test_dist_zip(tmp_path):
    subprocess.run(["make", "dist"], cwd=ROOT, check=True, capture_output=True)
    z = zipfile.ZipFile(ROOT / "dist" / "niche-lab-skill.zip")
    names = z.namelist()
    assert "SKILL.md" in names and "scripts/ingest.py" in names and "template/report.html" in names
    assert not any(n.startswith("agents/") for n in names)


@pytest.mark.skipif(not shutil.which("claude"), reason="claude CLI not installed")
def test_claude_plugin_validate():
    r = subprocess.run(["claude", "plugin", "validate", str(ROOT)], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
