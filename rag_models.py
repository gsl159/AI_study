# rag_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ChunkEntity(BaseModel):
    """底层存储单元：解耦的外键结构"""
    id: str = Field(description="全局唯一物理指纹")
    section_id: str = Field(description="所属章节的外键ID")
    order_index: int = Field(description="在当前章节内部的绝对物理顺序索引，防止并发乱序")
    content: str = Field(description="500字左右的物理切片内容")

class SectionEntity(BaseModel):
    """核心知识表达单元：放弃内嵌Chunk对象，只存物理ID引用"""
    id: str = Field(description="章节唯一标识")
    doc_id: str = Field(description="所属文档的外键ID")
    title: str = Field(description="章节标题")
    level: int = Field(description="标题层级")
    raw_content: str = Field(description="该章节下的完整原始文本")
    chunk_ids: List[str] = Field(default_factory=list, description="管辖的叶子切片ID列表（按顺序排列）")

class DocumentEntity(BaseModel):
    """最高层级文档实体"""
    id: str = Field(description="文档唯一指纹")
    title: str = Field(description="文档总标题")
    metadata: dict = Field(default_factory=dict, description="企业级元数据")
    section_ids: List[str] = Field(default_factory=list, description="包含的章节ID列表")
