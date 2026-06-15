# memory_models.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RootCauseType(str, Enum):
    """⚔️ 强类型根因分类法：消灭模糊的字符串模糊统计"""
    PERMISSION_DENIED = "PERMISSION_DENIED"
    PORT_OCCUPIED     = "PORT_OCCUPIED"
    DISK_FULL         = "DISK_FULL"
    CONFIG_ERROR      = "CONFIG_ERROR"
    NETWORK_ERROR     = "NETWORK_ERROR"
    UNKNOWN_INCIDENT  = "UNKNOWN_INCIDENT"

class HypothesisStep(BaseModel):
    """🧠 高保真诊断步骤快照：记录智能体思考的因果演变路径"""
    hypothesis: str = Field(description="推测的假设成因，例如: 'permission issue'")
    tool: str = Field(description="为此发起的验证工具")
    result: str = Field(description="工具返回的物理铁证摘要或状态")
    confidence: float = Field(description="该步骤执行后的置信度得分")

class CaseMemory(BaseModel):
    """Episodic Memory 完全体：单次故障的结构化病理档案"""
    case_id: str = Field(description="全局唯一案例编号")
    symptoms: List[str] = Field(description="宏观临床现象")
    evidence_fingerprint: Dict[str, str] = Field(description="经过清洗规整后的『键值对现场铁证指纹』")
    hypothesis_chain: List[HypothesisStep] = Field(default_factory=list, description="完整的因果推导链")
    root_cause_type: RootCauseType = Field(description="归一化后的强类型标准根因")
    fix_action: str = Field(description="验证成功的修复指令")
    diagnostic_time_ms: float = Field(default=0.0)

class SemanticProfile(BaseModel):
    """Semantic Memory：基于强类型根因的标准概率分布空间"""
    cause_probability_distribution: Dict[RootCauseType, float] = Field(
        default_factory=lambda: {rc: 0.0 for rc in RootCauseType},
        description="基于 Enum 的精准根因概率分布"
    )
    total_samples: int = Field(default=0)

class StrategyMetrics(BaseModel):
    """
    🟢 完璧归赵：Strategy Memory（策略记忆实体）
    用于统计各个排障工具锁定根因的物理效率
    """
    tool_success_rates: Dict[str, Dict[str, int]] = Field(
        default_factory=lambda: {
            "verify_mysql_dir_permission": {"success": 0, "total": 0},
            "check_port": {"success": 0, "total": 0},
            "check_service": {"success": 0, "total": 0}
        },
        description="工具胜率底表"
    )
