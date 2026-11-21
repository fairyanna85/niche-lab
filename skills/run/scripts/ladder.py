"""Generic six-band seniority ladder for any field. Title rules are checked top-down; first match wins.
The agent may override a band per posting when the employer's own ladder says otherwise (record why in date_evidence/note)."""
import re

BANDS6 = ["entry", "experienced", "lead", "manager", "director", "executive"]
RULES = [
    ("executive", r"\b(chief|ceo|coo|cfo|cto|cmo|cro|president|vp|vice president|svp|evp|partner at|managing director|founder)\b"),
    ("director", r"\b(director|head of|area manager|regional manager|multi-?unit|district manager|general manager,? (region|division)|directeur|directrice|leiter|jefe de área)\b"),
    ("manager", r"\b(manager|superintendent|supervisor|chef de service|responsable|gérant|gerente|leiterin)\b"),
    ("lead", r"\b(lead|senior|sr\.?|principal|staff engineer|charge|chief engineer|specialist ii|educator|consultant senior|team leader|chef d'équipe)\b"),
    ("entry", r"\b(junior|jr\.?|entry|graduate|intern|apprentice|trainee|assistant(?! (general )?manager)|line cook|associate|technician i\b|stagiaire)\b"),
]
LEGACY = {"IC": "experienced", "Mgr": "manager", "SrMgr": "manager", "Dir": "director", "SrDir": "director", "Head": "director", "VP": "executive", "SVP": "executive", "C": "executive"}


def band_for_title(title: str) -> str:
    t = title.lower()
    if re.search(r"assistant (general )?manager", t): return "lead"
    for band, rx in RULES:
        if re.search(rx, t): return band
    return "experienced"


def band_of(posting_level: str) -> str:
    """Accept either a generic band or a legacy level code."""
    return posting_level if posting_level in BANDS6 else LEGACY.get(posting_level, "experienced")
