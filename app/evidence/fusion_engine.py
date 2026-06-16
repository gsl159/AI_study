# app/evidence/fusion_engine.py
import logging
from typing import Dict, Any, List
from app.evidence.types import VerifiedEvidence, Hypothesis, EvidencePool, EvidenceSource
from app.evidence.ranker import HypothesisRanker
from app.evidence.weight_engine import WeightStrategyEngine

logger = logging.getLogger("Enterprise-Evidence-Engine")

class EvidenceFusionEngine:
    """
    Level 5 核心中枢：证据驱动的自主诊断系统
    """
    def __init__(self):
        self.evidence_pool = EvidencePool()
        self.ranker = HypothesisRanker()
        self.weight_engine = WeightStrategyEngine()

    def adjudicate_fault(self, initial_data: Dict[str, Any]) -> List[Hypothesis]:
        """【初始态】将原始输入封装为结构化证据并启动推理"""
        initial_ev = VerifiedEvidence(
            evidence_type="initial_context",
            source=EvidenceSource.SYSTEM_BOOTSTRAP,
            value=initial_data,
            confidence=0.5
        )
        self.evidence_pool.add(initial_ev)
        return self._run_inference()

    def re_adjudicate(self, new_evidence: VerifiedEvidence) -> List[Hypothesis]:
        """【闭环态】接收探针反馈的结构化证据，触发认知重排"""
        logger.info(f"🔄 [Re-Ranking] 接收证据反馈: {new_evidence.evidence_type} (Source: {new_evidence.source.value})")
        self.evidence_pool.add(new_evidence)
        return self._run_inference()

    def _run_inference(self) -> List[Hypothesis]:
        """内部推理引擎：确保初始计算与重排的逻辑同源"""
        # 消费证据池中的所有结构化数据进行综合权重判断
        dynamic_weights = self.weight_engine.calculate_weights(self.evidence_pool.get_all())
        
        # 产生基于当前证据池的新排名
        return self.ranker.rank_hypotheses(self.evidence_pool.get_all(), dynamic_weights)
