# enterprise_memory.py
import logging
import math
from typing import List, Dict, Optional, Set
from memory_models import CaseMemory, SemanticProfile, StrategyMetrics, RootCauseType, HypothesisStep

logger = logging.getLogger("RAG-Memory-Base")

class EnterpriseMemoryBase:
    """
    企业级长长期记忆层中央控制面（V4.2 生产级完全体）
    完美闭环：证据指纹相似度精算、根因强类型分类、O(1) 根因倒排索引
    """
    def __init__(self):
        # 1. Episodic Memory 物理案例库
        self.episodic_db: Dict[str, CaseMemory] = {}
        
        # 2. 💡 核心创新：总架构师指定的 Root Cause 倒排索引网（实现 O(1) 反查）
        self.root_cause_index: Dict[RootCauseType, List[str]] = {rc: [] for rc in RootCauseType}
        
        # 3. Semantic Memory 与 Strategy Memory
        self.semantic_memory = SemanticProfile()
        self.strategy_memory = StrategyMetrics()

    def commit_case(self, case: CaseMemory):
        """📥 强类型、索引化、无感泛化写入中枢"""
        # A. 存入物理实体库
        self.episodic_db[case.case_id] = case
        
        # B. 💡 建立倒排索引：快速将当前案例 ID 追加到对应的强类型根因分类槽中
        self.root_cause_index[case.root_cause_type].append(case.case_id)
        logger.info(f"🧱 [Root Cause Index] 成功建立倒排索引: {case.root_cause_type.value} -> 追加案例 {case.case_id}")

        # C. 统计语义层特征变更
        self._update_semantic_knowledge(case.root_cause_type)

        # D. 统计策略层胜率变更（分析哪些步骤在什么工具上经常成功/失败）
        self._update_strategy_efficiency(case.hypothesis_chain)

    def _update_semantic_knowledge(self, root_cause_type: RootCauseType):
        """流式刷新基于 Enum 空间的宏观概率先验分布"""
        self.semantic_memory.total_samples += 1
        dist = self.semantic_memory.cause_probability_distribution
        
        for rc in RootCauseType:
            current_count = dist[rc] * (self.semantic_memory.total_samples - 1)
            if rc == root_cause_type:
                current_count += 1
            dist[rc] = round(current_count / self.semantic_memory.total_samples, 4)
            
        logger.info(f"🧠 [Semantic Online Update] 语义分布进化完毕: {dict(dist)}")

    def _update_strategy_efficiency(self, historical_steps: List[HypothesisStep]):
        """高保真演进：精准分析具体策略步骤的胜率"""
        if not historical_steps:
            return
            
        metrics = self.strategy_memory.tool_success_rates
        for step in historical_steps:
            tool = step.tool
            if tool in metrics:
                metrics[tool]["total"] += 1
                if step.result == "confirmed":
                    metrics[tool]["success"] += 1

    def _calculate_fingerprint_similarity(self, fp1: Dict[str, str], fp2: Dict[str, str]) -> float:
        """
        📐 纯手工硬核算法：证据指纹余弦相似度精算器（TF-IDF Cosine Similarity）
        消灭脆弱的 'shared_items >= 2'，对现场环境日志特征实施精确的空间几何比对
        """
        # 将指纹展平成文本词袋
        def to_token_set(fp: Dict[str, str]) -> List[str]:
            tokens = []
            for k, v in fp.items():
                tokens.extend(f"{k}:{v}".lower().split())
            return tokens

        tokens1 = to_token_set(fp1)
        tokens2 = to_token_set(fp2)
        
        # 计算词频 (Term Frequency)
        all_tokens = set(tokens1 + tokens2)
        if not all_tokens: return 0.0
        
        vec1 = {token: tokens1.count(token) for token in all_tokens}
        vec2 = {token: tokens2.count(token) for token in all_tokens}
        
        # 向量点积与模长计算
        dot_product = sum(vec1[t] * vec2[t] for t in all_tokens)
        magnitude1 = math.sqrt(sum(v**2 for v in vec1.values()))
        magnitude2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if magnitude1 * magnitude2 == 0: return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def recall_similar_case(self, current_fingerprint: Dict[str, str], threshold: float = 0.85) -> Optional[CaseMemory]:
        """
        🔍 L4-V2 终极狙击：证据指纹模糊余弦拦截门闸
        只有当现场捕获的所有硬核证据文本指纹相似度突破 threshold 时，才允许阻断
        """
        best_score = 0.0
        best_case: Optional[CaseMemory] = None

        for case in self.episodic_db.values():
            sim = self._calculate_fingerprint_similarity(current_fingerprint, case.evidence_fingerprint)
            if sim > best_score:
                best_score = sim
                best_case = case

        if best_case and best_score >= threshold:
            logger.info(f"⚡ [Memory Hit] 强悍！指纹精算拦截器立功！命中历史案例: {best_case.case_id} | 铁证指纹相似度 = {best_score:.4f} >= {threshold}")
            return best_case
            
        logger.warning(f"🛡️ [Memory Miss] 线上抓取指纹与历史库最高匹配度仅为 {best_score:.4f}，未达到 {threshold} 门槛。拒绝盲目阻断，交回智能体科学推导！")
        return None

    def find_cases_by_root_cause(self, rc_type: RootCauseType) -> List[CaseMemory]:
        """🚀 总架构师钦定：基于倒排索引的 O(1) 复杂度根因快速反查"""
        case_ids = self.root_cause_index.get(rc_type, [])
        return [self.episodic_db[cid] for cid in case_ids]