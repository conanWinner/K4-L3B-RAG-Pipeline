import json
from pathlib import Path

import pytest

import src.task3_convert_markdown as task3


def configure_directories(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    landing = tmp_path / "landing"
    output = tmp_path / "standardized"
    (landing / "legal").mkdir(parents=True)
    (landing / "news").mkdir(parents=True)
    monkeypatch.setattr(task3, "LANDING_DIR", landing)
    monkeypatch.setattr(task3, "OUTPUT_DIR", output)
    return landing, output


def test_convert_legal_docs_is_stable(monkeypatch, tmp_path):
    landing, output = configure_directories(monkeypatch, tmp_path)
    source = landing / "legal" / "rulebook.pdf"
    source.write_bytes(b"fake PDF for isolated unit test")
    converted = "Rulebook content with stable text. " * 10
    monkeypatch.setattr(task3, "_convert_legal_file", lambda path: converted)

    task3.convert_legal_docs()
    target = output / "legal" / "rulebook.md"
    first_mtime = target.stat().st_mtime_ns
    task3.convert_legal_docs()

    assert target.read_text(encoding="utf-8") == f"{converted.strip()}\n"
    assert target.stat().st_mtime_ns == first_mtime


def test_convert_news_keeps_metadata_and_avoids_duplicate_title(monkeypatch, tmp_path):
    landing, output = configure_directories(monkeypatch, tmp_path)
    article = {
        "url": "https://example.com/article",
        "title": "Tournament update",
        "date_crawled": "2026-09-25T00:00:00+00:00",
        "content_markdown": "# Tournament update\n\n" + "Useful details. " * 20,
    }
    (landing / "news" / "update.json").write_text(
        json.dumps(article), encoding="utf-8"
    )

    task3.convert_news_articles()
    markdown = (output / "news" / "update.md").read_text(encoding="utf-8")

    assert markdown.count("# Tournament update") == 1
    assert article["url"] in markdown
    assert article["date_crawled"] in markdown


def test_invalid_news_does_not_create_output(monkeypatch, tmp_path):
    landing, output = configure_directories(monkeypatch, tmp_path)
    (landing / "news" / "invalid.json").write_text(
        json.dumps({"title": "Missing fields"}), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Missing or empty fields"):
        task3.convert_news_articles()

    assert not (output / "news" / "invalid.md").exists()
