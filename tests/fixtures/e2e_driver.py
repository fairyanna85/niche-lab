#!/usr/bin/env python3
"""Offline end-to-end driver. Plays the agent's role DETERMINISTICALLY for three fictional candidates in distant fields,
so every script in the pipeline is exercised outside partnerships. Agent judgement is replaced by fixed rules:
coding = cue matching, prose = templates built from script outputs. Real runs use the agent for these steps."""
import argparse, json, re, subprocess, sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "skills" / "run" / "scripts"
sys.path.insert(0, str(S))
from make_postings import build  # noqa: E402

RESUMES = {
 "nursing": """MARIA OKAFOR
Charge Nurse, Medical ICU
Chicago, IL · maria.okafor@example.com · linkedin.com/in/maria-okafor-example
SUMMARY
Critical care nurse with 9 years in adult intensive care units.
EXPERIENCE
Charge Nurse, Medical ICU — Lakeview Teaching Hospital
Jun 2020 – Present · Chicago, IL
Lead a 24-bed unit on night shift with 11 nurses per shift and set staffing assignments
Precepted 14 new graduate nurses through orientation
Cut central-line infections from 4 to 1 per year through a bundle audit
Run the daily safety huddle
Registered Nurse, ICU — Riverbend Medical Center
Aug 2016 – May 2020 · Evanston, IL
Cared for ventilated and post-surgical patients in a 16-bed ICU, including cardiac surgery recoveries, continuous renal replacement and proning during respiratory surges
Joined the sepsis response team that reduced time to antibiotics by 22 minutes
Registered Nurse, Medical-Surgical — Oak Park Community Hospital
Jul 2015 – Jul 2016 · Oak Park, IL
Managed 5 to 6 patients per shift on a 30-bed unit
EDUCATION
BSN, Lakeshore College of Nursing, 2015
CERTIFICATIONS
RN license, Illinois · BLS · ACLS · CCRN
SKILLS
Epic · ventilator management · precepting · patient and family communication
LANGUAGES
English · Spanish (conversational)
""",
 "civil": """DANIEL REYES
Project Engineer, Transportation
Denver, CO · daniel.reyes@example.com · linkedin.com/in/daniel-reyes-example
SUMMARY
Civil engineer with 8 years on public road and drainage projects.
EXPERIENCE
Project Engineer — Foothill Road Partners
Mar 2021 – Present · Denver, CO
Delivered a $14M interchange rebuild 3 weeks ahead of schedule
Coordinate 6 subcontractors
Prepared cost estimates and managed a $2.5M change-order budget
Review shop drawings and submittals against CDOT specifications
Site Engineer — Granite Peak Builders
Jun 2017 – Feb 2021 · Aurora, CO
Designed stormwater drainage for 4 subdivisions in AutoCAD Civil 3D, from hydrology models through county approval and construction support on site
Mentored 2 junior engineers through the EIT exam
Built schedules in Primavera P6 for crews of 40
Engineering Intern — Clearwater County Public Works
May 2016 – Aug 2016 · Golden, CO
Surveyed 12 culverts for a county condition report
EDUCATION
BS Civil Engineering, Front Range State University, 2017
CERTIFICATIONS
Professional Engineer (PE), Colorado · OSHA 30
SKILLS
AutoCAD Civil 3D · Primavera P6 · cost estimating · stormwater design
LANGUAGES
English · Spanish
""",
 "restaurant": """PRIYA NAIR
General Manager, Full-Service Restaurant
Austin, TX · priya.nair@example.com · linkedin.com/in/priya-nair-example
SUMMARY
Restaurant manager with 10 years in full-service and high-volume dining.
EXPERIENCE
General Manager — Barton Springs Bistro
Apr 2021 – Present · Austin, TX
Run a $4.2M restaurant with 46 hourly employees and own the P&L
Cut food cost from 33% to 29% in 12 months with weekly inventory counts
Raised online review scores from 4.1 to 4.6 stars
Opened a second patio service
Assistant General Manager — Riverside Grill House
Jan 2017 – Mar 2021 · San Antonio, TX
Trained 8 shift leads, 3 of whom became managers
Ordered from 15 vendors and kept health inspections at 100% across four years, including two unannounced county audits and a full kitchen remodel
Shift Lead — Market Street Kitchen
Jun 2015 – Dec 2016 · San Antonio, TX
Handled guest complaints and service recovery on 300-cover nights
EDUCATION
BA Hospitality Management, Hill Country University, 2015
CERTIFICATIONS
ServSafe Food Manager
SKILLS
Toast POS · P&L management · inventory · hiring and training
LANGUAGES
English · Spanish
""",
}
MODULES = {
 "nursing": [("nu_icu", "ICU or critical-care experience", [r"\bicu\b", r"critical care", r"intensive care"]),
             ("nu_acls", "BLS and ACLS certification", [r"\bbls\b", r"\bacls\b"]),
             ("nu_ccrn", "CCRN certification", [r"\bccrn\b"]),
             ("nu_bsn", "BSN degree", [r"\bbsn\b", r"bachelor of science in nursing"]),
             ("nu_vent", "Ventilated and post-surgical patients", [r"ventilat", r"post-surgical"]),
             ("nu_charge", "Charge nurse experience", [r"charge nurse"]),
             ("nu_qi", "Quality improvement and infection control", [r"quality improvement", r"infection"]),
             ("nu_staff", "Staffing assignments", [r"staffing assignment"]),
             ("nu_comm", "Patient and family communication", [r"family communication", r"patient and family"])],
 "civil": [("ce_pe", "PE licence or EIT path", [r"\bpe\b", r"professional engineer", r"\beit\b"]),
           ("ce_c3d", "AutoCAD Civil 3D", [r"civil 3d", r"autocad"]),
           ("ce_osha", "OSHA site safety", [r"osha"]),
           ("ce_est", "Cost estimates and project budgets", [r"cost estimat", r"project budget"]),
           ("ce_subs", "Coordinates subcontractors and crews", [r"subcontractor", r"site crews"]),
           ("ce_cdot", "CDOT standards", [r"\bcdot\b"]),
           ("ce_subm", "Shop drawings and submittals", [r"shop drawing", r"submittal"]),
           ("ce_p6", "Primavera P6 scheduling", [r"primavera", r"\bp6\b"]),
           ("ce_storm", "Stormwater and drainage design", [r"stormwater", r"drainage"])],
 "restaurant": [("rs_pnl", "Owns P&L, food and labor cost", [r"p&l", r"food cost", r"labor cost"]),
                ("rs_team", "Hires, trains and schedules hourly teams", [r"hourly", r"schedul", r"hire"]),
                ("rs_safe", "ServSafe food manager certification", [r"servsafe", r"food manager"]),
                ("rs_guest", "Guest satisfaction and reviews", [r"guest satisfaction", r"review"]),
                ("rs_pos", "Toast POS and scheduling software", [r"\btoast\b", r"\bpos\b"]),
                ("rs_inv", "Inventory, ordering and vendors", [r"inventor", r"ordering", r"vendor"]),
                ("rs_health", "Health code compliance", [r"health code", r"health inspection"]),
                ("rs_coach", "Coaches shift leads and managers", [r"shift lead", r"assistant manager"]),
                ("rs_recov", "Guest complaints and service recovery", [r"complaint", r"service recovery"])],
}
NICHES = {  # role family x band groups; every field gets three candidate niches
 "nursing": [("ICU staff and charge nursing, Chicago", ["experienced", "lead"], "lead"), ("Nurse leadership, ICU, Chicago", ["lead", "manager"], "manager"), ("Hospital nursing, all levels, Chicago", None, "experienced")],
 "civil": [("Project and site engineering, transportation, Denver", ["experienced"], "experienced"), ("Senior and principal civil engineering, Denver", ["lead"], "lead"), ("Construction and civil engineering, all levels, Denver", None, "manager")],
 "restaurant": [("Restaurant general management, full service, Austin", ["manager"], "manager"), ("Assistant and kitchen management, Austin", ["lead", "manager"], "lead"), ("Multi-unit and restaurant management, Austin", None, "director")],
}


def sh(*a):
    r = subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    if r.returncode not in (0,) and "gates.py" not in str(a[0]):
        print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit(f"step failed: {a}")
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--field", required=True); ap.add_argument("--run", required=True); a = ap.parse_args()
    F, run = a.field, Path(a.run); run.mkdir(parents=True, exist_ok=True)
    (run / "run_config.json").write_text(json.dumps(dict(skill_version="2.1.0", fictional=True, relaxed=True, depth="quick", data_window="synthetic fixture postings", banner="Synthetic test fixture.")))
    (run / "resume.in.txt").write_text(RESUMES[F])
    sh(S / "ingest.py", "--resume", run / "resume.in.txt", "--run", run)
    led = json.loads((run / "ledger.json").read_text())["lines"]
    # induced module (phase 2b)
    fam = f"induced-{F}"; (run / "codebooks").mkdir(exist_ok=True)
    mod = dict(module=fam, version=1, status="UNTESTED", title_patterns=[F],
               codes=[dict(id=i, label=l, posting_rule="2 if required; 1 if preferred or mentioned.", resume_cues=c) for i, l, c in MODULES[F]])
    (run / "codebooks" / f"{fam}.yml").write_text(yaml.safe_dump(mod, sort_keys=False))
    sh(S / "induce_codebook.py", "validate", run / "codebooks" / f"{fam}.yml")
    from common import codebook
    codes, _ = codebook([fam], run)
    # niches + postings (phases 2-3)
    fx = build()[F]; niches = []
    for k, (label, bands, sen) in enumerate(NICHES[F]):
        niches.append(dict(id=f"n{k + 1:02d}", label=label, role_family=F, seniority=sen, segment=label.split(",")[0], city=fx[0]["city"], module=fam, origin="current" if k == 0 else "adjacent_role",
                           triage=dict(score=7), screen=dict(n_postings=0, n_employers=0), verdict="keep", reason="",
                           pref_checks=[dict(pref="city", matched=True, grade="stated")], _bands=bands))
    rawdir = run / "tmp"; rawdir.mkdir(exist_ok=True)
    for j, p in enumerate(fx):
        ids = [n["id"] for n in niches if n["_bands"] is None or p["band"] in n["_bands"]]
        t = rawdir / f"{j}.txt"; t.write_text(p["text"])
        meta = dict(niche_ids=ids, company=p["company"], title=p["title"] + f" #{j}", city=p["city"], level=p["band"], segment=None, url=f"https://example.com/jobs/{F}/{j}",
                    source_type="employer", era="now", date_seen="2026-11-10", date_evidence="fixture")
        pid = sh(S / "postings.py", "store", "--run", run, "--text-file", t, "--meta", json.dumps(meta)).stdout.split()[0]
        cs = {}
        for c in codes:
            hits = [r for r in p["reqs"] if any(re.search(rx, r, re.I) for rx in c.get("resume_cues", []))]
            cs[c["id"]] = 2 if any(re.search(r"required|must", h, re.I) for h in hits) else (1 if hits else 0)
        cj = rawdir / f"{j}.codes.json"
        cj.write_text(json.dumps(dict(codes=cs, must_haves=p["reqs"][:5], phrases=p["reqs"][:2], builder_verbs=sum(w in p["text"].lower() for w in ("lead", "launch", "drive", "build")),
                                      maintain_verbs=sum(w in p["text"].lower() for w in ("manage", "maintain", "support", "coordinate")), years_required=p["years"],
                                      salary_min=p["pay"]["min"], salary_max=p["pay"]["max"], currency=p["pay"]["currency"], pay_unit=p["pay"]["unit"], level=p["band"])))
        sh(S / "postings.py", "code", "--run", run, "--id", pid, "--codes-json", cj)
    for n in niches: n.pop("_bands")
    (run / "niches.json").write_text(json.dumps(dict(niches=niches), indent=1))
    recs = [json.loads(l) for l in (run / "postings" / "postings.jsonl").read_text().splitlines()]
    sec = [dict(id=r["id"], codes={k: (v if i % 5 else (1 if v == 0 else v)) for i, (k, v) in enumerate(r["codes"].items())}) for r in recs[:8]]
    (run / "postings" / "second.jsonl").write_text("".join(json.dumps(x) + "\n" for x in sec))
    sh(S / "postings.py", "liveness", "--run", run, "--today", "2026-11-12")
    sh(S / "postings.py", "validate", "--run", run)
    # profile + evidence (phase 1)
    sh(S / "fit.py", "prefill", "--run", run, "--modules", fam)
    ev = json.loads((run / "evidence.json").read_text())
    for v in ev.values(): v["reviewed"] = True
    (run / "evidence.json").write_text(json.dumps(ev))
    exp = [l for l in led if l.get("employer")]
    band = "Manager" if F == "restaurant" else "IC"
    G = lambda v, ids, g="stated": dict(value=v, grade=g, evidence=ids)
    first = exp[0]["id"]
    prof = dict(candidate=dict(display_name=led[0]["text"].title() + " (fictional)", city=fx[0]["city"], languages=["English", "Spanish"], linkedin_status="absent"),
                fields=dict(role_family=G(F, [first]), seniority_band=G(band, [first]), level_map=G("as titled", [first], "inferred1"), industry=G(F, [first]), side_of_market=G("employer", [first], "inferred1"),
                            span_people=G("see ledger", [first], "inferred1"), span_budget_or_revenue=G(None, [], "absent"), own_role=G("led", [first], "inferred1"), years_experience=G(9, [first]),
                            current_pay_band_est=G({"mid": None, "currency": "USD"}, [first], "inferred1"), work_auth_signals=G("US career", [first], "inferred1"), positioning=G(f"An experienced {F} professional.", [first], "inferred1")),
                revealed_preferences=dict(employer_types=G([], [], "absent"), cities=G([fx[0]["city"]], [first]), median_tenure_years=G(3, [first]), company_stage=G("unknown", [], "absent"), mobility=G("one region", [first], "inferred1")),
                strengths=[dict(label=exp[i]["text"][:60], grade="stated", evidence=[exp[i]["id"]]) for i in range(0, min(4, len(exp)))],
                edges=[dict(label="Bilingual", evidence=[first], codes=["lang"])], disclosure_risks=[])
    (run / "profile.json").write_text(json.dumps(prof, indent=1))
    ids = [n["id"] for n in niches]
    for n in ids: sh(S / "analyze.py", "--run", run, "--niche", n)
    sh(S / "niches.py", "screen", "--run", run)
    kept = [n["id"] for n in json.loads((run / "niches.json").read_text())["niches"] if n["verdict"] == "keep"]
    for n in kept: sh(S / "fit.py", "score", "--run", run, "--niche", n)
    sh(S / "niches.py", "qualify", "--run", run)
    q = json.loads((run / "qualification.json").read_text())
    for n in kept:
        sh(S / "fit.py", "per-posting", "--run", run, "--niche", n); sh(S / "fit.py", "ladder", "--run", run, "--niche", n)
        emps = json.loads((run / "niches" / n / "analysis.json").read_text())["employers"]
        (run / "niches" / n / "access.json").write_text(json.dumps([dict(company=e, strength=1, path="Same city community: apply on the employer site and write to the hiring manager.", evidence="") for e in emps]))
    sh(S / "rank.py", "--run", run, "--draws", "200")
    rk = json.loads((run / "ranking.json").read_text()); order = rk["order"]
    N = {n["id"]: n for n in json.loads((run / "niches.json").read_text())["niches"]}
    # resumes (phase 8): ledger lines as written, grouped by role
    roles = {}
    for l in exp:
        roles.setdefault((l["employer"], l["title"], l["dates"]), []).append(l)
    num_line = next(l for l in exp if l["claim_type"] == "metric")
    res = []
    for n in order:
        lab = N[n]["label"].split(",")[0]
        experience = [dict(employer=e, title=t, dates=d, context=f"[What {e} is, its size]", scope=None,
                           bullets=[dict(text=l["text"], ledger=[l["id"]]) for l in ls if l["claim_type"] in ("metric", "duty")] or [dict(text=ls[0]["text"], ledger=[ls[0]["id"]])])
                      for (e, t, d), ls in roles.items()]
        res.append(dict(id=f"r-{n}", niche_id=n, header=dict(name=prof["candidate"]["display_name"].replace(" (fictional)", ""), headline=f"{lab} | {num_line['text'][:70]}", contact=led[2]["text"] if len(led) > 2 else ""),
                        profile=f"{lab}. {num_line['text']}.", skills=[l["text"] for l in led if l["claim_type"] == "skill"][:6] or ["—"], experience=experience,
                        education=[l["text"] for l in led if l["claim_type"] == "education"] or ["—"], placeholders=len(roles)))
    (run / "resumes.json").write_text(json.dumps(res, indent=1))
    # LinkedIn (phase 8b)
    top = res[0]; body = " ".join(l["text"] + "." for l in exp if l["claim_type"] in ("metric", "duty"))
    li = dict(niche_id=order[0], headline=top["header"]["headline"][:200], about=(num_line["text"] + ". " + body)[:2500],
              experience=[dict(employer=e["employer"], title=e["title"], dates=e["dates"], description="\n".join(b["text"] for b in e["bullets"])[:1900], ledger=[i for b in e["bullets"] for i in b["ledger"]]) for e in top["experience"]],
              skills=(top["skills"] + ["Communication", "Scheduling", "Training", "Safety", "Planning"])[:10], open_to_titles=[N[order[0]]["label"].split(",")[0][:60]], alternates=[], featured=[])
    (run / "linkedin.json").write_text(json.dumps(li, indent=1))
    # narrative (phase 10) from script outputs only
    def nb(n):
        an = json.loads((run / "niches" / n / "analysis.json").read_text()); top3 = [r["label"] for r in an["prevalence"][:3]]
        d = lambda t: dict(do_this=[t])
        return dict(demand=dict(insight=f"Most asked: {', '.join(top3)}.", do_this=[f"Lead with evidence for {top3[0].lower()}."]), change=d("Watch the trend as more archive postings are found."),
                    language=dict(use=[k["term"] for k in an["language"]["keyness"][:4]], avoid=[], do_this=["Use the niche's own words in the headline."]),
                    fit=dict(fixes={}, do_this=["Surface the evidence the fix ladder lists first."]), employers=d("Approach the top three employers this week."), access=d("Apply on the employer site within 72 hours."),
                    pitch=dict(one_liner=f"{N[n]['label'].split(',')[0]}: {num_line['text']}.", proof_points=[num_line["text"]], objections=[dict(objection="Why this move?", answer="[Your reason]")], do_this=["Rehearse the pitch aloud."]),
                    pay=dict(anchor="Ask for the band's 75th percentile.", walk_away="[Your floor]", script="Counter once with the 75th percentile.", do_this=["Counter once."]),
                    peers=d("—"), plan30=[dict(week="Week 1", actions=["Fill the blanks", "Send three approaches"])])
    nar = dict(summary=dict(headline=f"Run {N[order[0]]['label']} first.", run_now=order[:2], fixes=[dict(text="Fill the company context lines.", why="Every role lacks one.")], findings=[dict(title="The core", body="What every niche asks for, from its postings."), dict(title="The new demands", body="What is asked and not on the record."), dict(title="The rare proof", body="What the record proves that few postings require.")],
                            gaps=[], narrative=f"A {F} professional with measurable results.", do_this=["Start the top two niches this week."]),
               profile_view=dict(do_this=["Confirm the inferred fields."]), portfolio=dict(do_this=["Run the top two niches in parallel."]), funnel=dict(do_this=["Log every approach."]),
               niches={n: nb(n) for n in order}, method_steps=["fixture run"], limits=["synthetic postings"], sources=[],
               plan12=[dict(week="1", track="Resume", action="Fill the blanks", target="0 blanks"), dict(week="2-6", track="Approaches", action="Two approaches a week", target="10 approaches")],
               journey=dict(acts=[dict(act=a, question=q, answer=ans, learned=[], handover=h) for a, q, ans, h in [
                   ("cover", "What can the market do with this record?", "The postings in each niche were read and coded against the resume.", "It starts with what you bring."),
                   ("you", "What do you bring, on the evidence?", "Every strength below is traced to a line of the resume.", "That is the supply. Now, who is asking for it?"),
                   ("market", "Who is asking for it, and what do they want?", "Each niche's requirements, pay and liveness, from its postings.", "That is the demand. Who else is answering it?"),
                   ("peers", "Who else supplies this, and what is rare about you?", "Years asked, level mix and the benchmarks for getting hired.", "Here is what they add up to."),
                   ("verdict", "Where should you aim, and why?", f"Run {N[order[0]]['label']} first.", "Here is how to run it."),
                   ("course", "What exactly do you do, send and say?", "Fill the blanks, send the first versions, log every approach.", None),
                   ("method", "How was this measured, and what are its limits?", "Synthetic postings coded by fixed rules; see the limits.", None)]]))
    (run / "narrative.json").write_text(json.dumps(nar, indent=1))
    sh(S / "gates.py", "--run", run)
    sh(S / "gates.py", "--run", run, "--linkedin")
    sh(S / "baseline.py", "--run", run)
    sh(S / "render_linkedin.py", "--run", run)
    sh(S / "assemble.py", "--run", run)
    sh(S / "build_report.py", "--results", run / "results.json", "--out", run / "out" / "report.html")
    print("ok", F, order)


if __name__ == "__main__":
    main()
