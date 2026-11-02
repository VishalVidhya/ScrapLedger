# System Design

## Architecture
ScrapLedger uses a FastAPI backend containerized with Docker. It connects to a PostgreSQL database with `pgvector` for storing and querying CPCB document embeddings. LLM integrations handle structured extraction (JSON) and natural language queries (Text-to-SQL).

## API Endpoints
| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/health` | GET | Basic health check for CI/CD and deployment monitoring. |
| `/usage` | GET | Returns current LLM token usage and estimated costs. |
| `/extract` | POST | Takes raw CPCB text and returns validated JSON using Pydantic. |
| `/ask` | POST | Takes a natural language query and returns an answer with citations. |