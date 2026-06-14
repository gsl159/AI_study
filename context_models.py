# context_models.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class ContextPriority(Enum):
    SECTION_SUMMARY = 100
    HIGH_RELEVANCE_CHUNK = 90
    MEDIUM_RELEVANCE_CHUNK = 60
    LOW_RELEVANCE_CHUNK = 30

class ChunkEntityV3(BaseModel):
    id: str
    section_id: str
    order_index: int
    full_text: str = Field(description="500字左右的物理切片完整内容")
    short_summary: str = Field(description="80字左右的物理切片极致精炼摘要")
    score: float = Field(default=0.0, description="Rerank 重新打分后的语义相关性分数")
    
    # 模拟快速计算 Token 长度（生产环境可换为 tiktoken len()）
    @property
    def full_size(self) -> int:
        return len(self.full_text)
    
    @property
    def summary_size(self) -> int:
        return len(self.short_summary)

class SectionContext(BaseModel):
    id: str
    title: str
    summary: str = Field(description="当前章节 100 字左右的全局语义大纲（核心硬通货）")
    chunk_ids: List[str] = Field(default_factory=list)
