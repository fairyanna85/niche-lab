"""Every figure of the parity manifest is rendered in its act, draws as many marks as its data has rows (I12),
and every block of results.json is read by the renderer. Under the ratchet: tests/parity_baseline.json lists the
known gaps; new gaps fail, closed gaps must be deleted from it, and it may never grow against the last commit."""
import json, os, subprocess
from pathlib import Path
import pytest, yaml
from ui_invariants import CHROME, ROOT, open_report, results_for

pw = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.skipif(not CHROME, reason="no Chrome")
MANIFEST = yaml.safe_load((ROOT / "tests" / "parity_manifest.yml").read_text())
PB = ROOT / "tests" / "parity_baseline.json"
UPDATE = os.environ.get("NL_UPDATE_BASELINE") == "1"
_found = {}


def _sel(R, sel):
    return next(n for n in R["niches"] if n["id"] == sel)


# expected mark counts, computed from results.json, never from what the renderer stamps (I12)
ROWS = {
    "stars": lambda R, sel: len(R["market"]["points"]),
    # declared filter: the 14 requirements with the highest share in any niche
    "dna_cells": lambda R, sel: sum(len(d["cells"]) for d in sorted(R["market"]["dna"], key=lambda d: -max(c["present"] for c in d["cells"]))[:14]),
    "demand_rows": lambda R, sel: len([r for r in _sel(R, sel)["demand"]["rows"] if r["present"] >= .2][:16]),
    "fit_postings": lambda R, sel: len(_sel(R, sel)["fit_per_posting"]["postings"]),
    "ladder": lambda R, sel: len([x for x in _sel(R, sel)["fix_ladder"]["steps"] if x["coverage_gain"] >= .01 or x["fit_gain"] >= .01][:6]),
    "ranking": lambda R, sel: len(R["portfolio"]["niches"]),
    "timeline": lambda R, sel: len(R["profile_view"].get("timeline") or []),
    "bridge": lambda R, sel: len(R["market"].get("bridge") or []),
}

PROBE = """(m) => { const out = {}; const sel = (window.nicheLab && window.nicheLab.selected) || null;
  for (const f of m) { const e = document.querySelector(`[data-fig="${f.fig}"]`);
    if (!e) { out[f.fig] = {missing: true}; continue; }
    const act = e.closest('[data-act]');
    out[f.fig] = { act: act ? act.dataset.act : null, stub: e.hasAttribute('data-stub') ? e.getAttribute('data-stub') : null,
      marks: e.querySelectorAll('[data-mark]').length, text: e.textContent.trim().length, rows: e.querySelectorAll('tr,[data-row]').length }; }
  return { figs: out, selected: sel, srcs: [...new Set([...document.querySelectorAll('[data-src]')].flatMap(e => e.dataset.src.split(/\\s+/)))] }; }"""


def gaps(R, probe, fixture):
    out = []
    for f in MANIFEST:
        p = probe["figs"][f["fig"]]
        if p.get("missing"): out.append(f"{f['fig']}: missing"); continue
        if p["act"] != f["act"]: out.append(f"{f['fig']}: in act {p['act']}, expected {f['act']}")
        if p["stub"] is not None:
            if not p["stub"].strip(): out.append(f"{f['fig']}: stub without a reason")
            if f["kind"] != "stub-ok" or fixture == "example": out.append(f"{f['fig']}: stub")  # the showcase has no stubs
            continue
        if f["kind"] == "chart":
            exp = ROWS[f["rows"]](R, probe["selected"] or sorted(R["niches"], key=lambda n: n["rank"])[0]["id"]) if f.get("rows") else None
            if p["marks"] == 0: out.append(f"{f['fig']}: no data marks")
            elif exp is not None and p["marks"] != exp: out.append(f"{f['fig']}: {p['marks']} marks, data has {exp}")
        elif f["kind"] == "table" and p["rows"] < 2: out.append(f"{f['fig']}: empty table")
        elif p["text"] == 0: out.append(f"{f['fig']}: empty")
    return out


def unread_blocks(R, srcs):
    schema = json.loads((ROOT / "skills" / "run" / "schemas" / "results.schema.json").read_text())
    top = [k for k in schema["properties"] if k not in ("meta",)]
    niche = [k for k in schema["properties"]["niches"]["items"]["properties"] if k not in ("id", "label", "rank", "score", "resume_id", "hidden_reason")]
    return [f"unread: {k}" for k in top if k not in srcs] + [f"unread: niches.{k}" for k in niche if f"niches.{k}" not in srcs]


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]); yield b; b.close()
    if UPDATE and _found:
        PB.write_text(json.dumps(_found, indent=1) + "\n")


@pytest.mark.parametrize("fixture", ["example", "stress"])
def test_parity(browser, fixture):
    R = json.loads(Path(results_for(fixture)).read_text())
    pg, errs = open_report(browser, fixture, 1440)
    pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)"); pg.wait_for_timeout(400)
    probe = pg.evaluate(PROBE, MANIFEST); pg.context.close()
    found = sorted(gaps(R, probe, fixture) + unread_blocks(R, probe["srcs"]))
    if UPDATE: _found[fixture] = found; return
    known = set(json.loads(PB.read_text()).get(fixture, [])) if PB.exists() else set()
    new, stale = [g for g in found if g not in known], sorted(known - set(found))
    assert not new and not stale, f"new gaps: {new}\nclosed but still listed in parity_baseline.json: {stale}"


def test_parity_baseline_only_shrinks():
    try: head = json.loads(subprocess.run(["git", "show", "HEAD:tests/parity_baseline.json"], cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    except Exception: pytest.skip("no committed parity baseline")
    now = json.loads(PB.read_text())
    grown = {k: (len(head.get(k, [])), len(v)) for k, v in now.items() if len(v) > len(head.get(k, []))}
    assert not grown, f"parity_baseline.json grew (head, now): {grown}"
