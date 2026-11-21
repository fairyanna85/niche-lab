"""Cycle 4: generic seniority bands and pay normalisation for any field."""
import pytest
from ladder import band_for_title, BANDS6
from pay import annualize, pool_by_currency


@pytest.mark.parametrize("title,band", [
    ("Line Cook", "entry"), ("Junior Engineer", "entry"), ("Registered Nurse, ICU", "experienced"), ("Site Engineer", "experienced"),
    ("Charge Nurse", "lead"), ("Senior Civil Engineer", "lead"), ("Principal Engineer, Water Resources", "lead"),
    ("General Manager", "manager"), ("Nurse Manager, Cardiac ICU", "manager"), ("Construction Manager", "manager"),
    ("Director of Nursing", "director"), ("Head of Partnerships", "director"), ("Area Manager, Multi-unit", "director"),
    ("VP Strategic Partnerships", "executive"), ("Chief Operating Officer", "executive")])
def test_band(title, band):
    assert band_for_title(title) == band


def test_bands_ordered():
    assert BANDS6 == ["entry", "experienced", "lead", "manager", "director", "executive"]


def test_annualize():
    assert annualize(40, "hour") == 83200
    assert annualize(400, "day") == 92000
    assert annualize(5000, "month") == 60000
    assert annualize(90000, "year") == 90000
    with pytest.raises(ValueError): annualize(1, "fortnight")


def test_currencies_never_pooled():
    pools = pool_by_currency([(100000, "USD"), (90000, "EUR"), (120000, "USD")])
    assert pools == {"USD": [100000, 120000], "EUR": [90000]}
