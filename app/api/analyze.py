"""Meter analysis endpoint."""

from fastapi import APIRouter

from app.meter.bengali.scanner import scan_bengali_line
from app.meter.scanner import scan_poem
from app.meter.templates import get_template
from app.meter.urdu.scanner import scan_urdu_line
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BengaliAnalyzeRequest,
    BengaliAnalyzeResponse,
    UrduAnalyzeRequest,
    UrduAnalyzeResponse,
)

router = APIRouter(tags=["Meter"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_poem(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Deterministically calculates matra counts, syllable weights,
    break positions, and error diagnostics for a poem's charans.
    """
    template = get_template(request.meter, request.custom_pattern)
    return scan_poem(
        charans=request.charans,
        template=template,
        pronunciation_mode=request.pronunciation_mode,
        pronunciation_overrides=request.pronunciation_overrides,
    )


@router.post("/analyze/urdu", response_model=UrduAnalyzeResponse)
async def analyze_urdu_endpoint(request: UrduAnalyzeRequest) -> UrduAnalyzeResponse:
    """
    Analyze an Urdu poetic line using Arooz prosodic rules and Bahr matching.
    """
    res = scan_urdu_line(request.text, request.bahr)
    return UrduAnalyzeResponse(
        original_text=res.original_text,
        normalized_text=res.normalized_text,
        words=res.words,
        weight_pattern=res.weight_pattern,
        matched_bahr=res.matched_bahr,
        matched_bahr_name=res.matched_bahr_name,
        alternative_bahrs=res.alternative_bahrs,
        arkan_mapping=res.arkan_mapping,
        explanation=res.explanation,
        confidence=res.confidence,
        ambiguity_note=res.ambiguity_note,
    )


@router.post("/analyze/bengali", response_model=BengaliAnalyzeResponse)
async def analyze_bengali_endpoint(request: BengaliAnalyzeRequest) -> BengaliAnalyzeResponse:
    """
    Analyze a Bengali poetic line using Aksharbritta, Matrabritta, or Swarabritta rules.
    """
    res = scan_bengali_line(request.text, request.template)
    return BengaliAnalyzeResponse(
        original_text=res.original_text,
        normalized_text=res.normalized_text,
        aksharas=res.aksharas,
        count_value=res.count_value,
        count_unit=res.count_unit,
        template_name=res.template_name,
        target_count=res.target_count,
        difference=res.difference,
        status=res.status,
        diagnostic_message=res.diagnostic_message,
        system=res.system,
    )
