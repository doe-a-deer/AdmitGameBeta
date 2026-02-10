from dataclasses import dataclass, field


@dataclass
class College:
    id: str
    name: str
    motto: str
    tagline: str
    bias: dict  # {"capital": float, "grit": float, "performance": float}
    essay_prompts: list = field(default_factory=list)
    extracurriculars: list = field(default_factory=list)
