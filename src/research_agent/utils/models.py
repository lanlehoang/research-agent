"""
Define Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class Article(BaseModel):
    """An article."""
    doc_id: str = Field(..., description="The ID of the document.")
    doc_name: str = Field(..., description="The name of the document.")
    content: str = Field(..., description="The content of the document.")
    

class ArticleChunk(BaseModel):
    """A chunk of an article."""
    doc_id: str = Field(..., description="The ID of the document.")
    doc_name: str = Field(..., description="The name of the document.")
    chunk_id: str = Field(..., description="The ID of the chunk.")
    chunk_name: str = Field(..., description="The name of the chunk.")
    content: str = Field(..., description="The content of the chunk.")

