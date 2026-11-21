"""Act 1's career line: dates parsed from what resumes actually contain, in four languages."""
import json
from pathlib import Path
import pytest
from timeline import build_timeline, parse_dates

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("s,exp", [
    ("Mar 2022 – Present", ("2022-03", None)),
    ("Aug 2016 – May 2020", ("2016-08", "2020-05")),
    ("Jan. 2015 - Dec 2016", ("2015-01", "2016-12")),
    ("2019–21", ("2019-01", "2021-12")),
    ("2019 - 2021", ("2019-01", "2021-12")),
    ("03/2018 – 06/2020", ("2018-03", "2020-06")),
    ("2017-09 – 2019-02", ("2017-09", "2019-02")),
    ("janv. 2015 – déc. 2016", ("2015-01", "2016-12")),
    ("septembre 2018 - aujourd'hui", ("2018-09", None)),
    ("März 2019 – heute", ("2019-03", None)),
    ("ene 2020 – actualidad", ("2020-01", None)),
    ("2015", ("2015-01", "2015-12")),
    ("Jun 2020 – Present · Chicago, IL", ("2020-06", None)),
    ("", (None, None)),
    ("since forever", (None, None)),
])
def test_parse_dates(s, exp):
    assert parse_dates(s) == exp


def test_timeline_from_example_ledger():
    run = ROOT / "examples" / "fictional-candidate" / "run"
    lines = json.loads((run / "ledger.json").read_text())["lines"]
    t = build_timeline(lines, json.loads((run / "resumes.json").read_text()))
    assert len(t) >= 3 and t[0]["end"] is None and all(r["start"] for r in t)
    assert t[0]["scope"] and t[0]["n_metrics"] >= 1 and t[0]["ledger_ids"][0].startswith("R")


def test_messy_two_column_ledger_is_grouped_by_date_line():
    """Real resumes parse with the company in the title field, the location in the employer field and job titles
    after the bullets; roles must still come out one per date range (pattern seen on the real test resumes)."""
    L = []
    for i, (co, loc, d, ttl) in enumerate([("ACME CORP", "PARIS, FRANCE", "May 2024 – May 2026", "Director, Partnerships"),
                                           ("BETA LTD", "EMEA", "Sep 2017 – Aug 2023", None), ("GAMMA", "NEW YORK, NY", "2012 – 2013", None)]):
        L.append(dict(id=f"R{3 * i + 1}", source="resume", claim_type="header", employer=loc, title=co, dates=d, text=f"{co} | {loc}"))
        if ttl: L.append(dict(id=f"R{3 * i + 2}", source="resume", claim_type="header", employer=loc, title=co, dates=d, text=f"{ttl} | {d}"))
        L.append(dict(id=f"R{3 * i + 3}", source="resume", claim_type="metric", employer=loc, title=co, dates=d, text="Grew revenue 20%"))
    t = build_timeline(L)
    assert [(r["start"], r["end"]) for r in t] == [("2024-05", "2026-05"), ("2017-09", "2023-08"), ("2012-01", "2013-12")]
    assert t[0]["title"] == "Director, Partnerships" and t[0]["employer"] == "ACME CORP" and t[1]["employer"] == "BETA LTD"
