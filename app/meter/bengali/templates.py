"""Reviewed Bengali meter templates with prosodic parameters and literary citations."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class BengaliTemplate:
    """Descriptor for a traditional Bengali poetic meter."""

    id: str
    name: str
    bengali_name: str
    system: Literal["aksharbritta", "matrabritta", "swarobritta"]
    unit_name: str  # "aksharas", "matras", "dals"
    target_count: int
    grouping_pattern: str
    description: str
    source: str
    validation_status: str


BENGALI_TEMPLATES: dict[str, BengaliTemplate] = {
    "payar": BengaliTemplate(
        id="payar",
        name="Payar",
        bengali_name="পয়ার",
        system="aksharbritta",
        unit_name="aksharas",
        target_count=14,
        grouping_pattern="8 + 6",
        description="The foundational meter of Bengali medieval and classical narrative verse (14 aksharas, caesura at 8).",
        source="Krittibas Ojha, 'Krittivasi Ramayan'; Michael Madhusudan Dutt.",
        validation_status="reviewed",
    ),
    "mahapabar": BengaliTemplate(
        id="mahapabar",
        name="Mahapabar",
        bengali_name="মহাপয়ার",
        system="aksharbritta",
        unit_name="aksharas",
        target_count=18,
        grouping_pattern="8 + 10",
        description="Extended Payar meter carrying 18 aksharas for grand, majestic poetic expressions.",
        source="Bharatchandra Ray, 'Annadamangal'.",
        validation_status="reviewed",
    ),
    "chaturdashpadi": BengaliTemplate(
        id="chaturdashpadi",
        name="Chaturdashpadi",
        bengali_name="চতুর্দশপদী",
        system="aksharbritta",
        unit_name="aksharas",
        target_count=14,
        grouping_pattern="8 + 6",
        description="Bengali Petrarcan sonnet form perfected by Michael Madhusudan Dutt.",
        source="Michael Madhusudan Dutt, 'Chaturdashpadi Kavitavali' (1866).",
        validation_status="reviewed",
    ),
    "matrabritta_14": BengaliTemplate(
        id="matrabritta_14",
        name="Matrabritta 14",
        bengali_name="মাত্রাবৃত্ত ১৪",
        system="matrabritta",
        unit_name="matras",
        target_count=14,
        grouping_pattern="7 + 7",
        description="Classical quantitative matra meter where closed syllables weigh 2 and open weigh 1.",
        source="Rabindranath Tagore, 'Balaka' and 'Chitra'.",
        validation_status="reviewed",
    ),
    "swarabritta_basic": BengaliTemplate(
        id="swarabritta_basic",
        name="Swarabritta 8",
        bengali_name="স্বরবৃত্ত ৮",
        system="swarobritta",
        unit_name="dals",
        target_count=8,
        grouping_pattern="4 + 4",
        description="Folk rhythm pulse meter (Dalvritta) carrying 4+4 stress beats.",
        source="Traditional Bengali folk rhymes; Sukumar Ray, 'Abol Tabol'.",
        validation_status="reviewed",
    ),
}


def get_bengali_template(template_id: str) -> BengaliTemplate | None:
    """Return BengaliTemplate by ID, or None if not registered."""
    return BENGALI_TEMPLATES.get(template_id)


def list_bengali_templates() -> list[BengaliTemplate]:
    """Return list of all registered Bengali templates."""
    return list(BENGALI_TEMPLATES.values())
