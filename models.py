# models.py
from pydantic import BaseModel, Field
from typing import List

class TextAnalysisOutput(BaseModel) :
    """单片契约：处理每一个单独 Chunk 的格式，标签放宽为 List[str] 以防止 Pydantic 暴力崩溃"""
    summary: str = Field(description="用一句话高度概括输入文本的核心本质，50字以内。")
    tags: List[str] = Field(description="技术领域标签。如果不符合官方名单，允许返回空列表 []。")
    action_items: List[str] = Field(description="下一步明确可执行的动作项。注意：必须以具体动词开头（如：编写、优化、测试），拒绝虚词。")

class FinalAggregatedOutput(BaseModel):
    """总报告契约：Reducer 节点最终交付给前端的资产格式，恢复点号访问保护"""
    summary: str = Field(description="所有分片摘要的合并组合。")
    tags: List[str] = Field(description="经过代码层严格过滤、匹配并去重后的核心技术标签列表。")
    action_items: List[str] = Field(description="所有分片去重后的完整可执行动作项。")
