"""LLM client — supports HuggingFace Inference API and Ollama."""

import httpx

from ..config import settings


async def generate(prompt: str, system: str = "") -> str:
    if settings.LLM_PROVIDER == "ollama":
        return await _ollama_generate(prompt, system)
    return await _hf_generate(prompt, system)


async def _ollama_generate(prompt: str, system: str) -> str:
    base = settings.OLLAMA_URL.rstrip("/")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": settings.LLM_TEMPERATURE,
                    "num_ctx": 4096,
                },
            },
            timeout=120.0,
        )
        if resp.is_error:
            detail = None
            try:
                body = resp.json()
                if isinstance(body, dict) and body.get("error"):
                    detail = body["error"]
            except Exception:
                detail = (resp.text or "").strip() or None
            if resp.status_code == 404:
                msg = detail or "Not found"
                raise RuntimeError(
                    f"Ollama returned 404 ({msg}). "
                    f"Install the model with: ollama pull {settings.OLLAMA_MODEL} "
                    "or set OLLAMA_MODEL in backend/.env to a name from `ollama list`."
                ) from None
            resp.raise_for_status()
        return resp.json()["response"]


async def _hf_generate(prompt: str, system: str) -> str:
    full_prompt = f"[INST] {system}\n\n{prompt} [/INST]" if system else f"[INST] {prompt} [/INST]"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api-inference.huggingface.co/models/{settings.HF_MODEL}",
            headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": settings.LLM_MAX_TOKENS,
                    "temperature": settings.LLM_TEMPERATURE,
                    "return_full_text": False,
                },
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data[0]["generated_text"]
        return data["generated_text"]
