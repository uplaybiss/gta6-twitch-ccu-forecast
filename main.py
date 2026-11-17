"""Forecast hourly Twitch viewers with historical launch profiles."""

import json
import os
import sys
from math import exp, log, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analog import analog_quantiles, nearest_profiles, release_profiles

NORMAL_QUANTILES = (-1.645, -0.674, 0.0, 0.674, 1.645)


def forecast(case):
    first_hour = next(row for row in case["known"] if row["hour"] == 1)
    anchor = log(max(1, first_hour["viewers"]))
    profiles = nearest_profiles(release_profiles(case["comparables"]), anchor)
    rows = []
    for requested in case["forecast"]:
        hour = requested["hour"]
        if profiles:
            changes = analog_quantiles(profiles, hour, case["levels"])
        else:
            changes = [z * 0.15 * sqrt(hour - 1) for z in NORMAL_QUANTILES]
        counts = [round(min(1e9, max(0.01, exp(anchor + change))), 2) for change in changes]
        rows.append({"hour": hour, "q": counts})
    return {"hours": rows}


def main():
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(input_dir.glob("*.in")):
        case = json.loads(source.read_text(encoding="utf-8"))
        payload = json.dumps(forecast(case), separators=(",", ":"), allow_nan=False)
        (output_dir / (source.stem + ".out")).write_bytes((payload + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
