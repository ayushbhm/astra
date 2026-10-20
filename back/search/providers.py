import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NVIDIA_MODEL = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b")
NVIDIA_EMBEDDINGS_URL = os.getenv(
    "NVIDIA_EMBEDDINGS_URL", "https://integrate.api.nvidia.com/v1/embeddings"
)
GEMINI_MODEL = os.getenv("GEMINI_QUERY_MODEL", "gemini-3.5-flash-lite")


class SearchProviderError(RuntimeError):
    pass


def _post_json(url, headers, payload, provider):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        # Avoid returning provider response bodies, which can contain request data.
        raise SearchProviderError(f"{provider} request failed (HTTP {error.code}).") from None
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise SearchProviderError(f"Could not reach {provider}.") from error


class NvidiaEmbedder:
    name = "nemotron-3-embed-1b"

    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY", "").strip()

    def embed(self, texts, input_type):
        if not self.api_key:
            raise SearchProviderError("Set NVIDIA_API_KEY in back/.env to enable semantic search.")
        if not texts:
            return []
        response = _post_json(
            NVIDIA_EMBEDDINGS_URL,
            {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"},
            {
                "input": texts,
                "model": NVIDIA_MODEL,
                "input_type": input_type,
                "encoding_format": "float",
                "truncate": "END",
            },
            "NVIDIA embeddings",
        )
        data = response.get("data", [])
        if len(data) != len(texts):
            raise SearchProviderError("NVIDIA returned an unexpected number of embeddings.")
        return [item["embedding"] for item in sorted(data, key=lambda item: item.get("index", 0))]


class GeminiQueryPlanner:
    """Turns a search phrase into a few retrieval queries; it never answers it."""
    name = "gemini-query-planner"

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._cache = {}

    def plan(self, query):
        if not self.api_key:
            return {"intent": "semantic_chart_search", "queries": [query]}
        cache_key = query.casefold().strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        prompt = (
            "Prepare search queries for a private archive of astrological case records. "
            "The user wants relevant records, not advice or an answer. Preserve the user's "
            "meaning; add at most three concise alternate phrasings or related event terms. "
            "Do not invent chart facts. Return JSON only with keys intent and queries; "
            "intent is a short category and queries is an array of strings.\n"
            f"User search: {query[:500]}"
        )
        response = _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            {"x-goog-api-key": self.api_key},
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0,
                    "responseFormat": {
                        "text": {
                            "mimeType": "application/json",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "intent": {"type": "string"},
                                    "queries": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["intent", "queries"],
                            },
                        }
                    },
                },
            },
            "Gemini query planner",
        )
        try:
            raw = response["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw)
            queries = parsed.get("queries", [])
            queries = [value.strip()[:240] for value in queries if isinstance(value, str) and value.strip()]
            queries = list(dict.fromkeys([query, *queries]))[:4]
            plan = {"intent": str(parsed.get("intent", "semantic_chart_search"))[:80], "queries": queries}
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            plan = {"intent": "semantic_chart_search", "queries": [query]}

        if len(self._cache) >= 256:
            self._cache.clear()
        self._cache[cache_key] = plan
        return plan


nvidia_embedder = NvidiaEmbedder()
gemini_query_planner = GeminiQueryPlanner()
