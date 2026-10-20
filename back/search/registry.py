"""Stable plugin seam for query planning and retrieval strategies."""

from collections import defaultdict
import os

from models.model import Case, CaseSearchEmbedding
from search.providers import gemini_query_planner, nvidia_embedder


QUERY_PLANNERS = []
RETRIEVERS = []


def register_query_planner(planner):
    QUERY_PLANNERS.append(planner)
    return planner


def register_retriever(retriever):
    RETRIEVERS.append(retriever)
    return retriever


def _tokens(text):
    return [part.casefold() for part in text.split() if len(part) > 1]


class SemanticRetriever:
    name = "semantic"
    weight = 1.0

    def search(self, queries, cases):
        vectors = {entry.case_id: _unpack_vector(entry.vector) for entry in CaseSearchEmbedding.query.all()}
        available = [(case, vectors[case.id]) for case in cases if case.id in vectors]
        if not available:
            return []

        query_vectors = nvidia_embedder.embed(queries, input_type="query")
        best = {}
        for query_vector in query_vectors:
            for case, vector in available:
                score = _cosine(query_vector, vector)
                best[case.id] = max(best.get(case.id, -1.0), score)
        minimum = float(os.getenv("SEARCH_MIN_COSINE", "0.20"))
        return sorted(
            ((case, score) for case, _ in available if (score := best.get(case.id, -1)) >= minimum),
            key=lambda item: item[1], reverse=True,
        )


class LexicalRetriever:
    """Keeps exact terms useful alongside vector matches."""
    name = "lexical"
    weight = 0.55

    def search(self, queries, cases):
        terms = set(token for query in queries for token in _tokens(query))
        ranked = []
        for case in cases:
            fields = [case.title or "", case.place or "", case.state or "", case.story or ""]
            fields.extend(tag.name for tag in case.tags)
            text = " ".join(fields).casefold()
            hits = sum(text.count(term) for term in terms)
            if hits:
                ranked.append((case, hits / (1 + len(terms))))
        return sorted(ranked, key=lambda item: item[1], reverse=True)


def _cosine(left, right):
    if len(left) != len(right) or not left:
        return -1.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    return dot / (left_norm * right_norm) if left_norm and right_norm else -1.0


def _unpack_vector(value):
    import struct
    size = len(value) // 4
    return struct.unpack(f"<{size}f", value)


register_query_planner(gemini_query_planner)
register_retriever(SemanticRetriever())
register_retriever(LexicalRetriever())


def search_cases(query, cases):
    # A planner failure degrades to semantic + lexical retrieval with the raw query.
    try:
        plan = QUERY_PLANNERS[0].plan(query) if QUERY_PLANNERS else {"intent": "search", "queries": [query]}
    except Exception:
        plan = {"intent": "semantic_chart_search", "queries": [query], "planner_fallback": True}
    queries = [query, *plan.get("queries", [])]
    queries = list(dict.fromkeys(q.strip() for q in queries if isinstance(q, str) and q.strip()))[:4]

    combined = defaultdict(float)
    components = defaultdict(dict)
    for retriever in RETRIEVERS:
        results = retriever.search(queries, cases)
        for rank, (case, raw_score) in enumerate(results, start=1):
            contribution = retriever.weight / (60 + rank)
            combined[case.id] += contribution
            components[case.id][retriever.name] = round(float(raw_score), 4)

    case_by_id = {case.id: case for case in cases}
    ordered = sorted(combined, key=combined.get, reverse=True)
    return plan, [
        {"case": case_by_id[case_id], "score": combined[case_id], "matches": components[case_id]}
        for case_id in ordered
    ]
