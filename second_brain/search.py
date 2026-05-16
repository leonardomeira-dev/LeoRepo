"""Full-text search over the knowledge base."""

import re
from .models import DriveFile, SearchResult, KnowledgeBase


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _score(query_tokens: list[str], file: DriveFile) -> float:
    """Score a file against query tokens."""
    score = 0.0
    searchable = _normalize(" ".join(filter(None, [
        file.title,
        file.content_snippet,
        file.summary,
        file.category,
        file.full_content[:2000] if file.full_content else "",
    ])))

    for token in query_tokens:
        count = searchable.count(token)
        if count > 0:
            # Title matches worth more
            title_count = _normalize(file.title).count(token)
            score += title_count * 3.0 + (count - title_count) * 1.0

    return score


def _find_snippet(query_tokens: list[str], file: DriveFile) -> str | None:
    """Find the best matching snippet from file content."""
    sources = [file.content_snippet, file.summary]
    if file.full_content:
        sources.append(file.full_content[:3000])

    for source in sources:
        if not source:
            continue
        lower = source.lower()
        for token in query_tokens:
            idx = lower.find(token)
            if idx >= 0:
                start = max(0, idx - 80)
                end = min(len(source), idx + 200)
                snippet = source[start:end].strip()
                if start > 0:
                    snippet = "…" + snippet
                if end < len(source):
                    snippet = snippet + "…"
                return snippet
    return None


def search(kb: KnowledgeBase, query: str, top_k: int = 10) -> list[SearchResult]:
    """Search the knowledge base for files matching the query."""
    if not query.strip():
        return []

    query_tokens = _normalize(query).split()
    scored: list[tuple[float, DriveFile]] = []

    for file in kb.files:
        score = _score(query_tokens, file)
        if score > 0:
            scored.append((score, file))

    scored.sort(key=lambda x: -x[0])

    results = []
    for score, file in scored[:top_k]:
        results.append(SearchResult(
            file=file,
            relevance_score=score,
            matched_snippet=_find_snippet(query_tokens, file),
        ))
    return results


def filter_by_category(kb: KnowledgeBase, category: str) -> list[DriveFile]:
    """Return all files in a given category."""
    return [f for f in kb.files if f.category == category]


def get_readable_files(kb: KnowledgeBase) -> list[DriveFile]:
    """Return files that can be read/indexed."""
    from .knowledge_base import is_readable
    return [f for f in kb.files if is_readable(f.mime_type)]
