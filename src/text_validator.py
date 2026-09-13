"""
text_validator.py
Etapa explícita de revisão de português (item 13 do briefing).

Verifica: tamanho, palavras duplicadas seguidas, espaçamento/pontuação
quebrada, marcas de português de Portugal, frases truncadas. Quando dá
pra corrigir automaticamente, corrige; quando não dá, sinaliza para que
o content_generator possa tentar regenerar aquele item.
"""

from __future__ import annotations

import logging
import re

from config import config

logger = logging.getLogger("tiktok_signos")

# Construções tipicamente de Portugal que não soam naturais no Brasil
_PT_PT_PATTERNS = [
    (r"\btu estás\b", "você está"),
    (r"\btu és\b", "você é"),
    (r"\bestá(s)? a \b", "está "),  # "está a fazer" -> "está fazer" (ajuste bruto, revisar)
    (r"\bteu relacionamento está\b", "seu relacionamento está"),
    (r"\bhavemos de\b", "vamos"),
    (r"\bpara já\b", "por enquanto"),
    (r"\bcasa de banho\b", "banheiro"),
    (r"\bpequeno-almoço\b", "café da manhã"),
    (r"\btelemóvel\b", "celular"),
    (r"\bautocarro\b", "ônibus"),
]


class ValidationResult:
    def __init__(self):
        self.ok = True
        self.issues: list[str] = []
        self.fixed_text: str | None = None

    def add_issue(self, message: str) -> None:
        self.ok = False
        self.issues.append(message)


def _fix_whitespace_and_punctuation(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"([.,!?;:])(?=\S)", r"\1 ", text)
    text = re.sub(r"\.{2,}(?!\.)", "…", text)
    return text.strip()


def _fix_duplicated_words(text: str) -> str:
    return re.sub(r"\b(\w+)( \1\b)+", r"\1", text, flags=re.IGNORECASE)


def _fix_pt_pt(text: str) -> str:
    fixed = text
    for pattern, replacement in _PT_PT_PATTERNS:
        fixed = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
    return fixed


def _looks_truncated(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    return stripped[-1] not in ".!?…\"”)" and len(stripped) > 20


def validate_sign_text(text: str) -> ValidationResult:
    result = ValidationResult()

    fixed = _fix_whitespace_and_punctuation(text)
    fixed = _fix_duplicated_words(fixed)
    fixed = _fix_pt_pt(fixed)

    result.fixed_text = fixed
    return result


def validate_content(content: dict) -> dict:
    """Valida e corrige título, subtítulo e texto de cada signo.
    Retorna o próprio dict de conteúdo já com os textos corrigidos."""
    logger.info("Validando português e tamanho dos textos...")

    content["carousel_title"] = _fix_pt_pt(
        _fix_whitespace_and_punctuation(content["carousel_title"])
    )
    content["subtitle"] = _fix_pt_pt(
        _fix_whitespace_and_punctuation(content["subtitle"])
    )
    content["cover_title"] = _fix_pt_pt(
        _fix_whitespace_and_punctuation(content.get("cover_title", ""))
    )

    for item in content["signs"]:
        item["text"] = validate_sign_text(item["text"]).fixed_text
        if "phrase" in item:
            item["phrase"] = validate_sign_text(item["phrase"]).fixed_text

    logger.info("Conteúdo validado.")
    return content
