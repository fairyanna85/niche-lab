#!/usr/bin/env python3
"""Deterministic SYNTHETIC posting fixtures for three distant fields. Fictional employers; used only by offline tests.
Each posting: title, employer, city, level, pay (with unit), years, and ~150+ words of text mixing field requirements."""
import json, random
from pathlib import Path

FIELDS = {
    "nursing": dict(
        city="Chicago", unit="hour", pay=(42, 68), currency="USD",
        titles=[("Registered Nurse, ICU", "experienced"), ("Charge Nurse, Medical-Surgical", "lead"), ("Nurse Manager, Cardiac ICU", "manager"),
                ("ICU Staff Nurse", "experienced"), ("Clinical Nurse Educator", "lead")],
        employers=["Lakeshore General", "Northside Medical Center", "Prairie Health", "St. Brigid Hospital", "Wabash University Hospital", "Midway Community Health"],
        reqs=["Active RN license in the state of Illinois is required", "Current BLS and ACLS certification required", "CCRN certification preferred",
              "Minimum two years of ICU experience", "Experience with Epic electronic health records", "Ability to work 12-hour night shifts and weekends",
              "Precept and mentor new graduate nurses", "Lead daily safety huddles and escalate patient safety events", "Manage ventilated and post-surgical patients",
              "Bachelor of Science in Nursing (BSN) required", "Bilingual English/Spanish preferred", "Participate in quality improvement and infection-control audits",
              "Charge nurse experience preferred", "Manage staffing assignments for the unit", "Strong patient and family communication skills"]),
    "civil": dict(
        city="Denver", unit="year", pay=(78000, 145000), currency="USD",
        titles=[("Site Engineer", "experienced"), ("Project Engineer, Transportation", "experienced"), ("Senior Civil Engineer", "lead"),
                ("Construction Manager", "manager"), ("Principal Engineer, Water Resources", "lead")],
        employers=["Front Range Infrastructure", "Cherry Creek Civil", "Summit Transit Builders", "Platte River Engineering", "Mile High Structures", "Arapahoe Works"],
        reqs=["Professional Engineer (PE) license required, or EIT with PE within 12 months", "Proficiency in AutoCAD Civil 3D", "Experience with OSHA 30 site safety",
              "Prepare cost estimates and manage project budgets", "Coordinate subcontractors and site crews", "Five years of experience on public infrastructure projects",
              "Experience with CDOT standards and specifications", "Review shop drawings and submittals", "Lead design reviews with clients and agencies",
              "Use schedule software such as Primavera P6", "Travel to job sites up to 40% of the time", "Mentor junior engineers",
              "Stormwater and drainage design experience", "Bachelor's degree in civil engineering", "Write technical reports for public agencies"]),
    "restaurant": dict(
        city="Austin", unit="year", pay=(52000, 88000), currency="USD",
        titles=[("General Manager", "manager"), ("Assistant General Manager", "lead"), ("Kitchen Manager", "manager"),
                ("Restaurant Manager", "manager"), ("Area Manager, Multi-unit", "director")],
        employers=["Lone Star Kitchens", "Barton Creek Hospitality", "Rainey Street Group", "Congress Ave Dining", "Hill Country Grill Co.", "South Lamar Eats"],
        reqs=["Own the restaurant P&L, food cost and labor cost", "Hire, train and schedule a team of 40+ hourly employees", "Food Manager certification (ServSafe) required",
              "Three years of full-service restaurant management experience", "Drive guest satisfaction scores and online reviews", "Experience with Toast POS and scheduling software",
              "Open and close shifts, including nights, weekends and holidays", "Run inventory, ordering and vendor relationships", "Maintain health code and safety compliance",
              "Coach and develop shift leads and assistant managers", "Bilingual English/Spanish a plus", "Launch new menus and seasonal promotions",
              "Multi-unit experience preferred", "Use sales and labor data to make daily decisions", "Handle guest complaints and service recovery"]),
}
BOILER = ("We are an equal opportunity employer and value a diverse team. Our people are the reason guests, patients and clients return. "
          "This role offers competitive pay, health benefits, paid time off and a retirement plan with an employer match. "
          "You will join a team that cares about doing the work properly, learning every day and supporting one another through busy periods.")


def build(seed=7):
    out = {}
    for field, F in FIELDS.items():
        rng = random.Random(f"{seed}-{field}"); rows = []
        for i in range(15):
            title, band = F["titles"][i % len(F["titles"])]
            emp = F["employers"][i % len(F["employers"])]
            reqs = rng.sample(F["reqs"], rng.randint(7, 10))
            lo = round(rng.uniform(*F["pay"]) , 0 if F["unit"] == "year" else 2); hi = round(lo * rng.uniform(1.12, 1.35), 0 if F["unit"] == "year" else 2)
            text = (f"{emp} is hiring a {title} in {F['city']}. In this role you will be accountable for outcomes that matter to the people we serve. "
                    + " ".join(r + "." for r in reqs) + " " + BOILER + f" Pay range: {lo}–{hi} per {F['unit']}.")
            rows.append(dict(company=emp, title=title, city=F["city"], band=band, pay=dict(min=lo, max=hi, unit=F["unit"], currency=F["currency"]),
                             years=rng.choice([2, 3, 5]), reqs=reqs, text=text))
        out[field] = rows
    return out


if __name__ == "__main__":
    d = build()
    p = Path(__file__).parent / "postings_three_fields.json"
    p.write_text(json.dumps(d, indent=1))
    print({k: len(v) for k, v in d.items()}, "words/posting:", min(len(r["text"].split()) for v in d.values() for r in v))
