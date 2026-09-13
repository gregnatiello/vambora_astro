"""
trend_finder.py
Responsável por descobrir "o que está chamando atenção das pessoas hoje".

Cadeia de fallback (item 31 do briefing):
    Google News RSS  -->  NewsAPI (se houver key)  -->  banco de temas interno

Cada assunto encontrado recebe um ENGAGEMENT_SCORE simples baseado em
palavras-gatilho (traição, briga, término, ciúme...) e atualidade.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from typing import Optional

import requests

from config import config

logger = logging.getLogger("tiktok_signos")


def _score_text(text: str) -> int:
    text_low = text.lower()
    score = 0
    for keyword, weight in config.ENGAGEMENT_KEYWORDS.items():
        if keyword in text_low:
            score += weight
    return score


def _freshness_bonus(published_at: Optional[str]) -> int:
    """Quanto mais recente, maior o bônus (até +10)."""
    if not published_at:
        return 3
    try:
        dt = datetime(*published_at[:6], tzinfo=timezone.utc)
    except Exception:  # noqa: BLE001
        return 3
    hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    if hours <= 6:
        return 10
    if hours <= 24:
        return 7
    if hours <= config.FRESHNESS_MAX_HOURS:
        return 4
    return 1


def _from_google_news() -> list[dict]:
    """Busca tendências via RSS público do Google Notícias — não exige
    API key, o que evita dependência de acesso pago ao X/Twitter."""
    try:
        import feedparser
    except ImportError:
        logger.info("Pacote 'feedparser' não instalado — pulando Google News RSS.")
        return []

    trends: list[dict] = []
    for query in config.GOOGLE_NEWS_RSS_QUERIES:
        url = config.GOOGLE_NEWS_RSS_URL.format(query=requests.utils.quote(query))
        try:
            feed = feedparser.parse(url)
        except Exception as exc:  # noqa: BLE001
            logger.info(f"Google News RSS falhou para '{query}': {exc}")
            continue

        for entry in feed.entries[:5]:
            title = getattr(entry, "title", "").strip()
            if not title:
                continue
            summary = getattr(entry, "summary", "") or title
            published = getattr(entry, "published_parsed", None)
            base_score = _score_text(title + " " + summary)
            score = base_score + _freshness_bonus(published)
            trends.append({
                "title": title,
                "source": getattr(entry, "source", {}).get("title", "Google News")
                if isinstance(getattr(entry, "source", None), dict) else "Google News",
                "url": getattr(entry, "link", ""),
                "summary": summary[:280],
                "published_at": (
                    datetime(*published[:6]).isoformat() if published else None
                ),
                "engagement_score": score,
                "query": query,
            })
    return trends


def _from_news_api() -> list[dict]:
    """Fallback secundário via NewsAPI, se uma chave estiver configurada."""
    if not config.NEWS_API_KEY:
        return []

    trends: list[dict] = []
    url = "https://newsapi.org/v2/everything"
    for query in config.GOOGLE_NEWS_RSS_QUERIES:
        try:
            resp = requests.get(
                url,
                params={
                    "q": query,
                    "language": "pt",
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "apiKey": config.NEWS_API_KEY,
                },
                timeout=config.REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
        except Exception as exc:  # noqa: BLE001
            logger.info(f"NewsAPI falhou para '{query}': {exc}")
            continue

        for art in articles:
            title = (art.get("title") or "").strip()
            if not title:
                continue
            summary = art.get("description") or title
            score = _score_text(title + " " + summary) + 5
            trends.append({
                "title": title,
                "source": (art.get("source") or {}).get("name", "NewsAPI"),
                "url": art.get("url", ""),
                "summary": summary[:280],
                "published_at": art.get("publishedAt"),
                "engagement_score": score,
                "query": query,
            })
    return trends


def _from_internal_bank() -> list[dict]:
    """Último fallback: banco de temas interno, sempre disponível offline.
    Garante que o sistema NUNCA trava por falta de internet/API."""
    seeds = [
        ("Fim de romance badalado repercute nas redes", "Término", 30),
        ("Treta pública entre dois influenciadores viraliza", "Discussões", 32),
        ("Famoso é acusado de esconder novo affair", "Traição", 34),
        ("Ex-casal troca indiretas depois de separação", "Ex", 28),
        ("Participante de reality expõe ciúme do parceiro", "Ciúmes", 29),
        ("Celebridade ostenta viagem de luxo e web reage", "Ostentação", 26),
        ("Casal reata relacionamento após término polêmico", "Término", 27),
        ("Influencer é criticado por gastos excessivos", "Dinheiro", 25),
    ]
    random.shuffle(seeds)
    trends = []
    for title, category, score in seeds:
        trends.append({
            "title": title,
            "source": "Banco interno",
            "url": "",
            "summary": title,
            "published_at": None,
            "engagement_score": score,
            "query": category,
            "fallback_category": category,
        })
    return trends


def find_trends() -> list[dict]:
    """Executa a cadeia de fallback e retorna a lista consolidada de
    tendências, já ordenada por engagement_score (maior primeiro)."""
    logger.info("Pesquisando tendências (Google News RSS)...")
    trends = []
    try:
        trends = _from_google_news()
    except Exception as exc:  # noqa: BLE001
        logger.info(f"Google News indisponível: {exc}")

    if not trends:
        logger.info("Google News sem resultados — tentando NewsAPI...")
        trends = _from_news_api()

    if not trends:
        logger.info("Nenhuma fonte online disponível — usando banco de temas interno.")
        trends = _from_internal_bank()

    trends.sort(key=lambda t: t["engagement_score"], reverse=True)
    logger.info(f"{len(trends)} assuntos encontrados.")
    return trends
