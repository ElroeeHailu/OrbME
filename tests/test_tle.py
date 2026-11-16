import math

import pytest

from orbme.constants import MU, R_EARTH
from orbme.tle import checksum, parse_tle

# A classic ISS TLE from Sept 2008, used as fixed test data
ISS = (
    "ISS (ZARYA)",
    "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927",
    "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537",
)


def test_checksum_valid():
    assert checksum(ISS[1])
    assert checksum(ISS[2])


def test_checksum_rejects_corrupted_line():
    bad = ISS[2][:-1] + "0"          # same line, wrong last digit
    assert not checksum(bad)


def test_parse_rejects_bad_checksum():
    bad = ISS[2][:-1] + "0"
    with pytest.raises(ValueError):
        parse_tle(ISS[0], ISS[1], bad)


def test_fields():
    t = parse_tle(*ISS)
    assert t.name == "ISS (ZARYA)"
    assert t.norad_id == 25544
    assert math.isclose(math.degrees(t.inclination), 51.6416)
    assert math.isclose(math.degrees(t.raan), 247.4627)
    assert t.eccentricity == 0.0006703
    assert math.isclose(math.degrees(t.arg_perigee), 130.5360)
    assert math.isclose(math.degrees(t.mean_anomaly), 325.0288)


def test_epoch():
    t = parse_tle(*ISS)
    assert (t.epoch.year, t.epoch.month, t.epoch.day) == (2008, 9, 20)
    assert (t.epoch.hour, t.epoch.minute) == (12, 25)
    assert t.epoch.tzinfo is not None


def test_semi_major_axis_is_iss_like():
    t = parse_tle(*ISS)
    a = (MU / t.mean_motion**2) ** (1 / 3)
    altitude = a - R_EARTH
    assert 6700 < a < 6800
    assert 300 < altitude < 400       # ISS was ~353 km up in 2008