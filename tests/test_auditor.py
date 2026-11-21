"""The auditor is tested before anything relies on it: each page plants exactly one defect; clean pages plant none.
An auditor with false positives gets switched off; one with false negatives is how v2 shipped."""
import shutil
import pytest
from ui_invariants import AUDITOR, CHROME

pw = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.skipif(not CHROME, reason="no Chrome")

HEAD = "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'><style>body{margin:0;font:16px/1.5 sans-serif}*{box-sizing:border-box}" \
       ".g{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.g button{min-height:44px}</style>"
OK_GROUP = "<div class=g data-btn-group><button>One</button><button>Two</button><button>Three</button></div>"
OK_SVG = "<svg viewBox='0 0 300 60' width=300 height=60><text x=10 y=20 font-size=12>Alpha</text><text x=10 y=45 font-size=12>Beta</text></svg>"

PAGES = {
    "I1": (390, HEAD + "<div style='width:600px'>wide block</div>"),
    "I2": (390, HEAD + "<div style='overflow-x:auto;width:200px'><div style='width:500px'>scroller content</div></div>"),
    "I3-escape": (390, HEAD + "<div style='width:120px'><span style='white-space:nowrap'>a label that is far too long for its box</span></div>"),
    "I3-clip": (390, HEAD + "<div style='width:120px;overflow:hidden;white-space:nowrap'>a label that is cut by its own box</div>"),
    "I4-out": (390, HEAD + "<svg viewBox='0 0 200 40' width=200 height=40><text x=150 y=20 font-size=12>Label far past the right edge</text></svg>"),
    "I4-overlap": (390, HEAD + "<svg viewBox='0 0 300 40' width=300 height=40><text x=10 y=20 font-size=12>First label</text><text x=30 y=22 font-size=12>Second label</text></svg>"),
    "I5": (390, HEAD + "<div><span>Owns partner-sourced pi…</span></div>"),
    "I6": (390, HEAD + "<div data-btn-group style='display:flex;gap:8px'><button style='height:44px;width:60px'>A</button><button style='height:44px;width:140px'>Longer</button></div>"),
    "I7": (390, HEAD + "<div class=g data-btn-group><button style='min-height:0;height:30px'>A</button><button style='min-height:0;height:30px'>B</button><button style='min-height:0;height:30px'>C</button></div>"),
    "I8": (1280, HEAD + "<button style='height:40px'>Stray</button>"),
    "I9-body": (390, HEAD + "<p style='font-size:13px'>Body copy set too small for a phone.</p>"),
    "I9-form": (390, HEAD + "<label style='display:block;min-height:44px'>Name <input style='font-size:14px;height:44px;width:200px'></label>"),
}
CLEAN = {
    "clean-mobile": (390, HEAD + OK_GROUP + "<p>Prose may trail off… and still be fine.</p><p>See <a href='#x'>this source</a> for the details of the method used here.</p>" + OK_SVG),
    "clean-desktop": (1280, HEAD + OK_GROUP + "<table><tr><td>Cell</td><td><span>value</span></td></tr></table>" + OK_SVG),
}


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]); yield b; b.close()


def run(browser, width, html):
    ctx = browser.new_context(viewport={"width": width, "height": 700}); pg = ctx.new_page(); pg.set_content(html)
    out = pg.evaluate(AUDITOR, {}); ctx.close(); return out


@pytest.mark.parametrize("name", sorted(PAGES))
def test_flags_exactly_the_planted_defect(browser, name):
    width, html = PAGES[name]
    found = {v["inv"] for v in run(browser, width, html)}
    assert found == {name.split("-")[0]}, [v for v in run(browser, width, html)]


@pytest.mark.parametrize("name", sorted(CLEAN))
def test_clean_pages_pass(browser, name):
    width, html = CLEAN[name]
    assert run(browser, width, html) == []
