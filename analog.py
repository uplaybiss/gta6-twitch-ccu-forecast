from math import log


def release_profiles(comparables):
    """Read complete UTC launch days and express them relative to hour one."""
    profiles = []
    for game in comparables:
        if "tier: target-history" in game["unlock"].lower():
            continue
        day = game["day_start"][:10]
        counts = {
            int(row["from"][11:13]): row["viewers"]
            for row in game["hourly"]
            if row["from"].startswith(day) and row["viewers"] is not None
        }
        if len(counts) != 24 or counts[0] < 1:
            continue
        anchor = log(counts[0])
        profile = [log(max(1, counts[hour])) - anchor for hour in range(24)]
        profiles.append((anchor, profile))
    return profiles


def quantile(values, level):
    ordered = sorted(values)
    position = level * (len(ordered) - 1)
    left = int(position)
    right = min(left + 1, len(ordered) - 1)
    return ordered[left] + (position - left) * (ordered[right] - ordered[left])


def nearest_profiles(profiles, anchor):
    nearest = sorted(profiles, key=lambda row: abs(row[0] - anchor))[:12]
    return [profile for _, profile in nearest]


def analog_quantiles(profiles, hour, levels):
    changes = [profile[hour - 1] for profile in profiles]
    return [quantile(changes, level) for level in levels]
