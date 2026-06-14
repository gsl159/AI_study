# parser_engine.py
import re
import hashlib
from typing import List
from rag_models import DocumentEntity, SectionEntity, ChunkEntity

class MarkdownSectionParser:
    """
    遵循架构师V1设计：基于Markdown标准语法的确定性物理分层状态机。
    不引入概率模型，追求极致的稳定、极速与零成本。
    """
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # 匹配 Markdown 标题的正则表达式，如: # 标题一, ## 标题二
        self.header_regex = re.compile(r'^(#{1,6})\s+(.*)$')

    def _generate_md5(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _slide_chunking(self, text: str) -> List[str]:
        """确定性的物理滑动窗口切片算法"""
        chunks = []
        if not text.strip():
            return chunks
        
        # 为演示简化，此处采用字符切片。生产环境可替换为 tiktoken 编码切片
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start += (self.chunk_size - self.overlap)
        return chunks

    def parse_to_entity(self, doc_title: str, raw_markdown: str, metadata: dict = None) -> DocumentEntity:
        doc_id = self._generate_md5(doc_title + str(metadata or {}))
        lines = raw_markdown.split('\n')
        
        sections: List[SectionEntity] = []
        
        # 兜底配置：防范一上来没有任何标题的文档，为其设立虚拟的 0号根 Section
        current_section_title = "README / Overview"
        current_section_level = 1
        current_section_lines = []
        section_idx = 0

        def close_current_section():
            nonlocal section_idx
            section_content = "\n".join(current_section_lines).strip()
            if section_content or current_section_title != "README / Overview":
                sec_id = f"{doc_id}-S{section_idx}"
                section_entity = SectionEntity(
                    id=sec_id,
                    title=current_section_title,
                    level=current_section_level,
                    raw_content=section_content
                )
                
                # 在 Section 内部生成 Chunk，并建立确定性的指针绑定
                raw_chunks = self._slide_chunking(section_content)
                for c_idx, chunk_text in enumerate(raw_chunks):
                    chunk_entity = ChunkEntity(
                        id=f"{sec_id}-C{c_idx}",
                        content=chunk_text,
                        chunk_index=c_idx
                    )
                    section_entity.chunks.append(chunk_entity)
                
                sections.append(section_entity)
                section_idx += 1

        # ── 状态机核心流转循环 ────────────────────────────────────────────────
        for line in lines:
            match = self.header_regex.match(line)
            if match:
                # 撞墙检查：遇到新的标题，立刻封装并结算上一个 Section 资产
                close_current_section()
                
                # 状态变量更新
                current_section_level = len(match.group(1)) # 算出 # 的数量
                current_section_title = match.group(2).strip()
                current_section_lines = [line] # 新 Section 的开头保留当前标题行
            else:
                current_section_lines.append(line)
                
        # 循环结束，利索地结算最后一个 Section 资产
        close_current_section()
        
        return DocumentEntity(id=doc_id, title=doc_title, metadata=metadata or {}, sections=sections)
