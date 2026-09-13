"""
content_generator.py
Transforma o assunto selecionado em: tema, título, subtítulo, ranking de
5 signos e o texto de cada um. Segue as regras de tom do briefing (itens
6 a 13): informal, debochado, sem clichê de horóscopo, PT-BR natural.

Usa src/ai_client.py para gerar via IA. O banco local continua disponível
exclusivamente para o modo de teste (--test).
"""

from __future__ import annotations

import copy
import logging
import random

from config import config
from src.ai_client import AIClient
from src.fallback_bank import get_fallback_set
from src.utils import was_recently_used

logger = logging.getLogger("tiktok_signos")

_SYSTEM_PROMPT = """\
Você escreve para um canal de TikTok brasileiro sobre signos, astrologia,
relacionamentos e comportamento, com humor debochado.

REGRAS OBRIGATÓRIAS:
- Português do Brasil natural. Nunca português de Portugal (nada de "tu estás").
- Tom informal, direto, provocativo, engraçado, levemente ácido. Nunca acadêmico
  ou explicativo demais. Nunca ofensivo, preconceituoso ou grosseiro.
- PROIBIDO escrever como horóscopo tradicional (ex: "Arianos possuem uma
  personalidade intensa"). Isso é genérico e sem graça.
- PREFIRA cenas e comportamentos concretos, tipo: "Áries não quer discutir.
  Quer ganhar. Se perceber que está perdendo, muda de assunto."
- Use exagero proposital e humor de identificação (o leitor deve pensar
  "isso é muito o meu ex" ou "sou desse signo e me senti atacado").
- Cada texto de signo deve ter de 2 a 5 frases curtas, fácil de ler rápido
  passando o carrossel, sempre com uma ideia principal clara.
- O campo "text" deve ter entre 315 e 318 caracteres (alvo médio), sempre
  terminando em pontuação completa.
- O campo "phrase" deve ter entre 114 e 118 caracteres (alvo médio), sempre
  terminando em pontuação completa. Deve ser uma frase curta entre aspas,
  escrita como se fosse uma pessoa daquele signo falando sobre o tema.
- Nunca complete texto com frases repetidas, reticências ou cortes no meio de uma
  palavra/frase. Conte os caracteres antes de responder.
- O campo "cover_title" será colocado entre as linhas fixas "Os signos mais"
  e "do zodíaco". Gere somente o complemento direto do assunto, sem repetir
  "Os signos", "signos" ou "do zodíaco", com até 30 caracteres quando possível.
- Se o gatilho for uma notícia sobre pessoa real, NUNCA afirme fatos não
  confirmados nem transforme rumor em acusação. Use apenas como inspiração
  vaga de tema (ex.: "depois de mais uma polêmica de relacionamento que
  tomou conta da internet...").
- Responda SOMENTE com um JSON válido, no formato exato pedido no prompt do
  usuário. Nada de texto fora do JSON, nada de markdown.
"""

_USER_PROMPT_TEMPLATE = """\
Assunto em alta (gatilho, NÃO deve ser citado como fato sobre pessoas reais):
"{trend_title}"

Categoria temática: {category}

Transforme esse gatilho em um carrossel de TOP 5 SIGNOS sobre o tema
"{category}". Escolha os 5 signos que fazem mais sentido pra esse tema
específico (não repita sempre a mesma sequência) e ordene do #1 ao #5.

Responda apenas com este JSON:
{{
  "carousel_title": "título forte, até {max_title} caracteres, tudo relacionado a signos",
  "cover_title": "complemento para 'Os signos mais ___ do zodíaco', direto e ligado à notícia",
  "subtitle": "subtítulo curto e provocativo, até {max_subtitle} caracteres",
  "signs": [
    {{"sign": "Nome do signo", "text": "texto entre {text_target_min} e {text_target_max} caracteres", "phrase": "\"frase curta, entre aspas, como uma fala desse signo sobre o tema\""}},
    ... (exatamente 5 itens, do #1 ao #5)
  ]
}}

Instrução adicional de tom/abordagem:
{extra_instruction}
"""


def _build_user_prompt(topic: dict, extra_instruction: str = "") -> str:
    return _USER_PROMPT_TEMPLATE.format(
        trend_title=topic.get("title", ""),
        category=topic.get("category", "Relacionamentos"),
        max_title=config.MAX_TITLE_LENGTH,
        max_subtitle=config.MAX_SUBTITLE_LENGTH,
        min_text=config.MIN_TEXT_LENGTH,
        max_text=config.MAX_TEXT_LENGTH,
        min_phrase=config.MIN_PHRASE_LENGTH,
        max_phrase=config.MAX_PHRASE_LENGTH,
        text_target_min=config.TARGET_TEXT_MIN,
        text_target_max=config.TARGET_TEXT_MAX,
        phrase_target_min=config.TARGET_PHRASE_MIN,
        phrase_target_max=config.TARGET_PHRASE_MAX,
        extra_instruction=extra_instruction.strip() or "Nenhuma instrução adicional.",
    )


def _generate_via_ai(topic: dict, ai_client: AIClient, extra_instruction: str = "") -> dict | None:
    prompt = _build_user_prompt(topic, extra_instruction)
    data = ai_client.generate_json(_SYSTEM_PROMPT, prompt)
    if not data:
        return None
    validation_error = _validate_ai_payload(data)
    if validation_error:
        logger.info("Resposta Gemini inválida: %s", validation_error)
        return None
    data["ai_instruction"] = extra_instruction.strip()
    return data


def _validate_ai_payload(data: dict) -> str | None:
    signs = data.get("signs")
    if not isinstance(signs, list) or len(signs) != config.SIGNS_PER_POST:
        return f"é obrigatório retornar exatamente {config.SIGNS_PER_POST} signos"
    if not data.get("carousel_title") or not data.get("subtitle"):
        return "carousel_title e subtitle são obrigatórios"
    cover_title = data.get("cover_title", "")
    if not isinstance(cover_title, str) or not cover_title.strip():
      return "cover_title deve ser um texto não vazio"

    for item in signs:
        if not isinstance(item, dict):
            return "cada item de signs deve ser um objeto"
        text = item.get("text", "")
        phrase = item.get("phrase", "")
        if not isinstance(text, str) or not text.strip():
          return f"o texto de {item.get('sign', 'um signo')} deve ser um texto não vazio"
        if not isinstance(phrase, str) or not phrase.strip():
          return f"a frase de {item.get('sign', 'um signo')} deve ser um texto não vazio"
    return None


def _generate_via_fallback(topic: dict) -> dict:
    category = topic.get("category", "Relacionamentos")
    base = copy.deepcopy(get_fallback_set(category))

    # tenta não repetir o mesmo título usado recentemente; se repetir,
    # ao menos embaralha a ordem dos signos pra dar uma cara diferente
    if was_recently_used(base["carousel_title"], field="carousel_title"):
        random.shuffle(base["signs"])
    return base


def generate_content(topic: dict, force_offline: bool = False, extra_instruction: str = "") -> dict:
    """Ponto de entrada principal. Retorna um dict com:
    carousel_title, subtitle, signs (lista de 5 {sign, text})."""
    ai_client = AIClient()

    content = None
    if not force_offline:
        logger.info("Gerando conteúdo via IA...")
        content = _generate_via_ai(topic, ai_client, extra_instruction)

    if content is None:
        if not force_offline:
          raise RuntimeError(
            "A IA não gerou um conteúdo válido. Verifique a chave, cota, modelo e "
            "limites do provider configurado; o fallback local foi bloqueado para "
            "não publicar um tema chumbado no lugar da tendência pesquisada."
          )
        logger.info("Usando banco de conteúdo local (fallback).")
        content = _generate_via_fallback(topic)

    content["signs"] = content["signs"][: config.SIGNS_PER_POST]
    for i, item in enumerate(content["signs"], start=1):
        item["position"] = i

    content["source_topic"] = topic.get("title", "")
    content["source_summary"] = topic.get("summary", topic.get("title", ""))
    content["category"] = topic.get("category", "Relacionamentos")
    content.setdefault("cover_title", content["carousel_title"])
    content.setdefault("ai_instruction", extra_instruction.strip())
    return content
