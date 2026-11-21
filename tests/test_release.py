"""Cycle 11: release hygiene."""
import re, subprocess, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text()


def test_readme_images_exist():
    for m in re.findall(r"\]\((assets/[^)]+)\)", README):
        assert (ROOT / m).exists(), m


def test_readme_states_install_routes_and_limits():
    for t in ("/niche-lab:run", "niche-lab-skill.zip", "START_HERE.md", "LinkedIn", "web search", "pip"):
        assert t in README, t


def test_version_consistent():
    v = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
    assert f"v{v}" in README or v in README


def test_make_example_rebuilds():
    r = subprocess.run(["make", "example"], cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    assert (ROOT / "examples" / "fictional-candidate" / "report.html").stat().st_size > 200_000
