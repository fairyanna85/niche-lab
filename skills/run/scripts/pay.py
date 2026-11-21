"""Pay normalisation: any unit → annual, never pooled across currencies."""
from collections import defaultdict

FACTOR = {"hour": 2080, "day": 230, "week": 52, "month": 12, "year": 1}


def annualize(amount, unit: str) -> float:
    if unit not in FACTOR: raise ValueError(f"unknown pay unit {unit!r}; use one of {sorted(FACTOR)}")
    return round(amount * FACTOR[unit], 2) if FACTOR[unit] != 1 else amount


def pool_by_currency(points):
    out = defaultdict(list)
    for amount, cur in points: out[cur].append(amount)
    return dict(out)
