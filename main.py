#!/usr/bin/env python3
"""
main.py
Orquestra o fluxo completo do gerador de carrosséis de signos.

Uso:
    python main.py                          -> fluxo normal (pesquisa tendências)
    python main.py --test                   -> modo de teste, sem internet/IA
    python main.py --topic "Assunto aqui"    -> pula a pesquisa, usa o tema informado

O main.py fica deliberadamente enxuto — cada etapa mora em um módulo próprio
dentro de src/, seguindo a arquitetura pedida no briefing (item 23).
"""

from __future__ import annotations

import argparse
import sys
import traceback

from config import config
from src.utils import setup_logger, ensure_dirs, append_history
from src import trend_finder
from src import topic_selector
from src import content_generator
from src import text_validator
from src import carousel_builder
from src import caption_generator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerador automático de carrosséis de signos para TikTok.")
    parser.add_argument("--test", action="store_true", help="Roda em modo de teste, sem internet e sem IA (usa tema fictício).")
    parser.add_argument("--topic", type=str, default=None, help="Ignora a pesquisa de tendências e usa o tema informado.")
    parser.add_argument(
        "--instruction",
        type=str,
        default=config.EXTRA_AI_INSTRUCTION,
        help="Instrução adicional para ajustar o tom da IA (ex.: mais incisivo).",
    )
    return parser.parse_args()


def _fake_test_topic() -> dict:
    return {
        "title": "Teste local: treta fictícia entre dois famosos inventados",
        "source": "Modo de teste",
        "url": "",
        "summary": "Assunto fictício usado apenas para validar o pipeline e o layout.",
        "published_at": None,
        "engagement_score": 99,
        "category": "Discussões",
    }


def _topic_from_cli_arg(topic_text: str) -> dict:
    return {
        "title": topic_text,
        "source": "CLI (--topic)",
        "url": "",
        "summary": topic_text,
        "published_at": None,
        "engagement_score": 100,
        "category": topic_selector._categorize({"title": topic_text, "summary": topic_text}),
    }


def generate_post(
    mode: str = "trend",
    topic_text: str = "",
    selected_topic: dict | None = None,
    instruction: str = "",
    test: bool = False,
) -> str:
    """Executa o pipeline e retorna a pasta do post criado."""
    ensure_dirs()
    logger = setup_logger()

    logger.info("Iniciando geração")

    # 1) Descobrir/definir o tema ---------------------------------------------
    if mode == "custom":
        if not topic_text.strip():
            raise ValueError("Digite um tema antes de gerar o post.")
        logger.info(f"Tema informado: {topic_text}")
        topic = _topic_from_cli_arg(topic_text.strip())
    elif test:
        logger.info("Modo de teste ativado — pulando pesquisa de tendências.")
        topic = _fake_test_topic()
    elif selected_topic:
        topic = dict(selected_topic)
        topic["category"] = topic_selector._categorize(topic)
        logger.info(f"Tendência escolhida: {topic['title']}")
    else:
        logger.info("Pesquisando tendências")
        trends = trend_finder.find_trends()
        logger.info(f"{len(trends)} assuntos encontrados")
        topic = topic_selector.select_topic(trends)

    # 2) Gerar conteúdo --------------------------------------------------------
    logger.info("Gerando conteúdo")
    content = content_generator.generate_content(
        topic,
        force_offline=test,
        extra_instruction=instruction.strip(),
    )

    # 3) Validar ---------------------------------------------------------------
    content = text_validator.validate_content(content)
    logger.info("Conteúdo validado")

    # 4) Gerar imagens ---------------------------------------------------------
    logger.info("Gerando imagens")
    build_result = carousel_builder.build_carousel(content)
    post_dir = build_result["post_dir"]

    # 5) Legenda e hashtags ----------------------------------------------------
    caption_text, hashtags = caption_generator.generate_caption(content)
    content["caption"] = caption_text
    content["hashtags"] = hashtags
    content["date"] = post_dir.name.split("_", 1)[0]

    # 6) Salvar post.json e legenda.txt ----------------------------------------
    from src.utils import write_json, write_text
    write_json(post_dir / "post.json", content)
    write_text(post_dir / "legenda.txt", caption_text)

    # 7) Atualizar histórico ----------------------------------------------------
    append_history({
        "date": content["date"],
        "source_topic": topic.get("title", ""),
        "carousel_title": content["carousel_title"],
        "category": content.get("category"),
        "signs": [s["sign"] for s in content["signs"]],
    })

    logger.info(f"Output: {post_dir}")
    logger.info("Pronto! Abra a pasta acima, revise e publique manualmente no TikTok.")
    return str(post_dir)


def main() -> int:
    args = parse_args()
    try:
        generate_post(
            mode="custom" if args.topic else "trend",
            topic_text=args.topic or "",
            instruction=args.instruction,
            test=args.test,
        )
        return 0

    except Exception as exc:  # noqa: BLE001
        logger = setup_logger()
        logger.error(f"Falha na geração do post: {exc}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
