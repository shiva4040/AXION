import re
from typing import List, Optional
from pydantic import BaseModel

class ChunkResult(BaseModel):
    chunk_index: int
    page_number: int
    text_content: str
    token_count: int
    structural_header: Optional[str] = None
    is_equation_block: bool = False

class SemanticChunker:
    """
    Heading-aware and equation-preserving semantic chunker.
    Avoids arbitrary mid-sentence cuts and preserves scientific section lineage.
    """
    def __init__(self, target_chunk_tokens: int = 400, overlap_tokens: int = 50):
        self.target_tokens = target_chunk_tokens
        self.overlap_tokens = overlap_tokens
        
        # Regex for structural headings (Markdown or academic numbered headers)
        self.header_pattern = re.compile(
            r"^(?:#{1,4}\s+|(?:\d+\.)+\d*\s+[A-Z]|[A-Z\s]{4,}:?$)",
            re.MULTILINE
        )
        # Regex for mathematical equation environments
        self.equation_pattern = re.compile(r"(\$\$.*?\$\$|\\begin\{equation\}.*?\\end\{equation\})", re.DOTALL)

    def estimate_tokens(self, text: str) -> int:
        """Heuristic token estimator (~0.75 words per token or word count * 1.3)."""
        words = text.split()
        return max(1, int(len(words) * 1.3))

    def chunk_document_pages(
        self,
        pages_content: List[dict] # [{"page_number": int, "text": str}]
    ) -> List[ChunkResult]:
        """
        Chunks text across document pages, tracking source page boundaries and headers.
        """
        chunks: List[ChunkResult] = []
        chunk_idx = 0
        current_header: Optional[str] = None

        for page in pages_content:
            page_no = page["page_number"]
            text = page.get("text", "")
            if not text.strip():
                continue

            # Split page text into candidate blocks (by double newline or header)
            lines = text.split("\n")
            current_block_lines: List[str] = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if current_block_lines:
                        block_text = "\n".join(current_block_lines)
                        token_count = self.estimate_tokens(block_text)
                        
                        # Check if block is primarily an equation
                        is_eq = bool(self.equation_pattern.search(block_text)) or any(
                            sym in block_text for sym in ["=", "\\int", "\\sum", "∂", "∇"]
                        )
                        
                        chunks.append(
                            ChunkResult(
                                chunk_index=chunk_idx,
                                page_number=page_no,
                                text_content=block_text,
                                token_count=token_count,
                                structural_header=current_header,
                                is_equation_block=is_eq
                            )
                        )
                        chunk_idx += 1
                        current_block_lines = []
                    continue

                # Check if line looks like a section header
                if self.header_pattern.match(stripped) and len(stripped) < 80:
                    current_header = stripped
                    # If we had pending lines, flush them before switching header
                    if current_block_lines:
                        block_text = "\n".join(current_block_lines)
                        chunks.append(
                            ChunkResult(
                                chunk_index=chunk_idx,
                                page_number=page_no,
                                text_content=block_text,
                                token_count=self.estimate_tokens(block_text),
                                structural_header=current_header,
                                is_equation_block=False
                            )
                        )
                        chunk_idx += 1
                        current_block_lines = []

                current_block_lines.append(line)

            # Flush remaining lines on page
            if current_block_lines:
                block_text = "\n".join(current_block_lines)
                is_eq = bool(self.equation_pattern.search(block_text))
                chunks.append(
                    ChunkResult(
                        chunk_index=chunk_idx,
                        page_number=page_no,
                        text_content=block_text,
                        token_count=self.estimate_tokens(block_text),
                        structural_header=current_header,
                        is_equation_block=is_eq
                    )
                )
                chunk_idx += 1

        # Consolidate tiny adjacent blocks under identical header if below target tokens
        consolidated = self._consolidate_small_chunks(chunks)
        return consolidated

    def _consolidate_small_chunks(self, chunks: List[ChunkResult]) -> List[ChunkResult]:
        if not chunks:
            return []
        
        result: List[ChunkResult] = []
        current: Optional[ChunkResult] = None
        new_idx = 0

        for c in chunks:
            if current is None:
                current = c
                continue
            
            # Merge if same page, same header, not an equation, and combined tokens < target_tokens
            if (
                current.page_number == c.page_number
                and current.structural_header == c.structural_header
                and not current.is_equation_block
                and not c.is_equation_block
                and (current.token_count + c.token_count) <= self.target_tokens
            ):
                current = ChunkResult(
                    chunk_index=new_idx,
                    page_number=current.page_number,
                    text_content=f"{current.text_content}\n\n{c.text_content}",
                    token_count=current.token_count + c.token_count,
                    structural_header=current.structural_header,
                    is_equation_block=False
                )
            else:
                current.chunk_index = new_idx
                result.append(current)
                new_idx += 1
                current = c

        if current is not None:
            current.chunk_index = new_idx
            result.append(current)

        return result
