# Neural Translation Studio

> **Enterprise Multilingual Neural Translation Engine with Intelligent Technical Entity Preservation**

---

## 📌 Overview

**Neural Translation Studio** is a modular, high-accuracy machine translation system powered by Meta's **NLLB-200** (`facebook/nllb-200-distilled-600M`) architecture and built with **FastAPI** (backend) and a clean, modern responsive **Web UI** (frontend).

The system is specifically engineered to handle complex, real-world customer support messages, live chat inquiries, error reports, and emails exhibiting:
- **Informal conversational phrasing, abbreviations, and expressive emojis** (e.g., `pls`, `ASAP`, `thx`, `😭`, `🙏`, `😡`)
- **Strict domain-specific technical entities** (e.g., product names like `CloudSync Pro`, `PayGate`, error codes like `E104`, order IDs like `ORD-2026-8841`, ticket IDs `#49201`, account IDs `ACC_99201`, URLs, and emails)
- **Indian and low/medium-resource languages** (e.g., Tamil `tam_Taml` in native Tamil Unicode script, Hindi `hin_Deva`)
- **Mixed-language (code-switched) inputs** (e.g., French-English *Franglais*)
- **Typographical errors** and conversational slang

---

## 🚀 Key Features

1. **Intelligent Technical Entity Preservation:**
   - Automatically detects non-overlapping technical spans (URLs, emails, error codes `E104`, order IDs `ORD-*`, version tags `v2.4.1`, ticket IDs, and product glossary terms).
   - Uses a conservative two-stage pipeline: natural neural translation first, followed by automated verification audit and synthetic placeholder masking (`ZXQTERM0ZXQ`) fallback if any identifier was altered.
2. **Automatic Source-Language Detection:**
   - Multi-tier detection: explicit user override &rarr; Unicode script inspection (e.g. Tamil `U+0B80–U+0BFF`) &rarr; deterministic character n-gram probability estimation (`langdetect` with fixed seed) with technical noise pre-stripping.
3. **Enterprise REST API & Swagger UI:**
   - Fully documented OpenAPI (`/docs`) and ReDoc (`/redoc`) endpoints for `/translate`, `/detect-language`, `/languages`, `/samples`, `/glossary`, and `/health`.
4. **Interactive Web Interface:**
   - Clean, modern dual-pane translation workbench.
   - Quick preset chips for instant testing.
   - Real-time character & word counters.
   - Diagnostics trace panel displaying latency, token statistics, detection confidence, and entity verification audits.
   - Dynamic glossary management to add or update protected brand names on the fly.
5. **Modular Architecture:**
   - Clean separation of concerns across configuration, Pydantic schemas, language services, entity preservation services, translation engines, API routers, and UI components.

---

## 📂 Project Organization

```
Language_Translation_System/
│
├── .venv/                              # Python Virtual Environment
│
├── app/                                # Modular Application Package
│   ├── __init__.py
│   ├── config.py                       # App settings, language configs, model IDs, regexes
│   │
│   ├── schemas/                        # Pydantic Request & Response Schemas
│   │   ├── __init__.py
│   │   └── translation.py              # TranslationRequest, TranslationResponse, etc.
│   │
│   ├── core/                           # Core Translation Services
│   │   ├── __init__.py
│   │   ├── language_service.py         # Script heuristics, n-gram detection, FLORES lookup
│   │   ├── term_preservation.py        # Entity regex, glossary, placeholder masking & audit
│   │   └── translation_engine.py       # NLLB-200 loader, thread-safe tokenization, generation
│   │
│   ├── api/                            # API Endpoints
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes.py               # REST API endpoints (/translate, /languages, /health, etc.)
│   │
│   ├── static/                         # Frontend Static Assets
│   │   ├── css/
│   │   │   └── styles.css              # Modern responsive CSS styling
│   │   └── js/
│   │       └── app.js                  # Frontend interactive application logic
│   │
│   ├── templates/                      # HTML Frontend
│   │   └── index.html                  # Translation Studio Web Interface
│   │
│   └── main.py                         # FastAPI Application Entrypoint & Lifespan
│
├── notebooks/                          # Translation Pipeline Jupyter Notebook
│   └── multilingual_translation_system.ipynb
│
├── tests/                              # Automated Test Suite
│   ├── __init__.py
│   ├── test_language_detection.py      # Script heuristics & detection tests
│   ├── test_term_preservation.py       # Entity extraction & preservation audit tests
│   └── test_api.py                     # FastAPI endpoint integration tests
│
├── requirements.txt                    # Project dependencies
├── run.py                              # Web application launcher script
├── RUN_GUIDE.md                        # Activation guide for virtual environment & webapp
└── README.md                           # Complete system documentation
```

---

## 🧠 Transformer Architecture Details (`facebook/nllb-200-distilled-600M`)

| Dimension | Specification | Description |
| :--- | :--- | :--- |
| **Model Type** | `m2m_100` | Dense sequence-to-sequence encoder-decoder Transformer |
| **Parameters** | ~615 Million | Distilled from the 54.5B MoE teacher model across 200 languages |
| **Encoder** | 12 Layers | 16 Multi-Head Self-Attention heads, $d_{\text{model}}=1024$, $d_{\text{ffn}}=4096$ |
| **Decoder** | 12 Layers | 16 Causal Self-Attention heads + 16 Cross-Attention heads |
| **Vocabulary** | 256,206 Tokens | Shared SentencePiece Unigram vocabulary across all 200 languages |
| **Positional Encoding** | Sinusoidal | Non-learned fixed sinusoidal positional embeddings ($max=1024$) |
| **Target Conditioning** | `forced_bos_token_id` | Enforces target language prefix during autoregressive decoding |

---

## ⚡ Quick Start

### 1. Activate the Virtual Environment

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 2. Start the Application

```powershell
python run.py
```
Or with Uvicorn:
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser

- Web Interface: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
- Swagger OpenAPI: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```powershell
pytest tests/ -v
```

---

## 📄 License & Attribution

This translation engine utilizes pretrained weights from `facebook/nllb-200-distilled-600M` (`CC-BY-NC-4.0`).
