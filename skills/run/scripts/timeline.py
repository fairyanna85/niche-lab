#!/usr/bin/env python3
"""Career timeline from the fact ledger: one entry per role, with parsed dates and the scope stated for it.

parse_dates("Mar 2022 – Present") -> ("2022-03", None)   (None = ongoing)
Handles English, French, Spanish and German month names, numeric months, two-digit end years and year-only ranges.
"""
import re

MONTHS = {}
for i, names in enumerate([
    "jan january janv janvier ene enero januar jän jänner",
    "feb february fév fev février fevrier febrero februar",
    "mar march mars marzo märz maerz",
    "apr april avr avril abr abril",
    "may mai mayo",
    "jun june juin junio juni",
    "jul july juil juillet julio juli",
    "aug august août aout ago agosto",
    "sep sept september septembre septiembre",
    "oct october octobre octubre okt oktober",
    "nov november novembre noviembre",
    "dec december déc dec décembre decembre dic diciembre dez dezember"], start=1):
    for n in names.split(): MONTHS.setdefault(n, i)
ONGOING = r"(present|current|now|today|ongoing|aujourd[’']?hui|à ce jour|actuel(?:lement)?|en cours|presente|actualidad|actual|heute|derzeit|aktuell|bis heute)"
MON = r"([A-Za-zÀ-ÿ]{3,10})\.?"
PART = rf"(?:{MON}\s+(\d{{4}})|(\d{{1,2}})[/.](\d{{4}})|(\d{{4}})(?:[/.-](\d{{1,2}}))?)"


def _part(m, offset):
    mon, y1, num, y2, y3, num2 = m.group(offset, offset + 1, offset + 2, offset + 3, offset + 4, offset + 5)
    if y1:
        k = MONTHS.get(mon.lower().rstrip(".")[:10]) or MONTHS.get(mon.lower()[:3])
        return (int(y1), k) if k else None
    if y2: return (int(y2), int(num))
    if y3: return (int(y3), int(num2) if num2 and 1 <= int(num2) <= 12 else None)
    return None


def parse_dates(s):
    """Return (start, end) as 'YYYY-MM' strings; end is None when the role is ongoing. (None, None) if unparseable."""
    if not s: return (None, None)
    t = s.strip()
    m = re.search(rf"{PART}\s*(?:[–—-]|to|bis|à|a|au|hasta)\s*(?:{PART}|{ONGOING}|(\d{{2}})\b)", t, re.I)
    if m:
        a = _part(m, 1)
        if a is None: return (None, None)
        if m.group(13):
            end = None
        elif m.group(14):
            end = (a[0] // 100 * 100 + int(m.group(14)), None)
        else:
            end = _part(m, 7)
        fmt = lambda p, d: f"{p[0]:04d}-{(p[1] or d):02d}"
        return (fmt(a, 1), None if end is None else fmt(end, 12))
    m = re.search(rf"^{PART}$", t, re.I)
    if m:
        a = _part(m, 1)
        if a: return (f"{a[0]:04d}-{(a[1] or 1):02d}", f"{a[0]:04d}-{(a[1] or 12):02d}")
    return (None, None)


LOC = re.compile(r"^(remote|hybrid|emea|apac|amer|latam|north america|europe|emea & north america)$|,\\s*[A-Z]{2}$|^[A-Za-zÀ-ÿ .-]+,\\s*(france|uk|usa|united states|germany|spain|italy|canada)$|^(paris|london|new york|berlin|madrid|lyon)(,.*)?$", re.I)


def _clean(t, dates):
    t = (t or "").replace("\u200b", "").strip()
    if dates: t = t.replace(dates, "")
    t = re.sub(r"\s*[|·]\s*$|^\s*[|·]\s*", "", re.sub(r"\s{2,}.*$", "", t)).strip(" |·-–")
    return t


def build_timeline(ledger_lines, resumes=None):
    """One entry per distinct date range in the ledger. Real resumes parse messily (two columns, the company in the
    title field, the job title after the bullets), so roles are keyed by their date line, not by header order."""
    roles = _by_header(ledger_lines, resumes)
    groups, order = {}, []
    for l in ledger_lines:
        d = l.get("dates")
        if l.get("source") != "resume" or not d or parse_dates(d)[0] is None: continue
        if d not in groups: groups[d] = []; order.append(d)
        groups[d].append(l)
    if len(order) < len(roles): return roles
    scope_by_emp = {e['employer'].lower(): e.get('scope') for r in resumes or [] for e in r.get('experience', []) if e.get('scope')}
    out = []
    for d in order:
        ls = groups[d]; start, end = parse_dates(d)
        cands = [l["employer"] for l in ls if l.get("employer") and not LOC.search(l["employer"].strip())] or \
                [l["title"] for l in ls if l.get("title") and not LOC.search(l["title"].strip())]
        company = max(set(cands), key=cands.count) if cands else ""
        heads = []
        for l in ls:
            if l.get("claim_type") != "header": continue
            segs = [_clean(x, d) for x in re.split(r"\s[|·]\s", l["text"].replace("\u200b", ""))]
            segs = [x for x in segs if x and x.lower() != company.lower() and not LOC.search(x) and len(x) > 3 and parse_dates(x)[0] is None]
            if segs: heads.append(" · ".join(segs))
        title = heads[0] if heads else company
        if company and title != company: title = re.sub(rf"\s*[—–-]\s*{re.escape(company)}\s*$", "", title, flags=re.I)
        out.append(dict(employer=company or title, title=title, dates=d, start=start, end=end, scope=scope_by_emp.get((company or '').lower()),
                        n_metrics=sum(1 for l in ls if l.get("claim_type") == "metric"), ledger_ids=[l["id"] for l in ls]))
    return out


def _by_header(ledger_lines, resumes=None):
    """Roles in reverse-chronological order of the ledger, with stated scope and the count of measured claims."""
    roles, cur = [], None
    scopes = {}
    for r in resumes or []:
        for e in r.get("experience", []):
            if e.get("scope"): scopes.setdefault((e["employer"], e["title"]), e["scope"])
    for l in ledger_lines:
        if l.get("source") != "resume": continue
        if l.get("claim_type") == "header" and l.get("employer") and l.get("title") and not (cur and cur["employer"] == l["employer"] and cur["title"] == l["title"]):
            start, end = parse_dates(l.get("dates"))
            cur = dict(employer=l["employer"], title=l["title"], dates=l.get("dates"), start=start, end=end,
                       scope=scopes.get((l["employer"], l["title"])), n_metrics=0, ledger_ids=[l["id"]])
            roles.append(cur)
        elif cur and l.get("employer") == cur["employer"]:
            cur["ledger_ids"].append(l["id"])
            if l.get("claim_type") == "metric": cur["n_metrics"] += 1
    return roles
