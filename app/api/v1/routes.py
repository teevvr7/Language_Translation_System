"""
API V1 Endpoints Router
Exposes clean RESTful endpoints for translation, language detection, glossary, and health checks.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.config import APP_TITLE, APP_VERSION
from app.core.language_service import LanguageService
from app.core.term_preservation import TermPreservationService
from app.core.translation_engine import TranslationEngine
from app.schemas.translation import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    GlossaryResponse,
    GlossaryUpdateRequest,
    LanguageInfo,
    SampleCase,
    TranslationRequest,
    TranslationResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Translation API"])

# Shared service instances
lang_service = LanguageService()
term_service = TermPreservationService()
translation_engine = TranslationEngine(
    language_service=lang_service,
    term_service=term_service,
)

# Curated Representative Sample Cases for Quick Testing in UI
CURATED_SAMPLES: List[SampleCase] = [
    SampleCase(
        id="sample-1",
        category="General Request",
        source_lang="English",
        target_lang="French",
        message="Hello support team, could you please send me a copy of my January invoice and update my billing address?",
        description="Standard polite customer support inquiry without technical jargon.",
    ),
    SampleCase(
        id="sample-2",
        category="Urgent Complaint",
        source_lang="English",
        target_lang="Spanish",
        message="THIS IS UNACCEPTABLE! Our entire production workspace has been locked for 4 hours and nobody is replying! Escalate this IMMEDIATELY! 😡",
        description="High-urgency escalation with capitalization, exclamation marks, and emojis.",
    ),
    SampleCase(
        id="sample-3",
        category="Reverse Direction (FR -> EN)",
        source_lang="French",
        target_lang="English",
        message="Bonjour, j'ai été débité deux fois pour ma commande ORD-2026-4410 sur PayGate. Pouvez-vous me rembourser rapidement ?",
        description="French source message with order ID and payment gateway identifier.",
    ),
    SampleCase(
        id="sample-4",
        category="Informal Slang & Emoji",
        source_lang="English",
        target_lang="French",
        message="hey guys!! idk why my login keeps failing lol 😭 pls reset my 2FA ASAP thx so much 🙏✨",
        description="Informal chat vocabulary, abbreviations (idk, pls, ASAP, thx), and multiple emojis.",
    ),
    SampleCase(
        id="sample-5",
        category="Typographical Errors",
        source_lang="English",
        target_lang="Spanish",
        message="Hi, I havnt recieved my confirmashun email for my acount and I cant rest my passwrod, pls halp.",
        description="Common human spelling mistakes (havnt, recieved, confirmashun, acount, passwrod, halp).",
    ),
    SampleCase(
        id="sample-6",
        category="Technical Entity Preservation",
        source_lang="English",
        target_lang="French",
        message="When syncing CloudSync Pro v2.4.1 on account ACC_99201, I get error E104 and ERR-502. Log link: https://logs.example.com/tkt492",
        description="Dense technical identifiers (E104, ERR-502, ACC_99201, v2.4.1, URL, CloudSync Pro).",
    ),
    SampleCase(
        id="sample-7",
        category="Indian Language (Tamil)",
        source_lang="English",
        target_lang="Tamil",
        message="Your refund for order ORD-2026-8841 has been approved. If error E104 persists in Vault, please reply to this ticket.",
        description="Translates to Tamil script while preserving alphanumeric identifiers ORD-2026-8841 and E104.",
    ),
    SampleCase(
        id="sample-8",
        category="Multilingual Code-Switching",
        source_lang="French",
        target_lang="English",
        message="Salut team, mon dashboard sur OmniDesk is completely frozen après la mise à jour, even after clearing browser cache!",
        description="Bilingual Franglais blending French grammar with English technical expressions.",
    ),
]


@router.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """Returns the list of supported languages, FLORES-200 codes, and scripts."""
    languages = lang_service.get_supported_languages()
    return [
        LanguageInfo(
            name=lang.name,
            flores_code=lang.flores_code,
            iso639_1=lang.iso639_1,
            iso639_3=lang.iso639_3,
            script_name=lang.script_name,
            resource_category=lang.resource_category,
            token_id=lang.token_id,
        )
        for lang in languages
    ]


@router.post("/detect-language", response_model=DetectLanguageResponse)
async def detect_language(req: DetectLanguageRequest):
    """Detects the source language of input text using script heuristics and n-gram analysis."""
    try:
        res = lang_service.detect_language(
            req.text, explicit_source_lang=req.source_lang_override
        )
        return DetectLanguageResponse(
            language_name=res["language_name"],
            flores_code=res["flores_code"],
            iso639_1=res["iso639_1"],
            confidence=float(res["confidence"]),
            method=res["method"],
            used_override=bool(res["used_override"]),
            is_code_switched_suspect=bool(res["is_code_switched_suspect"]),
            raw_candidates=res.get("raw_candidates", []),
            warnings=res.get("warnings", []),
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    """Translates message with entity preservation and quality audit."""
    result = translation_engine.translate_message(
        message=req.message,
        target_lang=req.target_lang,
        source_lang=req.source_lang,
        protect_terms=req.protect_terms,
        num_beams=req.num_beams,
        max_new_tokens=req.max_new_tokens,
    )
    return TranslationResponse(**result)


@router.get("/samples", response_model=List[SampleCase])
async def get_sample_cases():
    """Returns curated representative customer-support scenarios for instant one-click testing."""
    return CURATED_SAMPLES


@router.get("/glossary", response_model=GlossaryResponse)
async def get_glossary():
    """Returns the list of protected technical and product terms."""
    terms = term_service.get_glossary()
    return GlossaryResponse(terms=terms, count=len(terms))


@router.post("/glossary", response_model=GlossaryResponse)
async def update_glossary(req: GlossaryUpdateRequest):
    """Updates the protected technical terms glossary."""
    term_service.set_glossary(req.terms)
    terms = term_service.get_glossary()
    return GlossaryResponse(terms=terms, count=len(terms))


@router.get("/health")
async def health_check():
    """Returns engine health, execution device, and model status."""
    return {
        "status": "online",
        "app_title": APP_TITLE,
        "version": APP_VERSION,
        "device": str(translation_engine.device),
        "dtype": str(translation_engine.dtype),
        "model_id": translation_engine.model_id,
        "model_loaded": translation_engine.is_loaded,
        "model_loading": translation_engine.is_loading,
        "model_loading_error": translation_engine.loading_error,
    }
