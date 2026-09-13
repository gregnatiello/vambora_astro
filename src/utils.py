"""
utils.py
Funções utilitárias compartilhadas: logging, manipulação de arquivos,
slugify, histórico de posts anteriores.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

from config import config


def setup_logger(name: str = "tiktok_signos") -> logging.Logger:
    """Configura um logger que escreve simultaneamente no console e em
    logs/run.log, no formato pedido no prompt: [HH:MM:SS] mensagem."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # já configurado (evita handlers duplicados)

    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


def slugify(text: str, max_words: int = 6) -> str:
    """Transforma um título em um slug de pasta seguro, ex.:
    'TOP 5 SIGNOS QUE MAIS TRAEM' -> 'top_5_signos_que_mais_traem'."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    words = text.split()[:max_words]
    slug = "_".join(words)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "post"


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_hms() -> str:
    return datetime.now().strftime("%H:%M:%S")


def ensure_dirs() -> None:
    for d in (config.OUTPUT_DIR, config.LOGS_DIR, config.DATA_DIR,
              config.TEMPLATES_DIR, config.FONTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# HISTÓRICO (evitar repetição — item 28 do briefing)
# ---------------------------------------------------------------------------

def load_history() -> list[dict]:
    return read_json(config.HISTORY_FILE, default=[]) or []


def append_history(entry: dict) -> None:
    history = load_history()
    history.append(entry)
    # mantém só os últimos 60 posts para o arquivo não crescer sem limite
    history = history[-60:]
    write_json(config.HISTORY_FILE, history)


def was_recently_used(value: str, field: str, limit: int = 30) -> bool:
    """Checa se um valor (título, tema, combinação de signos...) já apareceu
    nos últimos `limit` posts do histórico."""
    history = load_history()[-limit:]
    value_norm = value.strip().lower()
    return any(str(item.get(field, "")).strip().lower() == value_norm for item in history)
