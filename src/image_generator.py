"""
image_generator.py
Responsável por desenhar as imagens finais do carrossel usando Pillow.

Princípio do briefing (itens 15-17): o LAYOUT é fixo. Só o conteúdo muda.
Este módulo NÃO inventa um layout novo a cada execução — ele sempre monta:

    template base (templates/capa.png ou templates/signo.png)
        +
    texto do dia
        =
    imagem final

Se os arquivos de template ainda não existirem, `ensure_templates()` cria
versões básicas (fundo preto padrão) na primeira execução, para que o
projeto funcione imediatamente. Quando você tiver os PNGs reais da
identidade visual do canal, é só substituir os arquivos em templates/ —
nenhum código precisa mudar.
"""

from __future__ import annotations

import logging
import textwrap
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont

from config import config

logger = logging.getLogger("tiktok_signos")

W, H = config.IMAGE_WIDTH, config.IMAGE_HEIGHT


# ---------------------------------------------------------------------------
# Templates base
# ---------------------------------------------------------------------------

def ensure_templates() -> None:
    """Garante que templates/capa.png e templates/signo.png existam.
    Cria placeholders simples (fundo preto + moldura sutil) se faltarem."""
    config.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    capa_path = config.TEMPLATES_DIR / "capa.png"
    signo_path = config.TEMPLATES_DIR / "signo.png"

    if not capa_path.exists():
        img = _blank_canvas()
        img.save(capa_path)
        logger.info(f"Template padrão criado: {capa_path}")

    if not signo_path.exists():
        img = _blank_canvas()
        img.save(signo_path)
        logger.info(f"Template padrão criado: {signo_path}")


def _blank_canvas() -> Image.Image:
    return Image.new("RGB", (W, H), config.COLOR_BACKGROUND)


def _load_template(name: str) -> Image.Image:
    path = config.TEMPLATES_DIR / name
    with Image.open(path) as template:
        template_size = template.size
    if template_size != (W, H):
        logger.info("Template %s usado como referência de tamanho: %sx%s", name, *template_size)
    return _blank_canvas()


# ---------------------------------------------------------------------------
# Fontes
# ---------------------------------------------------------------------------

def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        logger.info(f"Fonte não encontrada em {path}, usando fonte padrão do sistema.")
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Helpers de texto
# ---------------------------------------------------------------------------

def _wrap_text_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Quebra o texto em linhas que cabem em max_width, respeitando quebras
    de parágrafo já existentes (\n\n)."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def _draw_multiline_centered(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    center_x: int,
    top_y: int,
    fill,
    line_spacing: float = 1.35,
) -> int:
    """Desenha linhas centralizadas horizontalmente a partir de top_y.
    Retorna a coordenada Y final (depois da última linha)."""
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    y = top_y
    for line in lines:
        if line == "":
            y += line_height // 2
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = center_x - line_w // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def _draw_brand_footer(draw: ImageDraw.ImageDraw, mono_font: ImageFont.FreeTypeFont) -> None:
    text = config.BRAND_HANDLE
    bbox = draw.textbbox((0, 0), text, font=mono_font)
    text_w = bbox[2] - bbox[0]
    draw.text(((W - text_w) // 2, H - 90), text, font=mono_font, fill=config.COLOR_TEXT_SECONDARY)


def _body_font_for_text(draw: ImageDraw.ImageDraw, text: str, width: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Escolhe a maior fonte que mantém o texto principal entre 6 e 8 linhas."""
    for size in range(40, 30, -1):
        font = _font(config.FONT_BODY, size)
        for current_width in range(width, 579, -40):
            lines = _wrap_text_to_width(draw, text, font, current_width)
            if 6 <= len(lines) <= 8:
                return font, lines
    font = _font(config.FONT_BODY, 31)
    return font, _wrap_text_to_width(draw, text, font, width)


def _phrase_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> list[str]:
    """Quebra a frase em pelo menos duas linhas, preservando todas as palavras."""
    lines = _wrap_text_to_width(draw, text, font, 720)
    if len(lines) >= 2:
        return lines
    words = text.split()
    midpoint = max(1, len(words) // 2)
    return [" ".join(words[:midpoint]), " ".join(words[midpoint:])]


def _load_reference_logo() -> Image.Image:
    """Recorta o pequeno logo existente no template de signo."""
    with Image.open(config.TEMPLATES_DIR / "signo.png").convert("RGBA") as template:
        logo = template.crop((305, 490, 370, 540))
    pixels = logo.load()
    for y in range(logo.height):
        for x in range(logo.width):
            red, green, blue, _ = pixels[x, y]
            if red < 45 and green < 45 and blue < 45:
                pixels[x, y] = (red, green, blue, 0)
    return logo.resize((104, 80), Image.Resampling.LANCZOS)


def _emoji_codepoints(emoji: str) -> str:
    return "-".join(f"{ord(char):x}" for char in emoji if ord(char) != 0xfe0f)


def _load_color_emoji(emoji: str, size: int = 42) -> Image.Image | None:
    """Baixa e faz cache do PNG colorido aberto usado para um emoji."""
    try:
        config.EMOJI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        codepoints = _emoji_codepoints(emoji)
        cache_path = config.EMOJI_CACHE_DIR / f"{codepoints}.png"
        if not cache_path.exists():
            import requests

            url = f"https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/{quote(codepoints)}.png"
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            cache_path.write_bytes(response.content)
        with Image.open(cache_path) as image:
            return image.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    except Exception as exc:  # noqa: BLE001
        logger.info("Asset colorido indisponível para emoji %s: %s", emoji, exc)
        return None


def _draw_color_emojis(image: Image.Image, emojis: list[str], center_x: int, top_y: int) -> bool:
    assets = [_load_color_emoji(emoji) for emoji in emojis[:3]]
    if not all(assets):
        return False
    gap = 8
    total_width = sum(asset.width for asset in assets) + gap * (len(assets) - 1)
    x = center_x - total_width // 2
    for asset in assets:
        image.paste(asset, (x, top_y), asset)
        x += asset.width + gap
    return True


# ---------------------------------------------------------------------------
# Renderização das páginas
# ---------------------------------------------------------------------------

def render_cover(title: str, subtitle: str) -> Image.Image:
    cover_size = (1080, 1080)
    img = Image.new("RGB", cover_size, (0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_path = config.FONT_COVER
    title_lines = textwrap.wrap(title.upper(), width=30) or ["SIGNOS"]
    fonts = [
        _font(font_path, 52),
        *[_font(font_path, 57) for _ in title_lines],
        _font(font_path, 52),
        _font(font_path, 38),
    ]
    lines = [
        ("Os signos mais", (255, 255, 255)),
        *[(f'"{line}"', (255, 31, 45)) for line in title_lines],
        ("do zodíaco", (255, 255, 255)),
        (f"|TOP {config.SIGNS_PER_POST:02d}|", (255, 255, 255)),
    ]
    center_x = cover_size[0] // 2
    line_heights = [draw.textbbox((0, 0), text, font=font)[3] for (text, _), font in zip(lines, fonts)]
    line_gap = 8
    block_height = sum(line_heights) + line_gap * (len(lines) - 1)
    current_y = (cover_size[1] - block_height) // 2

    for (text, color), font, line_height in zip(lines, fonts, line_heights):
        draw.text(
            (center_x, current_y + line_height // 2),
            text,
            font=font,
            fill=color,
            anchor="mm",
        )
        current_y += line_height + line_gap
    return img


def render_sign_page(
    position: int,
    sign: str,
    text: str,
    phrase: str = "",
    emojis: list[str] | None = None,
) -> Image.Image:
    sign_size = (1080, 1080)
    img = Image.new("RGB", sign_size, (0, 0, 0))
    draw = ImageDraw.Draw(img)

    number_font = _font(config.FONT_COVER, 58)
    sign_font = _font(config.FONT_TITLE, 73)
    handle_font = _font(config.FONT_COVER, 24)
    phrase_font = _font(config.FONT_BODY, 29)

    content_width = 850
    center_x = sign_size[0] // 2

    # número da posição
    _draw_multiline_centered(draw, [f"{position:02d}"], number_font, center_x, 38, config.COLOR_TEXT_PRIMARY, line_spacing=1.0)

    # nome do signo
    y = _draw_multiline_centered(draw, [sign.upper()], sign_font, center_x, 112, config.COLOR_TEXT_PRIMARY, line_spacing=1.0)

    handle = config.BRAND_HANDLE
    handle_width = draw.textbbox((0, 0), handle, font=handle_font)[2]
    draw.text(((sign_size[0] - handle_width) // 2, 202), handle, font=handle_font, fill=config.COLOR_TEXT_SECONDARY)

    emoji_list = (emojis or [])[:3]
    if emoji_list and not _draw_color_emojis(img, emoji_list, center_x, 240):
        emoji_text = "".join(emoji_list)
        emoji_font = _font(config.FONT_EMOJI, 32)
        emoji_width = draw.textbbox((0, 0), emoji_text, font=emoji_font)[2]
        draw.text(((sign_size[0] - emoji_width) // 2, 245), emoji_text, font=emoji_font, fill=config.COLOR_TEXT_PRIMARY)

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    body_font, body_lines = _body_font_for_text(draw, text, content_width)
    body_end = _draw_multiline_centered(draw, body_lines, body_font, center_x, 365, config.COLOR_TEXT_PRIMARY, line_spacing=1.25)

    logo = _load_reference_logo()
    logo_x = (sign_size[0] - logo.width) // 2
    logo_y = body_end + 34
    img.paste(logo, (logo_x, logo_y), logo)

    phrase_text = phrase.strip() or (paragraphs[1] if len(paragraphs) > 1 else "")
    if phrase_text:
        if not (phrase_text.startswith(('"', "“")) and phrase_text.endswith(('"', "”"))):
            phrase_text = f'"{phrase_text.strip(chr(34) + "“”")}"'
        phrase_lines = _phrase_lines(draw, phrase_text, phrase_font)
        _draw_multiline_centered(draw, phrase_lines, phrase_font, center_x, logo_y + logo.height + 28, config.COLOR_TEXT_PRIMARY, line_spacing=1.25)
    return img


def save_image(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=95)
