"""Shared helpers for every niche-lab script. Stdlib + numpy/scipy/statsmodels/yaml/jsonschema."""
from __future__ import annotations
import hashlib, json, math, os, re, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[1]
SCHEMAS = SKILL / "schemas"
CODEBOOKS = SKILL / "codebooks"

LEVELS = ["IC", "Mgr", "SrMgr", "Dir", "SrDir", "Head", "VP", "SVP", "C"]
BANDS = {"IC": "IC", "Mgr": "Manager", "SrMgr": "Manager", "Dir": "Director", "SrDir": "Director",
         "Head": "Head-VP", "VP": "Head-VP", "SVP": "Head-VP", "C": "C"}

# Thresholds (rubrics 05, 06, 10, 12). A run may relax them with --relaxed; the report then prints a banner.
THRESH = dict(min_postings=15, min_employers=8, stats_n=30, archive_n=15, peers_n=8, coverage_keep=0.40)
RELAXED = dict(min_postings=8, min_employers=5, stats_n=30, archive_n=10, peers_n=8, coverage_keep=0.40)


def load(path):
    path = Path(path)
    if path.suffix == ".jsonl":
        return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    return json.loads(path.read_text())


def save(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".jsonl":
        path.write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in obj))
    else:
        path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=_default))
    return path


def _default(o):
    try:
        import numpy as np
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return None if math.isnan(o) else float(o)
        if isinstance(o, np.ndarray): return o.tolist()
    except ImportError:
        pass
    return str(o)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def codebook(modules, run=None):
    """Load core + named modules. Run-specific (induced) modules live in RUN/codebooks/ and win over shipped ones.
    Returns (ordered list of code dicts, {id: code})."""
    import yaml
    names = ["core"] + [m for m in modules if m != "core"]
    codes = []
    for m in names:
        f = Path(run) / "codebooks" / f"{m}.yml" if run else None
        f = f if f and f.exists() else CODEBOOKS / f"{m}.yml"
        cb = yaml.safe_load(f.read_text())
        for c in cb["codes"]:
            c = dict(c); c["module"] = m; codes.append(c)
    ids = [c["id"] for c in codes]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: raise SystemExit(f"duplicate code ids across modules: {dup}")
    return codes, {c["id"]: c for c in codes}


def validate(obj, schema_name):
    import jsonschema
    schema = load(SCHEMAS / f"{schema_name}.schema.json")
    v = jsonschema.Draft202012Validator(schema)
    errs = sorted(v.iter_errors(obj), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errs]


def run_dir(p) -> Path:
    p = Path(p); p.mkdir(parents=True, exist_ok=True); return p


def thresholds(run: Path):
    cfg = run / "run_config.json"
    if cfg.exists() and load(cfg).get("relaxed"):
        return dict(RELAXED), True
    return dict(THRESH), False


NUM_RE = re.compile(r"(?:[$€£]\s?)?\d[\d,.]*\s?(?:%|[kKmMbB]\b|\+)?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b", re.I)


def numbers_in(text: str):
    out = []
    for m in NUM_RE.finditer(text):
        t = m.group(0).strip().rstrip(".,")
        if re.fullmatch(r"(19|20)\d\d", t):  # years are dates, not claims
            continue
        if t: out.append(t)
    return out


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr); sys.exit(2)


STOP = {
    "en": "the and of to in for with on at by from as is are our you your experience managed led team".split(),
    "fr": "le la les des du de et en pour avec sur par une un dans au aux équipe expérience gestion responsable".split(),
    "es": "el la los las de del y en para con por una un equipo experiencia gestión responsable".split(),
    "de": "der die das und mit für von im zu den des ein eine team erfahrung leitung verantwortlich".split(),
}


def detect_language(text: str) -> str:
    words = re.findall(r"[a-zà-ÿßäöü']+", text.lower())
    score = {k: sum(1 for w in words if w in set(v)) for k, v in STOP.items()}
    return max(score, key=score.get) if any(score.values()) else "en"


HEADERS = {
    "en": dict(profile="Profile", experience="Experience", education="Education", skills="Skills", languages="Languages"),
    "fr": dict(profile="Profil", experience="Expérience professionnelle", education="Formation", skills="Compétences", languages="Langues"),
    "es": dict(profile="Perfil", experience="Experiencia profesional", education="Formación", skills="Competencias", languages="Idiomas"),
    "de": dict(profile="Profil", experience="Berufserfahrung", education="Ausbildung", skills="Kompetenzen", languages="Sprachen"),
}
