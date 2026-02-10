from src.systems.profile_engine import PROFILE_BASELINES


def compute_final_stats(persistent):
    """
    Compute the 6 final stats from:
    1. Profile baseline
    2. Cosmetic tag modifiers
    3. Decision outcome modifiers
    """
    profile = persistent.get("profile", "first_gen")
    cosmetic_tags = persistent.get("cosmetic_tags", {})
    decisions = persistent.get("decisions", {})

    # 1. Start with base stats
    stats = dict(PROFILE_BASELINES[profile])

    # 2. Apply cosmetic modifiers
    wealth = cosmetic_tags.get("wealth", 0)
    striving = cosmetic_tags.get("striving", 0)
    rebellion = cosmetic_tags.get("rebellion", 0)

    stats["money"] += wealth * 3
    stats["connections"] += wealth * 2
    stats["integrity"] -= wealth * 2
    stats["stress"] += striving * 2
    stats["reputation"] += striving * 2
    stats["time"] -= striving * 2
    stats["integrity"] += rebellion * 3
    stats["reputation"] -= rebellion * 2
    stats["connections"] -= rebellion * 2

    # 3. Apply decision modifiers
    for college_name, result in decisions.items():
        if result == "accepted":
            stats["reputation"] += 10
            stats["stress"] += 5
        elif result == "waitlisted":
            stats["stress"] += 10
        elif result == "rejected":
            stats["reputation"] -= 5
            stats["integrity"] += 5

    # 4. Enforce Legacy integrity cap
    if profile == "legacy":
        stats["integrity"] = min(stats["integrity"], 40)

    # 5. Clamp all stats to 0-100
    for key in stats:
        stats[key] = max(0, min(100, stats[key]))

    return stats
