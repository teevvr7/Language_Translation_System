"""
Unit Tests for TermPreservationService
Verifies regex extraction, placeholder masking, and restoration audit.
"""

import pytest
from app.core.term_preservation import TermPreservationService


@pytest.fixture
def term_service():
    return TermPreservationService(
        glossary=["CloudSync Pro", "PayGate", "OmniDesk", "Vault"]
    )


def test_extract_technical_terms(term_service):
    text = (
        "Urgent: CloudSync Pro v2.4.1 crashed with E104 and ERR-502 on order ORD-2026-8841 "
        "(account ACC_99201, #49201). Link: https://logs.example.com/err or email support@example.com"
    )
    terms = term_service.extract_technical_terms(text)
    values = [t["value"] for t in terms]

    assert "CloudSync Pro" in values
    assert "v2.4.1" in values
    assert "E104" in values
    assert "ERR-502" in values
    assert "ORD-2026-8841" in values
    assert "ACC_99201" in values
    assert "#49201" in values
    assert "https://logs.example.com/err" in values
    assert "support@example.com" in values


def test_protect_and_restore_terms(term_service):
    original = "Payment failed with error E104 on order ORD-2026-8841 in PayGate."
    masked, terms = term_service.protect_terms(original, use_placeholders=True)

    assert "ZXQTERM" in masked
    assert "E104" not in masked
    assert "ORD-2026-8841" not in masked

    # Simulate translation where placeholders are preserved
    mock_translated = f"Le paiement a échoué avec l'erreur {terms[0]['placeholder']} sur la commande {terms[1]['placeholder']} dans {terms[2]['placeholder']}."
    audit = term_service.restore_and_audit_terms(mock_translated, terms, used_placeholders=True)

    assert audit["all_terms_preserved"] is True
    assert len(audit["missing_terms"]) == 0
    assert "E104" in audit["final_text"]
    assert "ORD-2026-8841" in audit["final_text"]
    assert "PayGate" in audit["final_text"]
    assert "ZXQTERM" not in audit["final_text"]


def test_audit_missing_terms(term_service):
    terms = [
        {"type": "TECH_ID", "value": "E104", "placeholder": "ZXQTERM0ZXQ"},
        {"type": "TECH_ID", "value": "ORD-2026-8841", "placeholder": "ZXQTERM1ZXQ"},
    ]
    translated = "Le paiement a échoué avec l'erreur E104."  # ORD-2026-8841 is missing
    audit = term_service.restore_and_audit_terms(translated, terms, used_placeholders=False)

    assert audit["all_terms_preserved"] is False
    assert "ORD-2026-8841" in audit["missing_terms"]
    assert "E104" not in audit["missing_terms"]


def test_glossary_management(term_service):
    initial = term_service.get_glossary()
    assert "PayGate" in initial

    term_service.add_term_to_glossary("CustomService")
    assert "CustomService" in term_service.get_glossary()

    term_service.set_glossary(["Alpha", "Beta"])
    assert term_service.get_glossary() == ["Alpha", "Beta"]
