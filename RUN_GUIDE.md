# Activation & User Guide: Neural Translation Studio

This guide provides step-by-step instructions for activating the Python virtual environment (`.venv`), running the FastAPI web application, exploring the interactive web interface, and testing the system functionality.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, Linux, or macOS
- **Python Version:** Python 3.10 – 3.13 (Python 3.13 is pre-configured in `.venv`)
- **Disk Space:** ~3 GB free for PyTorch, Transformers, and cached Hugging Face checkpoints
- **Hardware:** CPU supported (default `float32`); NVIDIA CUDA GPU automatically utilized if present (`float16`)

---

## 2. Virtual Environment (`.venv`) Activation

The dedicated virtual environment is pre-built at `.venv` in the project root.

### On Windows (PowerShell)
```powershell
# Open PowerShell in the project directory:
# cd Language_Translation_System

# If script execution is restricted on your machine, enable it for this process:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate the virtual environment:
.\.venv\Scripts\Activate.ps1
```

### On Windows (Command Prompt - `cmd.exe`)
```cmd
.venv\Scripts\activate.bat
```

### On macOS / Linux (bash / zsh)
```bash
source .venv/bin/activate
```

When activated, your terminal prompt will show `(.venv)` at the beginning of the line:
```
(.venv) PS ...\Language_Translation_System>
```

---

## 3. Verify & Install Dependencies

All required dependencies are listed in `requirements.txt`.

To ensure all packages in `.venv` are up to date:
```powershell
pip install -r requirements.txt
```

### Key Libraries Included:
- **FastAPI (`>=0.110.0`):** High-performance asynchronous backend and REST API.
- **Uvicorn (`>=0.29.0`):** Lightning-fast ASGI production web server.
- **PyTorch (`torch>=2.2.0`):** Neural tensor computation backend.
- **Transformers (`transformers>=4.40.0`):** Hugging Face Seq2Seq model and tokenizer loader.
- **SentencePiece (`sentencepiece>=0.2.0`):** Unigram subword tokenization backend.
- **Langdetect (`langdetect>=1.0.9`):** Deterministic character n-gram language identifier.
- **SacreBLEU (`sacrebleu>=2.4.0`):** Standardized BLEU and chrF2 translation evaluation metrics.
- **Pytest (`pytest>=8.0.0`):** Automated test framework.

---

## 4. Running the Web Application

You can start the web application using either of the following two methods:

### Method A: Using the Launcher Script (Recommended)
```powershell
python run.py
```

### Method B: Using Uvicorn Directly
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Server Output:
```
========================================================================
NEURAL TRANSLATION STUDIO - STARTING WEBSERVER
========================================================================
Server URL           : http://127.0.0.1:8000
API Documentation    : http://127.0.0.1:8000/docs
Alternative API Docs : http://127.0.0.1:8000/redoc
Health Check         : http://127.0.0.1:8000/api/v1/health
========================================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 5. Accessing the Web Application

Open your browser and navigate to:

👉 **Web Interface:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

👉 **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

👉 **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 6. Web Interface Walkthrough

### 1. Translation Studio (Tab 1)
- **Source Input:** Type or paste any support message, email, or chat.
- **Source Language:** Select an explicit language or leave on `⚡ Auto-Detect (Script & N-Gram)`.
- **Target Language:** Choose French, English, Spanish, Tamil, German, or Hindi.
- **Quick Preset Chips:** Click any chip (`General Billing`, `Urgent Outage 😡`, `Slang & Emoji 😭`, `Spelling Typos`, `IDs & Error E104`, `Tamil`, `Franglais Mix`) to instantly populate the studio.
- **Intelligent Entity Preservation Toggle:** Keeps product names, URLs, error codes (`E104`), and order IDs (`ORD-2026-8841`) verbatim in the translated output.
- **Beam Search Slider:** Configurable from 1 (Fast greedy decoding) to 6 (Thorough beam search).
- **One-Click Actions:** Copy translation to clipboard, detect language, or swap languages.
- **Diagnostics Panel:** Inspects detected language, confidence score, token counts, per-call latency, and entity verification audits.

### 2. Curated Scenarios Suite (Tab 2)
- Browse 8 real-world support ticket categories.
- Click **"⚡ Test in Studio"** on any card to automatically load it into the Studio and execute translation.

### 3. Entity Preservation Glossary (Tab 3)
- Inspect protected product names and custom terms.
- Add new domain terms into the active runtime glossary.

### 4. Architecture & Pipeline Trace (Tab 4)
- View the 5-stage transformation pipeline: Unicode NFC &rarr; Language Detection &rarr; Entity Span Extraction &rarr; Transformer Seq2Seq &rarr; Entity Audit.

---

## 7. Running Automated Tests

To run the complete test suite verifying language detection, entity preservation, and API endpoints:

```powershell
pytest tests/ -v
```

### Expected Output:
```
tests/test_language_detection.py::test_resolve_language_names PASSED
tests/test_language_detection.py::test_detect_tamil_unicode_script PASSED
tests/test_language_detection.py::test_detect_explicit_override PASSED
tests/test_language_detection.py::test_detect_french_text PASSED
tests/test_language_detection.py::test_detect_spanish_text PASSED
tests/test_language_detection.py::test_detect_empty_text_fallback PASSED
tests/test_term_preservation.py::test_extract_technical_terms PASSED
tests/test_term_preservation.py::test_protect_and_restore_terms PASSED
tests/test_term_preservation.py::test_audit_missing_terms PASSED
tests/test_term_preservation.py::test_glossary_management PASSED
tests/test_api.py::test_index_page PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_languages_endpoint PASSED
tests/test_api.py::test_detect_language_endpoint PASSED
tests/test_api.py::test_samples_endpoint PASSED
tests/test_api.py::test_glossary_endpoints PASSED
tests/test_api.py::test_translate_validation_rejections PASSED
```

---

## 8. Stopping the Server

Press `CTRL + C` in the terminal to cleanly terminate the Uvicorn web server process. To exit the virtual environment:
```powershell
deactivate
```
