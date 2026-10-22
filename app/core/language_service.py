"""
Language Detection and Resolution Service
Supports FLORES-200, ISO 639-1, ISO 639-3, Unicode script heuristics, and probabilistic n-gram detection.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional
from app.config import SUPPORTED_LANGUAGES, LanguageConfig

try:
    from langdetect import detect_langs, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    # Enforce deterministic character n-gram probability estimation
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class LanguageService:
    """Manages language identification, script inspection, and code resolution."""

    # Unicode script ranges
    TAMIL_UNICODE_PATTERN = re.compile(r"[\u0B80-\u0BFF]")
    DEVANAGARI_UNICODE_PATTERN = re.compile(r"[\u0900-\u097F]")
    LATIN_LETTER_PATTERN = re.compile(r"[A-Za-z\u00C0-\u024F]")

    # Strip URLs, emails, and technical codes before n-gram sampling
    NOISE_STRIP_PATTERN = re.compile(
        r"https?://\S+|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b|"
        r"\b(?:ERR|ORD|ACC|TKT|INV|SKU|BUG|REF)[-_][A-Za-z0-9_-]+\b|\bE[0-9]{2,5}\b|#[0-9]{4,10}"
    )

    def __init__(self, registry: Optional[Dict[str, LanguageConfig]] = None):
        self.registry = registry or SUPPORTED_LANGUAGES
        self.flores_map: Dict[str, LanguageConfig] = {
            lang.flores_code: lang for lang in self.registry.values()
        }
        self.iso1_map: Dict[str, LanguageConfig] = {
            lang.iso639_1: lang for lang in self.registry.values()
        }
        self.name_map: Dict[str, LanguageConfig] = {
            lang.name.lower(): lang for lang in self.registry.values()
        }

    def resolve_language(self, identifier: Optional[str]) -> Optional[LanguageConfig]:
        """
        Resolves a language string (name, ISO-1 code, or FLORES-200 code) to a LanguageConfig.
        Returns None for auto-detect or unknown identifiers.
        """
        if not identifier or not isinstance(identifier, str):
            return None
        cleaned = identifier.strip()
        if not cleaned or cleaned.lower() in ("auto", "auto-detect", "none", "null"):
            return None

        # Check exact FLORES-200 code (case-sensitive)
        if cleaned in self.flores_map:
            return self.flores_map[cleaned]

        # Check case-insensitive human name
        lower = cleaned.lower()
        if lower in self.name_map:
            return self.name_map[lower]

        # Check ISO 639-1 two-letter code
        if lower in self.iso1_map:
            return self.iso1_map[lower]

        return None

    def get_supported_languages(self) -> List[LanguageConfig]:
        """Returns the list of all registered languages."""
        return list(self.registry.values())

    def detect_language(
        self,
        text: str,
        explicit_source_lang: Optional[str] = None,
        default_fallback: str = "English",
    ) -> Dict[str, Any]:
        """
        Detects source language with explicit override, script inspection, and statistical n-gram analysis.
        """
        warnings: List[str] = []

        # 1. Explicit override check
        if explicit_source_lang and str(explicit_source_lang).strip().lower() not in (
            "", "auto", "auto-detect", "none", "null"
        ):
            override = self.resolve_language(explicit_source_lang)
            if override is None:
                supported_names = ", ".join(self.registry.keys())
                raise ValueError(
                    f"Unsupported source language override '{explicit_source_lang}'. "
                    f"Supported languages: {supported_names} (or 'auto')."
                )
            return {
                "language_name": override.name,
                "flores_code": override.flores_code,
                "iso639_1": override.iso639_1,
                "confidence": 1.0,
                "method": "explicit_override",
                "used_override": True,
                "is_code_switched_suspect": False,
                "raw_candidates": [f"{override.iso639_1}:1.000 (override)"],
                "warnings": [],
            }

        cleaned_text = unicodedata.normalize("NFC", text or "").strip()
        if not cleaned_text:
            fallback = self.resolve_language(default_fallback) or self.registry["English"]
            return {
                "language_name": fallback.name,
                "flores_code": fallback.flores_code,
                "iso639_1": fallback.iso639_1,
                "confidence": 0.0,
                "method": "fallback_empty",
                "used_override": False,
                "is_code_switched_suspect": False,
                "raw_candidates": [],
                "warnings": ["Empty input text; defaulted to fallback language."],
            }

        # 2. Unicode script inspection
        stripped = self.NOISE_STRIP_PATTERN.sub(" ", cleaned_text).strip()
        tamil_chars = len(self.TAMIL_UNICODE_PATTERN.findall(stripped))
        deva_chars = len(self.DEVANAGARI_UNICODE_PATTERN.findall(stripped))
        latin_chars = len(self.LATIN_LETTER_PATTERN.findall(stripped))

        if tamil_chars > 0 and "Tamil" in self.registry:
            tamil_entry = self.registry["Tamil"]
            is_mixed = latin_chars >= 5
            if is_mixed:
                warnings.append(
                    f"Mixed script detected ({tamil_chars} Tamil chars, {latin_chars} Latin chars). "
                    "Code-switched quality may vary."
                )
            return {
                "language_name": tamil_entry.name,
                "flores_code": tamil_entry.flores_code,
                "iso639_1": tamil_entry.iso639_1,
                "confidence": round(tamil_chars / max(1, tamil_chars + latin_chars), 3),
                "method": "unicode_script_tamil",
                "used_override": False,
                "is_code_switched_suspect": is_mixed,
                "raw_candidates": [f"ta:{tamil_chars}_chars", f"latn:{latin_chars}_chars"],
                "warnings": warnings,
            }

        if deva_chars > 0 and "Hindi" in self.registry:
            hindi_entry = self.registry["Hindi"]
            is_mixed = latin_chars >= 5
            if is_mixed:
                warnings.append(
                    f"Mixed script detected ({deva_chars} Devanagari chars, {latin_chars} Latin chars)."
                )
            return {
                "language_name": hindi_entry.name,
                "flores_code": hindi_entry.flores_code,
                "iso639_1": hindi_entry.iso639_1,
                "confidence": round(deva_chars / max(1, deva_chars + latin_chars), 3),
                "method": "unicode_script_devanagari",
                "used_override": False,
                "is_code_switched_suspect": is_mixed,
                "raw_candidates": [f"hi:{deva_chars}_chars", f"latn:{latin_chars}_chars"],
                "warnings": warnings,
            }

        # 3. Statistical n-gram detection
        if latin_chars < 15:
            warnings.append(
                f"Short linguistic input ({latin_chars} alphabetic characters after stripping technical entities). "
                "Consider specifying the source language explicitly."
            )

        if not LANGDETECT_AVAILABLE:
            fallback = self.resolve_language(default_fallback) or self.registry["English"]
            return {
                "language_name": fallback.name,
                "flores_code": fallback.flores_code,
                "iso639_1": fallback.iso639_1,
                "confidence": 0.5,
                "method": "fallback_no_langdetect",
                "used_override": False,
                "is_code_switched_suspect": False,
                "raw_candidates": [],
                "warnings": warnings + ["Statistical detector library not installed; used fallback."],
            }

        try:
            sample_text = stripped if latin_chars > 0 else cleaned_text
            candidates = detect_langs(sample_text)
            raw_cands = [f"{c.lang}:{c.prob:.3f}" for c in candidates]
        except LangDetectException:
            fallback = self.resolve_language(default_fallback) or self.registry["English"]
            warnings.append(f"Insufficient alphabetic features; defaulted to {fallback.name}.")
            return {
                "language_name": fallback.name,
                "flores_code": fallback.flores_code,
                "iso639_1": fallback.iso639_1,
                "confidence": 0.0,
                "method": "fallback_default",
                "used_override": False,
                "is_code_switched_suspect": False,
                "raw_candidates": [],
                "warnings": warnings,
            }

        is_code_switched = len(candidates) >= 2 and candidates[1].prob >= 0.20
        if is_code_switched:
            warnings.append(
                f"Potential multilingual or code-switched text (candidates: {', '.join(raw_cands)})."
            )

        # Match top candidate against registered languages
        for cand in candidates:
            if cand.lang in self.iso1_map:
                matched = self.iso1_map[cand.lang]
                if cand.prob < 0.75:
                    warnings.append(
                        f"Moderate language confidence ({cand.prob:.2f} for {matched.name})."
                    )
                return {
                    "language_name": matched.name,
                    "flores_code": matched.flores_code,
                    "iso639_1": matched.iso639_1,
                    "confidence": round(float(cand.prob), 3),
                    "method": "langdetect_ngram",
                    "used_override": False,
                    "is_code_switched_suspect": is_code_switched,
                    "raw_candidates": raw_cands,
                    "warnings": warnings,
                }

        # Fallback if detected language is outside registered set
        fallback = self.resolve_language(default_fallback) or self.registry["English"]
        warnings.append(
            f"Detected language '{candidates[0].lang}' ({candidates[0].prob:.2f}) is outside registered set; "
            f"defaulted to {fallback.name}."
        )
        return {
            "language_name": fallback.name,
            "flores_code": fallback.flores_code,
            "iso639_1": fallback.iso639_1,
            "confidence": round(float(candidates[0].prob), 3),
            "method": "langdetect_unmapped_fallback",
            "used_override": False,
            "is_code_switched_suspect": is_code_switched,
            "raw_candidates": raw_cands,
            "warnings": warnings,
        }
