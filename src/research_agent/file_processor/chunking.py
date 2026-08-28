"""
Chunking based on article sections (Abstract, Introduction, Methods, Results, Discussion,...)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
import re

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


class Chunker:
    """Chunks an article into sections."""

    def __init__(self):
        pass

    def chunk(self, article: str) -> List[ArticleChunk]:
        """Chunks an article into sections.

        Args:
            article (str): The article to chunk in markdown format.

        Returns:
            List[ArticleChunk]: A list of chunks.
        """
        pass

    def build_table_of_contents(self, article: str):
        """
        Parse section hierarchy from markdown headers
        Ignore code comments and other non-header #
        """
        # Split the article into lines
        lines = article.split("\n")

        CODE_BLOCK_BOUNDARY = "```"
        is_in_code_block = False