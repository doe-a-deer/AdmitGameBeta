from src.entities.college import College

COLLEGES = [
    College(
        id="princesstown",
        name="Princesstown University",
        motto="Tradition. Refinement. Civilizational Inheritance.",
        tagline="Where effortlessness is a moral category.",
        bias={"capital": 1.5, "grit": 0.5, "performance": 0.8},
        essay_prompts=[
            "Describe the tradition that most shaped your sense of belonging.",
            "How has your upbringing prepared you to steward something larger than yourself?",
        ],
        extracurriculars=[
            "Formal Hall Committee",
            "The Punting Society",
            "Chapel Choir",
            "Debating Union",
            "May Ball Planning Board",
        ],
    ),
    College(
        id="cit",
        name="California Institute of Technology",
        motto="Disrupt. Build. Transcend.",
        tagline="Where impact is a moral category.",
        bias={"capital": 0.8, "grit": 0.8, "performance": 1.5},
        essay_prompts=[
            "Tell us about something you built and the problem it solved.",
            "How will your trajectory create measurable change in the world?",
        ],
        extracurriculars=[
            "Startup Incubator",
            "Impact Ventures Club",
            "Plaza Organizing Coalition",
            "Lab Rush Team",
            "Demo Day Speaker Circuit",
        ],
    ),
    College(
        id="yale_state",
        name="Yale State Polytechnic Institute",
        motto="Selection. Excellence. Sovereign Prestige.",
        tagline="Where seriousness is a moral category.",
        bias={"capital": 1.2, "grit": 1.0, "performance": 1.0},
        essay_prompts=[
            "Describe a sacrifice you made in pursuit of something you believed in.",
            "How has your background prepared you for the weight of institutional expectation?",
        ],
        extracurriculars=[
            "The Committee Circuit",
            "Fellowship Pipeline Seminar",
            "Housing Sort Orientation",
            "Donor Relations Board",
            "Closed Door Reading Group",
        ],
    ),
]

COLLEGE_LOOKUP = {c.id: c for c in COLLEGES}
