# app/evidence/types.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

class EvidenceSource(Enum):
    """证据的物理来源标识"""
    SYSTEM_BOOTSTRAP = "system_bootstrap"
    LOG_COLLECTOR = "log_collector"
    METRICS_COLLECTOR = "metrics_collector"
    TRACE_COLLECTOR = "trace_collector"
    RAG_COLLECTOR = "rag_collector"
    PROBE_EXECUTION = "probe_execution"  # 关键：识别来自执行器的回灌证据
    MEMORY_INDEX = "memory_index"

@dataclass
class VerifiedEvidence:
    """
    生产级结构化证据模型
    所有传入 FusionEngine 的数据都必须封装为此对象
    """
    evidence_type: str        # e.g., "filesystem_permission", "service_status"
    source: EvidenceSource    # 来源枚举，方便溯源
    value: Dict[str, Any]     # 物理执行的结果 (e.g., {"owner": "root", "permission": "755"})
    confidence: float         # 该证据的置信度 (0.0 - 1.0)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Hypothesis:
    """
    诊断假说模型
    """
    cause: str                # 假说名称
    score: float              # 当前概率得分
    metadata: Dict[str, Any] = field(default_factory=dict) # 假说相关的上下文

@dataclass
class EvidencePool:
    """
    证据池：负责维护推理循环中的所有证据状态
    """
    evidences: List[VerifiedEvidence] = field(default_factory=list)

    def add(self, evidence: VerifiedEvidence):
        self.evidences.append(evidence)

    def get_all(self) -> List[VerifiedEvidence]:
        return self.evidences

    def get_by_source(self, source: EvidenceSource) -> List[VerifiedEvidence]:
        return [e for e in self.evidences if e.source == source]

# 为了兼容性，保留给其他模块使用的通用返回契约
@dataclass
class ProbeResult:
    stdout: str
    exit_code: int
    tool_confidence: float = 0.95
    latency_ms: int = 0
