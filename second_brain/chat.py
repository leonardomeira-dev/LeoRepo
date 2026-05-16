"""Claude-powered Q&A over the knowledge base."""

import os
import anthropic
from .models import KnowledgeBase, ChatMessage, ConversationHistory
from .search import search


MODEL = "claude-sonnet-4-6"
MAX_CONTEXT_FILES = 5
MAX_CONTENT_CHARS = 8000


def _build_context(kb: KnowledgeBase, query: str) -> str:
    """Build context from the knowledge base for the query."""
    results = search(kb, query, top_k=MAX_CONTEXT_FILES)
    if not results:
        files_sample = kb.files[:MAX_CONTEXT_FILES]
        context_parts = [
            f"[{f.category}] {f.title}: {f.content_snippet or 'Sem trecho disponível'}"
            for f in files_sample
        ]
        return "Arquivos disponíveis (amostra):\n" + "\n".join(context_parts)

    parts = []
    for r in results:
        f = r.file
        content = ""
        if f.full_content:
            content = f.full_content[:MAX_CONTENT_CHARS]
        elif f.summary:
            content = f.summary
        elif f.content_snippet:
            content = f.content_snippet

        parts.append(
            f"--- ARQUIVO: {f.title} ---\n"
            f"Categoria: {f.category}\n"
            f"Tipo: {f.mime_type}\n"
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
        f"Base de conhecimento: {kb.total_files} arquivos organizados em: {cats_str}.\n\n"
        "Seu papel:\n"
        "- Responder perguntas com base nos documentos do usuário\n"
        "- Conectar ideias entre diferentes arquivos\n"
        "- Resumir e explicar conteúdos\n"
        "- Sugerir conexões entre tópicos\n"
        "- Ser proativo em trazer insights relevantes\n\n"
        "Quando não tiver informação suficiente no contexto fornecido, diga claramente "
        "e sugira quais tipos de arquivos podem conter a resposta.\n"
        "Responda sempre em português do Brasil, de forma clara e útil."
    )


def ask(
    kb: KnowledgeBase,
    query: str,
    history: ConversationHistory,
    api_key: str | None = None,
) -> str:
    """Ask a question to the knowledge base using Claude."""
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    context = _build_context(kb, query)

    messages = []
    for msg in history.messages[-10:]:  # Keep last 10 messages for context
        messages.append({"role": msg.role, "content": msg.content})

    user_message = f"Contexto dos meus arquivos:\n\n{context}\n\n---\n\nPergunta: {query}"
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=_system_prompt(kb),
        messages=messages,
    )

    return response.content[0].text


def summarize_file(file_content: str, file_title: str, api_key: str | None = None) -> str:
    """Generate a concise summary of a file's content."""
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                f"Leia o seguinte conteúdo do arquivo '{file_title}' e gere um resumo "
                f"conciso (máx. 3 parágrafos) em português, destacando os pontos principais:\n\n"
                f"{file_content[:6000]}"
            ),
        }],
    )
    return response.content[0].text
