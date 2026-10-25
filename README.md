**# ScrapLedger**

**## Problem**

Electronics makers and recyclers must meet strict Extended Producer Responsibility (EPR) targets under the E-Waste and Battery Waste rules. The rules, SOPs, and amendments are long, scattered across 800+ pages of dense legal text. Missing a filing step, misunderstanding a formula, or missing a deadline directly leads to heavy financial penalties and environmental compensation charges. Manually parsing these rules to build compliance checklists and track targets is error-prone and time-consuming. ScrapLedger solves this by turning CPCB e-waste and battery waste rules into clear, structured EPR checklists. It uses structured extraction and a natural-language data analyst to track compliance, citing the exact rule behind each obligation.

**## Who it is for**

EHS Executive: An Environment, Health, and Safety executive at an electronics manufacturing unit in Hosur who needs to ensure strict environmental compliance and track EPR targets.

Compliance Officer: A regulatory compliance manager at a battery manufacturing firm who needs to calculate annual EPR obligations and track return deadlines.

**## Signature feature**

One-Click EPR Checklist & Analyst: Enter a producer type (e.g., laptop manufacturer) to generate a structured EPR integration checklist (exported as validated JSON or a printable list) detailing who, what, deadline, form, and penalty. Additionally, it features a natural-language data analyst agent (using safe, read-only SQL) that queries the firm's EPR targets and filed quantities in a Postgres table, answering questions like "how far are we from this year's e-waste target?" while citing the specific rule behind each target.

**## Hardest problem (my interview story)**

The hardest engineering challenge in ScrapLedger is accurately parsing and extracting structured obligations (who, what, deadline, form, penalty) from 800+ pages of dense, poorly formatted government PDFs, and achieving a 90%+ field-level accuracy. Legal documents often span requirements across multiple sections, amendments, and tables. To solve this, I designed a pipeline that chunks the PDFs, embeds them into a PostgreSQL database with pgvector, and uses a structured extraction LLM call validated against strict Pydantic schemas. Additionally, I had to securely combine natural-language Text-to-SQL for querying internal compliance data with RAG for citing the external legal rules, ensuring the AI agent cannot hallucinate targets or execute destructive database queries.

**## Dataset**

| Source | Link | Documents | Pages | Licence / terms |

|---|---|---|---|---|

| Central Pollution Control Board (CPCB) | [cpcb.nic.in](https://cpcb.nic.in/) | E-Waste (Management) Rules 2022, Battery Waste Management Rules 2022, SOPs, and amendments | 800+ pages | Publicly available government regulatory documents |

**## 10 real questions**

See [docs/QUESTIONS.md](docs/QUESTIONS.md).

**## Run it**

```bash

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt

cp .env.example .env                                 # Windows: copy .env.example .env

uvicorn app.main:app --reload

curl localhost:8000/health

## Live link

<Added in Week 2>
