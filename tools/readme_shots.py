#!/usr/bin/env python3
"""README screenshots: one viewport per act at 1440 px, plus phone and light mode. usage: tools/readme_shots.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from ui_invariants import CHROME, open_report  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
OUT = Path(__file__).resolve().parents[1] / "assets"
SHOTS = [("cover", "#cover", 0), ("you", "#you", 0), ("market", "#market [data-sky-opener]", 300), ("dna", "[data-fig=mkt-dna]", -60),
         ("peers", "[data-fig=cmp-rarity]", -80), ("verdict", "[data-fig=vrd-bridge]", -80), ("course", "[data-fig=crs-plan12]", -120)]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg, _ = open_report(b, "example", 1440, height=900)
    for name, sel, dy in SHOTS:
        pg.evaluate(f"""(() => {{ const e = document.querySelector('{sel}'); window.scrollTo(0, e.getBoundingClientRect().top + scrollY + {dy} - (innerWidth >= 860 ? 104 : 0)); }})()"""); pg.wait_for_timeout(900)
        pg.screenshot(path=str(OUT / f"v21-{name}.png"))
    pg.context.close()
    pg, _ = open_report(b, "example", 390, height=844)
    for name, sel in [("mobile-cover", "#cover"), ("mobile-verdict", "[data-fig=vrd-findings]")]:
        pg.evaluate(f"window.scrollTo(0, document.querySelector('{sel}').getBoundingClientRect().top + scrollY - 60)"); pg.wait_for_timeout(700)
        pg.screenshot(path=str(OUT / f"v21-{name}.png"))
    pg.context.close()
    pg, _ = open_report(b, "example", 1440, theme="light", height=900)
    pg.evaluate("window.scrollTo(0, document.querySelector('#verdict').getBoundingClientRect().top + scrollY)"); pg.wait_for_timeout(900)
    pg.screenshot(path=str(OUT / "v21-light.png"))
    b.close()
print("ok")
