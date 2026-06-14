from pydantic import BaseModel, Field
from typing import List, Literal

# 1. 锁死标签的范围：大模型只能在这四个里选，选别的直接拦截报错
TagType = Literal["LLM", "Agent", "RAG", "LangChain", "LangGraph", "MCP", "Prompt工程", "模型部署", "推理优化", "AI工程化", "多模态", "向量数据库", "知识图谱", "数据处理", "论文解读", "框架更新", "最佳实践", "性能优化"]

class TextAnalysisOutput(BaseModel):
    """Level 0 核心输出契约：大模型必须严格按照这个 JSON 结构返回"""
    
    summary: str = Field(
        description="用一句话高度概括输入文本的核心本质，字数控制在50字以内。"
    )
    
    tags: List[TagType] = Field(
        description="从给定的标签列表中选择1-2个最符合文本属性的标签。"
    )
    
    action_items: List[str] = Field(
        description="基于文本内容提炼出的下一步明确可执行的动作项。注意：必须以具体动词开头（如：编写、优化、测试、重构），拒绝虚假空洞的词汇。"
    )


class FinalAggregatedOutput(BaseModel):
    """总报告契约：Reducre 节点最终交付给前端的资产格式，锁死边界"""
    summary: str = Field(description="所有分片摘要的合并组合。")
    tags: List[TagType] = Field(description="所有分片去重后的完整标签列表。")
    action_items: List[str] = Field(description="所有分片去重后的完整待办事项列表。")