# Admin chart search

The admin search API is a retrieval pipeline, not a chatbot. It returns existing
chart records and never asks a model to write an answer.

## Providers

- `GeminiQueryPlanner` turns the search phrase into a short intent and up to three
  alternate retrieval phrases. It receives the query only, never chart records.
- `NvidiaEmbedder` uses `nvidia/nemotron-3-embed-1b` to embed chart passages once
  and search queries on demand. Index vectors are stored in the app database.
- `LexicalRetriever` preserves exact-term matches. Results from retrievers are
  merged with reciprocal-rank fusion.

The indexer hashes the text sent for each chart and its embedding model ID. On
each index sync it embeds only new or changed charts and removes deleted records.
The admin page syncs on load and every five minutes while visible.

## Add a search capability

Implement a planner with `plan(query)` or a retriever with
`search(queries, cases) -> [(case, score), ...]`, then register it with
`register_query_planner()` or `register_retriever()` in `registry.py`. The HTTP
routes, chart CRUD endpoints, and index table do not need to change. Planners
should only transform query intent; retrievers should return chart IDs or model
records, never generated answers.

## Keys

Set `NVIDIA_API_KEY` and `GEMINI_API_KEY` in `back/.env` from newly generated
provider keys. `back/.env.example` lists the supported settings. Never expose
these values through `VITE_` variables or frontend code.
