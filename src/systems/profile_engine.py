from src.data.questions import QUESTIONS

# Base stat lines for each profile. Legacy caps Integrity at 40.
PROFILE_BASELINES = {
    "legacy": {
        "money": 80,
        "connections": 75,
        "time": 60,
        "stress": 20,
        "reputation": 50,
        "integrity": 25,
    },
    "first_gen": {
        "money": 20,
        "connections": 15,
        "time": 40,
        "stress": 70,
        "reputation": 30,
        "integrity": 80,
    },
    "scholarship": {
        "money": 40,
        "connections": 30,
        "time": 20,
        "stress": 50,
        "reputation": 60,
        "integrity": 50,
    },
}

# Euphemistic labels shown to the player
PROFILE_LABELS = {
    "legacy": "Well-Rounded Leader",
    "first_gen": "Resilient Achiever",
    "scholarship": "Impact-Driven Scholar",
}


def assign_profile(quiz_answers):
    """
    Given a list of answer indices (one per question), compute hidden
    dimension scores and return (profile_key, euphemistic_label).
    """
    totals = {"capital": 0, "grit": 0, "performance": 0}

    for q_index, a_index in enumerate(quiz_answers):
        scores = QUESTIONS[q_index]["answers"][a_index]["scores"]
        for key in totals:
            totals[key] += scores[key]

    # Dominant dimension determines profile
    dominant = max(totals, key=totals.get)

    profile_map = {
        "capital": "legacy",
        "grit": "first_gen",
        "performance": "scholarship",
    }

    profile_key = profile_map[dominant]
    return profile_key, PROFILE_LABELS[profile_key]
