"""
Integration Tests for FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.routes import translation_engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def prevent_hub_download_during_tests(monkeypatch):
    """Prevents unit tests from attempting to acquire HuggingFace hub download locks."""
    monkeypatch.setattr(translation_engine, "load_model", lambda *args, **kwargs: False)


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Neural Translation Studio" in response.text
    assert "Assessment" not in response.text


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "device" in data
    assert "model_id" in data


def test_languages_endpoint():
    response = client.get("/api/v1/languages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    names = [l["name"] for l in data]
    assert "English" in names
    assert "French" in names
    assert "Spanish" in names
    assert "Tamil" in names


def test_detect_language_endpoint():
    payload = {"text": "வணக்கம், உதவி தேவை."}
    response = client.post("/api/v1/detect-language", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language_name"] == "Tamil"
    assert data["flores_code"] == "tam_Taml"


def test_samples_endpoint():
    response = client.get("/api/v1/samples")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert data[0]["category"] == "General Request"


def test_glossary_endpoints():
    get_res = client.get("/api/v1/glossary")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "terms" in data

    post_res = client.post(
        "/api/v1/glossary", json={"terms": ["PayGate", "CloudSync", "CustomAPI"]}
    )
    assert post_res.status_code == 200
    updated = post_res.json()
    assert "CustomAPI" in updated["terms"]


def test_translate_validation_rejections():
    # Empty message rejection
    res = client.post(
        "/api/v1/translate",
        json={"message": "   ", "target_lang": "French"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"

    # Invalid target language rejection
    res = client.post(
        "/api/v1/translate",
        json={"message": "Hello", "target_lang": "Klingon123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"


def test_translate_endpoint_success():
    res = client.post(
        "/api/v1/translate",
        json={
            "message": "Hello support team, could you please send me a copy of my January invoice and update my billing address?",
            "target_lang": "French",
            "source_lang": "English",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["translated_text"] is not None
