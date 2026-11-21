"""v2.1 contract: the career timeline and the authored journey text, gated against the results."""
import copy, json
from pathlib import Path
from build_report import journey_errors
from common import validate

R = json.loads((Path(__file__).resolve().parents[1] / "examples/fictional-candidate/run/results.json").read_text())


def test_example_has_timeline_and_journey():
    assert validate(R, "results") == []
    assert len(R["profile_view"]["timeline"]) >= 3
    assert [a["act"] for a in R["journey"]["acts"]] == ["cover", "you", "market", "peers", "verdict", "course", "method"]
    assert journey_errors(R) == []


def test_journey_gate_catches_an_invented_number():
    r = copy.deepcopy(R); r["journey"]["acts"][2]["answer"] = "Employers asked for 4,321 requirements on average."
    assert any("'4,321'" in e for e in journey_errors(r))


def test_journey_questions_end_with_a_question_mark():
    r = copy.deepcopy(R); r["journey"]["acts"][1]["question"] = "What you bring"
    assert validate(r, "results")
