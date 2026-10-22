"""
Live server end-to-end integration verification script.
Run directly via: python tests/test_live_server.py
"""

import io
import sys
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8000"


def run_live_tests():
    print("=" * 72)
    print("RUNNING LIVE END-TO-END HTTP TESTS AGAINST FASTAPI SERVER")
    print("=" * 72)

    # 1. Health
    h = requests.get(f"{BASE}/api/v1/health").json()
    print("1. Health Endpoint   :", h["status"], "| Device:", h["device"])
    assert h["status"] == "online"

    # 2. Languages
    langs = requests.get(f"{BASE}/api/v1/languages").json()
    lang_names = [l["name"] for l in langs]
    print(f"2. Languages Endpoint: {len(langs)} languages supported -> {lang_names}")
    assert len(langs) >= 4

    # 3. Detect Language
    detect_payload = {"text": "வணக்கம், எனது கணக்கில் E104 பிழை வருகிறது."}
    d = requests.post(f"{BASE}/api/v1/detect-language", json=detect_payload).json()
    print(f"3. Detect Tamil      : {d['language_name']} ({d['flores_code']}) | method={d['method']} | conf={d['confidence']}")
    assert d["language_name"] == "Tamil"

    # 4. Translate Normal Request
    t1 = requests.post(
        f"{BASE}/api/v1/translate",
        json={
            "message": "Hello support team, could you please send me a copy of my January invoice and update my billing address?",
            "target_lang": "French",
            "source_lang": "English",
        },
    ).json()
    print(f"4. Normal Translate  : {t1['status'].upper()} | {t1['source_language']} -> {t1['target_language']}")
    print(f"   Output: {t1['translated_text']}")
    assert t1["status"] == "success"

    # 5. Technical Ticket Preservation
    t2 = requests.post(
        f"{BASE}/api/v1/translate",
        json={
            "message": "When syncing CloudSync Pro v2.4.1 on account ACC_99201, I get error E104 and ERR-502. Log link: https://logs.example.com/tkt492",
            "target_lang": "French",
            "source_lang": "English",
            "protect_terms": True,
        },
    ).json()
    print(f"5. Tech Term Preserv : {t2['status'].upper()}")
    print(f"   Protected Terms   : {t2['protected_terms']}")
    print(f"   All Preserved     : {t2['all_terms_preserved']}")
    print(f"   Output            : {t2['translated_text']}")
    assert t2["all_terms_preserved"] is True

    # 6. Indian Language (Tamil)
    t3 = requests.post(
        f"{BASE}/api/v1/translate",
        json={
            "message": "Your refund for order ORD-2026-8841 has been approved. If error E104 persists in Vault, please reply to this ticket.",
            "target_lang": "Tamil",
            "source_lang": "English",
        },
    ).json()
    print(f"6. Tamil Translation : {t3['status'].upper()}")
    print(f"   Protected Terms   : {t3['protected_terms']}")
    print(f"   All Preserved     : {t3['all_terms_preserved']}")
    print(f"   Output            : {t3['translated_text']}")
    assert t3["all_terms_preserved"] is True

    # 7. Check UI HTML
    ui = requests.get(f"{BASE}/")
    print(f"7. Web Interface UI  : HTTP {ui.status_code} ({len(ui.text):,} bytes)")
    assert "Neural Translation Studio" in ui.text
    assert "Assessment" not in ui.text
    print("=" * 72)
    print("ALL LIVE HTTP FUNCTIONALITY VERIFIED 100% SUCCESSFULLY!")
    print("=" * 72)


if __name__ == "__main__":
    run_live_tests()
