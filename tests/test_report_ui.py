"""Cycles 8–9: the atlas report and the workbench, tested in a real browser (Playwright + Chrome).
v2.1 cycle 3: the four-chapter atlas, its static plates and the single-width overflow check are superseded by
tests/test_journey.py (sky states, plates per opener) and tests/test_ui_invariants.py (the full matrix). The workbench
tests are unchanged except that the tool panels they use are opened first, since they now sit in expanders."""
import json, shutil, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
EX = ROOT / "examples" / "fictional-candidate" / "run"
pw = pytest.importorskip("playwright.sync_api")
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
pytestmark = pytest.mark.skipif(not CHROME, reason="no Chrome")
R = json.loads((EX / "results.json").read_text())


@pytest.fixture(scope="module")
def html(tmp_path_factory):
    out = tmp_path_factory.mktemp("rep") / "report.html"
    subprocess.run([sys.executable, S / "build_report.py", "--results", EX / "results.json", "--out", out], check=True, capture_output=True)
    return out.as_uri()


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]); yield b; b.close()


def open_page(browser, html, width=1280, dark=False, reduced=False, init=None, perms=None):
    ctx = browser.new_context(viewport={"width": width, "height": 900}, color_scheme="dark" if dark else "light",
                              reduced_motion="reduce" if reduced else "no-preference")
    if perms: ctx.grant_permissions(perms)
    if init: ctx.add_init_script(init)
    pg = ctx.new_page(); errs, reqs = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
    pg.goto(html); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)"); pg.wait_for_timeout(150)
    return pg, errs, reqs


@pytest.mark.parametrize("width,dark", [(1280, False), (1280, True), (390, False), (390, True)])
def test_no_errors_no_network(browser, html, width, dark):
    pg, errs, reqs = open_page(browser, html, width, dark)
    pg.mouse.wheel(0, 20000); pg.wait_for_timeout(300)
    assert errs == [] and reqs == []


def test_star_per_posting_and_you(browser, html):
    pg, _, _ = open_page(browser, html)
    assert pg.locator("#atlas .star").count() == len(R["market"]["points"])
    assert pg.locator("#atlas .you").count() == 1


def test_placeholder_fill_updates_every_version_and_export(browser, html):
    pg, errs, _ = open_page(browser, html)
    inp = pg.locator(".ph-field input").first
    key = inp.get_attribute("data-key"); inp.fill("$2.1M"); inp.dispatch_event("input"); pg.wait_for_timeout(100)
    for r in R["resumes"]:
        txt = pg.evaluate(f"window.nicheLab.exportResume('{r['id']}')")
        raw = json.dumps(r)
        if key in raw: assert "$2.1M" in txt and key not in txt
    assert errs == []


def test_actions_persist(browser, html):
    pg, _, _ = open_page(browser, html)
    pg.locator(".act-row input[type=checkbox]").first.check()
    pg.reload(); pg.wait_for_timeout(500)
    assert pg.locator(".act-row input[type=checkbox]").first.is_checked()


def test_storage_errors_are_survived(browser, html):
    init = "Object.defineProperty(window, 'localStorage', {get(){ throw new Error('blocked') }});"
    pg, errs, _ = open_page(browser, html, init=init)
    cb = pg.locator(".act-row input[type=checkbox]").first; cb.check()
    assert cb.is_checked() and errs == []


def test_copy_buttons(browser, html):
    pg, errs, _ = open_page(browser, html, perms=["clipboard-read", "clipboard-write"])
    pg.locator("[data-copy='li-headline']").first.click(); pg.wait_for_timeout(150)
    assert pg.evaluate("navigator.clipboard.readText()") == R["linkedin"]["headline"]


def test_tracker_diagnosis(browser, html):
    pg, errs, _ = open_page(browser, html)
    for k in range(10):
        pg.fill("#trk-employer", f"Co {k}"); pg.select_option("#trk-outcome", "no_reply"); pg.click("#trk-add")
    assert "No replies" in pg.locator("#trk-diag").inner_text()
