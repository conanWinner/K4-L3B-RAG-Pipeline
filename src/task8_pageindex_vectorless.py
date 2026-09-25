"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

_CACHE_FILE = Path(__file__).parent.parent / ".pageindex_cache.json"


def _load_cache() -> dict:
    if _CACHE_FILE.exists():
        return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    _CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY not set, skipping upload")
        return

    try:
        import pageindex
    except ImportError:
        print("pageindex not installed, skipping upload")
        return

    client = pageindex.Client(api_key=PAGEINDEX_API_KEY, timeout=60)
    cache = _load_cache()

    documents = []
    for path in STANDARDIZED_DIR.rglob("*.md"):
        if path.name in cache:
            continue
        content = path.read_text(encoding="utf-8")
        documents.append({
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem,
            }
        })

    if not documents:
        print("No new documents to upload")
        return

    # Upload in batches if needed
    try:
        response = client.documents.create(documents)
        for i, doc in enumerate(documents):
            cache[doc["metadata"]["source"]] = response[i].id
        _save_cache(cache)
        print(f"Uploaded {len(documents)} documents to PageIndex")
    except Exception as e:
        print(f"PageIndex upload failed: {e}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not PAGEINDEX_API_KEY:
        return []

    try:
        import pageindex
    except ImportError:
        return []

    cache = _load_cache()
    if not cache:
        return []

    client = pageindex.Client(api_key=PAGEINDEX_API_KEY, timeout=30)

    try:
        # Search across all uploaded documents
        document_ids = list(cache.values())
        response = client.search.query(
            query=query,
            document_ids=document_ids,
            top_k=top_k
        )

        results = []
        for rank, node in enumerate(response.nodes):
            metadata = node.metadata
            results.append({
                "id": f"pageindex::{node.id}",
                "content": node.text,
                "score": max(0.01, 1.0 - rank * 0.1),  # fallback score by rank
                "metadata": {
                    "source": metadata.get("source", "unknown"),
                    "title": metadata.get("title", "unknown"),
                    "doc_type": metadata.get("doc_type", "news"),
                    "url": None,
                    "chunk_index": 0,
                },
                "retrieval_method": "pageindex",
            })
        return results
    except Exception as e:
        print(f"PageIndex search failed: {e}")
        return []


if __name__ == "__main__":
    upload_documents()
