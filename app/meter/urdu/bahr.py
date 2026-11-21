"""Reviewed Urdu Bahr templates with Arkan patterns and prosodic definitions."""

from dataclasses import dataclass


@dataclass
class BahrDefinition:
    """Descriptor for an Urdu poetic meter (Bahr)."""

    id: str
    name: str
    urdu_name: str
    arkan: list[str]
    pattern: str  # Short (S) and Long (L) sequence
    misra_length: int
    description: str
    limitations: str
    source: str


BAHRS: dict[str, BahrDefinition] = {
    "hazaj_musamman": BahrDefinition(
        id="hazaj_musamman",
        name="Bahr Hazaj Musamman Salim",
        urdu_name="بحر ہزج مثمن سالم",
        arkan=["مفاعیلن", "مفاعیلن", "مفاعیلن", "مفاعیلن"],
        pattern="SLLLSLLLSLLLSLLL",
        misra_length=16,
        description="One of the most melodic and common classical meters in Urdu Ghazal.",
        limitations="Does not account for rare zihafat (metrical variations) in unreviewed hemistichs.",
        source="Shamsur Rahman Faruqi, 'Dars-e-Balaghat'",
    ),
    "ramal_musamman": BahrDefinition(
        id="ramal_musamman",
        name="Bahr Ramal Musamman Salim",
        urdu_name="بحر رمل مثمن سالم",
        arkan=["فاعلاتن", "فاعلاتن", "فاعلاتن", "فاعلاتن"],
        pattern="LSLLLSLLLSLLLSLL",
        misra_length=16,
        description="A flowing, majestic meter widely used by Ghalib and Mir.",
        limitations="Requires careful handling of ending syllables (mahzoof / maqsoor).",
        source="Classical Urdu prosodic treatises; Faruqi, 1980.",
    ),
    "mutaqarib_musamman": BahrDefinition(
        id="mutaqarib_musamman",
        name="Bahr Mutaqarib Musamman Salim",
        urdu_name="بحر متقارب مثمن سالم",
        arkan=["فعولن", "فعولن", "فعولن", "فعولن"],
        pattern="SLLSLLSLLSLL",
        misra_length=12,
        description="The traditional epic / narrative meter, famous for Shahnama and Masnavis.",
        limitations="Short hemistichs; variations in final rukn are common.",
        source="Classical Persian/Urdu Arooz; Mir Taqi Mir's Mathnavis.",
    ),
    "kamil_musaddas": BahrDefinition(
        id="kamil_musaddas",
        name="Bahr Kamil Musaddas Salim",
        urdu_name="بحر کامل مسدس سالم",
        arkan=["متفاعلن", "متفاعلن", "متفاعلن"],
        pattern="SSLLSSLLSSLL",
        misra_length=12,
        description="A lively meter with rapid double-short openings in each foot.",
        limitations="Less common in standard Urdu ghazal, frequently used in Nazm.",
        source="Abdul Majeed, 'Urdu Arooz-o-Bayan'.",
    ),
    "khafif_musaddas": BahrDefinition(
        id="khafif_musaddas",
        name="Bahr Khafif Musaddas Makhboon Maqsoor",
        urdu_name="بحر خفیف مسدس مخبون مقصور",
        arkan=["فاعلاتن", "مفاعلن", "فعلن"],
        pattern="LSLLSLSLLL",
        misra_length=10,
        description="A light, contemplative meter frequent in classical Urdu and Persian poetry.",
        limitations="Mixed feet require precise syllable weighting.",
        source="Ghalib's Divan; Faruqi's analysis of Ghalib's meters.",
    ),
}


def get_bahr(bahr_id: str) -> BahrDefinition | None:
    """Return BahrDefinition by ID, or None if not found."""
    return BAHRS.get(bahr_id)


def list_bahrs() -> list[BahrDefinition]:
    """Return all reviewed Bahr definitions."""
    return list(BAHRS.values())
