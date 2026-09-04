# SkillSync

SkillSync is an intelligent, multi-modal competency verification and career guidance platform. It bridges the gap between student skill sets, verifiable technical competencies, and evolving job market expectations.

---

## Target Architecture

SkillSync is built on a **provider-agnostic architecture** where AI extraction is completely decoupled from competency scoring:

```text
Flask (app.py)
  ↓
Routes (/analyze-skills, /analyze-resume, /courses, /api/health)
  ↓
AIService (backend/services/ai_service.py)
  ↓
AIProvider Interface (backend/providers/base.py)
  ├── GeminiProvider (backend/providers/gemini_provider.py) [PRIMARY]
  └── OpenAIProvider (backend/providers/openai_provider.py) [OPTIONAL]
  ↓
Validated Structured JSON
  ↓
Deterministic Competency Engine (backend/competency_engine.py)
  ↓
Evidence Engine (backend/models/evidence.py)
```

### Why the Competency Engine is Provider-Independent
The Competency Engine contains **zero AI SDK imports, zero network requests, zero prompts, and zero API credentials**. It operates purely as a deterministic rules and evidence-weighting engine:
- **Reproducibility**: Identical profiles produce identical competency evaluations and gap rankings.
- **Fairness & Auditability**: Decisions are transparent, explainable, and grounded in the `data/skills.csv` taxonomy.
- **Offline & Low-Connectivity**: The engine can evaluate skills and calculate readiness even when the internet or AI providers are completely unavailable.
- **Evidence Weighting**: Single unverified sources (such as a self-reported resume or unverified credential) can never alone award mastery without verified practical proof.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` to configure your preferred AI provider.

#### Primary Provider: Google Gemini (Recommended)
SkillSync uses Google's official `google-genai` SDK with `gemini-2.5-flash`:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/).*

#### Optional Provider: OpenAI
To switch to OpenAI without changing any application code:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

---

## Running the Application

### Start the Flask Server
```bash
python3 app.py
```
Visit `http://localhost:5000` in your web browser.

### Health Check Endpoint
To inspect the active AI provider, health status, and loaded taxonomy:
```bash
curl http://localhost:5000/api/health
```

---

## Running Tests

SkillSync includes a comprehensive test suite that runs 100% offline with zero live API key dependencies:

```bash
# Run all unit and integration tests
python3 -m unittest discover -s tests -p "test_*.py"

# Run full system integration check
python3 -m tests.verify_full_system
```

---

## Core API Endpoints

- `GET /` — SkillSync Web Portal.
- `GET /api/health` — Provider availability and taxonomy status.
- `POST /analyze-skills` — Analyzes student skills, computes competency levels, archetype alignment, and gap recommendations.
- `POST /analyze-resume` — Compares uploaded resume (`.pdf` or `.txt`) against target job description.
- `GET /courses` — Curated learning pathways mapped to verified competency gaps from trusted providers (Coursera, edX, Microsoft Learn, Google Cloud Skills Boost).
