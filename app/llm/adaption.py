"""
LoRA / Fine-tuned adapter integration for Hindi poetic diction.

Routes generation requests to the optimal model for each language using
app.llm.model_router.  When fine-tuned model support is enabled via
ENABLE_FINE_TUNED_MODEL=true and a language-specific tuned model endpoint is
configured (e.g. GEMINI_TUNED_HINDI_MODEL), this module creates an LLMClient
pre-configured for that model; otherwise it falls back to the global default.
"""

from app.llm.client import LLMClient
from app.llm.model_router import get_model_for_language


def get_client_for_language(language: str) -> LLMClient:
    """
    Return an LLMClient configured for the best available model for the given
    BCP-47 language code.

    Args:
        language: BCP-47 language code, e.g. ``"hi"``, ``"ur"``, ``"bn"``.

    Returns:
        An :class:`~app.llm.client.LLMClient` instance using the resolved model.
    """
    model = get_model_for_language(language)
    return LLMClient(model=model)
