"""
Pydantic Schemas for API Requests & Responses
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LanguageInfo(BaseModel):
    name: str
    flores_code: str
    iso639_1: str
    iso639_3: str
    script_name: str
    resource_category: str
    token_id: int


class DetectLanguageRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Source text to detect language for")
    source_lang_override: Optional[str] = Field(
        None, description="Optional explicit language name or code to override automatic detection"
    )


class DetectLanguageResponse(BaseModel):
    language_name: str
    flores_code: str
    iso639_1: str
    confidence: float
    method: str
    used_override: bool
    is_code_switched_suspect: bool
    raw_candidates: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class TranslationRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Message text to translate")
    target_lang: str = Field(..., min_length=2, description="Target language name or code (e.g. French, fra_Latn, fr)")
    source_lang: Optional[str] = Field(
        None, description="Source language (e.g. English, eng_Latn, en, or 'auto' for auto-detect)"
    )
    protect_terms: bool = Field(
        True, description="Whether to extract and protect technical terms (IDs, error codes, URLs, product names)"
    )
    num_beams: int = Field(
        4, ge=1, le=8, description="Number of beams for beam search decoding (1 for greedy, 4 standard)"
    )
    max_new_tokens: int = Field(
        256, ge=16, le=512, description="Maximum number of tokens to generate"
    )


class TranslationResponse(BaseModel):
    status: str = Field(..., description="'success' or 'error'")
    source_text: str
    translated_text: Optional[str] = None
    source_language: str
    source_flores_code: Optional[str] = None
    target_language: str
    target_flores_code: Optional[str] = None
    detection_method: Optional[str] = None
    detection_confidence: Optional[float] = None
    input_token_count: int = 0
    output_token_count: int = 0
    latency_sec: float = 0.0
    protected_terms: List[str] = Field(default_factory=list)
    missing_terms: List[str] = Field(default_factory=list)
    all_terms_preserved: bool = True
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class SampleCase(BaseModel):
    id: str
    category: str
    source_lang: str
    target_lang: str
    message: str
    description: str


class GlossaryUpdateRequest(BaseModel):
    terms: List[str] = Field(..., description="List of technical terms or product names to protect")


class GlossaryResponse(BaseModel):
    terms: List[str]
    count: int
