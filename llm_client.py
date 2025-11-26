"""
Универсальный LLM клиент
"""
import os
import logging
from typing import List, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """Универсальный клиент для работы с разными LLM провайдерами."""

    def __init__(
            self,
            provider: str = "gemini",
            api_key: Optional[str] = None,
            router_model: Optional[str] = None,
            assistant_model: Optional[str] = None,
            fallback_provider: Optional[str] = None,
            fallback_api_key: Optional[str] = None,
    ):
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key(self.provider)

        self.router_model = router_model or self._get_router_model(self.provider)
        self.assistant_model = assistant_model or self._get_assistant_model(self.provider)

        self.fallback_provider = fallback_provider
        self.fallback_api_key = fallback_api_key or (
            self._get_api_key(fallback_provider) if fallback_provider else None
        )

        self.client = httpx.AsyncClient(timeout=60.0)

        logger.info(f"LLM Client initialized: {self.provider}")
        logger.info(f"  Router model: {self.router_model}")
        logger.info(f"  Assistant model: {self.assistant_model}")
        if self.fallback_provider:
            logger.info(f"  Fallback: {self.fallback_provider}")

    def _get_router_model(self, provider: str) -> str:
        """Получить быструю модель для классификации интентов."""
        models = {
            "gemini": "gemini-2.0-flash-exp",
            "groq": "llama-3.3-70b-versatile",
            "openrouter": "google/gemini-flash-1.5",
            "mistral": "mistral-small-latest",
        }
        return models.get(provider, "gemini-2.0-flash-exp")

    def _get_assistant_model(self, provider: str) -> str:
        """Получить основную модель для генерации ответов."""
        models = {
            "gemini": "gemini-2.0-flash-exp",
            "groq": "llama-3.3-70b-versatile",
            "openrouter": "google/gemini-flash-1.5-8b",
            "mistral": "pixtral-large-latest",
        }
        return models.get(provider, "gemini-2.0-flash-exp")

    def _get_api_key(self, provider: str) -> str:
        """Получить API ключ из environment."""
        key_map = {
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }
        env_var = key_map.get(provider)
        if not env_var:
            raise ValueError(f"Unknown provider: {provider}")

        key = os.getenv(env_var)
        if not key:
            raise ValueError(f"{env_var} not found in environment")
        return key

    def _get_endpoint(self, provider: str) -> str:
        """Получить API endpoint для провайдера."""
        endpoints = {
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "openrouter": "https://openrouter.ai/api/v1/chat/completions",
            "mistral": "https://api.mistral.ai/v1/chat/completions",
        }
        return endpoints[provider]

    async def chat(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: int = 1000,
            model: Optional[str] = None,
    ) -> str:
        """
        Отправить запрос к LLM.

        Args:
            messages: История сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Температура генерации (0-1)
            max_tokens: Максимум токенов в ответе
            model: Модель (по умолчанию assistant_model)

        Returns:
            Текст ответа от модели
        """
        if model is None:
            model = self.assistant_model

        try:
            return await self._chat_with_provider(
                messages, temperature, max_tokens,
                self.provider, self.api_key, model
            )
        except Exception as e:
            logger.error(f"{self.provider} error: {e}")

            if self.fallback_provider and self.fallback_api_key:
                logger.warning(f"Trying fallback: {self.fallback_provider}")
                try:
                    fallback_model = self._get_assistant_model(self.fallback_provider)
                    return await self._chat_with_provider(
                        messages, temperature, max_tokens,
                        self.fallback_provider, self.fallback_api_key, fallback_model
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback {self.fallback_provider} failed: {fallback_error}")

            raise

    async def _chat_with_provider(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int,
            provider: str,
            api_key: str,
            model: str,
    ) -> str:
        """Выполнить запрос к конкретному провайдеру."""
        if provider == "gemini":
            return await self._chat_gemini(messages, temperature, max_tokens, api_key, model)
        elif provider in ["groq", "openrouter", "mistral"]:
            return await self._chat_openai_compatible(
                messages, temperature, max_tokens, provider, api_key, model
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _chat_gemini(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int,
            api_key: str,
            model: str,
    ) -> str:
        """Запрос к Gemini API."""
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        resp = await self.client.post(endpoint, json=payload)
        resp.raise_for_status()

        data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {data}")
            raise ValueError("Invalid Gemini API response format")

    async def _chat_openai_compatible(
            self,
            messages: List[Dict[str, str]],
            temperature: float,
            max_tokens: int,
            provider: str,
            api_key: str,
            model: str,
    ) -> str:
        """Запрос к OpenAI-compatible API (Groq, OpenRouter, Mistral)."""
        endpoint = self._get_endpoint(provider)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://fortebank-hackathon.com"
            headers["X-Title"] = "ForteBank BA Assistant"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = await self.client.post(endpoint, headers=headers, json=payload)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()

    async def ask_router(
            self,
            prompt: str,
            temperature: float = 0.1,
            max_tokens: int = 150,
    ) -> str:
        """
        Совместимость с IntentRouter.
        Использует быструю модель для классификации.
        """
        messages = [
            {"role": "user", "content": prompt},
        ]
        return await self.chat(
            messages,
            temperature,
            max_tokens,
            model=self.router_model
        )


def create_llm_client_from_env() -> LLMClient:
    """Создать LLM клиент на основе переменных окружения."""
    from config import settings
    
    provider = settings.LLM_PROVIDER
    router_model = settings.LLM_ROUTER_MODEL
    assistant_model = settings.LLM_ASSISTANT_MODEL
    fallback_provider = settings.LLM_FALLBACK_PROVIDER

    # API ключи из settings
    api_key = None
    if provider == "groq":
        api_key = settings.GROQ_API_KEY
    elif provider == "gemini":
        api_key = settings.GEMINI_API_KEY
    elif provider == "openrouter":
        api_key = settings.OPENROUTER_API_KEY
    elif provider == "mistral":
        api_key = settings.MISTRAL_API_KEY

    fallback_api_key = None
    if fallback_provider:
        if fallback_provider == "groq":
            fallback_api_key = settings.GROQ_API_KEY
        elif fallback_provider == "gemini":
            fallback_api_key = settings.GEMINI_API_KEY
        elif fallback_provider == "openrouter":
            fallback_api_key = settings.OPENROUTER_API_KEY
        elif fallback_provider == "mistral":
            fallback_api_key = settings.MISTRAL_API_KEY

    return LLMClient(
        provider=provider,
        api_key=api_key,
        router_model=router_model,
        assistant_model=assistant_model,
        fallback_provider=fallback_provider,
        fallback_api_key=fallback_api_key,
    )