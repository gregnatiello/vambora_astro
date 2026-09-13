"""
topic_selector.py
Escolhe o assunto com maior potencial de engajamento entre os candidatos
encontrados pelo trend_finder, associa a uma categoria do banco de temas e
evita repetir categorias/títulos usados recentemente (item 28 do briefing).
"""

from __future__ import annotations

import logging

from config import config
from src.utils import was_recently_used

logger = logging.getLogger("tiktok_signos")

_CATEGORY_KEYWORDS = {
    "Traição": ["traição", "traiu", "trair", "affair", "chifre", "infiel"],
    "Término": ["término", "terminou", "separação", "separou", "reconciliou", "reataram", "reata"],
    "Ciúmes": ["ciúme", "ciúmes", "possessivo"],
    "Ex": ["ex-namorado", "ex-namorada", "ex-casal", " ex "],
    "Casamento": ["casamento", "casou", "noivado", "noivou"],
    "Discussões": ["treta", "briga", "brigou", "discussão", "climão", "atrito"],
    "Dinheiro": ["gastos", "dívida", "fortuna", "salário", "cachê"],
    "Ostentação": ["ostenta", "luxo", "milionário", "riqueza", "mansão", "viagem de luxo"],
    "Vaidade": ["procedimento estético", "vaidade", "aparência"],
    "Drama": ["choro", "desabafo", "crise", "escândalo"],
    "Fofoca": ["fofoca", "expôs", "indireta"],
}


def _categorize(topic: dict) -> str:
    if topic.get("fallback_category"):
        return topic["fallback_category"]

    text = f"{topic.get('title', '')} {topic.get('summary', '')}".lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    # sem correspondência clara -> categoria genérica de comportamento
    return "Relacionamentos"


def select_topic(trends: list[dict]) -> dict:
    """Recebe a lista ordenada de tendências e devolve a escolhida, já com
    a categoria anexada, pulando títulos repetidos recentemente."""
    if not trends:
        raise ValueError("Nenhuma tendência disponível para seleção.")

    for candidate in trends:
        if was_recently_used(candidate["title"], field="source_topic"):
            logger.info(f"Ignorando tema repetido: {candidate['title']}")
            continue
        candidate["category"] = _categorize(candidate)
        logger.info(
            f"Tema selecionado: {candidate['category']} "
            f"(score={candidate['engagement_score']}) — {candidate['title']}"
        )
        return candidate

    # todos repetidos: usa o de maior score mesmo assim, para nunca travar
    chosen = trends[0]
    chosen["category"] = _categorize(chosen)
    logger.info(f"Todos os temas eram recentes — reutilizando o de maior score: {chosen['title']}")
    return chosen
