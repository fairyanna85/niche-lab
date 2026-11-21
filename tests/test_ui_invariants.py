"""Invariants I1–I11 across the width × theme × text-size × fixture × state matrix, under the ratchet.

NL_FULL=1          run the full matrix (10 widths, nursing fixture); required before commits from cycle 3 on.
NL_UPDATE_BASELINE=1  rewrite tests/ui_baseline.json from what is found (only to record fixes; it may never grow).
"""
import json, os
import pytest
from ui_invariants import (BUDGET_FIXTURES, CHROME, BASELINE, audit, baseline_at_head, cell, load_baseline, matrix, open_report, states)

pw = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.skipif(not CHROME, reason="no Chrome")
FULL = os.environ.get("NL_FULL") == "1"
UPDATE = os.environ.get("NL_UPDATE_BASELINE") == "1"
_found = {}


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]); yield b; b.close()
    if UPDATE and _found:
        base = load_baseline(); base.update(_found)
        BASELINE.write_text(json.dumps({k: base[k] for k in sorted(base) if base[k]}, indent=1, ensure_ascii=False) + "\n")


@pytest.mark.parametrize("fixture,width,theme,scale", matrix(FULL), ids=lambda v: str(v))
def test_invariants(browser, fixture, width, theme, scale):
    pg, errs = open_report(browser, fixture, width, theme, text_scale=scale)
    assert errs == [], errs
    base = load_baseline(); failures = []
    for name, setup, bud in states(pg):
        if setup: pg.evaluate(setup); pg.wait_for_timeout(200)
        occl = width <= 430 and name == "closed" and theme == "dark" and scale == 1.0
        found = audit(pg, width, occlusion=occl, budgets=bud and scale == 1.0 and fixture in BUDGET_FIXTURES)
        key = cell(fixture, width, f"{theme}{'' if scale == 1 else '@' + str(int(scale * 100))}", name)
        keys = sorted({v["key"] for v in found})
        if UPDATE: _found[key] = keys; continue
        known = set(base.get(key, []))
        new = [v for v in found if v["key"] not in known]
        stale = sorted(known - set(keys))
        if new: failures.append(f"{key}: {len(new)} new violation(s):\n  " + "\n  ".join(f'{v["key"]} :: {v["detail"]}' for v in new[:25]))
        if stale: failures.append(f"{key}: fixed but still in the baseline (delete them):\n  " + "\n  ".join(stale[:25]))
    pg.context.close()
    assert not failures, "\n".join(failures)


def test_baseline_only_shrinks():
    """Counts, not keys: a restructure renames selectors, but no cell may hold more known violations than at HEAD."""
    head = baseline_at_head()
    if head is None: pytest.skip("no committed baseline to compare against")
    now = load_baseline()
    grown = {k: (len(head.get(k, [])), len(v)) for k, v in now.items() if len(v) > len(head.get(k, []))}
    assert not grown and sum(map(len, now.values())) <= sum(map(len, head.values())), f"ui_baseline.json grew (head, now): {grown}"


def test_escape_hatches_capped():
    from pathlib import Path
    tpl = (Path(__file__).resolve().parents[1] / "skills" / "run" / "template" / "report.html").read_text()
    assert tpl.count("data-audit-ignore") == 0
