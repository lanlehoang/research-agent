"""
Chunking based on article sections (Abstract, Introduction, Methods, Results, Discussion,...)
"""
from typing import List, Tuple
import re
import uuid
import research_agent.utils.models as models


class Chunker:
    """Chunks an article into sections."""

    def __init__(self):
        pass

    def build_chunks(self, article: models.Article) -> Tuple[models.TocSection, List[models.ArticleChunk]]:
        """Chunks an article into sections.

        Hierarchy rules:
          - Parent chunks capture EVERYTHING beneath them (direct content + all
            descendant headers and content) until the next header at same level
            or higher.
          - Names are prefixed: "Parent > Child > Grandchild".
          - Ids are assigned immediately at parse time (depth-first, stable).

        Args:
            article (Article): The article to chunk in markdown format.

        Returns:
            Tuple[TocSection, List[ArticleChunk]]: Root ToC and list of chunks.
        """
        lines = article.content.split("\n")
        header_pattern = re.compile(r"^(#{1,6})\s+(\S.*)$")

        # Phase 1: tag each line with header info
        tagged = []
        for raw_line in lines:
            stripped = raw_line.strip()
            match = re.match(header_pattern, stripped)
            if match:
                level = len(match.group(1))
                name = match.group(2).strip()
                c_id = uuid.uuid4().hex[:16]
                tagged.append((level, name, c_id))
            else:
                tagged.append((0, None, ""))

        n = len(tagged)
        header_indices = [i for i, (lvl, _, _) in enumerate(tagged) if lvl > 0]

        # Phase 2: content boundaries
        content_end = {}
        for pos, idx in enumerate(header_indices):
            my_level = tagged[idx][0]
            end = n
            for j in range(pos + 1, len(header_indices)):
                nxt = header_indices[j]
                if tagged[nxt][0] <= my_level:
                    end = nxt
                    break
            content_end[idx] = end

        # Phase 3: assign content lines to each header
        header_lines = {idx: [] for idx in header_indices}
        for line_no in range(n):
            lvl, _, _ = tagged[line_no]
            if lvl > 0:
                continue
            best = max((i for i in header_indices if i < line_no), default=None)
            if best is not None and line_no < content_end[best]:
                header_lines[best].append(lines[line_no])

        # Phase 4: build prefixed names and TocSection tree
        # First pass: collect level/name/id for each header
        headers = []
        for idx in header_indices:
            level = tagged[idx][0]
            name = tagged[idx][1]
            c_id = tagged[idx][2]
            headers.append({"idx": idx, "level": level, "name": name, "id": c_id})

        # Build prefixed names
        name_prefix = {}
        stack = []
        for h in headers:
            while stack and stack[-1]["level"] >= h["level"]:
                stack.pop()
            if stack:
                prefix = stack[-1]["prefix"] + " > " + h["name"]
            else:
                prefix = h["name"]
            h["prefix"] = prefix
            stack.append(h)
            name_prefix[h["idx"]] = prefix

        # Build TocSection tree (depth-first, parent captures children)
        root_sections = []
        stack = []
        for h in headers:
            section = models.TocSection(section_id=h["id"], subsections=[])
            h["section"] = section
            while stack and stack[-1]["level"] >= h["level"]:
                stack.pop()
            if stack:
                stack[-1]["section"].subsections.append(section)
            else:
                root_sections.append(section)
            stack.append(h)

        toc_root = models.TocSection(section_id="root", subsections=root_sections)

        # Phase 5: build chunks
        chunks = []
        for h in headers:
            idx = h["idx"]
            body = "\n".join(header_lines[idx]).strip()
            chunk = models.ArticleChunk(
                doc_id=article.doc_id,
                chunk_id=h["id"],
                chunk_name=name_prefix[idx],
                content=body,
            )
            chunks.append(chunk)

        return toc_root, chunks
