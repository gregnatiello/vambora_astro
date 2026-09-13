"""
config.py
Configurações centrais do projeto. Nada de valores "mágicos" espalhados
pelo código — tudo relevante fica aqui.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# CAMINHOS
# ---------------------------------------------------------------------------
BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent
)

OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"
FONTS_DIR = BASE_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
EMOJI_CACHE_DIR = DATA_DIR / "emoji_cache"
HISTORY_FILE = DATA_DIR / "history.json"

# ---------------------------------------------------------------------------
# IMAGEM / LAYOUT
# ---------------------------------------------------------------------------
IMAGE_WIDTH = 672
IMAGE_HEIGHT = 672

SIGNS_PER_POST = 5
TOTAL_IMAGES = SIGNS_PER_POST + 1  # 5 signos + 1 capa

# Paleta fixa da identidade visual (baseada no template de referência:
# fundo preto, texto branco, destaque vermelho)
COLOR_BACKGROUND = (10, 10, 10)
COLOR_TEXT_PRIMARY = (245, 245, 245)
COLOR_TEXT_SECONDARY = (190, 190, 190)
COLOR_ACCENT = (214, 40, 40)

# Marca / identidade do canal (ajuste para o seu @ real)
BRAND_HANDLE = os.getenv("BRAND_HANDLE", "@vambora.astro")
BRAND_NAME = os.getenv("BRAND_NAME", "VAMBORA")

# Fontes (fallback para as fontes disponíveis no sistema; troque os arquivos
# em fonts/ pelas fontes reais da identidade visual quando tiver os arquivos)
FONT_COVER = str(FONTS_DIR / "computer-says-no.otf")
FONT_TITLE = str(FONTS_DIR / "Kapsalon Brush DEMO.otf")
FONT_BODY = str(FONTS_DIR / "Cardo-Regular.ttf")
FONT_MONO = str(FONTS_DIR / "label.ttf")
FONT_EMOJI = r"C:\Windows\Fonts\seguiemj.ttf"

# ---------------------------------------------------------------------------
# CONTEÚDO / TEXTO
# ---------------------------------------------------------------------------
LANGUAGE = "pt-BR"
MIN_TEXT_LENGTH = 310
MAX_TEXT_LENGTH = 320
MIN_PHRASE_LENGTH = 110
MAX_PHRASE_LENGTH = 120
TARGET_TEXT_MIN = 315
TARGET_TEXT_MAX = 318
TARGET_PHRASE_MIN = 114
TARGET_PHRASE_MAX = 118

MAX_TITLE_LENGTH = 60
MAX_SUBTITLE_LENGTH = 90

SIGNS = [
    "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
    "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes",
]

# Banco de categorias de temas (usado para classificar tendências e para
# fallback quando a pesquisa online falha)
THEME_CATEGORIES = [
    "Relacionamentos", "Traição", "Ciúmes", "Término", "Ex", "Casamento",
    "Flertes", "Amizade", "Dinheiro", "Trabalho", "Ego", "Vaidade",
    "Mentiras", "Drama", "Discussões", "Orgulho", "Vingança", "Festas",
    "Ostentação", "Preguiça", "Ansiedade", "Controle", "Manipulação",
    "Romance", "Fidelidade", "Desapego", "Carência",
]

# Palavras-gatilho usadas para pontuar tendências por potencial de
# engajamento em um perfil de signos (ENGAJAMENTO_SCORE)
ENGAGEMENT_KEYWORDS = {
    "traição": 10, "traiu": 10, "trair": 9, "chifre": 8,
    "término": 8, "terminou": 8, "separação": 7, "separou": 7,
    "polêmica": 9, "briga": 8, "brigou": 8, "climão": 7,
    "ciúme": 7, "ciúmes": 7, "affair": 7,
    "ostentação": 6, "luxo": 5, "milionário": 5, "riqueza": 4,
    "reality": 6, "bbb": 7, "fazenda": 5, "traição amorosa": 10,
    "ex": 5, "namoro": 5, "casamento": 5, "casou": 4, "noivado": 4,
    "fofoca": 6, "expôs": 7, "indireta": 6, "treta": 8,
    "cancelamento": 6, "cancelada": 6, "cancelado": 6,
    "crise": 4, "escândalo": 8, "confissão": 5, "revelou": 5,
}

# Peso mínimo de atualidade — assuntos mais recentes pontuam mais
FRESHNESS_MAX_HOURS = 48

# ---------------------------------------------------------------------------
# IA
# ---------------------------------------------------------------------------
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
AI_TEMPERATURE = 0.9
AI_MAX_RETRIES = 2
EXTRA_AI_INSTRUCTION = os.getenv("EXTRA_AI_INSTRUCTION", "").strip()

# ---------------------------------------------------------------------------
# FONTES DE TENDÊNCIA
# ---------------------------------------------------------------------------
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

GOOGLE_NEWS_RSS_QUERIES = [
    "famosos briga",          # conflitos públicos e repercussão
    "celebridade traição",    # relacionamentos e rumores noticiados
    "influencer polêmica",    # polêmicas de influenciadores
    "término namoro famoso",  # separações e términos
    "BBB treta",              # realities e discussões
]

GOOGLE_NEWS_RSS_URL = (
    "https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
)

# O X/Twitter não oferece mais busca de tendências gratuita (API de search
# paga desde 2023). O Google Trends (via pytrends) é o substituto gratuito
# mais próximo de "o que está sendo comentado/pesquisado agora" no Brasil.
SOCIAL_BUZZ_MAX_RESULTS = 10
SOCIAL_BUZZ_SCORE_BONUS = 8  # bônus por já estar bombando "ao vivo"

REQUEST_TIMEOUT_SECONDS = 8

# ---------------------------------------------------------------------------
# LOG
# ---------------------------------------------------------------------------
LOG_FILE = LOGS_DIR / "run.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")