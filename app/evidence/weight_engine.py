# app/evidence/weight_engine.py
from typing import List, Dict
from app.evidence.types import VerifiedEvidence

class WeightStrategyEngine:
    """
    Level 5 权重计算器：消费结构化证据池，输出假说修正权重
    """
    def calculate_weights(self, evidence_list: List[VerifiedEvidence]) -> Dict[str, float]:
        """
        统一接口：不再需要显式传入 metrics/trace，直接通过分析 evidence_list 推理权重
        """
        # 1. 初始化权重分
        weights = {
            "INFRA_FS_PERMISSION_DENIED": 0.5,
            "SYSTEM_SELINUX_BLOCKED": 0.3,
            "DISTRIBUTED_RESOURCE_COMPLETION_BLOCKED": 0.2
        }
        
        # 2. 核心：根据证据源头动态调整权重
        for ev in evidence_list:
            if ev.evidence_type == "initial_context":
                # 初始上下文微调权重
                pass
            elif ev.evidence_type == "filesystem_permission":
                # 针对特定证据进行权重补偿
                weights["INFRA_FS_PERMISSION_DENIED"] += 0.2
                
        return weights
