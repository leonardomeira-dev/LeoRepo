"""Data models for the Second Brain knowledge base."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DriveFile(BaseModel):
    id: str
    title: str
    mime_type: str
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    file_size: Optional[int] = None
    view_url: Optional[str] = None
    content_snippet: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    full_content: Optional[str] = None
    indexed_at: Optional[str] = None


class KnowledgeBase(BaseModel):
    version: str = "1.0"
    last_synced: Optional[str] = None
    total_files: int = 0
    files: list[DriveFile] = Field(default_factory=list)


class SearchResult(BaseModel):
    file: DriveFile
    relevance_score: float
    matched_snippet: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ConversationHistory(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)
