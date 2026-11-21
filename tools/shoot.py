#!/usr/bin/env python3
"""Screenshots for the visual pass and the independent design review (plan §3.6).

usage: tools/shoot.py OUTDIR [--fixtures example,stress,nursing]
Writes one image per act (or per top-level section before the journey exists) at 390 and 1440, dark and light.
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from ui_invariants import CHROME, open_report  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--fixtures", default="example,stress"); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        for fx in a.fixtures.split(","):
            for w in (390, 1440):
                for theme in ("dark", "light"):
                    pg, _ = open_report(b, fx, w, theme, height=844 if w == 390 else 900)
                    parts = pg.evaluate("[...document.querySelectorAll('[data-act]')].map(e => '[data-act=' + e.dataset.act + ']')") or \
                            pg.evaluate("[...document.querySelectorAll('main > section')].map(e => '#' + e.id)")
                    for i, sel in enumerate(parts):
                        loc = pg.locator(sel).first
                        if not loc.count(): continue
                        loc.scroll_into_view_if_needed(); pg.wait_for_timeout(450)
                        name = sel.strip("#[]").replace("data-act=", "")
                        loc.screenshot(path=str(out / f"{fx}-{w}-{theme}-{i:02d}-{name}.png"), timeout=20000)
                    pg.context.close()
        b.close()
    print(f"wrote {len(list(out.glob('*.png')))} images to {out}")


if __name__ == "__main__":
    main()
