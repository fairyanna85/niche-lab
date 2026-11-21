"""Codebook YAML parses to what it says: unquoted commas in labels silently split entries (found in v2.1 review)."""
from pathlib import Path
import pytest, yaml

CB = sorted((Path(__file__).resolve().parents[1] / "skills" / "run" / "codebooks").glob("*.yml"))


@pytest.mark.parametrize("path", CB, ids=lambda p: p.name)
def test_labels_are_whole(path):
    d = yaml.safe_load(path.read_text()); codes = d["codes"] if isinstance(d, dict) else d
    for c in codes:
        assert isinstance(c.get("label"), str) and c["label"].count("(") == c["label"].count(")"), (path.name, c.get("id"), c.get("label"))
        assert all(v is not None for k, v in c.items()), (path.name, c.get("id"), [k for k, v in c.items() if v is None])
