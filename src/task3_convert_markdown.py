"""Task 3 — Chuẩn hóa dữ liệu nguồn sang Markdown.

PDF/DOC/DOCX được chuyển bằng MarkItDown khi thư viện có sẵn. Với PDF và
DOCX, module có phương án dự phòng cục bộ để pipeline vẫn chạy được trong môi
trường chưa cài đủ dependency. JSON bài viết được kiểm tra schema trước khi
ghi và luôn giữ metadata nguồn ở đầu tài liệu.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"

LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}
REQUIRED_NEWS_FIELDS = ("url", "title", "date_crawled", "content_markdown")
MIN_CONTENT_LENGTH = 200
PDFTOTEXT_TIMEOUT_SECONDS = 120


def _normalise_markdown(text: str, source: Path) -> str:
    """Chuẩn hóa newline và từ chối nội dung rỗng hoặc lỗi mã hóa rõ ràng."""
    if "\ufffd" in text:
        raise ValueError(f"Encoding replacement character found in {source}")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "").replace("\f", "\n\n")
    lines = [line.rstrip() for line in text.splitlines()]
    normalized = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    if len(normalized) < MIN_CONTENT_LENGTH:
        raise ValueError(
            f"Converted content from {source} is shorter than "
            f"{MIN_CONTENT_LENGTH} characters"
        )
    return f"{normalized}\n"


def _convert_with_markitdown(path: Path) -> str | None:
    """Dùng MarkItDown nếu dependency đã được cài trong môi trường hiện tại."""
    try:
        from markitdown import MarkItDown
    except ImportError:
        return None

    result = MarkItDown().convert(str(path))
    text = getattr(result, "text_content", None)
    if not isinstance(text, str):
        raise ValueError(f"MarkItDown returned no text for {path}")
    return text


def _convert_pdf_with_pdftotext(path: Path) -> str:
    executable = shutil.which("pdftotext")
    if executable is None:
        raise RuntimeError(
            "Cannot convert PDF: install project dependency 'markitdown[pdf]' "
            "or the 'pdftotext' command"
        )

    completed = subprocess.run(
        [executable, "-layout", "-nopgbrk", str(path), "-"],
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="strict",
        timeout=PDFTOTEXT_TIMEOUT_SECONDS,
    )
    return completed.stdout


def _convert_docx_with_stdlib(path: Path) -> str:
    """Trích xuất đoạn văn và bảng từ DOCX khi MarkItDown chưa được cài."""
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as error:
        raise ValueError(f"Invalid DOCX file: {path}") from error

    root = ElementTree.fromstring(xml)
    blocks: list[str] = []
    for paragraph in root.findall(".//w:p", namespaces):
        text = "".join(
            node.text or "" for node in paragraph.findall(".//w:t", namespaces)
        ).strip()
        if text:
            blocks.append(text)
    return "\n\n".join(blocks)


def _convert_legal_file(path: Path) -> str:
    converted = _convert_with_markitdown(path)
    if converted is not None:
        return converted
    if path.suffix.lower() == ".pdf":
        return _convert_pdf_with_pdftotext(path)
    if path.suffix.lower() == ".docx":
        return _convert_docx_with_stdlib(path)
    raise RuntimeError(
        f"Cannot convert legacy DOC file without MarkItDown: {path}. "
        "Convert it to DOCX or install the declared project dependencies."
    )


def _write_if_changed(path: Path, content: str) -> bool:
    """Ghi output xác định; không chạm vào tệp nếu nội dung không đổi."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _source_files(directory: Path, extensions: set[str]) -> list[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(f"Missing input directory: {directory}")
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in extensions
    )


def _ensure_unique_output_names(paths: list[Path]) -> None:
    stems = [path.stem.casefold() for path in paths]
    duplicates = sorted({stem for stem in stems if stems.count(stem) > 1})
    if duplicates:
        raise ValueError(f"Input files would overwrite the same output: {duplicates}")


def convert_legal_docs() -> None:
    """Chuyển toàn bộ PDF/DOC/DOCX thành Markdown trong nhánh legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    source_files = _source_files(legal_dir, LEGAL_EXTENSIONS)
    _ensure_unique_output_names(source_files)
    output_dir.mkdir(parents=True, exist_ok=True)

    changed = 0
    for path in source_files:
        content = _normalise_markdown(_convert_legal_file(path), path)
        changed += _write_if_changed(output_dir / f"{path.stem}.md", content)
    print(f"Legal Markdown: {len(source_files)} files ({changed} updated)")


def _news_markdown(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error.msg}") from error
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")

    missing = [
        field
        for field in REQUIRED_NEWS_FIELDS
        if not isinstance(data.get(field), str) or not data[field].strip()
    ]
    if missing:
        raise ValueError(f"Missing or empty fields in {path}: {', '.join(missing)}")

    title = data["title"].strip()
    body = data["content_markdown"].strip()
    first_line, separator, remainder = body.partition("\n")
    if first_line.strip().casefold() == f"# {title}".casefold():
        body = remainder.lstrip() if separator else ""

    markdown = (
        f"# {title}\n\n"
        f"- **Source:** {data['url'].strip()}\n"
        f"- **Crawled:** {data['date_crawled'].strip()}\n\n"
        f"---\n\n{body}"
    )
    return _normalise_markdown(markdown, path)


def convert_news_articles() -> None:
    """Chuyển JSON bài viết thành Markdown có metadata nguồn."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    source_files = _source_files(news_dir, {".json"})
    _ensure_unique_output_names(source_files)
    output_dir.mkdir(parents=True, exist_ok=True)

    changed = 0
    for path in source_files:
        changed += _write_if_changed(
            output_dir / f"{path.stem}.md",
            _news_markdown(path),
        )
    print(f"News Markdown: {len(source_files)} files ({changed} updated)")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
