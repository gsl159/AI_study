# app/evidence/fusion_engine.py
import logging
import math
from typing import Dict, Any

from app.evidence.log_collector import LogCollector
from app.evidence.metrics_collector import MetricsCollector
from app.evidence.trace_collector import TraceCollector
from app.evidence.rag_collector import RagCollector
from app.evidence.weight_engine import WeightStrategyEngine
from app.evidence.ranker import HypothesisRanker
from app.evidence.verification import VerificationPlanner

from production_memory_index import ProductionMemoryIndexBase

logger = logging.getLogger("Enterprise-Evidence-Engine")

class EvidenceFusionEngine:
    def __init__(self, memory_engine: ProductionMemoryIndexBase):
        self.memory_engine = memory_engine
        self.weight_engine = WeightStrategyEngine()
        self.ranker = HypothesisRanker()
        self.planner = VerificationPlanner()

    def adjudicate_fault(self, raw_log: str, metrics_data: Dict[str, float], trace_data: Dict[str, int], topology_features: Dict[str, str], simulated_days_ago: float = 0.0) -> Dict[str, Any]:
        logger.info("⚖️ [L4.4 Engine] 多模态分布式证据层收集启动...")
        log_ev = LogCollector().collect(raw_log)
        metric_ev = MetricsCollector().collect(metrics_data)
        trace_ev = TraceCollector().collect(trace_data)
        rag_ev = RagCollector().collect(raw_log)

        memory_score = 0.0
        has_memory = False
        memory_ctx = {"service_status": topology_features.get("service_status", "unknown"), "port_status": topology_features.get("port_status", "unknown"), "error_log": raw_log}
        
        memory_hit = self.memory_engine.fast_path_lsh_recall(memory_ctx)
        if memory_hit:
            has_memory = True
            similarity = 0.92 
            historical_success_rate = 0.87
            freshness_factor = math.exp(-simulated_days_ago / 90.0)
            memory_score = similarity * historical_success_rate * freshness_factor
            logger.info(f"💾 撞中历史案例 {memory_hit.case_id}。时间衰减因子: {freshness_factor:.4f}")

        dynamic_weights = self.weight_engine.calculate_weights(log_ev, metric_ev, trace_ev, rag_ev, has_mem=has_memory)
        evidences_pack = {"log": log_ev, "metrics": metric_ev, "trace": trace_ev, "rag": rag_ev, "memory_score": memory_score}
        ranked_hypotheses = self.ranker.rank_hypotheses(evidences_pack, dynamic_weights)
        verification_plan = self.planner.generate_plan(ranked_hypotheses)

        return {"weights_applied": dynamic_weights, "hypotheses_ranking": ranked_hypotheses, "verification_plan": verification_plan}
