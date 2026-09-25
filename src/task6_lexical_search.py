"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import numpy as np
from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def _term_overlap_score(query_terms: list[str], content: str) -> int:
    """Count matching terms for tiebreaking when BM25 scores are equal."""
    content_lower = content.lower()
    return sum(1 for term in query_terms if term in content_lower)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    corpus = CORPUS
    if not corpus:
        return []
    query_terms = query.lower().split()
    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(query_terms)
    # Use term overlap as tiebreaker for equal BM25 scores
    term_scores = [_term_overlap_score(query_terms, item["content"]) for item in corpus]
    # Sort by (bm25_score, term_overlap) descending
    indices = np.lexsort((term_scores, scores))[::-1][:top_k]
    results = []
    for index in indices:
        item = corpus[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
