"""Drive sync script - indexes content from Google Drive files into the knowledge base."""

import json
import sys
from pathlib import Path
from typing import Callable

DATA_DIR = Path(__file__).parent.parent / "data"
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


def merge_index_pages() -> list[dict]:
    """Merge all drive_index_page*.json files into a single combined index."""
    import glob
    all_files = []
    seen: set[str] = set()

    page_files = sorted(glob.glob(str(DATA_DIR / "drive_index*.json")))
    for page_file in page_files:
        if "combined" in page_file:
            continue
        with open(page_file) as f:
            files = json.load(f)
        for item in files:
            item_id = item.get("id")
            if item_id and item_id not in seen:
                seen.add(item_id)
                all_files.append(item)

    with open(DATA_DIR / "drive_index_combined.json", "w", encoding="utf-8") as f:
        json.dump(all_files, f, ensure_ascii=False, indent=2)

    return all_files


def get_unindexed_readable_files(files: list[dict]) -> list[dict]:
    """Return files that are readable but not yet indexed."""
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    return [
        f for f in files
        if f.get("mimeType") in READABLE_MIME_TYPES
        and not (FILES_DIR / f"{f['id']}.json").exists()
    ]


def store_content(file_id: str, title: str, content: str, summary: str | None = None) -> None:
    """Store file content locally."""
    import time
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "file_id": file_id,
        "full_content": content[:50000],
        "summary": summary,
        "indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(FILES_DIR / f"{file_id}.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def print_sync_instructions():
    """Print instructions for syncing new content from Google Drive via Claude Code."""
    print("""
=== COMO SINCRONIZAR NOVOS ARQUIVOS DO GOOGLE DRIVE ===

Este Second Brain usa o MCP do Google Drive via Claude Code para ler arquivos.
Para indexar novos arquivos ou atualizar o conteúdo:

1. Abra uma sessão no Claude Code com o MCP do Google Drive configurado
2. Execute o comando: python main.py build
3. Para indexar conteúdo de um arquivo específico, peça ao Claude:
   "Leia o arquivo [nome] do meu Google Drive e armazene no Second Brain"

O Claude Code pode:
- Listar arquivos: mcp__gdrive__list_recent_files
- Buscar arquivos: mcp__gdrive__search_files
- Ler conteúdo: mcp__gdrive__read_file_content

Após ler o conteúdo, salve em: data/files/<file_id>.json
""")


if __name__ == "__main__":
    print("Merging index pages...")
    files = merge_index_pages()
    readable = [f for f in files if f.get("mimeType") in READABLE_MIME_TYPES]
    indexed = [f for f in files if (FILES_DIR / f"{f['id']}.json").exists()]
    unindexed = get_unindexed_readable_files(files)

    print(f"Total files: {len(files)}")
    print(f"Readable files: {len(readable)}")
    print(f"Already indexed: {len(indexed)}")
    print(f"Pending indexing: {len(unindexed)}")
    print()

    if unindexed:
        print("Files pending indexing:")
        for f in unindexed[:20]:
            print(f"  - {f.get('title', 'Unknown')} ({f.get('mimeType', '')})")
        if len(unindexed) > 20:
            print(f"  ... and {len(unindexed) - 20} more")
