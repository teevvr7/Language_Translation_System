"""
Application Configuration and Constants
Multilingual Neural Translation System
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Application Metadata (Generic & Professional — No Company / Assessment references)
APP_TITLE = "Neural Translation Studio"
APP_SUBTITLE = "Enterprise Multilingual Translation Engine with Intelligent Entity Preservation"
APP_VERSION = "1.0.0"

# Model Configuration
MODEL_ID = os.getenv("TRANSLATION_MODEL_ID", "facebook/nllb-200-distilled-600M")
DEFAULT_NUM_BEAMS = int(os.getenv("DEFAULT_NUM_BEAMS", "4"))
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("DEFAULT_MAX_NEW_TOKENS", "256"))
MAX_RECOMMENDED_INPUT_TOKENS = 512
GLOBAL_SEED = 42

# Execution Device Settings
CUDA_ENABLED = os.getenv("ENABLE_CUDA", "true").lower() in ("true", "1", "yes")

# Language Specifications
@dataclass(frozen=True)
class LanguageConfig:
    name: str
    flores_code: str
    iso639_1: str
    iso639_3: str
    script_name: str
    resource_category: str
    token_id: int

# Primary & Extended Supported Languages in NLLB-200
SUPPORTED_LANGUAGES: Dict[str, LanguageConfig] = {
    "English": LanguageConfig(
        name="English",
        flores_code="eng_Latn",
        iso639_1="en",
        iso639_3="eng",
        script_name="Latin (Latn)",
        resource_category="High-Resource",
        token_id=256047,
    ),
    "French": LanguageConfig(
        name="French",
        flores_code="fra_Latn",
        iso639_1="fr",
        iso639_3="fra",
        script_name="Latin (Latn)",
        resource_category="High-Resource",
        token_id=256057,
    ),
    "Spanish": LanguageConfig(
        name="Spanish",
        flores_code="spa_Latn",
        iso639_1="es",
        iso639_3="spa",
        script_name="Latin (Latn)",
        resource_category="High-Resource",
        token_id=256161,
    ),
    "Tamil": LanguageConfig(
        name="Tamil",
        flores_code="tam_Taml",
        iso639_1="ta",
        iso639_3="tam",
        script_name="Tamil (Taml)",
        resource_category="Medium-Resource Indian Language",
        token_id=256168,
    ),
    "German": LanguageConfig(
        name="German",
        flores_code="deu_Latn",
        iso639_1="de",
        iso639_3="deu",
        script_name="Latin (Latn)",
        resource_category="High-Resource",
        token_id=256038,
    ),
    "Hindi": LanguageConfig(
        name="Hindi",
        flores_code="hin_Deva",
        iso639_1="hi",
        iso639_3="hin",
        script_name="Devanagari (Deva)",
        resource_category="Medium-Resource Indian Language",
        token_id=256073,
    ),
}

# Default Technical Glossary for Entity Preservation
DEFAULT_PRODUCT_GLOSSARY: List[str] = [
    "CloudSync Pro",
    "PayGate",
    "OmniDesk",
    "Vault",
    "DataBridge",
    "AuthGuard",
]

# Regular Expression Patterns for Technical Terms
TECHNICAL_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("URL", re.compile(r"https?://[^\s<>\"')]+")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    (
        "TECH_ID",
        re.compile(
            r"(?:(?<=\s)|(?<=^)|(?<=[(\[\"'#]))"
            r"(?:#[0-9]{4,10}"
            r"|\b(?:ERR|ORD|ACC|TKT|INV|SKU|BUG|REF)[-_][A-Za-z0-9_-]{2,20}\b"
            r"|\bE[0-9]{2,5}\b"
            r"|\bv[0-9]+\.[0-9]+(?:\.[0-9]+)?\b)"
        ),
    ),
]
