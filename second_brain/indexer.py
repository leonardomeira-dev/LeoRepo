"""Indexer - reads file content from Google Drive and stores it locally."""

import json
import time
from pathlib import Path
from typing import Callable

from .models import DriveFile, KnowledgeBase
from .knowledge_base import save_file_content, is_readable, FILES_DIR


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


def is_already_indexed(file_id: str) -> bool:
    return (FILES_DIR / f"{file_id}.json").exists()


def store_file_content(file_id: str, content: str, summary: str | None = None) -> None:
    """Store file content without generating a summary (summary can be added later)."""
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "file_id": file_id,
        "full_content": content,
        "summary": summary,
        "indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(FILES_DIR / f"{file_id}.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def index_file_content(
    file: DriveFile,
    content: str,
    generate_summary: Callable[[str, str], str] | None = None,
) -> None:
    """Store file content and optionally generate a summary."""
    summary = None
    if generate_summary and content:
        try:
            summary = generate_summary(content, file.title)
        except Exception:
            pass
    store_file_content(file.id, content, summary)


def get_unindexed_files(kb: KnowledgeBase) -> list[DriveFile]:
    """Return files that are readable but not yet indexed."""
    return [
        f for f in kb.files
        if is_readable(f.mime_type) and not is_already_indexed(f.id)
    ]


def get_indexed_count(kb: KnowledgeBase) -> int:
    """Count how many readable files have been indexed."""
    return sum(
        1 for f in kb.files
        if is_readable(f.mime_type) and is_already_indexed(f.id)
    )
