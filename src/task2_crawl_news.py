"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://pubg.com/en/clause/term_of_service/label_steam/latest",
]

OUTPUT_FILENAMES = {
    ARTICLE_URLS[0]: "pubg_terms_of_service.json",
}

REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = "K4-RAG-Pipeline/1.0"


class ArticleHTMLParser(HTMLParser):
    """Extract readable Markdown-like text from the page's main article."""

    BLOCK_TAGS = {
        "article",
        "blockquote",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._article_depth = 0
        self._ignored_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())

        if self._article_depth == 0 and tag == "article" and (
            "content-template__content" in classes
        ):
            self._article_depth = 1
            return

        if self._article_depth == 0:
            return

        if tag not in self.VOID_TAGS:
            self._article_depth += 1
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        elif self._ignored_depth == 0:
            if tag == "br":
                self._parts.append("\n")
            elif tag == "li":
                self._parts.append("\n- ")
            elif tag in self.BLOCK_TAGS:
                self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._article_depth == 0 or tag in self.VOID_TAGS:
            return

        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif self._ignored_depth == 0 and tag in self.BLOCK_TAGS:
            self._parts.append("\n")

        self._article_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._article_depth and self._ignored_depth == 0:
            self._parts.append(data)

    def markdown(self) -> str:
        lines = []
        for raw_line in "".join(self._parts).splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if line and (not lines or line != lines[-1]):
                lines.append(line)
        return "\n\n".join(lines)


def _fetch_article(url: str) -> dict:
    """Fetch one public page and extract its main article without browser automation."""
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type:
        raise ValueError(f"Expected HTML from {url}, received {content_type!r}")

    parser = ArticleHTMLParser()
    parser.feed(response.text)
    content = parser.markdown()
    if len(content) < 200:
        raise ValueError(f"Main article content is missing or too short: {url}")

    content_lines = content.splitlines()
    first_line = content_lines[0]
    title = first_line if len(first_line) <= 200 else urlparse(url).netloc
    body = "\n".join(content_lines[1:]).strip()
    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": f"# {title}\n\n{body}",
    }


async def crawl_article(url: str) -> dict:
    """Crawl one article without blocking the asyncio event loop."""
    return await asyncio.to_thread(_fetch_article, url)


async def crawl_all(*, refresh: bool = False) -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        output = DATA_DIR / OUTPUT_FILENAMES.get(url, f"article_{index:02d}.json")
        if output.exists() and not refresh:
            print(f"Skipped existing file: {output}")
            continue

        try:
            article = await crawl_article(url)
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--refresh",
        action="store_true",
        help="Crawl lại và cập nhật đúng các JSON được cấu hình.",
    )
    arguments = argument_parser.parse_args()
    asyncio.run(crawl_all(refresh=arguments.refresh))
