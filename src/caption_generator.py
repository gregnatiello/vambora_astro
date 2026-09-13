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
    "Quero ver quem vai admitir que é exatamente assim.",
    "Comenta o signo que mais merecia estar nessa lista.",
    "Marca alguém que vai ficar ofendido com esse ranking.",
    "Qual posição você mudaria?",
    "Não vale escolher o signo dos outros. E o seu?",
    "A verdade apareceu. Agora quero ver a defesa nos comentários.",
]

OPENERS = [
    "Não adianta ficar bravo. 👀",
    "Calma, é só brincadeira... ou não. 😅",
    "Se ofendeu, provavelmente é você.",
    "Prepara o print pra mandar pro grupo.",
    "A lista saiu e já tem signo preparando a defesa.",
    "Isso aqui vai causar uma pequena crise no grupo.",
    "Alguns signos vão passar reto. Outros vão comentar em caps lock.",
    "O zodíaco pediu exposição. Então está aqui.",
    "Ninguém está pronto para se reconhecer nessa lista.",
    "Pode respirar antes de procurar o seu signo.",
]

THEME_HOOKS = {
    "Traição": [
        "Quando o assunto é traição, a desculpa já vem pronta.",
        "Tem signo que chama de acaso aquilo que todo mundo chama de traição.",
        "Aqui, o problema nunca é a oportunidade. É a falta de vergonha mesmo.",
        "Se aparecer um 'foi só conversa', desconfie do signo imediatamente.",
    ],
    "Término": [
        "Terminar é fácil. Difícil é não voltar para o mesmo problema.",
        "Tem signo que termina hoje e sente saudade antes de dormir.",
        "O fim do namoro chegou, mas o drama ainda está só começando.",
        "Alguns superam. Outros só esperam o ex mandar mensagem.",
    ],
    "Ciúmes": [
        "Tem signo que chama de intuição o que já é investigação criminal.",
        "Um like suspeito e pronto: começou a auditoria do relacionamento.",
        "Aqui, cinco minutos sem resposta já viram uma teoria completa.",
        "O problema não é sentir ciúme. É montar um dossiê com provas.",
    ],
    "Discussões": [
        "Tem signo que não quer resolver a briga. Quer ganhar o debate.",
        "Uma conversa normal dura pouco quando esses signos entram no assunto.",
        "Aqui, qualquer detalhe vira argumento, discurso e replay da briga.",
        "A discussão podia acabar rápido, mas alguém decidiu fazer um podcast.",
    ],
    "Relacionamentos": [
        "No amor, esses signos conseguem transformar detalhe em temporada inteira.",
        "O problema começa pequeno e termina com textão no celular.",
        "Tem signo que ama a pessoa e o drama na mesma intensidade.",
        "Relacionamento tranquilo? Para esses signos, só se for em outro mapa astral.",
    ],
}

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
    category = content.get("category", "Relacionamentos")
    hooks = THEME_HOOKS.get(category, THEME_HOOKS["Relacionamentos"])
    theme_hook = random.choice(hooks)
    ctas = random.sample(CTA_LINES, k=2)

    caption_lines = [
        opener,
        "",
        theme_hook,
        "",
        ctas[0],
        ctas[1],
    ]

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
