"""Cycles 4 and 8: six-second-zone coverage, golden formulas (gated), the blind old-vs-new panel."""
import copy, json
from pathlib import Path
from assemble import formula_errors, zone_text
from blind_panel import as_text

ROOT = Path(__file__).resolve().parents[1]; RUN = ROOT / "examples/fictional-candidate/run"
R = json.loads((RUN / "results.json").read_text()); LEDGER = json.loads((RUN / "ledger.json").read_text())["lines"]


def test_zone_coverage_per_niche():
    z = R["baseline"]["zone_coverage"]
    assert set(z) == {n["id"] for n in R["niches"]}
    for v in z.values():
        assert 0 <= v["original"]["zone"] <= v["original"]["whole"] <= v["total"]
        assert 0 <= v["rewritten"]["zone"] <= v["rewritten"]["whole"] <= v["total"]


def test_zone_is_headline_profile_and_first_three_bullets():
    r = R["resumes"][0]; z = zone_text(r)
    assert r["header"]["headline"] in z and r["experience"][0]["bullets"][2]["text"] in z
    assert len(r["experience"][0]["bullets"]) < 4 or r["experience"][0]["bullets"][3]["text"] not in z


def test_formula_gate():
    assert formula_errors(R["niches"], LEDGER) == []
    bad = copy.deepcopy(R["niches"]); f = bad[0]["formulas"][0]
    f["example"] += " Grew it by 97% in 2 quarters."; f["bundle"] = ["zz", "yy"]
    errs = formula_errors(bad, LEDGER)
    assert any("not a bundle" in e for e in errs) and any("'97'" in e for e in errs)


def test_blind_panel_is_unblinded_and_honest():
    for r in R["resumes"]:
        if r["niche_id"] in R["summary"]["run_now"]:
            p = r["review"]["panel"]
            assert len(p) == 3 and {x["chose"] for x in p} <= {"old", "new"} and r["review"]["independent"] is False
    pk = json.loads((RUN / "reviews/blind-n02.json").read_text())
    assert "new" not in pk and "old" not in pk and set(pk) == {"niche", "A", "B"}


def test_plan12_weeks_within_twelve():
    for i in R["plan12"]:
        a, *b = [int(x) for x in i["week"].split("-")]
        assert 1 <= a <= (b[0] if b else a) <= 12
