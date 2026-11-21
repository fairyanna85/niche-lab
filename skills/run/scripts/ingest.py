#!/usr/bin/env python3
"""Phase 0 — ingest the resume (+ optional LinkedIn export), fix reading order, lint, and build the ledger skeleton.

usage: ingest.py --resume FILE [--linkedin FILE_OR_URL] --run RUN_DIR

Outputs in RUN_DIR: resume.txt, linkedin.txt (if any), parse_report.json, ledger.json
The agent then reviews ledger.json (employer/title/dates/own_role per line) before phase 1.
"""
import argparse, re, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import save, sha256, numbers_in, run_dir, validate, detect_language

MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|janv|févr|fevr|mars|avr|mai|juin|juil|août|aout|sept|oct|nov|déc|dec)[a-zé]*\.?"
DATE = rf"(?:{MONTHS}\s+|\d{{1,2}}/)?(?:19|20)\d\d"
RANGE = re.compile(rf"({DATE})\s*(?:[-–—]|to|à)\s*({DATE}|present|current|now|today|aujourd'hui|présent|ongoing)", re.I)
SECTION = re.compile(r"^\s*(experience|professional experience|work experience|employment|expérience|expériences|expérience professionnelle|experiencia|experiencia profesional|berufserfahrung|education|formation|formación|ausbildung|skills|compétences|competencias|kompetenzen|languages|langues|idiomas|sprachen|certifications?|awards?|projects?|summary|profile|profil|perfil|about|publications|volunteer|interests)\s*:?\s*$", re.I)
PLACEHOLDER = re.compile(r"(\[[^\]]{0,40}\]|\bTBD\b|\bXX+\b|\b[XYZ]\s?%|[+−-]\s?[XYZ]\s?(?:ppt|pts|%)?\b|\?\?)")
CONTACT = re.compile(r"@|linkedin\.com|\+\d[\d\s().-]{7,}", re.I)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def extract(path: Path):
    """Return (text, method, two_column_ratio, pages)."""
    suf = path.suffix.lower()
    if suf == ".pdf" and not shutil.which("pdftotext"):
        from pypdf import PdfReader
        rd = PdfReader(str(path))
        try:
            text = "\n".join(p.extract_text(extraction_mode="layout") or "" for p in rd.pages)
        except TypeError:
            text = "\n".join(p.extract_text() or "" for p in rd.pages)
        lines = [l for l in text.splitlines() if l.strip()]
        ratio = sum(1 for l in lines if re.search(r"\S\s{8,}\S", l.strip())) / max(1, len(lines))
        if ratio >= 0.25:
            return split_columns(text), "pypdf-layout+column-split", ratio, len(rd.pages)
        return "\n".join(p.extract_text() or "" for p in rd.pages), "pypdf", ratio, len(rd.pages)
    if suf == ".pdf":
        layout = run(["pdftotext", "-layout", str(path), "-"])
        pages = layout.count("\f") + (0 if layout.endswith("\f") else 1)
        lines = [l for l in layout.splitlines() if l.strip()]
        split = [l for l in lines if re.search(r"\S\s{8,}\S", l.strip())]
        ratio = len(split) / max(1, len(lines))
        if ratio >= 0.25:
            return split_columns(layout), "pdftotext-layout+column-split", ratio, pages
        return run(["pdftotext", str(path), "-"]), "pdftotext", ratio, pages
    if suf in (".docx", ".doc", ".odt", ".rtf"):
        if shutil.which("pandoc"):
            return run(["pandoc", str(path), "-t", "plain", "--wrap=none"]), "pandoc", 0.0, None
        import docx
        return "\n".join(p.text for p in docx.Document(str(path)).paragraphs), "python-docx", 0.0, None
    return path.read_text(errors="replace"), "text", 0.0, None


def split_columns(layout: str) -> str:
    """Find the gutter (the column that is blank in the most lines that reach past it) and emit the
    left column, then the right column, page by page. Lines with a word crossing the gutter stay whole."""
    out = []
    for page in layout.split("\f"):
        lines = page.splitlines()
        width = max((len(l) for l in lines), default=0)
        if width < 40:
            out.append(page); continue
        best, best_score = None, -1.0
        for c in range(int(width * 0.2), int(width * 0.8)):
            reach = [l for l in lines if len(l.rstrip()) > c + 2]
            if len(reach) < 5: continue
            blank = sum(1 for l in reach if l[c - 1:c + 2].strip() == "") / len(reach)
            score = blank * len(reach) ** 0.5
            if score > best_score: best, best_score = c, score
        if best is None:
            out.append(page); continue
        left, right = [], []
        for l in lines:
            if len(l) > best and l[best - 1:best + 1].strip() and l[best - 1] != " " and l[best] != " ":
                left.append(l.strip()); continue      # spanning line
            left.append(l[:best].rstrip()); right.append(l[best:].strip())
        out.append("\n".join(x for x in left) + "\n" + "\n".join(x for x in right if x))
    return "\n".join(out)


def normalize(text: str) -> str:
    rep = {"ﬁ": "fi", "ﬂ": "fl", "’": "'", "‘": "'", "“": '"', "”": '"', " ": " ", "": "•", "●": "•", "▪": "•"}
    for a, b in rep.items(): text = text.replace(a, b)
    return text


def unwrap(text: str):
    """Join PDF line-wraps: a line starting lowercase (or with '&', ')', ',') continues the previous one."""
    out = []
    for raw in text.splitlines():
        t = raw.strip()
        if not t: out.append(""); continue
        bullet = bool(re.match(r"[•·*▪◦●]|[-–] ", t))
        if out and out[-1] and not bullet and re.match(r"[a-zà-ÿ&),]", t) and not re.search(r"[.;:!?]$", out[-1]) and not SECTION.match(out[-1].lstrip("•·-–*▪◦● ")):
            out[-1] = out[-1] + " " + t
        else:
            out.append(t)
    return out


ROLE_SPLIT = re.compile(r"\s+(?:—|–|-|\||@|at)\s+")


def ledger_lines(text: str, prefix: str, source: str):
    lines, section, role = [], "header", None
    for raw in unwrap(text):
        t = raw.strip().lstrip("•·-–*▪◦● ").strip()
        if not t or re.fullmatch(r"page \d+( of \d+)?|\d+", t, re.I):
            continue
        if SECTION.match(t):
            section = SECTION.match(t).group(1).lower(); role = None; continue
        m = RANGE.search(t)
        if m and section not in ("education", "formation", "formación", "ausbildung"):
            role = dict(dates=m.group(0), text=t)
        nums = numbers_in(t)
        ctype = ("contact" if CONTACT.search(t) and section == "header" else
                 "header" if section == "header" else
                 "education" if section in ("education", "formation") else
                 "skill" if section in ("skills", "compétences", "languages", "langues", "certifications", "certification") else
                 "metric" if any(re.search(r"\d", n) for n in nums) else "duty")
        lines.append(dict(id=f"{prefix}{len(lines) + 1}", source=source, text=t, section=section,
                          employer=None, title=None, dates=role["dates"] if role and section not in ("header",) else None,
                          numbers=nums, own_role="unknown" if ctype in ("metric", "duty") else None,
                          claim_type=ctype, conflict=None))
    # role headers: the line holding a date range, and the line just before it if that line is not a bullet claim
    for i, l in enumerate(lines):
        if l["section"] in ("education", "formation") or not RANGE.search(l["text"]): continue
        head = [l]
        if i > 0 and not RANGE.search(lines[i - 1]["text"]) and lines[i - 1]["claim_type"] in ("duty", "metric") and len(lines[i - 1]["text"]) < 90:
            head.insert(0, lines[i - 1])
        title_line = head[0]["text"] if len(head) == 2 else RANGE.sub("", l["text"]).strip(" ·|,-–")
        parts = [p.strip() for p in ROLE_SPLIT.split(title_line, maxsplit=1) if p.strip()]
        if len(parts) < 2: parts = [p.strip() for p in title_line.rsplit(",", 1) if p.strip()]
        title, employer = (parts + [None, None])[:2]
        for h in head:
            h["claim_type"] = "header"; h["numbers"] = []; h["own_role"] = None; h["dates"] = l["dates"]
        j = lines.index(head[0])
        while j < len(lines) and lines[j]["section"] == l["section"]:
            if j > lines.index(l) and RANGE.search(lines[j]["text"]): break
            if j + 1 < len(lines) and j > lines.index(l) and RANGE.search(lines[j + 1]["text"]) and lines[j]["claim_type"] in ("duty", "metric") and len(lines[j]["text"]) < 90: break
            lines[j]["title"], lines[j]["employer"], lines[j]["dates"] = title, employer, l["dates"]
            j += 1
    return lines


def lint(text: str, lines, pages, ratio):
    issues = []
    for l in lines:
        for m in PLACEHOLDER.finditer(l["text"]):
            issues.append(dict(kind="unfilled_placeholder", line=l["id"], detail=m.group(0)))
    norm = Counter(re.sub(r"\W+", " ", l["text"].lower()).strip() for l in lines if len(l["text"]) > 25)
    for t, c in norm.items():
        if c > 1: issues.append(dict(kind="duplicate_line", line=None, detail=t[:80]))
    # date ranges → overlaps
    spans = []
    for l in lines:
        m = RANGE.search(l["text"])
        if m and l["section"] not in ("education", "formation"):
            y = [int(x) for x in re.findall(r"(?:19|20)\d\d", m.group(0))]
            end = y[1] if len(y) > 1 else 2100
            spans.append((y[0], end, l["id"]))
            if len(y) > 1 and y[1] < y[0]:
                issues.append(dict(kind="impossible_dates", line=l["id"], detail=m.group(0)))
    spans = sorted(set(spans))
    for a, b in zip(spans, spans[1:]):
        if b[0] < a[1] - 0 and b[0] > a[0]:
            issues.append(dict(kind="overlapping_roles", line=b[2], detail=f"{a[2]} {a[0]}-{a[1]} overlaps {b[2]} {b[0]}-{b[1]} (fine if a side role; label it)"))
    years = (max(s[1] if s[1] < 2100 else 2026 for s in spans) - min(s[0] for s in spans)) if spans else None
    score = 100
    if ratio >= 0.25: score -= 30
    secs = {l["section"] for l in lines}
    if not secs & {"experience", "professional experience", "work experience", "employment", "expérience", "expériences"}: score -= 20
    if not secs & {"education", "formation"}: score -= 20
    if not any(CONTACT.search(l["text"]) for l in lines[:8]): score -= 10
    if pages and years and pages > max(1, min(2, round(years / 10 + 0.49))): score -= 10 * (pages - max(1, min(2, round(years / 10 + 0.49))))
    if "�" in text: score -= 10
    return issues, dict(score=max(0, score), two_column_ratio=round(ratio, 3), pages=pages, career_years=years,
                        words=len(text.split()), sections=sorted(secs), roles_dated=len(spans))


def crosscheck(r_lines, l_lines):
    conflicts = []
    r_dates = {l["dates"] for l in r_lines if l["dates"]}
    for l in l_lines:
        m = RANGE.search(l["text"])
        if m and m.group(0) not in r_dates and l["section"] not in ("education", "formation"):
            conflicts.append(dict(line=l["id"], detail=f"LinkedIn date range '{m.group(0)}' not found verbatim on the resume"))
    return conflicts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", required=True); ap.add_argument("--linkedin"); ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run_ = run_dir(a.run)
    src = Path(a.resume)
    text, method, ratio, pages = extract(src)
    text = normalize(text)
    (run_ / "resume.txt").write_text(text)
    r_lines = ledger_lines(text, "R", "resume")
    issues, stats = lint(text, r_lines, pages, ratio)
    sources = [dict(kind="resume", path=src.name, sha256=sha256(text))]
    l_lines, li_status = [], "absent"
    if a.linkedin:
        if re.match(r"https?://", a.linkedin):
            li_status = "blocked"
            issues.append(dict(kind="linkedin_not_read", line=None,
                               detail="LinkedIn URL given; LinkedIn blocks automated reads. Try WebFetch once; if it fails, run resume-only and mark LinkedIn checks not_run."))
        else:
            lt, _, _, _ = extract(Path(a.linkedin)); lt = normalize(lt)
            (run_ / "linkedin.txt").write_text(lt)
            l_lines = ledger_lines(lt, "L", "linkedin"); li_status = "parsed"
            sources.append(dict(kind="linkedin", path=Path(a.linkedin).name, sha256=sha256(lt)))
            for c in crosscheck(r_lines, l_lines):
                issues.append(dict(kind="resume_linkedin_conflict", **c))
    ledger = dict(sources=sources, lines=r_lines + l_lines)
    errs = validate(ledger, "ledger")
    if errs: print("ledger schema errors:", *errs[:10], sep="\n  ")
    save(run_ / "ledger.json", ledger)
    report = dict(method=method, linkedin_status=li_status, language=detect_language(text), **stats, issues=issues,
                  action=("READ THE PDF PAGES AS IMAGES AND FIX resume.txt BY HAND" if stats["score"] < 70 else "ok"))
    save(run_ / "parse_report.json", report)
    print(f"parse score {stats['score']}  method {method}  two-column {ratio:.2f}  lines {len(r_lines)}+{len(l_lines)}  issues {len(issues)}")
    for i in issues[:15]: print("  -", i["kind"], i.get("line") or "", i["detail"])


if __name__ == "__main__":
    main()
