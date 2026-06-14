"""Gemini-powered Q&A over the knowledge base (via REST API)."""

import os
import httpx
from .models import KnowledgeBase, ChatMessage, ConversationHistory
from .search import search


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent"
)
MAX_CONTEXT_FILES = 5
MAX_CONTENT_CHARS = 8000


def _build_context(kb: KnowledgeBase, query: str) -> str:
    results = search(kb, query, top_k=MAX_CONTEXT_FILES)
    if not results:
        files_sample = kb.files[:MAX_CONTEXT_FILES]
        return "Arquivos disponíveis (amostra):\n" + "\n".join(
            f"[{f.category}] {f.title}: {f.content_snippet or 'Sem trecho'}"
            for f in files_sample
        )

    parts = []
    for r in results:
        f = r.file
        content = f.full_content[:MAX_CONTENT_CHARS] if f.full_content else (f.summary or f.content_snippet or "")
        parts.append(
            f"--- ARQUIVO: {f.title} ---\n"
            f"Categoria: {f.category}\n"
            f"Conteúdo:\n{content}\n"
        )
    return "\n".join(parts)


def _system_prompt(kb: KnowledgeBase) -> str:
    from .knowledge_base import get_categories_summary
    cats = get_categories_summary(kb)
    cats_str = ", ".join(f"{k} ({v})" for k, v in cats.items())
    return (
        "Você é o Second Brain pessoal do usuário — um assistente de conhecimento "
        "alimentado pelo conteúdo do Google Drive dele.\n\n"
        f"Base de conhecimento: {kb.total_files} arquivos em: {cats_str}.\n\n"
        "Seu papel: responder com base nos documentos, conectar ideias, resumir e "
        "trazer insights relevantes. Quando não tiver informação suficiente, diga claramente.\n"
        "Responda sempre em português do Brasil."
    )


def _call_gemini(api_key: str, contents: list, system: str) -> str:
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 2048},
    }
    resp = httpx.post(
        GEMINI_URL,
        headers={"X-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def ask(
    kb: KnowledgeBase,
    query: str,
    history: ConversationHistory,
    api_key: str | None = None,
) -> str:
    key = api_key or os.environ.get("GOOGLE_API_KEY") or ""

    contents = []
    for msg in history.messages[-10:]:
        role = "user" if msg.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg.content}]})

    context = _build_context(kb, query)
    user_text = f"Contexto dos meus arquivos:\n\n{context}\n\n---\n\nPergunta: {query}"
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    return _call_gemini(key, contents, _system_prompt(kb))


def summarize_file(file_content: str, file_title: str, api_key: str | None = None) -> str:
    key = api_key or os.environ.get("GOOGLE_API_KEY") or ""
    contents = [{
        "role": "user",
        "parts": [{"text": (
            f"Leia o conteúdo do arquivo '{file_title}' e gere um resumo "
            f"conciso (máx. 3 parágrafos) em português:\n\n{file_content[:6000]}"
        )}],
    }]
    return _call_gemini(key, contents, "Você é um assistente especialista em resumir documentos.")
