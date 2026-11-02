# Progress

Commit after every class. Tag every Friday: `git tag week-N && git push origin week-N`.

## Week 1 (tag week-1 by Fri 23 Oct)
- [x] Repo created from the Examate template and registered on the form
- [x] README top section filled from my project card
- [x] /health runs locally
- [x] docs/QUESTIONS.md: 10 real questions
- [x] 50+ pages collected, DATASET.md filled, sample in data/sample/
- [x] Tag week-1 pushed

## Week 2 (tag week-2 by Fri 30 Oct)
- [x] POST /chat calls an LLM and returns structured JSON
- [x] Streaming, timeouts, retry and a fallback model
- [x] Cost log + GET /usage
- [x] Docker Compose (API + Postgres/pgvector) runs
- [x] CI green, live link in README
- [x] Tag week-2 pushed

## Week 3 (tag week-3 by Fri 6 Nov)
- [ ] Parser keeps page numbers and headings
- [ ] 500+ pages chunked, embedded and stored in pgvector
- [ ] POST /ask answers with [document, page] citations
- [ ] docs/EVAL_v0.md with my 10 questions scored
- [ ] Tag week-3 pushed

## Daily log
| Date | What I did today | Commit |
|---|---|---|
| 2026-10-23 | Initial setup from Examate template | 97769bb |
| 2026-10-24 | Added polite PDF downloader tool | fbf00cd |
| 2026-10-25 | Added questions, CPCB dataset, and sample PDFs | 334c580 |
| 2026-10-25 | Completed Week 1 documentation and DATASET.md | 578de08 |
| 2026-10-30 | Implemented LLM fallback model chain, /usage endpoint, and Docker setup | b002420 |
| 2026-11-02 | Completed Week 2: DESIGN.md tables & endpoints, live host docs, test suite | HEAD |
