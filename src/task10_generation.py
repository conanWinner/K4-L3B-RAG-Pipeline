"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from typing import Optional

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời câu hỏi nội dung chỉ từ context được cung cấp.
Mỗi khẳng định về tài liệu phải có citation. Nếu thiếu evidence, hãy từ chối xác minh.
Nếu người dùng chỉ chào hỏi, hãy chào lại ngắn và mời họ hỏi về tài liệu.
 Không gắn nguồn cho lời chào. Các câu hỏi vu vơ hay không liên quan 
 của người dùng thì vẫn sẽ trả lời theo kiểu hướng người dùng đến chủ đề chính."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (lost-in-the-middle mitigation)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label để LLM tạo citation."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[Document {index} | Title: {metadata['title']} | "
            f"Source: {metadata['source']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def _call_openai(system_prompt: str, user_message: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(system_prompt: str, user_message: str, model: str) -> str:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=model or "gemini-3.8-flash",
        contents=f"{system_prompt}\n\n{user_message}",
        config=genai.types.GenerateContentConfig(
            temperature=TEMPERATURE,
            top_p=TOP_P,
        ),
    )
    return response.text.strip()


def _call_anthropic(system_prompt: str, user_message: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model or "claude-3-haiku-20240307",
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        temperature=TEMPERATURE,
        max_tokens=1024,
    )
    return response.content[0].text.strip()


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = LLM_PROVIDER.lower()
    model = LLM_MODEL

    if provider == "openai":
        return _call_openai(system_prompt, user_message, model)
    elif provider == "gemini":
        return _call_gemini(system_prompt, user_message, model)
    elif provider == "anthropic":
        return _call_anthropic(system_prompt, user_message, model)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as e:
        print(f"LLM call failed: {e}")
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": chunks,
            "retrieval_source": chunks[0]["retrieval_method"] if chunks else "none",
        }
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0]["retrieval_method"],
    }


if __name__ == "__main__":
    print(generate_with_citation("test query"))
