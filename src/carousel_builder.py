"""
carousel_builder.py
Monta o carrossel completo (capa + 5 páginas de signos), salva as imagens
na pasta do dia e monta o dicionário final que vira post.json.
"""

from __future__ import annotations

import logging
from pathlib import Path

from config import config
from src import image_generator
from src.utils import slugify, today_str

logger = logging.getLogger("tiktok_signos")

_SIGN_FILE_SLUGS = {
    "áries": "aries", "touro": "touro", "gêmeos": "gemeos", "câncer": "cancer",
    "leão": "leao", "virgem": "virgem", "libra": "libra", "escorpião": "escorpiao",
    "sagitário": "sagitario", "capricórnio": "capricornio", "aquário": "aquario",
    "peixes": "peixes",
}


def _sign_slug(sign_name: str) -> str:
    key = sign_name.strip().lower()
    return _SIGN_FILE_SLUGS.get(key, slugify(sign_name, max_words=1))


def build_post_folder(content: dict) -> Path:
    date_str = today_str()
    slug = slugify(content["carousel_title"])
    folder_name = f"{date_str}_{slug}"
    post_dir = config.OUTPUT_DIR / folder_name

    # evita colisão se rodar mais de uma vez no mesmo dia com o mesmo título
    suffix = 2
    original_dir = post_dir
    while post_dir.exists():
        post_dir = Path(f"{original_dir}_{suffix}")
        suffix += 1

    post_dir.mkdir(parents=True, exist_ok=True)
    return post_dir


def build_carousel(content: dict) -> dict:
    """Gera as 6 imagens, salva na pasta do post e retorna metadados
    (caminho da pasta e lista de arquivos de imagem gerados)."""
    image_generator.ensure_templates()

    post_dir = build_post_folder(content)
    logger.info(f"Pasta do post: {post_dir}")

    image_files = []

    logger.info("Gerando imagem 1/6 (capa)...")
    cover = image_generator.render_cover(
        content.get("cover_title", content["carousel_title"]),
        content["subtitle"],
    )
    cover_path = post_dir / "01_capa.png"
    image_generator.save_image(cover, cover_path)
    image_files.append(cover_path.name)

    for idx, sign_item in enumerate(content["signs"], start=2):
        position = sign_item["position"]
        sign_name = sign_item["sign"]
        logger.info(f"Gerando imagem {idx}/6 (#{position} {sign_name})...")
        page = image_generator.render_sign_page(
            position,
            sign_name,
            sign_item["text"],
            sign_item.get("phrase", ""),
            sign_item.get("emojis", []),
        )
        filename = f"{idx:02d}_{_sign_slug(sign_name)}.png"
        page_path = post_dir / filename
        image_generator.save_image(page, page_path)
        image_files.append(page_path.name)

    logger.info("Carrossel finalizado.")
    return {"post_dir": post_dir, "image_files": image_files}
