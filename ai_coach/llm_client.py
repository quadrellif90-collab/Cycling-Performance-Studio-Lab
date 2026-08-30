"""Multi-provider LLM client for CPSL AI Coach.

Supporta 14 provider LLM usando solo httpx (già in requirements-common.txt).
Nessuna nuova dipendenza richiesta.
"""
import os

import httpx

# ── Provider registry ──────────────────────────────────────────────────────
# Chiave ambiente usata, base URL e percorso endpoint chat completions.
PROVIDERS = {
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,  # Usa httpx + OpenAI-compatible format
    },
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1",
        "chat_endpoint": "/messages",
        "native": True,  # API Anthropic è nativo (different from OpenAI)
    },
    "google": {
        "env_key": "GOOGLE_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "chat_endpoint": None,  # Gemini usa modello diverso
        "native": True,
    },
    "mistral": {
        "env_key": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "groq": {
        "env_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "openrouter": {
        "env_key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "ollama": {
        "env_key": "OLLAMA_API_KEY",  # opzionale, localhost di default
        "base_url": "http://localhost:11434/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "lmstudio": {
        "env_key": "LMSTUDIO_API_KEY",  # opzionale, localhost di default
        "base_url": "http://localhost:1234/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "perplexity": {
        "env_key": "PERPLEXITY_API_KEY",
        "base_url": "https://api.perplexity.ai",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "replicate": {
        "env_key": "REPLICATE_API_TOKEN",
        "base_url": "https://api.replicate.com/v1",
        "chat_endpoint": "/models",
        "native": False,
    },
    "cohere": {
        "env_key": "COHERE_API_KEY",
        "base_url": "https://api.cohere.com/v1",
        "chat_endpoint": "/chat",
        "native": True,
    },
    "xai": {
        "env_key": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "chat_endpoint": "/chat/completions",
        "native": False,
    },
    "azure": {
        "env_key": "AZURE_OPENAI_API_KEY",
        "base_url": None,  # Da settings Azure: <resource>.openai.azure.com
        "chat_endpoint": "/openai/deployments/{model}/extensions",
        "native": True,  # Azure OpenAI usa formato esteso
    },
}


class LLMClient:
    """Client LLM multiplu provider.

    Usa httpx per tutte le chiamate → zero nuove dipendenze.
    Ogni provider ha il suo formato di richiesta (alcuni nativi, altri
    OpenAI-compatible).
    """

    def __init__(
        self,
        provider: str = "openai",
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        fallback: dict | None = None,
    ):
        provider = provider or "openai"
        if provider not in PROVIDERS:
            raise ValueError(f"Provider '{provider}' non supportato")

        cfg = PROVIDERS[provider]
        self.provider = provider
        self.api_key = api_key or os.environ.get(cfg["env_key"], "")
        self.model = model or self._default_model(provider)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = cfg["base_url"]
        self.chat_endpoint = cfg["chat_endpoint"]
        self.native = cfg["native"]
        # Optional fallback config: {"provider":..., "api_key":..., "model":...}
        self.fallback = fallback

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _default_model(provider: str) -> str:
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20240620",
            "google": "gemini-1.5-pro",
            "mistral": "mistral-large-2402",
            "deepseek": "deepseek-chat",
            "groq": "llama-3.1-70b-versatile",
            "openrouter": "anthropic/claude-3.5-sonnet",
            "ollama": "llama3.1:8b",
            "lmstudio": "llama3.1:8b",
            "perplexity": "sonar-pro",
            "replicate": "replicate/cmd-r-plus",
            "cohere": "command-r-plus",
            "xai": "grok-2",
            "azure": "gpt-4o",
        }
        return defaults.get(provider, "gpt-4o")

    def _headers(self) -> dict:
        """Headers HTTP per la richiesta al provider."""
        if self.provider == "anthropic":
            return {"x-api-key": self.api_key, "Content-Type": "application/json"}
        if self.provider == "cohere":
            return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.provider == "azure":
            # Azure usa header Authorization: API key + deployname nel path
            return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        # Default: OpenAI-compatible
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    # ── Public API ───────────────────────────────────────────────────────

    def chat(
        self,
        messages: list[dict],
        system: str | None = None,
    ) -> str:
        """Invia una chat al provider LLM e restituisce la risposta testuale.

        In caso di errore sul provider primario, prova il provider di fallback
        (se configurato in self.fallback) prima di propagare l'errore.
        """
        try:
            return self._chat_primary(messages, system)
        except Exception as primary_err:
            if self.fallback:
                try:
                    fb = LLMClient(
                        provider=self.fallback.get("provider", "groq"),
                        api_key=self.fallback.get("api_key") or self.api_key,
                        model=self.fallback.get("model"),
                    )
                    return f"[fallback:{fb.provider}] " + fb._chat_primary(messages, system)
                except Exception:
                    pass
            return f"[AI Coach error: {primary_err}]"

    def _chat_primary(self, messages, system=None) -> str:
        if self.provider == "anthropic":
            return self._chat_anthropic(messages, system)
        if self.provider == "google":
            return self._chat_google(messages, system)
        if self.provider == "cohere":
            return self._chat_cohere(messages, system)
        if self.provider == "azure":
            return self._chat_azure(messages, system)
        return self._chat_openai_compatible(messages, system)

    # ── Provider-specific implementations ────────────────────────────────

    def _chat_openai_compatible(self, messages, system=None) -> str:
        """Formato OpenAI-compatible (usato da openai, mistral, deepseek, groq, openrouter, ollama, lmstudio, perplexity, xai)."""
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}] * (system is not None)
            + messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        url = f"{self.base_url}{self.chat_endpoint}"
        last_err = None
        for attempt in range(3):  # retry on transient 429/503 (rate-limit)
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(url, headers=self._headers(), json=payload)
                    if resp.status_code in (429, 503):
                        import time as _t
                        _t.sleep(1.5 * (attempt + 1))
                        last_err = f"{resp.status_code}"
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                if self.provider == "openrouter":
                    return data["choices"][0]["message"]["content"]
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_err = str(e)
        return f"[AI Coach error: provider unavailable after retries ({last_err})]"

    def _chat_anthropic(self, messages, system=None) -> str:
        """API nativo Anthropic."""
        content = system or ""
        # Anthropic usa 'system' separato + 'messages' con ruoli
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": content,
            "messages": [
                {"role": m.get("role", "user"), "content": m["content"]} for m in messages
            ],
        }
        url = f"{self.base_url}{self.chat_endpoint}"
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()
        # Anthropic restituisce content blocchi
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block["text"]
        return text

    def _chat_google(self, messages, system=None) -> str:
        """API Google Gemini."""
        text = "\n".join(m["content"] for m in messages)
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"role": "user", "parts": [{"text": text}]}]}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        last_err = None
        for attempt in range(3):  # retry on transient 503/429 from preview models
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code in (503, 429):
                        import time as _t
                        _t.sleep(1.5 * (attempt + 1))
                        last_err = f"{resp.status_code}"
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    return str(data)
            except Exception as e:
                last_err = str(e)
        return f"[AI Coach error: Gemini unavailable after retries ({last_err})]"

    def _chat_cohere(self, messages, system=None) -> str:
        """API Cohere."""
        text = "\n".join(m["content"] for m in messages)
        url = f"{self.base_url}{self.chat_endpoint}"
        payload = {"message": text, "temperature": self.temperature, "max_tokens": self.max_tokens}
        if system:
            payload["system"] = system
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data.get("text", str(data))

    def _chat_azure(self, messages, system=None) -> str:
        """API Azure OpenAI."""
        # Azure richiede il nome deployment nel path URL
        deployment = self.model.replace("/", "_")
        url = f"{self.base_url}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
        payload = {
            "model": self.model,
            "messages": [
                {"role": m.get("role", "user"), "content": m["content"]} for m in messages
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if system:
            payload["system"] = system
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    @classmethod
    def from_config(cls, config_section: dict = None) -> "LLMClient":
        """Istanzia da configurazione (dict o oggetto tipo module config)."""
        if config_section is None:
            from . import config
            cs = {
                "provider": getattr(config, "AI_LLM_PROVIDER", "openai"),
                "api_key": getattr(config, "AI_LLM_API_KEY", ""),
                "model": getattr(config, "AI_LLM_MODEL", "gpt-4o"),
                "temperature": float(getattr(config, "AI_LLM_TEMPERATURE", 0.7)),
                "max_tokens": int(getattr(config, "AI_LLM_MAX_TOKENS", 2000)),
            }
            fb = getattr(config, "AI_LLM_FALLBACK", None)
        else:
            cs = {
                "provider": config_section.get("provider", "openai"),
                "api_key": config_section.get("api_key", ""),
                "model": config_section.get("model", "gpt-4o"),
                "temperature": float(config_section.get("temperature", 0.7)),
                "max_tokens": int(config_section.get("max_tokens", 2000)),
            }
            fb = config_section.get("fallback")
        if isinstance(fb, str):
            # shorthand: "provider:model"
            parts = fb.split(":", 1)
            fb = {"provider": parts[0], "model": parts[1] if len(parts) > 1 else None}
        cs["fallback"] = fb
        return cls(**cs)


def get_client(config_section: dict = None) -> LLMClient:
    """Convenience factory: restituisce LLMClient istanziato dalla config."""
    return LLMClient.from_config(config_section)
