#!/usr/bin/env python3
"""Render resume objects (results.schema resumes[]) to ATS-safe single-column HTML, Markdown and PDF.

usage: render_resume.py --run RUN [--pdf]
Reads  RUN/resumes.json ; writes RUN/out/resume-<id>.{html,md,pdf}
PDF uses headless Chrome/Chromium if present (gate ats_parse needs it).
"""
import argparse, html, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load, HEADERS

CSS = """body{font-family:Arial,Helvetica,sans-serif;font-size:10.5pt;line-height:1.35;color:#111;max-width:7.3in;margin:0.45in auto}
h1{font-size:19pt;margin:0}.hl{font-size:11pt;margin:2px 0 4px}.ct{font-size:9.5pt;color:#333}
h2{font-size:10.5pt;letter-spacing:.06em;text-transform:uppercase;border-bottom:1px solid #999;margin:12px 0 5px;padding-bottom:2px}
.role{margin:7px 0 2px}.role b{font-size:10.5pt}.d{float:right}.ctx{font-size:9.5pt;color:#333;font-style:italic}.sc{font-size:9.5pt}
ul{margin:3px 0 0 16px;padding:0}li{margin:1px 0}p{margin:3px 0}@page{size:Letter;margin:0}"""


def esc(s): return html.escape(s or "")


def H(r): return HEADERS.get(r.get("language", "en"), HEADERS["en"])


def to_html(r):
    L = H(r)
    h = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{esc(r['header']['name'])}</title><style>{CSS}</style></head><body>",
         f"<h1>{esc(r['header']['name'])}</h1><div class='hl'>{esc(r['header']['headline'])}</div><div class='ct'>{esc(r['header'].get('contact', ''))}</div>",
         f"<h2>{L['profile']}</h2><p>{esc(r['profile'])}</p>", f"<h2>{L['experience']}</h2>"]
    for e in r["experience"]:
        h.append(f"<div class='role'><b>{esc(e['title'])}</b>, {esc(e['employer'])}<span class='d'>{esc(e['dates'])}{' · ' + esc(e['location']) if e.get('location') else ''}</span></div>")
        if e.get("context"): h.append(f"<div class='ctx'>{esc(e['context'])}</div>")
        if e.get("scope"): h.append(f"<div class='sc'>{esc(e['scope'])}</div>")
        h.append("<ul>" + "".join(f"<li>{esc(b['text'])}</li>" for b in e["bullets"]) + "</ul>")
    h.append(f"<h2>{L['education']}</h2>" + "".join(f"<p>{esc(x)}</p>" for x in r["education"]))
    h.append(f"<h2>{L['skills']}</h2><p>" + esc(" · ".join(r["skills"])) + "</p>")
    if r.get("languages"): h.append(f"<h2>{L['languages']}</h2><p>" + esc(" · ".join(r["languages"])) + "</p>")
    h.append("</body></html>")
    return "\n".join(h)


def to_md(r):
    L = H(r)
    m = [f"# {r['header']['name']}", f"**{r['header']['headline']}**", r["header"].get("contact", ""), "", f"## {L['profile']}", r["profile"], "", f"## {L['experience']}"]
    for e in r["experience"]:
        m += [f"**{e['title']}**, {e['employer']} — {e['dates']}" + (f" · {e['location']}" if e.get('location') else "")] + ([f"_{e['context']}_"] if e.get("context") else []) + ([e["scope"]] if e.get("scope") else [])
        m += [f"- {b['text']}" for b in e["bullets"]] + [""]
    m += [f"## {L['education']}"] + [f"- {x}" for x in r["education"]] + ["", f"## {L['skills']}", " · ".join(r["skills"])]
    if r.get("languages"): m += ["", f"## {L['languages']}", " · ".join(r["languages"])]
    return "\n".join(m) + "\n"


def to_docx(r, path):
    """ATS-safe Word file: one column, real headings, real bullets, no tables or text boxes."""
    import docx
    from docx.shared import Pt, Inches
    L = H(r); d = docx.Document()
    for sec in d.sections:
        sec.left_margin = sec.right_margin = Inches(0.7); sec.top_margin = sec.bottom_margin = Inches(0.55)
    st = d.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10.5)
    d.add_heading(r["header"]["name"], level=0)
    p = d.add_paragraph(); p.add_run(r["header"]["headline"]).bold = True
    if r["header"].get("contact"): d.add_paragraph(r["header"]["contact"])
    d.add_heading(L["profile"], level=1); d.add_paragraph(r["profile"])
    d.add_heading(L["experience"], level=1)
    for e in r["experience"]:
        p = d.add_paragraph(); p.add_run(f"{e['title']}, {e['employer']}").bold = True
        p.add_run(f"    {e['dates']}" + (f" · {e['location']}" if e.get("location") else ""))
        if e.get("context"): d.add_paragraph(e["context"]).runs[0].italic = True
        if e.get("scope"): d.add_paragraph(e["scope"])
        for b in e["bullets"]: d.add_paragraph(b["text"], style="List Bullet")
    d.add_heading(L["education"], level=1)
    for x in r["education"]: d.add_paragraph(x)
    d.add_heading(L["skills"], level=1); d.add_paragraph(" · ".join(r["skills"]))
    if r.get("languages"): d.add_heading(L["languages"], level=1); d.add_paragraph(" · ".join(r["languages"]))
    d.save(str(path))


def chrome():
    for c in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(c): return shutil.which(c)
    return None


def to_pdf(html_path: Path, pdf_path: Path):
    c = chrome()
    if not c: return False
    subprocess.run([c, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], capture_output=True, timeout=120)
    return pdf_path.exists()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); ap.add_argument("--pdf", action="store_true"); ap.add_argument("--docx", action="store_true")
    a = ap.parse_args(); run = Path(a.run); out = run / "out"; out.mkdir(exist_ok=True)
    for r in load(run / "resumes.json"):
        hp = out / f"resume-{r['id']}.html"; hp.write_text(to_html(r)); (out / f"resume-{r['id']}.md").write_text(to_md(r))
        ok = to_pdf(hp, out / f"resume-{r['id']}.pdf") if a.pdf else False
        if a.docx: to_docx(r, out / f"resume-{r['id']}.docx")
        print(r["id"], "html md" + (" pdf" if ok else "") + (" docx" if a.docx else ""))


if __name__ == "__main__":
    main()
