"""Act 3: competing supply from public text (plan §5.1), placed on the sky, compared with the candidate."""
import json
from pathlib import Path
from peers import aggregate, kappa

R = json.loads((Path(__file__).resolve().parents[1] / "examples/fictional-candidate/run/results.json").read_text())


def row(i, years, codes, path="x"):
    return dict(id=f"p{i}", source_type="announcement", years=years, prior_role_type=path, prior_employer_type="SaaS vendor", codes=codes)


def test_below_threshold_is_hidden_with_count_and_sources():
    out = aggregate([row(i, 5, {"a": 1}) for i in range(7)], 8)
    assert out["n"] == 7 and "hidden" in out and "< 8" in out["hidden"] and out["sources"] == {"announcement": 7}


def test_aggregate_shares_years_paths():
    rows = [row(i, 4 + i, {"a": int(i < 6), "b": 1}, path="alliances" if i < 5 else "sales") for i in range(10)]
    out = aggregate(rows, 8)
    assert out["codes"] == {"a": 0.6, "b": 1.0} and out["years"]["median"] == 8.5 and out["paths"][0] == {"path": "alliances", "n": 5}


def test_kappa():
    assert kappa([(1, 1), (0, 0), (1, 0), (0, 0)]) == 0.5 and kappa([]) is None


def test_example_market_has_peers_rarity_and_points():
    m = R["market"]
    assert sum(p["n"] for p in m["peers"]) == len(m["peer_points"]) == 19
    gaps = [r["asked_share"] - r["peer_share"] for r in m["rarity"]]
    assert gaps == sorted(gaps, reverse=True) and m["rarity"][0]["code"] == "src"
    assert all(r["grade"] >= 2 for r in m["rarity"])


def test_bridge_links_rest_on_shared_resume_lines():
    ev = json.loads((Path(__file__).resolve().parents[1] / "examples/fictional-candidate/run/evidence.json").read_text())
    st = {f"s{i + 1}": s for i, s in enumerate(R["profile_view"]["strengths"])}
    B = R["market"]["bridge"]
    assert len(B) >= 5
    for b in B:
        assert ev[b["code"]]["grade"] >= 2 and b["ledger_ids"]
        assert set(b["ledger_ids"]) <= set(st[b["strength_id"]]["evidence"]) & set(ev[b["code"]]["evidence"])


def test_findings_are_three_and_gated():
    from build_report import journey_errors
    import copy
    assert len(R["summary"]["findings"]) == 3
    r = copy.deepcopy(R); r["summary"]["findings"][0]["body"] = "Employers asked for 4,321 things."
    assert any("4,321" in e for e in journey_errors(r))
