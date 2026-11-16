import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import requests

@dataclass(frozen=True)
class TLE:
    name: str
    line1: str
    line2: str
    norad_id: int
    epoch: datetime         #UTC
    inclination: float      #rad
    raan: float             
    eccentricity: float
    arg_perigee: float
    mean_anomaly: float
    mean_motion: float      #rad/s

def checksum(line: str) -> bool:
    total = 0
    for ch in line[:68]:
        if ch.isdigit():
            total += int(ch)
        elif ch == "-":
            total += 1
    return total % 10 == int(line[68])

def parse_tle(name: str, line1:str, line2:str) -> TLE:
    name = name.strip()
    line1 = line1.rstrip()
    line2 = line2.rstrip()

    if not line1.startswith("1 ") or not line2.startswith("2"):
        raise ValueError("Line 1 must start with '1' and Line 2 must start with '2'.")

    if not checksum(line1) or not checksum(line2):
        raise ValueError("TLE checksum failed - data might be corrupted.")

    norad_id = int(line2[2:7])
    inclination = math.radians(float(line2[8:16]))
    raan = math.radians(float(line2[17:25]))
    eccentricity = float(f"0.{line2[26:33]}")
    arg_perigee = math.radians(float(line2[34:42]))
    mean_anomaly = math.radians(float(line2[43:51]))
    mean_motion = float(line2[52:63]) * 2 * math.pi / 86400

    epoch = _parse_epoch(line1)

    return TLE(
        name=name,
        line1 = line1,
        line2 = line2,
        norad_id=norad_id,
        epoch=epoch,
        inclination=inclination,
        raan=raan,
        eccentricity=eccentricity,
        arg_perigee=arg_perigee,
        mean_anomaly=mean_anomaly,
        mean_motion=mean_motion
    )

def _parse_epoch(line1: str) -> datetime:
    year = int(line1[18:20])
    year = 2000 + year if year < 57 else 1900 + year
    day = float(line1[20:32])

    return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days= day - 1)



