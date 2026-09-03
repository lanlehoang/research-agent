"""
Chunking based on article sections (Abstract, Introduction, Methods, Results, Discussion,...)
"""
from typing import Optional, List, Tuple
import re
import research_agent.utils.models as models


class Chunker:
    """Chunks an article into sections."""

    def __init__(self):
        pass

    def build_chunks(self, article: models.Article) -> Tuple[List[dict], List[models.ArticleChunk]]:
        """Chunks an article into sections.

        Each chunk's content contains everything from its header down to (but not including)
        the next header at the same level or higher level.

        Args:
            article (Article): The article to chunk in markdown format.

        Returns:
            Tuple[List[dict], List[ArticleChunk]]: Table of contents with chunk ids and list of chunks.
        """
        lines = article.content.split("\n")
        header_pattern = re.compile(r"^(#{1,6})\s+(\S.*)$")

        # entries item: [chunk_id, name, content, level]
        entries = []
        current_lines = []
        current_header = None

        for raw_line in lines:
            stripped = raw_line.strip()
            match = re.match(header_pattern, stripped)
            if match:
                # Finalize the previous chunk
                if current_header is not None:
                    c_id, c_name, c_level = current_header
                    content = "\n".join(current_lines).strip()
                    entries.append([c_id, c_name, content, c_level])
                    current_lines = []
                level = len(match.group(1))
                name = match.group(2).strip()
                chunk_id = f"chunk_{len(entries)}"
                current_header = (chunk_id, name, level)
            else:
                current_lines.append(raw_line)

        # Finalize the last chunk
        if current_header is not None:
            c_id, c_name, c_level = current_header
            content = "\n".join(current_lines).strip()
            entries.append([c_id, c_name, content, c_level])

        # Build ToC with chunk ids
        toc = []
        for e in entries:
            e_id, e_name, e_content, e_level = e
            toc.append({
                "chunk_id": e_id,
                "name": e_name,
                "level": e_level,
            })

        # Create ArticleChunk objects
        chunks = []
        for e in entries:
            e_id, e_name, e_content, e_level = e
            chunk = models.ArticleChunk(
                doc_id=article.doc_id,
                doc_name=article.doc_name,
                chunk_id=e_id,
                chunk_name=e_name,
                content=e_content,
            )
            chunks.append(chunk)

        return toc, chunks
