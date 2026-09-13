"""
ai_client.py

Camada única de acesso a modelos de IA.

Providers suportados:
- gemini
- openai

O provider é definido por AI_PROVIDER.

Para Gemini:
    GEMINI_API_KEY=...
    GEMINI_MODEL=gemini-3.5-flash-lite

Para OpenAI:
    OPENAI_API_KEY=...
    OPENAI_MODEL=...

Nenhum outro módulo deve chamar uma API de IA diretamente.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

import requests

from config import config

logger = logging.getLogger("tiktok_signos")


class AIClientError(Exception):
    pass


class AIClient:

    def __init__(self):
        self.provider = getattr(config, "AI_PROVIDER", "gemini").lower()

        # Gemini
        self.gemini_api_key = getattr(config, "GEMINI_API_KEY", "")
        self.gemini_model = getattr(config, "GEMINI_MODEL", "gemini-3.5-flash-lite")

        # OpenAI
        self.openai_api_key = getattr(config, "OPENAI_API_KEY", "")
        self.openai_model = getattr(
            config,
            "OPENAI_MODEL",
            "gpt-4o-mini",
        )

        # Mantém compatibilidade com o restante do projeto
        if self.provider == "gemini":
            self.api_key = self.gemini_api_key
            self.model = self.gemini_model
        else:
            self.api_key = self.openai_api_key
            self.model = self.openai_model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = None,
        json_mode: bool = False,
    ) -> Optional[str]:
        """
        Gera texto a partir de um prompt.

        Retorna None se a IA não estiver configurada
        ou se todas as tentativas falharem.
        """

        if not self.is_configured:
            logger.info(
                "IA não configurada para provider '%s' — verifique a variável de API no .env.",
                self.provider,
            )
            return None

        temperature = (
            config.AI_TEMPERATURE
            if temperature is None
            else temperature
        )

        for attempt in range(1, config.AI_MAX_RETRIES + 1):
            try:

                if self.provider == "gemini":
                    return self._call_gemini(
                        system_prompt,
                        user_prompt,
                        temperature,
                        json_mode,
                    )

                elif self.provider == "openai":
                    return self._call_openai(
                        system_prompt,
                        user_prompt,
                        temperature,
                        json_mode,
                    )

                else:
                    raise AIClientError(
                        f"Provider de IA desconhecido: {self.provider}"
                    )

            except Exception as exc:
                logger.info(
                    "Falha na chamada de IA "
                    "(tentativa %s): %s",
                    attempt,
                    exc,
                )

        return None

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = None,
    ) -> Optional[dict]:

        raw = self.generate_text(
            system_prompt,
            user_prompt,
            temperature=temperature,
            json_mode=True,
        )

        if raw is None:
            return None

        raw = raw.strip()

        # Remove cercas de markdown caso algum modelo retorne:
        # ```json
        # {...}
        # ```
        if raw.startswith("```"):
            lines = raw.splitlines()

            if lines and lines[0].strip().lower() in (
                "```json",
                "```",
            ):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            raw = "\n".join(lines).strip()

        try:
            data = json.loads(raw)

            if isinstance(data, dict):
                return data

            logger.info(
                "Resposta da IA não era um objeto JSON."
            )
            return None

        except json.JSONDecodeError:
            logger.info(
                "Resposta da IA não era um JSON válido."
            )
            return None

    # ------------------------------------------------------------------
    # Gemini
    # ------------------------------------------------------------------

    def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool,
    ) -> str:

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.gemini_model}:generateContent"
        )

        params = {
            "key": self.gemini_api_key,
        }

        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": system_prompt
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            },
        }

        if json_mode:
            payload["generationConfig"]["responseMimeType"] = (
                "application/json"
            )

        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=config.REQUEST_TIMEOUT_SECONDS * 3,
        )

        if not response.ok:
            detail = response.text[:500].replace("\n", " ")
            raise AIClientError(
                f"Gemini HTTP {response.status_code}: {detail}"
            )

        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except (KeyError, IndexError, TypeError) as exc:
            logger.info(
                "Resposta inesperada da API Gemini: %s",
                data,
            )
            raise AIClientError(
                "Gemini não retornou texto válido."
            ) from exc

    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------

    def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        json_mode: bool,
    ) -> str:

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.openai_model,
            "temperature": temperature,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        if json_mode:
            payload["response_format"] = {
                "type": "json_object"
            }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=config.REQUEST_TIMEOUT_SECONDS * 3,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]