# storage_engine.py
import re
import hashlib
from typing import List, Dict
from rag_models import DocumentEntity, SectionEntity, ChunkEntity

class EnterpriseKnowledgeStore:
    """
    企业级元数据与倒排索引存储引擎
    遵循架构师设计：解耦存储，建立三级高并发内存索引
    """
    def __init__(self, chunk_size: int = 150, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.header_regex = re.compile(r'^(#{1,6})\s+(.*)$')
        
        # ── 💡 你的核心设计：三大核心硬核索引表 ─────────────────────────────
        self.section_index: Dict[str, SectionEntity] = {}       # id -> Section实体
        self.section_chunk_index: Dict[str, List[str]] = {}    # section_id -> [chunk_ids]
        self.chunk_index: Dict[str, ChunkEntity] = {}           # chunk_id -> Chunk实体
        # ───────────────────────────────────────────────────────────────
        
        self.document_store: Dict[str, DocumentEntity] = {}

    def _generate_md5(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _slide_chunking(self, text: str) -> List[str]:
        chunks = []
        if not text.strip(): return chunks
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            if end >= len(text): break
            start += (self.chunk_size - self.overlap)
        return chunks

    def add_document(self, doc_title: str, raw_markdown: str, metadata: dict = None) -> str:
        """数据摄入管线：解析并自动挂载三级索引"""
        doc_id = self._generate_md5(doc_title + str(metadata or {}))
        lines = raw_markdown.split('\n')
        
        doc_section_ids = []
        current_section_title = "README / Overview"
        current_section_level = 1
        current_section_lines = []
        sec_counter = 0

        def close_section():
            nonlocal sec_counter
            content = "\n".join(current_section_lines).strip()
            if content or current_section_title != "README / Overview":
                sec_id = f"{doc_id}-S{sec_counter}"
                doc_section_ids.append(sec_id)
                
                # 1. 创建并固化 Section 实体
                sec_entity = SectionEntity(
                    id=sec_id, doc_id=doc_id, title=current_section_title,
                    level=current_section_level, raw_content=content
                )
                
                # 2. 切片并建立二级与三级索引
                raw_chunks = self._slide_chunking(content)
                current_chunk_ids = []
                
                for c_idx, chunk_text in enumerate(raw_chunks):
                    chunk_id = f"{sec_id}-C{c_idx}"
                    current_chunk_ids.append(chunk_id)
                    
                    # 固化最底层 Chunk 实体
                    chunk_entity = ChunkEntity(
                        id=chunk_id, section_id=sec_id, order_index=c_idx, content=chunk_text
                    )
                    # 挂载三级索引
                    self.chunk_index[chunk_id] = chunk_entity
                
                # 建立 Section 的内部 ID 引用，并挂载一二级索引
                sec_entity.chunk_ids = current_chunk_ids
                self.section_index[sec_id] = sec_entity
                self.section_chunk_index[sec_id] = current_chunk_ids
                
                sec_counter += 1

        for line in lines:
            match = self.header_regex.match(line)
            if match:
                close_section()
                current_section_level = len(match.group(1))
                current_section_title = match.group(2).strip()
                current_section_lines = [line]
            else:
                current_section_lines.append(line)
        close_section()

        # 固化根节点
        self.document_store[doc_id] = DocumentEntity(
            id=doc_id, title=doc_title, metadata=metadata or {}, section_ids=doc_section_ids
        )
        return doc_id