import json
import os
from threading import Lock
from time import monotonic
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NVIDIA_MODEL = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b")
NVIDIA_EMBEDDINGS_URL = os.getenv(
    "NVIDIA_EMBEDDINGS_URL", "https://integrate.api.nvidia.com/v1/embeddings"
)
GEMINI_MODEL = os.getenv("GEMINI_QUERY_MODEL", "gemini-3.5-flash-lite")


class SearchProviderError(RuntimeError):
    pass


def _post_json(url, headers, payload, provider, timeout=60):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
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
        self._query_cache = {}
        self._cooldown_until = 0
        self._lock = Lock()

    def embed(self, texts, input_type):
        if not self.api_key:
            raise SearchProviderError("Set NVIDIA_API_KEY in back/.env to enable semantic search.")
        if not texts:
            return []
        cache_key = tuple(texts)
        if input_type == "query" and cache_key in self._query_cache:
            return self._query_cache[cache_key]
        with self._lock:
            if input_type == "query" and monotonic() < self._cooldown_until:
                raise SearchProviderError("NVIDIA query embeddings are temporarily unavailable.")
            try:
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
                    timeout=5 if input_type == "query" else 60,
                )
            except SearchProviderError:
                if input_type == "query":
                    self._cooldown_until = monotonic() + 60
                raise
        data = response.get("data", [])
        if len(data) != len(texts):
            raise SearchProviderError("NVIDIA returned an unexpected number of embeddings.")
        vectors = [item["embedding"] for item in sorted(data, key=lambda item: item.get("index", 0))]
        if input_type == "query":
            if len(self._query_cache) >= 128:
                self._query_cache.clear()
            self._query_cache[cache_key] = vectors
        return vectors


class GeminiQueryPlanner:
    """Turns a search phrase into a few retrieval queries; it never answers it."""
    name = "gemini-query-planner"

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._cache = {}
        self._cooldown_until = 0
        self._lock = Lock()

    def plan(self, query):
        if not self.api_key:
            return {"intent": "semantic_chart_search", "queries": [query]}
        cache_key = query.casefold().strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
            if monotonic() < self._cooldown_until:
                return {"intent": "semantic_chart_search", "queries": [query], "planner_fallback": True}
            # Let one request try Gemini; concurrent typeahead requests use
            # the raw query while that call is in flight.
            self._cooldown_until = monotonic() + 7

        try:
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
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "object",
                            "properties": {
                                "intent": {"type": "string"},
                                "queries": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["intent", "queries"],
                        },
                    },
                },
                "Gemini query planner",
                timeout=6,
            )
            raw = response["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw)
            queries = parsed.get("queries", [])
            queries = [value.strip()[:240] for value in queries if isinstance(value, str) and value.strip()]
            queries = list(dict.fromkeys([query, *queries]))[:4]
            plan = {"intent": str(parsed.get("intent", "semantic_chart_search"))[:80], "queries": queries}
            self._cooldown_until = 0
        except SearchProviderError as error:
            self._cooldown_until = monotonic() + 60
            print(f"Gemini query planning unavailable; using raw query: {error}", flush=True)
            plan = {"intent": "semantic_chart_search", "queries": [query], "planner_fallback": True}
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            plan = {"intent": "semantic_chart_search", "queries": [query]}

        if len(self._cache) >= 256:
            self._cache.clear()
        self._cache[cache_key] = plan
        return plan


nvidia_embedder = NvidiaEmbedder()
gemini_query_planner = GeminiQueryPlanner()
