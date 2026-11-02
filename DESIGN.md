# System Design — ScrapLedger

## 1. Architecture Overview

ScrapLedger is an AI-powered compliance and Extended Producer Responsibility (EPR) intelligence system built for electronics and battery manufacturers complying with Central Pollution Control Board (CPCB) regulations in India.

The system consists of:
- **FastAPI Backend Application**: Provides RESTful endpoints for health monitoring, LLM token & cost usage tracking, structured chat queries, document extraction, and citation-backed question answering.
- **LLM Orchestration Layer**: Powered by `litellm` with an intelligent fallback chain (Google Gemini primary, falling back across Gemini models, OpenAI, and Anthropic), enforcing structured JSON output, timeouts (10s), and automatic retries (3 attempts).
- **PostgreSQL Database with `pgvector`**: Stores firm compliance targets, filed quantities, and high-dimensional vector embeddings of chunked CPCB regulatory PDFs.
- **Docker Containerization**: Portable Docker container with non-root security (`appuser`), automated Docker healthchecks, and Docker Compose orchestration.

```
       +-------------------------------------------------------------+
       |                         Client / UI                         |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                  FastAPI Backend Service                    |
       |  /health  |  /usage  |  /chat  |  /extract  |  /ask         |
       +-------------------------------------------------------------+
               |                                             |
               v (Embeddings / Read-Only SQL)                 v (Multi-Provider Fallback)
+-------------------------------+              +------------------------------+
|     PostgreSQL + pgvector     |              |     LiteLLM Gateway          |
| - epr_obligations             |              | 1. Gemini Flash (Primary)    |
| - document_chunks (embeddings)|              | 2. Gemini Pro / Flash-Lite   |
| - llm_audit_logs              |              | 3. GPT-4o-mini / Claude      |
+-------------------------------+              +------------------------------+
```

---

## 2. API Endpoints

### 2.1 `GET /health`
* **Purpose**: Liveness and readiness probe for Docker healthchecks, CI/CD pipelines, and cloud monitoring.
* **Authentication**: None.
* **Response (200 OK)**:
```json
{
  "status": "ok",
  "app": "ScrapLedger",
  "environment": "local"
}
```

---

### 2.2 `GET /usage`
* **Purpose**: Returns cumulative token usage and accumulated cost in USD across all LLM requests.
* **Authentication**: None.
* **Response (200 OK)**:
```json
{
  "total_tokens": 1250,
  "prompt_tokens": 850,
  "completion_tokens": 400,
  "cost_usd": 0.000425,
  "total_calls": 5
}
```

---

### 2.3 `POST /chat`
* **Purpose**: Accepts compliance queries, invokes the LLM fallback chain, and returns structured JSON (or Server-Sent Events stream).
* **Request Body**:
```json
{
  "query": "What are the EPR collection targets for a producer of laptops in 2026-27?",
  "stream": false,
  "model": "gemini/gemini-flash-latest"
}
```
* **Response (200 OK — JSON mode)**:
```json
{
  "status": "success",
  "model_used": "gemini/gemini-flash-latest",
  "response": {
    "producer_type": "Laptop Manufacturer",
    "rule_reference": "E-Waste (Management) Rules 2022, Schedule III",
    "target_percentage": "80%",
    "deadline": "30th June annually",
    "mandatory_form": "Form 1 (Annual Return)"
  },
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 65,
    "total_tokens": 185,
    "cost_usd": 0.000035
  }
}
```
* **Response (200 OK — Streaming mode `stream: true`)**:
  - `Content-Type: text/event-stream`
  - Yields chunks formatted as `data: {"content": "..."}\n\n` ending with `data: [DONE]\n\n`.
* **Error Responses**:
  - `422 Unprocessable Entity`: Invalid request payload.
  - `503 Service Unavailable`: All primary and fallback models failed or timed out.

---

### 2.4 `POST /extract` *(Planned Week 3)*
* **Purpose**: Ingests raw regulatory text from CPCB gazettes and returns a validated Pydantic EPR obligation checklist.
* **Request Body**:
```json
{
  "raw_text": "Every producer of electrical and electronic equipment listed in Schedule I shall submit an annual return in Form 3 on or before the 30th day of June..."
}
```
* **Response (200 OK)**:
```json
{
  "obligated_entity": "Producer",
  "action_required": "Submit Annual Return",
  "form_number": "Form 3",
  "statutory_deadline": "June 30",
  "penalty_clause": "Environmental Compensation under Rule 22"
}
```

---

### 2.5 `POST /ask` *(Planned Week 3)*
* **Purpose**: Answers user compliance questions with specific citations `[document, page]` by retrieving relevant chunks from `pgvector` and querying target data using safe read-only SQL.
* **Request Body**:
```json
{
  "query": "What is the penalty for selling batteries without EPR registration?"
}
```
* **Response (200 OK)**:
```json
{
  "answer": "Operating without EPR registration attracts Environmental Compensation charges and closure notices under Chapter VIII of the Battery Waste Management Rules 2022.",
  "citations": [
    {
      "document": "Battery_Waste_Management_Rules_2022.pdf",
      "chapter": "VIII",
      "page": 42
    }
  ]
}
```

---

## 3. Database Tables

The database is built on PostgreSQL 16 with the `pgvector` extension enabled.

### 3.1 Table: `epr_obligations`
Stores enterprise EPR targets, filed quantities, deadlines, and compliance status for reporting and Text-to-SQL analyst queries.

| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY DEFAULT gen_random_uuid()` | Unique obligation identifier |
| `producer_name` | `VARCHAR(255)` | `NOT NULL` | Name of the registered producer or recycler |
| `entity_type` | `VARCHAR(100)` | `NOT NULL` | Producer, Recycler, Refurbisher, or Importer |
| `product_category` | `VARCHAR(100)` | `NOT NULL` | e.g., "ITEW1 (Laptops)", "Portable Batteries" |
| `financial_year` | `VARCHAR(10)` | `NOT NULL` | Fiscal year, e.g., "2026-27" |
| `target_quantity_kg` | `NUMERIC(12, 2)` | `NOT NULL` | Mandatory EPR collection target in kilograms |
| `filed_quantity_kg` | `NUMERIC(12, 2)` | `DEFAULT 0.00` | Actual collected/filed quantity to date |
| `shortfall_kg` | `NUMERIC(12, 2)` | `GENERATED ALWAYS AS (target_quantity_kg - filed_quantity_kg) STORED` | Outstanding quantity to achieve target |
| `applicable_form` | `VARCHAR(50)` | `NOT NULL` | Required filing form (e.g., "Form 1", "Form 3") |
| `filing_deadline` | `DATE` | `NOT NULL` | Statutory CPCB submission deadline |
| `rule_citation` | `VARCHAR(255)` | `NOT NULL` | Specific rule and schedule reference |
| `status` | `VARCHAR(50)` | `DEFAULT 'pending'` | 'compliant', 'pending', or 'defaulted' |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT CURRENT_TIMESTAMP` | Last update timestamp |

---

### 3.2 Table: `document_chunks`
Stores chunked passages from CPCB gazettes, SOPs, and amendments along with dense vector embeddings for semantic search.

| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY DEFAULT gen_random_uuid()` | Unique chunk ID |
| `document_name` | `VARCHAR(255)` | `NOT NULL` | Source PDF filename (e.g. `E-Waste_Rules_2022.pdf`) |
| `section_heading` | `VARCHAR(255)` | `NULL` | Section or Schedule title |
| `page_number` | `INTEGER` | `NOT NULL` | Exact page number within the source PDF |
| `chunk_index` | `INTEGER` | `NOT NULL` | Sequential chunk index within the document |
| `chunk_text` | `TEXT` | `NOT NULL` | Extracted legal chunk text |
| `token_count` | `INTEGER` | `NOT NULL` | Number of tokens in this chunk |
| `embedding` | `vector(768)` | `NOT NULL` | Dense vector embedding generated by embedding model |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of embedding ingestion |

---

### 3.3 Table: `llm_audit_logs`
Logs every LLM call for cost accounting, latency tracking, and auditing.

| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY DEFAULT gen_random_uuid()` | Unique log ID |
| `endpoint` | `VARCHAR(50)` | `NOT NULL` | Endpoint invoked (`/chat`, `/extract`, `/ask`) |
| `model_used` | `VARCHAR(100)` | `NOT NULL` | Actual model that fulfilled the request |
| `prompt_tokens` | `INTEGER` | `NOT NULL` | Input tokens consumed |
| `completion_tokens` | `INTEGER` | `NOT NULL` | Output tokens generated |
| `total_tokens` | `INTEGER` | `NOT NULL` | Total tokens consumed |
| `cost_usd` | `NUMERIC(10, 6)` | `NOT NULL` | Exact or estimated cost in USD |
| `latency_ms` | `INTEGER` | `NULL` | Request duration in milliseconds |
| `status` | `VARCHAR(20)` | `NOT NULL` | 'success' or 'fallback' or 'failed' |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of invocation |

---

## 4. SQL DDL Schema

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Create epr_obligations table
CREATE TABLE IF NOT EXISTS epr_obligations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    producer_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    product_category VARCHAR(100) NOT NULL,
    financial_year VARCHAR(10) NOT NULL,
    target_quantity_kg NUMERIC(12, 2) NOT NULL,
    filed_quantity_kg NUMERIC(12, 2) DEFAULT 0.00,
    shortfall_kg NUMERIC(12, 2) GENERATED ALWAYS AS (target_quantity_kg - filed_quantity_kg) STORED,
    applicable_form VARCHAR(50) NOT NULL,
    filing_deadline DATE NOT NULL,
    rule_citation VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_obligations_producer ON epr_obligations(producer_name);
CREATE INDEX idx_obligations_category ON epr_obligations(product_category);
CREATE INDEX idx_obligations_fy ON epr_obligations(financial_year);

-- 2. Create document_chunks table with pgvector
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_name VARCHAR(255) NOT NULL,
    section_heading VARCHAR(255),
    page_number INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_doc_page ON document_chunks(document_name, page_number);
-- HNSW index for fast approximate nearest neighbor vector similarity search
CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- 3. Create llm_audit_logs table
CREATE TABLE IF NOT EXISTS llm_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint VARCHAR(50) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost_usd NUMERIC(10, 6) NOT NULL,
    latency_ms INTEGER,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_created ON llm_audit_logs(created_at DESC);
```
