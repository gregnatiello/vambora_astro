"""
caption_generator.py
Cria a legenda (caption) e as hashtags do post, no mesmo tom debochado do
carrossel, estimulando comentário/marcação (item 20-21 do briefing).
"""

from __future__ import annotations

import random

CTA_LINES = [
    "Seu signo apareceu? 👀",
    "Marca aquela pessoa que precisa ver isso.",
    "Concorda ou essa lista está completamente errada?",
    "Manda pra quem é exatamente assim.",
    "Comenta seu signo aí embaixo.",
    "Marca o ex que se encaixa perfeitamente.",
    "Discorda? Defende seu signo nos comentários.",
    "Isso aqui vai dar briga nos comentários, eu já sei.",
]

OPENERS = [
    "Não adianta ficar bravo. 👀",
    "Calma, é só brincadeira... ou não. 😅",
    "Se ofendeu, provavelmente é você.",
    "Prepara o print pra mandar pro grupo.",
]

BASE_HASHTAGS = ["#signos", "#astrologia", "#horoscopo", "#zodiaco"]

CATEGORY_HASHTAGS = {
    "Traição": ["#relacionamento", "#traicao", "#fofoca"],
    "Término": ["#relacionamento", "#termino", "#ex"],
    "Ciúmes": ["#relacionamento", "#ciumes", "#comportamento"],
    "Discussões": ["#comportamento", "#discussao", "#viral"],
    "Ostentação": ["#dinheiro", "#luxo", "#comportamento"],
    "Dinheiro": ["#dinheiro", "#comportamento", "#viral"],
    "Ex": ["#relacionamento", "#ex", "#fofoca"],
    "Relacionamentos": ["#relacionamento", "#comportamento", "#viral"],
}

EXTRA_HASHTAGS = ["#tiktokbrasil", "#paravoce", "#fy", "#signosdozodiaco"]


def generate_caption(content: dict) -> tuple[str, list[str]]:
    opener = random.choice(OPENERS)
    ctas = random.sample(CTA_LINES, k=2)

    caption_lines = [
        opener,
        "",
        ctas[0],
        ctas[1],
    ]

    category = content.get("category", "Relacionamentos")
    hashtags = list(BASE_HASHTAGS)
    hashtags += CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS["Relacionamentos"])
    hashtags += random.sample(EXTRA_HASHTAGS, k=2)

    # remove duplicatas mantendo ordem, e limita a um conjunto pequeno (item 21)
    seen = set()
    unique_hashtags = []
    for tag in hashtags:
        if tag not in seen:
            seen.add(tag)
            unique_hashtags.append(tag)
    unique_hashtags = unique_hashtags[:8]

    caption_lines.append("")
    caption_lines.append(" ".join(unique_hashtags))

    caption_text = "\n".join(caption_lines)
    return caption_text, unique_hashtags
