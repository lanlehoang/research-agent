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

    def build_chunks(self, article: models.Article) -> Tuple[dict, List[models.ArticleChunk]]:
        """Chunks an article into sections.

        Each chunk's content contains everything from its header down to (but not including)
        the next header at the same level or higher level.

        Args:
            article (str): The article to chunk in markdown format.

        Returns:
            Tuple[dict, List[ArticleChunk]]: Table of contents and list of chunks.
        """
        toc = self._build_table_of_contents(article)

        lines = article.split("\n")
        header_pattern = re.compile(r"^(#{1,6})\s+(\S.*)$")

        # entries item: [chunk_id, name, content, level, parent_id]
        entries = []
        current_lines = []
        current_header = None

        for raw_line in lines:
            stripped = raw_line.strip()
            match = re.match(header_pattern, stripped)
            if match:
                # Finalize the previous chunk
                if current_header is not None:
                    c_id, c_name, c_level, c_parent = current_header
                    content = "\n".join(current_lines).strip()
                    entries.append([c_id, c_name, content, c_level, c_parent])
                    current_lines = []
                level = len(match.group(1))
                name = match.group(2).strip()
                chunk_id = f"chunk_{len(entries)}"
                # Find parent: last header with strictly shallower level
                parent_id = None
                for idx in range(len(entries) - 1, -1, -1):
                    if entries[idx][3] < level:
                        parent_id = entries[idx][0]
                        break
                current_header = (chunk_id, name, level, parent_id)
            else:
                current_lines.append(raw_line)

        # Finalize the last chunk
        if current_header is not None:
            c_id, c_name, c_level, c_parent = current_header
            content = "\n".join(current_lines).strip()
            entries.append([c_id, c_name, content, c_level, c_parent])

        # Build children mapping
        children_map = {e[0]: [] for e in entries}
        for e in entries:
            e_id, e_name, e_content, e_level, e_parent = e
            if e_parent is not None:
                children_map[e_parent].append(e_id)

        # Create ArticleChunk objects (placeholder doc_id/doc_name)
        chunks = []
        for e in entries:
            e_id, e_name, e_content, e_level, e_parent = e
            chunk = models.ArticleChunk(
                doc_id=article.doc_id,
                doc_name=article.doc_name,
                chunk_id=e_id,
                chunk_name=e_name,
                content=e_content,
                parent_id=e_parent,
                children_ids=children_map[e_id] or None,
            )
            chunks.append(chunk)

        return toc, chunks

    def _build_table_of_contents(self, article: str) -> dict:
        """Parse section hierarchy from markdown headers into a nested dict."""
        lines = article.split("\n")
        in_code_block = False
        root = {}
        stack = [(0, root)]  # (header_level, dict_at_that_level)

        header_pattern = re.compile(r"^(#{1,6})\s+(\S.*)$")

        for raw_line in lines:
            line = raw_line.strip()

            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            match = header_pattern.match(line)
            if not match:
                continue

            level = len(match.group(1))
            content = match.group(2).strip()

            # pop back to the nearest ancestor shallower than this header
            while stack[-1][0] >= level:
                stack.pop()

            parent_dict = stack[-1][1]
            parent_dict[content] = {}
            stack.append((level, parent_dict[content]))

        return root
