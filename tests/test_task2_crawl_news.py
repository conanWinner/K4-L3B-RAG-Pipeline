from src.task2_crawl_news import ArticleHTMLParser


def test_parser_extracts_pubg_esports_title_and_body_only():
    html = """
    <div class="news-detail-header__title">PUBG Esports 2026 Roadmap</div>
    <div class="news-detail-body__editor fr-view normalize">
      <h2>A New Beginning</h2>
      <p>Detailed tournament information for players and fans.</p>
    </div>
    <nav class="news-detail-footer">Previous article should not appear.</nav>
    """
    parser = ArticleHTMLParser()
    parser.feed(html)

    assert parser.title() == "PUBG Esports 2026 Roadmap"
    assert "Detailed tournament information" in parser.markdown()
    assert "Previous article" not in parser.markdown()


def test_parser_keeps_existing_pubg_article_support():
    html = """
    <article class="content-template__content">
      <h1>Terms of Service</h1>
      <p>Existing PUBG article content remains supported.</p>
    </article>
    """
    parser = ArticleHTMLParser()
    parser.feed(html)

    assert parser.title() is None
    assert parser.markdown().startswith("Terms of Service")
