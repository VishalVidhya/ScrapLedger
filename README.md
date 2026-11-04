# ScrapLedger

[![CI](https://github.com/VishalVidhya/ScrapLedger/actions/workflows/ci.yml/badge.svg)](https://github.com/VishalVidhya/ScrapLedger/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![Python 3.12](https://img.shields.io/badge/python-3.12-brightgreen.svg)](https://www.python.org/)
[![Live Host](https://img.shields.io/badge/Render-Live%20Host-success.svg)](https://scrapledger.onrender.com/health)

## Problem
Electronics makers and recyclers must meet strict Extended Producer Responsibility (EPR) targets under the E-Waste and Battery Waste rules. The rules, SOPs, and amendments are long, scattered across 800+ pages of dense legal text. Missing a filing step, misunderstanding a formula, or missing a deadline directly leads to heavy financial penalties and environmental compensation charges. Manually parsing these rules to build compliance checklists and track targets is error-prone and time-consuming. ScrapLedger solves this by turning CPCB e-waste and battery waste rules into clear, structured EPR checklists. It uses structured extraction and a natural-language data analyst to track compliance, citing the exact rule behind each obligation.

## Who it is for
* **EHS Executive**: An Environment, Health, and Safety executive at an electronics manufacturing unit in Hosur who needs to ensure strict environmental compliance and track EPR targets.
* **Compliance Officer**: A regulatory compliance manager at a battery manufacturing firm who needs to calculate annual EPR obligations and track return deadlines.

## Signature feature
**One-Click EPR Checklist & Analyst**: Enter a producer type (e.g., laptop manufacturer) to generate a structured EPR integration checklist (exported as validated JSON or a printable list) detailing who, what, deadline, form, and penalty. Additionally, it features a natural-language data analyst agent (using safe, read-only SQL) that queries the firm's EPR targets and filed quantities in a Postgres table, answering questions like "how far are we from this year's e-waste target?" while citing the specific rule behind each target.

## Hardest problem 
The hardest engineering challenge in ScrapLedger is accurately parsing and extracting structured obligations (who, what, deadline, form, penalty) from 800+ pages of dense, poorly formatted government PDFs, and achieving a 90%+ field-level accuracy. Legal documents often span requirements across multiple sections, amendments, and tables. To solve this, I designed a pipeline that chunks the PDFs, embeds them into a PostgreSQL database with pgvector, and uses a structured extraction LLM call validated against strict Pydantic schemas. Additionally, I had to securely combine natural-language Text-to-SQL for querying internal compliance data with RAG for citing the external legal rules, ensuring the AI agent cannot hallucinate targets or execute destructive database queries.

## Live Service
The service is deployed live on a free Render host:
* **Health Check**: [https://scrapledger.onrender.com/health](https://scrapledger.onrender.com/health)
* **Usage Endpoint**: [https://scrapledger.onrender.com/usage](https://scrapledger.onrender.com/usage)

## Dataset
| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| Central Pollution Control Board (CPCB) / MoEFCC | [cpcb.gov.in](https://cpcb.gov.in/) / [eprewaste.cpcb.gov.in](https://eprewaste.cpcb.gov.in/) / [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/) | E-Waste Rules 2022, Battery Waste Rules 2022, Hazardous Waste Rules 2016, ELV Recycling Guidelines, SOPs & Amendments (38 docs) | 537 pages collected (800+ pages full corpus) | Public domain government regulatory gazettes |

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

## System Design
Detailed API specifications and database tables are documented in [DESIGN.md](DESIGN.md).

---

## Run it

### Local Python Environment
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

### Docker
Build and run the standalone container:
```bash
docker build -t scrapledger .
docker run -p 8000:8000 --env-file .env scrapledger
```

### Docker Compose (API + Postgres/pgvector)
Run the full stack with PostgreSQL & pgvector:
```bash
docker compose up --build
```

---

## API Verification

1. **Health Check**:
```bash
curl http://localhost:8000/health
# {"status":"ok","app":"ScrapLedger","environment":"local"}
```

2. **LLM Chat with Fallback & Structured JSON**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the EPR collection targets for a producer of laptops in 2026-27?"}'
```

3. **Cumulative Usage & Cost**:
```bash
curl http://localhost:8000/usage
# {"total_tokens":185,"prompt_tokens":120,"completion_tokens":65,"cost_usd":0.000035,"total_calls":1}
```

4. **Run Tests**:
```bash
pytest -v
ruff check .
```
