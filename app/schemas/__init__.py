"""Schemas package."""
from app.schemas.translation import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    LanguageInfo,
    SampleCase,
    TranslationRequest,
    TranslationResponse,
)

__all__ = [
    "LanguageInfo",
    "DetectLanguageRequest",
    "DetectLanguageResponse",
    "TranslationRequest",
    "TranslationResponse",
    "SampleCase",
]
