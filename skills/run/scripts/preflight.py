#!/usr/bin/env python3
"""Step 0 — what this environment can do. Tools the agent must check itself (web search, page fetch, subagents)
are reported as `agent_must_check`; the agent tests them with one call each before asking the person anything."""
import argparse, importlib.util, json, shutil, sys

PKGS = ["numpy", "scipy", "statsmodels", "yaml", "jsonschema", "pypdf", "docx"]


def check():
    missing = [p for p in PKGS if importlib.util.find_spec(p) is None]
    chrome = next((shutil.which(c) for c in ("google-chrome", "chromium", "chromium-browser") if shutil.which(c)), None)
    pdf = "pdftotext" if shutil.which("pdftotext") else ("pypdf" if importlib.util.find_spec("pypdf") else None)
    return {
        "python_packages": {"status": "ok" if not missing else "missing", "missing": missing,
                            "fix": "pip install -r requirements.txt (add --break-system-packages if pip refuses)"},
        "pdf_reader": {"status": "ok" if pdf else "missing", "using": pdf, "degraded": pdf == "pypdf",
                       "note": "pypdf cannot repair two-column reading order as well as pdftotext -layout; read the PDF pages as images if the parse score is low"},
        "chrome": {"status": "ok" if chrome else "missing", "path": chrome, "degraded_effect": None if chrome else "no PDF resumes; ATS parse gate not run; DOCX and Markdown still delivered"},
        "pandoc": {"status": "ok" if shutil.which("pandoc") else "missing", "degraded_effect": None if shutil.which("pandoc") else "DOCX resumes read with python-docx instead"},
        "web_search": {"status": "agent_must_check", "if_missing": "stop: niche-lab cannot run without web search"},
        "page_fetch": {"status": "agent_must_check", "if_missing": "stop: niche-lab cannot run without page fetch"},
        "subagents": {"status": "agent_must_check", "if_missing": "run reviewers inline; set independent=false in reviews/<id>.json"},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--json", action="store_true"); a = ap.parse_args()
    r = check()
    if a.json: print(json.dumps(r, indent=1))
    else:
        for k, v in r.items(): print(f"{v['status']:17s} {k}")
