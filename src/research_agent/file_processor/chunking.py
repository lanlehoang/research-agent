"""
Chunking based on article sections (Abstract, Introduction, Methods, Results, Discussion,...)
"""
from pydantic import BaseModel, Field
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from typing import Optional, List

MARKDOWN_HEADERS = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
    ("#####", "Header 5"),
    ("######", "Header 6"),
]


class ArticleChunk(BaseModel):
    """A chunk of an article."""
    doc_id: str = Field(..., description="The ID of the document.")
    doc_name: str = Field(..., description="The name of the document.")
    chunk_id: str = Field(..., description="The ID of the chunk.")
    chunk_name: str = Field(..., description="The name of the chunk.")
    content: str = Field(..., description="The content of the chunk.")
    parent_id: Optional[str] = Field(None, description="The ID of the parent chunk.")
    chilren_ids: Optional[List[str]] = Field(None, description="The IDs of the children chunks.")
