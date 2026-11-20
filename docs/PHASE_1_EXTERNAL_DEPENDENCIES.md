# AXION — Phase 1 External Dependencies & API Integration Guide
## Formal Service Inventory, Credential Requirements, and Mock vs. Real Configuration

**Document Version:** 1.0.0  
**Phase:** Phase 1 — Foundation & Working Pipeline  
**Date:** November 20, 2026  
**Audience:** System Administrators, Research Engineers, and Project Owner  

---

## 1. Overview

AXION is engineered to operate in two distinct execution modes:
1. **Hermetic / Offline Testing Mode (Default in CI/CD):** Uses local deterministic mock providers (`MockProvider`) and local SQLite storage to guarantee zero-network test flakiness, zero API cost, and reproducible evaluation scores.
2. **Production / Live Research Mode:** Connects to external frontier LLM providers (Google Gemini or OpenAI) and live scientific publishing APIs (arXiv, Crossref, PubMed, OpenAlex, HuggingFace, Kaggle) for open-world discovery.

---

## 2. Complete External Service & API Inventory

The table below catalogs every external service, its provider, authentication requirements, and current testing classification:

| Service / Component | Provider | Target Model / Endpoint | Credential Required | Classification | Testing Status | Action Required by Owner |
|---|---|---|---|---|---|---|
| **Deterministic LLM Mock** | Internal | `MockProvider` (in-memory) | None | LOCAL | REAL LOCAL (Tested in CI) | None (Default out of the box) |
| **Google Gemini API** | Google AI | `gemini-1.5-flash` / `gemini-1.5-pro` | `GEMINI_API_KEY` | REAL (Remote API) | FALLBACK TO MOCK | Add API Key in `.env` |
| **OpenAI API** | OpenAI | `gpt-4o` / `text-embedding-3-small` | `OPENAI_API_KEY` | REAL (Remote API) | FALLBACK TO MOCK | Optional: Add API Key in `.env` |
| **arXiv Connector** | Cornell University | `https://export.arxiv.org/api/query` | None (Public) | REAL (Remote API) | LIVE HEALTH CHECK (Tested) | None |
| **Crossref Connector** | Crossref | `https://api.crossref.org/works` | Optional Polite Pool Email | REAL (Remote API) | MOCKED UNIT TESTS | Optional: Configure email in `.env` |
| **PubMed Connector** | NCBI / NIH | `https://eutils.ncbi.nlm.nih.gov/` | Optional `NCBI_API_KEY` | REAL (Remote API) | MOCKED UNIT TESTS | Optional: Configure key for >3 req/s |
| **OpenAlex Connector** | OurResearch | `https://api.openalex.org/` | Optional mailto header | REAL (Remote API) | MOCKED UNIT TESTS | Optional: Configure email |
| **Hugging Face Hub** | Hugging Face | `https://huggingface.co/api/datasets` | None for public | REAL (Remote API) | MOCKED UNIT TESTS | Optional: `HF_TOKEN` for gated repos |
| **Kaggle Datasets** | Kaggle / Google | Kaggle REST API | `KAGGLE_USERNAME`, `KAGGLE_KEY` | REAL (Remote API) | OFFLINE FALLBACK | Required only if querying Kaggle |
| **Web Search** | DuckDuckGo / SerpApi | DuckDuckGo HTML / SerpApi | Optional `SERPAPI_API_KEY` | REAL (Remote API) | MOCKED UNIT TESTS | None (DDG is free fallback) |
| **Database Storage** | SQLite / SQLAlchemy | `axion_dev.db` (local) | None | LOCAL | REAL LOCAL (Tested in CI) | None |

### Classification Key:
- **LOCAL:** Complete native local implementation executing without network access.
- **REAL:** Genuine remote API integration implemented with rate-limiting, error handling, and backoff.
- **FALLBACK TO MOCK:** Module is fully implemented, but gracefully falls back to deterministic local mock when no API key is provided in the environment.

---

## 3. Configuration Procedure for Live Model Providers

To transition AXION from local deterministic testing to live frontier AI inference, configure the `.env` file in the project root:

```ini
# ==============================================================================
# AXION PLATFORM CONFIGURATION (.env)
# ==============================================================================

# Execution Environment: "development" or "production"
AXION_ENV=production
LOG_LEVEL=INFO

# Default LLM Provider: "mock", "gemini", or "openai"
DEFAULT_LLM_PROVIDER=gemini

# Google Gemini Credentials (Recommended)
# Obtain from: https://aistudio.google.com/
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere

# OpenAI Credentials (Alternative)
# Obtain from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-YourOpenAIApiKeyHere

# Model Selections
GEMINI_MODEL=gemini-1.5-flash
OPENAI_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Scholarly Connectors Polite Headers (Optional but Recommended)
CROSSREF_MAILTO=researcher@axion.internal
OPENALEX_MAILTO=researcher@axion.internal

# Kaggle Credentials (Optional - only if searching Kaggle datasets)
KAGGLE_USERNAME=
KAGGLE_KEY=
```

---

## 4. Security & Secret Management Protocols

1. **Zero Secret Leakage:** Never commit `.env` or plain-text credentials to Git. `.env` is included in `.gitignore`.
2. **Safe Fallback Behavior:** If an API key is missing or invalid, AXION logs a warning and routes queries to `MockProvider` rather than crashing the pipeline.
3. **Audit Verification:** During the Phase 1 audit, `git status` and commit history were verified to ensure no API keys or personal tokens were exposed.
