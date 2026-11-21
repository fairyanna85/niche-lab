"""The five-act journey (plan §2.1, §3.5): order, hand-overs, station bar, sky states, niche selection.
These start red and sit in tests/ratchet.json (strict xfail) until the journey cycle makes them pass."""
import json
import pytest
from ui_invariants import CHROME, open_report, results_for

pw = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.skipif(not CHROME, reason="no Chrome")
ACTS = ["cover", "you", "market", "peers", "verdict", "course", "method"]
STATIONS = ["you", "market", "peers", "verdict", "course"]


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]); yield b; b.close()


def test_journey_order(browser):
    R = json.loads(results_for("example").read_text())
    pg, _ = open_report(browser, "example", 1440)
    acts = pg.evaluate("[...document.querySelectorAll('[data-act]')].map(e => e.dataset.act)")
    assert acts == ACTS
    for a in ACTS[1:-1]:
        head = pg.locator(f"[data-act={a}] [data-chapter-head]")
        assert head.count() == 1 and head.locator("h2").inner_text().strip().endswith("?"), a
        assert pg.locator(f"[data-act={a}] [data-learned]").count() == 1, a
    for a, b in zip(ACTS[1:-2], ACTS[2:-1]):
        assert pg.locator(f"[data-act={a}] [data-next]").get_attribute("href") == f"#{b}"
    first_verdict = pg.evaluate("""(h) => { const v = document.querySelector('[data-act=verdict]'); const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        for (let t; (t = w.nextNode());) { if (t.nodeValue.includes(h)) return v && v.contains(t) ? 'verdict' : (t.parentElement.closest('[data-act]')?.dataset.act || 'outside'); } return 'absent'; }""", R["summary"]["headline"][:60])
    assert first_verdict == "verdict"
    assert pg.locator("[data-act=cover] a[href='#verdict']").count() == 1
    for a in ACTS[1:]: assert pg.locator(f"#{a}[data-act={a}]").count() == 1


@pytest.mark.parametrize("width", [320, 390, 1440])
def test_station_bar(browser, width):
    pg, _ = open_report(browser, "example", width)
    st = pg.locator("[data-stations] a")
    assert st.count() == 5 and [x.get_attribute("href") for x in st.all()] == [f"#{a}" for a in STATIONS]
    for x in st.all():
        b = x.bounding_box(); assert b and b["x"] >= 0 and b["x"] + b["width"] <= width + 1 and b["width"] >= 44 and b["height"] >= 44
    for a in STATIONS:
        pg.evaluate(f"document.getElementById('{a}').scrollIntoView({{behavior:'instant'}})"); pg.wait_for_timeout(300)
        assert pg.locator("[data-stations] a[aria-current]").get_attribute("href") == f"#{a}"


def test_niche_selection_persists(browser):
    pg, _ = open_report(browser, "example", 390)
    ids = pg.evaluate("window.nicheLab.niches")
    pg.evaluate(f"window.nicheLab.selectNiche('{ids[-1]}')"); pg.wait_for_timeout(100)
    stored = pg.evaluate("Object.keys(localStorage).filter(k => k.endsWith(':niche')).map(k => localStorage.getItem(k))")
    assert stored == [f'"{ids[-1]}"'], stored
    pg.reload(); pg.wait_for_function("window.nicheLab && window.nicheLab.niches")
    assert pg.evaluate("window.nicheLab.selected") == ids[-1]


def test_sky_states(browser):
    pg, _ = open_report(browser, "example", 1440)
    seen = []
    for a in ["cover", "market", "peers", "verdict"]:
        pg.evaluate(f"document.querySelector('[data-act={a}] [data-sky-opener]').scrollIntoView({{behavior:'instant'}})"); pg.wait_for_timeout(600)
        seen.append(pg.evaluate(f"document.querySelector('[data-act={a}] [data-sky]')?.dataset.state"))
    assert seen[0] == "cover" and seen[-1] == "fit" and len(set(seen)) == 4


def test_reduced_motion_static_plates(browser):
    pg, _ = open_report(browser, "example", 1440, reduced=True)
    assert pg.locator("[data-sky-opener] [data-plate] svg").count() >= 4


def test_ratchet_only_shrinks():
    import subprocess
    from ui_invariants import ROOT
    try: head = set(json.loads(subprocess.run(["git", "show", "HEAD:tests/ratchet.json"], cwd=ROOT, capture_output=True, text=True, check=True).stdout))
    except Exception: pytest.skip("no committed ratchet")
    now = set(json.loads((ROOT / "tests" / "ratchet.json").read_text()))
    assert now <= head, f"ratchet.json grew: {sorted(now - head)}"
