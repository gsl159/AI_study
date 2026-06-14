# agent_models.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AgentState(Enum):
    """硬核企业级 Agent 状态机：每一步都有明确的退出条件"""
    INIT = "INIT"                               # 初始化，解析问题
    GENERATE_HYPOTHESIS = "GENERATE_HYPOTHESIS" # 提出排障假设
    COLLECT_EVIDENCE = "COLLECT_EVIDENCE"       # 调用工具/RAG 搜集证据
    VERIFY_HYPOTHESIS = "VERIFY_HYPOTHESIS"     # 验证假设是否成立
    REPLAN_REFLECT = "REPLAN_REFLECT"           # 假设失败，触发反思与重规划
    SUCCESS = "SUCCESS"                         # 锁定根因，成功收敛
    FAILED = "FAILED"                           # 尝试所有路径，宣告无能为力

class Hypothesis(BaseModel):
    """Agent 内部生成的排障假设实体"""
    id: str
    description: str = Field(description="假设的原因，例如：'3306端口被占用'")
    target_tool: str = Field(description="验证该假设需要动用的工具或知识库查询")
    verified: Optional[bool] = Field(default=None, description="验证结果：True 成立, False 排除")
    reasoning: Optional[str] = Field(default=None, description="反思或证明的证据结论")

class ExecutionPlan(BaseModel):
    """Planner 生成的排障计划书"""
    current_hypothesis_index: int = 0
    hypotheses: List[Hypothesis] = Field(default_factory=list)
