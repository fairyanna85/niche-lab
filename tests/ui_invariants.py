"""Shared UI harness: report fixtures, the in-page auditor, the test matrix and the ratchet.

The ratchet (docs/CORRECTIVE-PLAN-v2.1.md §3.3): tests/ui_baseline.json records known violations per matrix cell.
A cell fails on any violation not in the baseline, and on any baseline entry that no longer occurs. A separate test
fails if the baseline grew against the last commit, so the file can only shrink.
"""
import json, os, shutil, subprocess, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
EX = ROOT / "examples" / "fictional-candidate" / "run" / "results.json"
AUDITOR = (ROOT / "tests" / "ui" / "auditor.js").read_text()
BASELINE = ROOT / "tests" / "ui_baseline.json"
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
BUILD = Path(os.environ.get("NL_UI_BUILD", "/tmp/niche-lab-ui"))

# act length budgets in screens, (390 px, 1440 px), plan §2.1
BUDGETS = {390: {"cover": 1.5, "you": 7, "market": 7, "peers": 7, "verdict": 7, "course": 12, "method": 3},
           1440: {"cover": 1, "you": 3.5, "market": 4.75, "peers": 3.5, "verdict": 4.25, "course": 6, "method": 1.5}}
# 1440 market and verdict raised from 3.5 after measurement; verdict to 4.25 when the decision sentence was set at display size (design review round 3) (docs/visual-review.md, cycle 3); the whole-report budget is unchanged.
FAST_WIDTHS = [320, 390, 1440]
FULL_WIDTHS = [320, 360, 390, 430, 600, 768, 1024, 1280, 1440, 1920]


def results_for(fixture: str) -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    if fixture == "example": return EX
    if fixture == "stress":
        out = BUILD / "stress.json"
        subprocess.run([sys.executable, ROOT / "tests" / "fixtures" / "make_stress_results.py", out], check=True)
        return out
    if fixture == "nursing":
        run = BUILD / "nursing"
        if not (run / "results.json").exists():
            subprocess.run([sys.executable, ROOT / "tests" / "fixtures" / "e2e_driver.py", "--field", "nursing", "--run", run], check=True, capture_output=True)
        return run / "results.json"
    raise ValueError(fixture)


@lru_cache(maxsize=None)
def report(fixture: str) -> str:
    res = results_for(fixture)
    out = BUILD / f"{fixture}.html"
    r = subprocess.run([sys.executable, S / "build_report.py", "--results", res, "--out", out], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return out.as_uri()


def open_report(browser, fixture, width, theme="dark", height=800, text_scale=1.0, reduced=False):
    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=theme,
                              reduced_motion="reduce" if reduced else "no-preference")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(report(fixture)); pg.evaluate("try{localStorage.clear()}catch(e){}"); pg.reload(); pg.wait_for_timeout(500)
    pg.evaluate(f"document.documentElement.dataset.theme = {json.dumps(theme)}")
    if text_scale != 1.0: pg.evaluate(f"document.documentElement.style.fontSize = '{int(text_scale * 100)}%'")
    pg.wait_for_timeout(250)
    return pg, errs


def audit(pg, width=None, occlusion=False, budgets=True):
    budgets = BUDGETS.get(width) if budgets else None
    return pg.evaluate(AUDITOR, {"budgets": budgets, "occlusion": occlusion})


def states(pg):
    """Yield (name, setup, budgets_apply) for the page's interactive states. Length budgets (I11) apply only with
    every expander closed, since they are defined that way (plan §2.1)."""
    yield "closed", None, True
    if pg.evaluate("!!(window.nicheLab && window.nicheLab.selectNiche)"):
        yield "last-niche", "window.nicheLab.selectNiche(window.nicheLab.niches.at(-1))", True
        yield "longest-niche", "window.nicheLab.selectNiche(window.nicheLab.longestNiche)", True
    if pg.evaluate("document.querySelectorAll('details').length"):
        yield "open", "document.querySelectorAll('details').forEach(d => d.open = true)", False


# length budgets are checked on realistic fixtures at default text size; the stress fixture (10 niches, extreme
# labels) and the 125% text state are checked for geometry only.
BUDGET_FIXTURES = {"example", "nursing"}


def cell(fixture, width, theme, state):
    return f"{fixture}|{width}|{theme}|{state}"


def matrix(full=False):
    widths = FULL_WIDTHS if full else FAST_WIDTHS
    fixtures = ["example", "stress"] + (["nursing"] if full else [])
    out = []
    for f in fixtures:
        for w in widths:
            out.append((f, w, "dark", 1.0))
            if w in (390, 1440): out.append((f, w, "light", 1.0))
        out.append((f, 390, "dark", 1.25))
    return out


def load_baseline():
    return json.loads(BASELINE.read_text()) if BASELINE.exists() else {}


def baseline_at_head():
    try:
        txt = subprocess.run(["git", "show", "HEAD:tests/ui_baseline.json"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return json.loads(txt)
    except Exception:
        return None
