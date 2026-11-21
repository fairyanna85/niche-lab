import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "run" / "scripts"))


# Ratchet for whole tests (docs/CORRECTIVE-PLAN-v2.1.md §3.3): node ids listed in tests/ratchet.json are expected to
# fail (strict xfail). When one starts passing, the strict marker fails the run until it is deleted from the file.
import json as _json, pytest as _pytest
_RATCHET = ROOT / "tests" / "ratchet.json"


def pytest_collection_modifyitems(config, items):
    if not _RATCHET.exists(): return
    known = set(_json.loads(_RATCHET.read_text()))
    for it in items:
        if it.nodeid in known:
            it.add_marker(_pytest.mark.xfail(strict=True, reason="on the ratchet: expected to fail until its cycle lands"))
