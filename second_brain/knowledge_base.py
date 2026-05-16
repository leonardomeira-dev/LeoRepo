"""Knowledge base management - loading, saving, and organizing Drive content."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from .models import DriveFile, KnowledgeBase

DATA_DIR = Path(__file__).parent.parent / "data"
KB_FILE = DATA_DIR / "knowledge_base.json"
FILES_DIR = DATA_DIR / "files"

READABLE_MIME_TYPES = {
    "application/pdf",
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.presentation",
    "application/vnd.google-apps.spreadsheet",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

CATEGORY_RULES = {
    "Pessoal & Saúde": [
        "leonardomeira", "exames_", "exame", "receita_", "dentista", "pesquisa sobre leonardo",
        "fdownloader", "img_", "engenharia_emocional", "sistema paul brunton", "resumo_"
    ],
    "Finanças": [
        "fatura_itau", "itau_", "bac+", "bradesco", "portfolio", "multiativo",
        "wealth", "fortune", "annual report", "relatorio_anual", "latam digital",
        "atlantico", "a.f.dig", "guia de gestao"
    ],
    "Desenvolvimento Pessoal": [
        "cura", "sombra", "emocional", "vibracional", "paul brunton", "elevacao",
        "healing", "chave+do+poder", "diario", "gratidao"
    ],
    "Espiritualidade & Filosofia": [
        "cristo", "nous", "o-mundo-das-energias", "oculto", "a+chave"
    ],
    "IA & Tecnologia": [
        "_agents_", "agent_", "gpt_", "llm", "agentic", "mcp_", "mcp cookbook",
        "generative_ai", "generarive", "multi_agent", "super_prompt", "framework_ai",
        "guide_to_build_ai", "bertelsmann", "roi of ai", "mastering_multi", "ipaas",
        "openai", "artificial intelligence", "machine learning"
    ],
    "Jurídico & Contratos": [
        "contrato_", "acqua_park", "republica federativa", "quadro resumo", "181c"
    ],
    "Negócios & Estratégia": [
        "imatec", "revista it", "macrotendencias", "estudo macro"
    ],
    "Relatórios & Documentos": [
        "relatorio_anual", "annual_report", "bac+2024", "bac+2025"
    ],
}


def clean_title(title: str) -> str:
    """URL-decode and clean a file title."""
    return unquote(title).replace("+", " ").strip()


def categorize_file(title: str, snippet: str = "") -> str:
    """Assign a category based on title and content snippet."""
    title_lower = title.lower()
    snippet_lower = (snippet or "").lower()

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in title_lower:
                return category

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in snippet_lower:
                return category

    # Fallback: simple keyword matching on title
    title_words = set(title_lower.replace("_", " ").replace("-", " ").replace("+", " ").split())
    if any(w in title_words for w in ["ai", "agent", "gpt", "mcp", "llm"]):
        return "IA & Tecnologia"
    if any(w in title_words for w in ["fatura", "banco", "invest", "relatorio", "finance"]):
        return "Finanças"
    if any(w in title_words for w in ["cura", "sombra", "espiritual", "meditacao"]):
        return "Desenvolvimento Pessoal"

    return "Geral"


def load_raw_index() -> list[dict]:
    """Load and merge all raw drive index pages."""
    all_files = []
    for page_file in sorted(DATA_DIR.glob("drive_index*.json")):
        with open(page_file) as f:
            files = json.load(f)
            all_files.extend(files)
    return all_files


def build_knowledge_base() -> KnowledgeBase:
    """Build the knowledge base from raw Drive index files."""
    raw_files = load_raw_index()
    seen_ids = set()
    drive_files = []

    for raw in raw_files:
        file_id = raw.get("id")
        if not file_id or file_id in seen_ids:
            continue
        seen_ids.add(file_id)

        title = clean_title(raw.get("title") or "Sem título")
        mime_type = raw.get("mimeType", "")
        snippet = raw.get("contentSnippet") or ""

        drive_file = DriveFile(
            id=file_id,
            title=title,
            mime_type=mime_type,
            created_time=raw.get("createdTime"),
            modified_time=raw.get("modifiedTime"),
            file_size=raw.get("fileSize"),
            view_url=raw.get("viewUrl"),
            content_snippet=snippet[:500] if snippet else None,
            category=categorize_file(title, snippet),
        )

        content_file = FILES_DIR / f"{file_id}.json"
        if content_file.exists():
            with open(content_file) as f:
                stored = json.load(f)
                drive_file.summary = stored.get("summary")
                drive_file.full_content = stored.get("full_content")
                drive_file.indexed_at = stored.get("indexed_at")

        drive_files.append(drive_file)

    kb = KnowledgeBase(
        last_synced=datetime.now(timezone.utc).isoformat(),
        total_files=len(drive_files),
        files=drive_files,
    )
    return kb


def save_knowledge_base(kb: KnowledgeBase) -> None:
    KB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb.model_dump(), f, ensure_ascii=False, indent=2)


def load_knowledge_base() -> KnowledgeBase:
    if not KB_FILE.exists():
        return build_knowledge_base()
    with open(KB_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return KnowledgeBase(**data)


def save_file_content(file_id: str, content: str, summary: str) -> None:
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "file_id": file_id,
        "full_content": content,
        "summary": summary,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(FILES_DIR / f"{file_id}.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def get_categories_summary(kb: KnowledgeBase) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in kb.files:
        cat = f.category or "Geral"
        counts[cat] = counts.get(cat, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def is_readable(mime_type: str) -> bool:
    return mime_type in READABLE_MIME_TYPES
