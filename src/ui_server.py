"""Serve the PUBG UI and expose the RAG pipeline behind it."""

import json
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.task10_generation import SYSTEM_PROMPT, call_llm, format_context, reorder_for_llm
from src.task4_chunking_indexing import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKING_METHOD,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    chunk_documents,
    get_collection,
    load_documents,
)
from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank_rrf
from src.task9_retrieval_pipeline import SCORE_THRESHOLD
import src.task6_lexical_search as lexical


ROOT = Path(__file__).resolve().parent.parent
UI_DIR = ROOT / "UI"
SESSION = {
    "id": uuid.uuid4().hex[:8],
    "started_at": datetime.now(timezone.utc).isoformat(),
    "turns": [],
}


def load_corpus() -> list[dict]:
    """Load the same chunks used for vector indexing into BM25."""
    chunks = chunk_documents(load_documents())
    lexical.CORPUS = chunks
    return chunks


def brief(results: list[dict], limit: int = 5) -> list[dict]:
    items = []
    for item in results[:limit]:
        metadata = item.get("metadata") or {}
        items.append({
            "id": item["id"],
            "score": round(float(item["score"]), 4),
            "method": item["retrieval_method"],
            "title": metadata.get("title"),
            "source": metadata.get("source"),
            "chunk_index": metadata.get("chunk_index"),
            "preview": " ".join(item["content"].split())[:220],
        })
    return items


def pipeline_meta() -> dict:
    collection = get_collection()
    return {
        "session": {
            "id": SESSION["id"],
            "started_at": SESSION["started_at"],
            "turns": len(SESSION["turns"]),
        },
        "chunking": {
            "method": CHUNKING_METHOD,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "indexed_chunks": collection.count(),
            "bm25_chunks": len(lexical.CORPUS),
            "collection": COLLECTION_NAME,
            "embedding_provider": EMBEDDING_PROVIDER,
            "embedding_model": EMBEDDING_MODEL,
        },
    }


def expand_neighbors(results: list[dict], radius: int = 2, limit: int = 8) -> list[dict]:
    """Keep a hit and the following chunks from the same document."""
    by_source = {}
    for item in lexical.CORPUS:
        metadata = item["metadata"]
        by_source.setdefault(metadata.get("source"), {})[metadata.get("chunk_index")] = item
    chosen = []
    seen = set()
    for result in results:
        metadata = result.get("metadata") or {}
        source_chunks = by_source.get(metadata.get("source"), {})
        start = metadata.get("chunk_index")
        indexes = range(start, start + radius + 1) if isinstance(start, int) else []
        for index in indexes:
            item = source_chunks.get(index)
            if not item or item["id"] in seen:
                continue
            chosen.append({
                "id": item["id"],
                "content": item["content"],
                "score": result["score"],
                "metadata": item["metadata"],
                "retrieval_method": result["retrieval_method"],
            })
            seen.add(item["id"])
            if len(chosen) >= limit:
                return chosen
    return chosen


def is_greeting(query: str) -> bool:
    text = unicodedata.normalize("NFD", query.lower().replace("đ", "d"))
    text = "".join(char for char in text if unicodedata.category(char) != "Mn").strip()
    return bool(re.fullmatch(r"(xin chao|chao|chao ban|hello|hi|hey)[!. ]*", text))


def answer_query(query: str, top_k: int = 5) -> dict:
    if is_greeting(query):
        result = {
            "answer": "Xin chào. Mình trả lời từ luật PUBG Esports đã lập chỉ mục. Hỏi về luật SUPER, điểm PGC, roadmap 2026 hoặc Terms of Service.",
            "retrieval_source": "none",
            "sources": [],
        }
        turn = {"query": query, "answer": result["answer"], "retrieval_source": "none"}
        SESSION["turns"].append(turn)
        return {**pipeline_meta(), **result, "semantic": [], "hybrid": [], "turn": turn}

    semantic = semantic_search(query, top_k=top_k)
    lexical_hits = lexical_search(query, top_k=top_k * 2)
    hybrid = rerank_rrf([semantic, lexical_hits], top_k=top_k) if lexical_hits else semantic[:top_k]
    best_dense = semantic[0]["score"] if semantic else 0.0
    used_fallback = best_dense < SCORE_THRESHOLD
    chunks = expand_neighbors(hybrid)
    if not chunks:
        result = {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "retrieval_source": "none",
            "sources": [],
        }
    else:
        try:
            answer = call_llm(
                SYSTEM_PROMPT,
                f"Context:\n{format_context(reorder_for_llm(chunks))}\n\nQuestion: {query}",
            )
            source = chunks[0]["retrieval_method"]
        except Exception as error:
            answer = f"Đã tìm thấy nguồn nhưng không sinh được câu trả lời: {error}"
            source = chunks[0]["retrieval_method"]
        result = {
            "answer": answer,
            "retrieval_source": source,
            "sources": brief(chunks, top_k),
        }
    turn = {
        "query": query,
        "answer": result["answer"],
        "retrieval_source": result["retrieval_source"],
        "best_dense_score": round(best_dense, 4),
        "threshold": SCORE_THRESHOLD,
        "used_fallback_rule": used_fallback,
    }
    SESSION["turns"].append(turn)
    return {
        **pipeline_meta(),
        **result,
        "semantic": brief(semantic, top_k),
        "hybrid": brief(hybrid, top_k),
        "turn": turn,
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/meta":
            self._send(pipeline_meta())
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/ask":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        query = str(payload.get("query", "")).strip()
        if not query:
            self._send({"error": "Thiếu câu hỏi."}, 400)
            return
        try:
            self._send(answer_query(query, int(payload.get("top_k", 5))))
        except Exception as error:
            self._send({"error": str(error)}, 500)

    def _send(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    load_corpus()
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("UI: http://127.0.0.1:8765")
    server.serve_forever()
