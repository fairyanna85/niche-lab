import datetime as dt, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "skills" / "run" / "scripts"
PDF = ROOT / "examples" / "fictional-candidate" / "input" / "jordan-avery-resume.pdf"
import postings


def test_ingest_example(tmp_path):
    subprocess.run([sys.executable, S / "ingest.py", "--resume", PDF, "--run", tmp_path], check=True, capture_output=True)
    led = json.loads((tmp_path / "ledger.json").read_text())
    roles = {(l["employer"], l["title"]) for l in led["lines"] if l["employer"]}
    assert ("Northwind Data", "Director, Strategic Partnerships") in roles and len(roles) == 3
    rep = json.loads((tmp_path / "parse_report.json").read_text())
    assert rep["score"] >= 70


def test_placeholder_lint(tmp_path):
    f = tmp_path / "r.txt"
    f.write_text("NAME\nemail@x.com\nEXPERIENCE\nLead, Acme — Jan 2020 – Present\nGrew share +X ppt and cut cost by X%\nEDUCATION\nMBA 2010\n")
    subprocess.run([sys.executable, S / "ingest.py", "--resume", f, "--run", tmp_path / "r"], check=True, capture_output=True)
    rep = json.loads((tmp_path / "r" / "parse_report.json").read_text())
    assert sum(1 for i in rep["issues"] if i["kind"] == "unfilled_placeholder") >= 2


def test_liveness_bands():
    today = dt.date(2026, 11, 12)
    base = dict(era="now", source_type="employer", company="Acme", city="Denver", reposts=0, text_sha256="0" * 64, raw_retained=False, pay={"min": 1, "max": 2})
    assert postings.liveness(dict(base, date_seen="2026-11-01"), today)["band"] == "live"
    assert postings.liveness(dict(base, date_seen="2026-07-01", source_type="agency", reposts=2), today)["band"] == "likely_ghost"
    assert postings.liveness(dict(base, era="2024-25"), today)["band"] == "closed"
