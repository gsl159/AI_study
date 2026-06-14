# budget_context_builder.py
import logging
from typing import List, Dict
from context_models import ChunkEntityV3, SectionContext, ContextPriority

logger = logging.getLogger("RAG-Budget-Builder")

class BudgetContextBuilder:
    """
    企业级 Budget-Based Context Builder
    核心任务：在固定 Token 预算内，构建最大信息密度的上下文。
    包含：1. 优先级排序 2. 流程时序骨架保护 3. 渐进式动态降级压缩
    """
    def __init__(self, max_context_budget: int = 600):
        self.max_context = max_context_budget # 设置默认较小的预算，以便测试极端的裁剪工况

    def build_context(self, query_intent: str, target_sections: List[SectionContext], recalled_chunks: List[ChunkEntityV3]) -> str:
        logger.info(f"🧱 [Context Builder] 启动预算精算流水线。硬预算上限: {self.max_context} 字符")
        
        remaining_budget = self.max_context
        final_prompt_blocks = []

        # ── 【第一层保护：Section Summary 永不裁剪】 ────────────────────────────
        # 无论是何种意图，章节的大纲语义是绝对的底线，必须先占领宝贵的头部预算空间
        for sec in target_sections:
            summary_block = f"【章节大纲】{sec.title}: {sec.summary}\n"
            block_size = len(summary_block)
            
            if remaining_budget >= block_size:
                final_prompt_blocks.append(summary_block)
                remaining_budget -= block_size
                logger.info(f"🌲 [Summary 保留] 锁定章节大纲 '{sec.title}'，消耗预算: {block_size}")
            else:
                # 极端工况防护：如果连大纲都塞不下了，强行破例保留半行，作为最终防线
                final_prompt_blocks.append(summary_block[:remaining_budget])
                remaining_budget = 0
                logger.warning("🚨 [Budget Crash] 预算极其凶残，大纲触发截断处理！")
                return "".join(final_prompt_blocks)

        # ── 【第二层保护：Procedure 流程问答时序骨架强行注入】 ───────────────────
        # 如果是流程类问答，必须防止步骤中段迷失，先把所有步骤的“短摘要/骨架”无缝拉出来排好队
        if query_intent == "PROCEDURE":
            logger.info("⛓️ [Procedure Protection] 检测到流程问答！启动步骤骨架强行占位机制...")
            skeleton_items = []
            
            # 按物理时序对所有召回的块进行强制排序
            sorted_chunks = sorted(recalled_chunks, key=lambda x: x.order_index)
            
            skeleton_text = "【核心执行步骤完整骨架清单】:\n"
            for chk in sorted_chunks:
                skeleton_text += f"  - 步骤 {chk.order_index + 1}: {chk.short_summary}\n"
            
            skeleton_size = len(skeleton_text)
            if remaining_budget >= skeleton_size:
                final_prompt_blocks.append(skeleton_text)
                remaining_budget -= skeleton_size
                logger.info(f"✅ [骨架锁死] 步骤连续性骨架已经稳固注入，消耗预算: {skeleton_size}")
            else:
                logger.warning("⚠️ [Budget Tight] 预算无空间容纳完整骨架，优先跳过骨架，直接由 Chunk 压缩层承接。")

        # ── 【第三层：叶子 Chunk 渐进式动态降级压缩（核心滑窗漏斗）】 ───────────────
        # 根据 Rerank 分数对 Chunk 进行紧急程度分类
        logger.info(f"⚙️ [Progressive Compression] 启动切片渐进式漏斗决策，剩余可用预算: {remaining_budget}")
        
        # 按照 Rerank 分数由高到低降序重新排列
        reranked_chunks = sorted(recalled_chunks, key=lambda x: x.score, reverse=True)

        for chk in reranked_chunks:
            if remaining_budget <= 0:
                logger.info(f"🛑 [Budget Exhausted] 预算已耗尽，后续 Chunk {chk.id} 被拒绝入场（Drop）。")
                break
                
            # 漏斗状态机决策一：预算充沛，全量无损吞吐
            if remaining_budget >= chk.full_size:
                detail_block = f"【核心证据原文】(相关度 score: {chk.score}): {chk.full_text}\n"
                final_prompt_blocks.append(detail_block)
                remaining_budget -= len(detail_block)
                logger.info(f"   ⚡ [Full Text] 满血保留高价值证据 {chk.id}，消耗预算: {len(detail_block)}")
                
            # 漏斗状态机决策二：预算告急，无情降级为短摘要
            elif remaining_budget >= chk.summary_size:
                summary_block = f"【核心证据降级摘要】(score: {chk.score}): {chk.short_summary}\n"
                final_prompt_blocks.append(summary_block)
                remaining_budget -= len(summary_block)
                logger.info(f"   📉 [Compression] 预算不足！自动将证据 {chk.id} 动态降级压缩为短摘要，消耗: {len(summary_block)}")
                
            # 漏斗状态机决策三：彻底破产，无情抛弃低价值末尾块
            else:
                logger.info(f"   🗑️ [Drop] 预算连摘要都无法容纳，无情切断低相关度块: {chk.id}")
                break

        logger.info(f"🏁 [Context Builder 竣工] 上下文最终拼装完毕。剩余闲置 Token 额度: {remaining_budget}")
        return "".join(final_prompt_blocks)
