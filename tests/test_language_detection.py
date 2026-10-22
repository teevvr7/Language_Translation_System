"""
Unit Tests for LanguageService
Verifies script heuristics, n-gram detection, and override logic.
"""

import pytest
from app.core.language_service import LanguageService


@pytest.fixture
def service():
    return LanguageService()


def test_resolve_language_names(service):
    assert service.resolve_language("English").flores_code == "eng_Latn"
    assert service.resolve_language("french").flores_code == "fra_Latn"
    assert service.resolve_language("spa_Latn").name == "Spanish"
    assert service.resolve_language("ta").flores_code == "tam_Taml"
    assert service.resolve_language("auto") is None
    assert service.resolve_language(None) is None


def test_detect_tamil_unicode_script(service):
    tamil_msg = "வணக்கம், எனது கணக்கில் E104 பிழை வருகிறது. உடனடியாக உதவும்."
    res = service.detect_language(tamil_msg)
    assert res["language_name"] == "Tamil"
    assert res["flores_code"] == "tam_Taml"
    assert res["method"] == "unicode_script_tamil"
    assert res["confidence"] > 0.5


def test_detect_explicit_override(service):
    short_msg = "pls help E104 😭"
    res = service.detect_language(short_msg, explicit_source_lang="English")
    assert res["language_name"] == "English"
    assert res["flores_code"] == "eng_Latn"
    assert res["method"] == "explicit_override"
    assert res["used_override"] is True
    assert res["confidence"] == 1.0


def test_detect_french_text(service):
    fr_msg = "Bonjour, ma commande ORD-2026-8841 est bloquée avec l'erreur E104. Pouvez-vous m'aider s'il vous plaît ?"
    res = service.detect_language(fr_msg)
    assert res["language_name"] == "French"
    assert res["flores_code"] == "fra_Latn"
    assert res["confidence"] > 0.7


def test_detect_spanish_text(service):
    es_msg = "Hola equipo de soporte, necesito ayuda urgente con la factura de este mes."
    res = service.detect_language(es_msg)
    assert res["language_name"] == "Spanish"
    assert res["flores_code"] == "spa_Latn"
    assert res["confidence"] > 0.7


def test_detect_empty_text_fallback(service):
    res = service.detect_language("   ")
    assert res["language_name"] == "English"
    assert res["method"] == "fallback_empty"
