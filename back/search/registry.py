"""Stable plugin seam for query planning and retrieval strategies."""

from collections import defaultdict
import os
import re

from models.model import Case, CaseSearchEmbedding
from search.providers import SearchProviderError, gemini_query_planner, nvidia_embedder


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


def _query_constraints(query):
    """Parse hard degree constraints from the user's wording, without an LLM."""
    text = query.casefold().replace("’", "'")
    constraints = {"require_bachelor": False, "exclude_master": False}
    if re.search(r"\b(bachelor'?s?|undergraduate|undergrad)\b", text):
        constraints["require_bachelor"] = True
    if re.search(
        r"\b(?:did\s+not|didn't|has\s+not|hasn't|have\s+not|haven't|not|no|without|incomplete|unfinished)\b"
        r"(?:\s+\w+){0,3}\s+\bmaster'?s?\b|\bmaster'?s?\b\s+(?:incomplete|unfinished|not completed)\b",
        text,
    ):
        constraints["exclude_master"] = True
    return constraints


def _matches_constraints(case, constraints):
    text = " ".join([
        case.title or "", case.story or "", *(tag.name for tag in case.tags)
    ]).casefold().replace("’", "'")
    if constraints["exclude_master"] and re.search(r"\bmasters?\b|\bmaster's\b", text):
        return False
    if constraints["require_bachelor"] and not re.search(
        r"\b(bachelors?|undergraduate|undergrad)\b", text
    ):
        return False
    return True


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
        ranked = sorted(
            ((case, best.get(case.id, -1.0)) for case, _ in available),
            key=lambda item: item[1], reverse=True,
        )
        minimum = float(os.getenv("SEARCH_MIN_COSINE", "0.20"))
        matches = [(case, score) for case, score in ranked if score >= minimum]
        # A hard cutoff can erase every result for a valid but broad question.
        # Keep the closest charts available when none clear the configured bar.
        return matches if matches else ranked[:20]


class LexicalRetriever:
    """Keeps exact terms useful alongside vector matches."""
    name = "lexical"
    weight = 0.55

    def search(self, queries, cases):
        terms = set(token for query in queries for token in _tokens(query))
        query_text = " ".join(queries).casefold().replace("'", "")
        if any(phrase in query_text for phrase in ("higher education", "higher studies", "postgraduate", "masters", "master degree")) and not re.search(r"\b(?:not|no|without|didn't|incomplete|unfinished)\b.{0,24}\bmasters?\b", query_text):
            terms.update({"master", "masters", "postgraduate", "graduate", "degree", "graduation", "education", "studied", "study", "university", "college"})
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
    constraints = _query_constraints(query)
    candidates = [case for case in cases if _matches_constraints(case, constraints)]
    if not candidates:
        return {"intent": "semantic_chart_search", "queries": [query], "constraints_applied": True}, []
    # A planner failure degrades to semantic + lexical retrieval with the raw query.
    try:
        plan = QUERY_PLANNERS[0].plan(query) if QUERY_PLANNERS else {"intent": "search", "queries": [query]}
    except Exception as error:
        print(f"Gemini query planning failed; using semantic fallback: {error}", flush=True)
        plan = {"intent": "semantic_chart_search", "queries": [query], "planner_fallback": True}
    queries = [query, *plan.get("queries", [])]
    queries = list(dict.fromkeys(q.strip() for q in queries if isinstance(q, str) and q.strip()))[:4]

    combined = defaultdict(float)
    components = defaultdict(dict)
    for retriever in RETRIEVERS:
        try:
            results = retriever.search(queries, candidates)
        except SearchProviderError as error:
            # A provider outage must not prevent local lexical retrieval.
            print(f"{retriever.name} retrieval unavailable; continuing with local search: {error}", flush=True)
            plan["retriever_fallback"] = True
            continue
        for rank, (case, raw_score) in enumerate(results, start=1):
            contribution = retriever.weight / (60 + rank)
            combined[case.id] += contribution
            components[case.id][retriever.name] = round(float(raw_score), 4)

    case_by_id = {case.id: case for case in candidates}
    ordered = sorted(combined, key=combined.get, reverse=True)
    return plan, [
        {"case": case_by_id[case_id], "score": combined[case_id], "matches": components[case_id]}
        for case_id in ordered
    ]
