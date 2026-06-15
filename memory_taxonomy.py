# memory_taxonomy.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional

class RootCauseTaxonomy(str, Enum):
    """
    企业级根因标准分类法枚举
    """
    FS_PERMISSION_DENIED = "INFRA_FS_PERMISSION_DENIED"
    PORT_CONFLICT = "INFRA_PORT_CONFLICT"
    OOM_KILLED = "KERNEL_OOM_KILLED"
    UNKNOWN_ERROR = "GENERIC_UNKNOWN_ERROR"

class ProductionCaseMemory(BaseModel):
    """
    工业级案例长期记忆实体卷宗（契约模型）
    """
    case_id: str = Field(..., description="全局唯一案例索引 ID")
    taxonomy_cause: RootCauseTaxonomy = Field(..., description="标准分类法归一化根因")
    raw_fingerprint_data: Dict[str, str] = Field(..., description="包含服务状态、日志等核心特征矩阵")
    standard_fix_cmd: str = Field(..., description="标准可复现、可直接下发的修复指令")
    
    # 辅助持久化资产属性（由索引内核隐式维护，允许为 None）
    simhash_fingerprint: Optional[str] = None

    class Config:
        use_enum_values = True
