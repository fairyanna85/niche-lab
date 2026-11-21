"""Cycle 5: contrasts reproduce the reference study (reference/partnerships-2026) on the same 42 postings."""
import json
from pathlib import Path
import pytest
from contrasts import contrast, pay_ranges, pooled_change, seniority, title_shift, versus, wilson

ROOT = Path(__file__).resolve().parents[1]
REF = json.loads((ROOT / "reference/partnerships-2026/results.json").read_text())
P = [json.loads(l) for l in (ROOT / "examples/fictional-candidate/run/postings/postings.jsonl").read_text().splitlines() if l.strip()]
NOW = [p for p in P if p["era"] == "now"]


def test_same_corpus_as_reference():
    assert len(NOW) == REF["n"]["ALL"] == 42


def test_seniority_reproduces_reference_gaps():
    S = [p for p in NOW if p["level"] in ("Head", "VP", "SVP")]; D = [p for p in NOW if p["level"] in ("Mgr", "Dir", "SrDir")]
    assert (len(S), len(D)) == (REF["n"]["SENIOR"], REF["n"]["DIRMGR"])
    rows = {r["code"]: r for r in contrast(S, D, sorted({k for p in NOW for k in p["codes"]}), {})}
    checked = 0
    for code, d_sen, p_sen, *_ in REF["gaps"]:
        if code in rows:
            assert rows[code]["diff"] == pytest.approx(d_sen, abs=1e-3), code
            assert rows[code]["p"] == pytest.approx(p_sen, abs=1e-3), code
            checked += 1
    assert checked >= 25


def test_seniority_small_sample_rule():
    tiny = NOW[:12]
    out = seniority(tiny, NOW, ["src"], {})
    assert out["scope"] == "all niches" and out["n_senior"] >= 10


def test_versus_withholds_below_ten():
    out = versus("a", "b", {"a": NOW[:9], "b": NOW[9:30]}, ["src"], {})
    assert out["rows"] == [] and "10 each" in out["reason"]


def test_title_shift_and_pooled_change():
    then = [p for p in P if p["era"] != "now"]
    rows = title_shift([p["title"] for p in then], [p["title"] for p in NOW])
    assert rows and all(0 <= r["p"] <= 1 for r in rows)
    ch = pooled_change(then, NOW, sorted({k for p in P for k in p["codes"]}), {})
    assert ch and abs(ch[0]["delta"]) >= abs(ch[-1]["delta"])


def test_wilson_and_pay_ranges():
    p, lo, hi = wilson(37, 42); assert (round(p, 3), round(lo, 2), round(hi, 3)) == (0.881, 0.75, 0.948)
    r = pay_ranges(NOW, "USD"); assert r and all(x["lo"] <= x["hi"] for x in r)
