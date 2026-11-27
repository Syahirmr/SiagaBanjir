"""Adapter LLM Provider untuk Gemini API (utama) dan Groq API (cadangan).

Ketentuan ARCHITECTURE.md v0.2 (Bag. 5 & 12.3):
- Nama model spesifik tidak di-hardcode; dibaca dari AppConfig (OD-02).
- Menggunakan LangChain secara selektif bila paket terpasang, atau panggilan
  HTTP langsung melalui `requests` di balik antarmuka seragam yang sama.
- Melarang *silent fallback* saat `allow_fallback=False` (wajib pada eksperimen).
- Pesan kesalahan selalu disanitasi agar tidak membocorkan API key.
"""

from __future__ import annotations

import time
from typing import Any, Callable

import requests

from src.config import AppConfig, sanitize_secret_text
from src.schemas import ErrorType, LLMCallResult

TransportCallable = Callable[
    [str, str, list[dict[str, str]], dict[str, Any]],
    str,
]

_FALLBACK_ELIGIBLE_ERRORS: frozenset[ErrorType] = frozenset(
    {"timeout", "rate_limit", "network_error", "provider_error"}
)


class ProviderCallError(RuntimeError):
    """Error terklasifikasi dari panggilan provider LLM."""

    def __init__(self, error_type: ErrorType, message: str) -> None:
        super().__init__(message)
        self.error_type: ErrorType = error_type


def _classify_http_error(status_code: int) -> ErrorType:
    if status_code in (401, 403):
        return "auth_error"
    if status_code == 429:
        return "rate_limit"
    if status_code in (408, 504):
        return "timeout"
    return "provider_error"


class LLMProviderAdapter:
    """Adapter seragam untuk Gemini API (utama) dan Groq API (fallback demo)."""

    def __init__(
        self,
        config: AppConfig,
        transport: TransportCallable | None = None,
        use_langchain_if_available: bool = True,
    ) -> None:
        self.config = config
        self._transport = transport
        self._use_langchain = use_langchain_if_available

    def generate(
        self,
        messages: list[dict[str, str]],
        allow_fallback: bool = False,
    ) -> LLMCallResult:
        """Memanggil provider utama, dengan fallback terkontrol hanya bila diizinkan."""
        params = self.config.llm_parameters()
        primary_provider = self.config.primary_provider
        primary_model = self.config.primary_model

        start = time.perf_counter()
        try:
            text = self._invoke_provider(
                provider=primary_provider,
                model=primary_model,
                messages=messages,
                params=params,
            )
            return LLMCallResult(
                provider_requested=primary_provider,
                provider_actual=primary_provider,
                model_requested=primary_model,
                model_actual=primary_model,
                parameters=params,
                raw_text=text,
                api_status="success",
                fallback_used=False,
                fallback_reason=None,
                error_type=None,
                error_message_sanitized=None,
                latency_sec=round(time.perf_counter() - start, 4),
            )
        except ProviderCallError as primary_err:
            sanitized_primary = sanitize_secret_text(
                str(primary_err), self.config.known_secrets()
            )
            can_fallback = (
                allow_fallback
                and primary_err.error_type in _FALLBACK_ELIGIBLE_ERRORS
                and self.config.fallback_provider != primary_provider
                and self.config.is_fallback_model_configured
            )
            if not can_fallback:
                return LLMCallResult(
                    provider_requested=primary_provider,
                    provider_actual=primary_provider,
                    model_requested=primary_model,
                    model_actual=primary_model,
                    parameters=params,
                    raw_text=None,
                    api_status="error",
                    fallback_used=False,
                    fallback_reason=None,
                    error_type=primary_err.error_type,
                    error_message_sanitized=sanitized_primary,
                    latency_sec=round(time.perf_counter() - start, 4),
                )

            fb_provider = self.config.fallback_provider
            fb_model = self.config.fallback_model
            try:
                fb_text = self._invoke_provider(
                    provider=fb_provider,
                    model=fb_model,
                    messages=messages,
                    params=params,
                )
                return LLMCallResult(
                    provider_requested=primary_provider,
                    provider_actual=fb_provider,
                    model_requested=primary_model,
                    model_actual=fb_model,
                    parameters=params,
                    raw_text=fb_text,
                    api_status="success",
                    fallback_used=True,
                    fallback_reason=f"primary_{primary_err.error_type}",
                    error_type=None,
                    error_message_sanitized=None,
                    latency_sec=round(time.perf_counter() - start, 4),
                )
            except ProviderCallError as fb_err:
                sanitized_fb = sanitize_secret_text(
                    str(fb_err), self.config.known_secrets()
                )
                return LLMCallResult(
                    provider_requested=primary_provider,
                    provider_actual=fb_provider,
                    model_requested=primary_model,
                    model_actual=fb_model,
                    parameters=params,
                    raw_text=None,
                    api_status="error",
                    fallback_used=True,
                    fallback_reason=f"primary_{primary_err.error_type}",
                    error_type=fb_err.error_type,
                    error_message_sanitized=(
                        f"Primary gagal ({primary_err.error_type}); "
                        f"fallback gagal ({fb_err.error_type}): {sanitized_fb}"
                    ),
                    latency_sec=round(time.perf_counter() - start, 4),
                )

    def _invoke_provider(
        self,
        provider: str,
        model: str,
        messages: list[dict[str, str]],
        params: dict[str, Any],
    ) -> str:
        if not model or model.startswith("TBD_"):
            raise ProviderCallError(
                "provider_error",
                f"Model untuk provider '{provider}' belum ditetapkan ({model}).",
            )

        if self._transport is not None:
            try:
                return self._transport(provider, model, messages, params)
            except ProviderCallError:
                raise
            except TimeoutError as exc:
                raise ProviderCallError("timeout", str(exc)) from exc
            except Exception as exc:
                raise ProviderCallError("provider_error", str(exc)) from exc

        if provider == "gemini":
            if not self.config.has_gemini_key:
                raise ProviderCallError("auth_error", "GEMINI_API_KEY belum tersedia.")
            if self._use_langchain:
                lc_text = self._try_langchain_gemini(model, messages, params)
                if lc_text is not None:
                    return lc_text
            return self._call_gemini_http(model, messages, params)

        if provider == "groq":
            if not self.config.has_groq_key:
                raise ProviderCallError("auth_error", "GROQ_API_KEY belum tersedia.")
            if self._use_langchain:
                lc_text = self._try_langchain_groq(model, messages, params)
                if lc_text is not None:
                    return lc_text
            return self._call_groq_http(model, messages, params)

        raise ProviderCallError(
            "provider_error", f"Provider tidak didukung: {provider!r}"
        )

    def _try_langchain_gemini(
        self,
        model: str,
        messages: list[dict[str, str]],
        params: dict[str, Any],
    ) -> str | None:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            return None

        lc_messages = [
            SystemMessage(content=m["content"])
            if m["role"] == "system"
            else HumanMessage(content=m["content"])
            for m in messages
        ]
        try:
            client = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=self.config.gemini_api_key,
                temperature=params["temperature"],
                max_output_tokens=params["max_tokens"],
                timeout=params["timeout_sec"],
                max_retries=0,
            )
            resp = client.invoke(lc_messages)
            text = getattr(resp, "text", None) or getattr(resp, "content", "")
            return str(text).strip()
        except Exception as exc:
            raise self._map_generic_exception(exc) from exc

    def _try_langchain_groq(
        self,
        model: str,
        messages: list[dict[str, str]],
        params: dict[str, Any],
    ) -> str | None:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_groq import ChatGroq
        except ImportError:
            return None

        lc_messages = [
            SystemMessage(content=m["content"])
            if m["role"] == "system"
            else HumanMessage(content=m["content"])
            for m in messages
        ]
        try:
            client = ChatGroq(
                model=model,
                groq_api_key=self.config.groq_api_key,
                temperature=params["temperature"],
                max_tokens=params["max_tokens"],
                timeout=params["timeout_sec"],
                max_retries=0,
            )
            resp = client.invoke(lc_messages)
            text = getattr(resp, "text", None) or getattr(resp, "content", "")
            return str(text).strip()
        except Exception as exc:
            raise self._map_generic_exception(exc) from exc

    def _call_gemini_http(
        self,
        model: str,
        messages: list[dict[str, str]],
        params: dict[str, Any],
    ) -> str:
        model_path = model if model.startswith("models/") else f"models/{model}"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"{model_path}:generateContent"
        )
        system_parts = [
            {"text": m["content"]} for m in messages if m["role"] == "system"
        ]
        contents = [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": [{"text": m["content"]}],
            }
            for m in messages
            if m["role"] != "system"
        ]
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": params["temperature"],
                "maxOutputTokens": params["max_tokens"],
            },
        }
        if system_parts:
            payload["systemInstruction"] = {"parts": system_parts}

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.config.gemini_api_key or "",
        }
        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=params["timeout_sec"],
            )
        except requests.Timeout as exc:
            raise ProviderCallError("timeout", "Permintaan Gemini API timeout.") from exc
        except requests.RequestException as exc:
            raise ProviderCallError(
                "network_error", f"Gangguan jaringan ke Gemini API: {exc}"
            ) from exc

        if resp.status_code >= 400:
            raise ProviderCallError(
                _classify_http_error(resp.status_code),
                f"Gemini HTTP {resp.status_code}: {resp.text[:300]}",
            )

        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise ProviderCallError("provider_error", "Respons Gemini kosong (0 kandidat).")
        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(str(p.get("text", "")) for p in parts).strip()
        if not text:
            raise ProviderCallError("provider_error", "Respons teks Gemini kosong.")
        return text

    def _call_groq_http(
        self,
        model: str,
        messages: list[dict[str, str]],
        params: dict[str, Any],
    ) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.groq_api_key or ''}",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": params["temperature"],
            "max_tokens": params["max_tokens"],
        }
        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=params["timeout_sec"],
            )
        except requests.Timeout as exc:
            raise ProviderCallError("timeout", "Permintaan Groq API timeout.") from exc
        except requests.RequestException as exc:
            raise ProviderCallError(
                "network_error", f"Gangguan jaringan ke Groq API: {exc}"
            ) from exc

        if resp.status_code >= 400:
            raise ProviderCallError(
                _classify_http_error(resp.status_code),
                f"Groq HTTP {resp.status_code}: {resp.text[:300]}",
            )

        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise ProviderCallError("provider_error", "Respons Groq kosong (0 choices).")
        content = (choices[0].get("message") or {}).get("content", "")
        text = str(content).strip()
        if not text:
            raise ProviderCallError("provider_error", "Respons teks Groq kosong.")
        return text

    @staticmethod
    def _map_generic_exception(exc: Exception) -> ProviderCallError:
        msg = str(exc)
        low = msg.lower()
        if "timeout" in low or "timed out" in low:
            return ProviderCallError("timeout", msg)
        if "429" in low or "rate limit" in low or "quota" in low:
            return ProviderCallError("rate_limit", msg)
        if "401" in low or "403" in low or "api key" in low or "auth" in low:
            return ProviderCallError("auth_error", msg)
        if "connection" in low or "network" in low or "dns" in low:
            return ProviderCallError("network_error", msg)
        return ProviderCallError("provider_error", msg)
