from src.data.colleges import COLLEGE_LOOKUP


# How each profile aligns with hidden institutional dimensions
PROFILE_SCORES = {
    "legacy": {"capital": 8, "grit": 2, "performance": 4},
    "first_gen": {"capital": 2, "grit": 8, "performance": 5},
    "scholarship": {"capital": 3, "grit": 5, "performance": 8},
}

# How each college weighs cosmetic tags
COSMETIC_WEIGHTS = {
    "princesstown": {"wealth": 2.0, "striving": 0.5, "rebellion": -1.0},
    "cit": {"wealth": 0.8, "striving": 1.0, "rebellion": -0.8},
    "yale_state": {"wealth": 1.5, "striving": 1.2, "rebellion": -0.5},
}

# Thresholds tuned so ~1/3 of combos yield acceptance
ACCEPT_THRESHOLD = 22
WAITLIST_THRESHOLD = 16


def compute_decision(persistent, college_id):
    """
    Returns 'accepted', 'waitlisted', or 'rejected' based on:
    1. Profile alignment with college bias
    2. Cosmetic tag alignment
    3. Extracurricular choices (small bonus)
    """
    profile = persistent.get("profile", "first_gen")
    cosmetic_tags = persistent.get("cosmetic_tags", {})
    college = COLLEGE_LOOKUP[college_id]

    # 1. Profile alignment score
    p_scores = PROFILE_SCORES[profile]
    profile_alignment = sum(
        p_scores[dim] * college.bias[dim] for dim in college.bias
    )

    # 2. Cosmetic alignment score
    c_weights = COSMETIC_WEIGHTS.get(college_id, {})
    cosmetic_score = sum(
        cosmetic_tags.get(tag, 0) * c_weights.get(tag, 0)
        for tag in cosmetic_tags
    )

    # 3. Small extracurricular bonus (check if apps match)
    extra_bonus = 0
    for app in persistent.get("applications", []):
        if app.get("college_id") == college_id:
            # More selections = small boost
            extra_bonus += len(app.get("extracurricular_selections", [])) * 0.5

    total = profile_alignment + cosmetic_score + extra_bonus

    if total >= ACCEPT_THRESHOLD:
        return "accepted"
    elif total >= WAITLIST_THRESHOLD:
        return "waitlisted"
    else:
        return "rejected"


def compute_all_decisions(persistent):
    """Compute decisions for all applied colleges. Returns dict of {college_name: result}."""
    decisions = {}
    for app in persistent.get("applications", []):
        college_id = app.get("college_id")
        if college_id:
            college = COLLEGE_LOOKUP[college_id]
            result = compute_decision(persistent, college_id)
            decisions[college.name] = result
    return decisions
