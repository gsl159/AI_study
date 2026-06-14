# reducer.py
from typing import List, Set
from models import TextAnalysisOutput, FinalAggregatedOutput

def aggregate_and_deduplicate(chunk_outputs: List[TextAnalysisOutput], allowed_tags: Set[str]) -> FinalAggregatedOutput:
    """
    工业级一致性 Reducer：遵循领域强耦合原则，标签为0时无情熔断待办事项
    """
    final_tags = set()
    final_actions = set()
    summaries = []
    
    for output in chunk_outputs:
        if output.summary == "当前分片解析失败":
            continue
            
        # 1. 先用代码闸门严格过滤单片的标签
        valid_chunk_tags = set()
        for tag in output.tags:
            cleaned_tag = tag.strip()
            if cleaned_tag in allowed_tags:
                valid_chunk_tags.add(cleaned_tag)
            else:
                print(f"[Reducer 拦截] 过滤越界技术标签: {cleaned_tag}")
        
        # 2. ── 💡 你的强一致性重构逻辑 ───────────────────────────────────────
        # 如果经过过滤后，该切片没有命中任何官方标签，则判定该片属于“非核心噪声”
        if len(valid_chunk_tags) == 0:
            print(f"[领域熔断] 当前分片未命中核心标签，自动抹杀该片的待办事项。")
            # 连带抹杀：不把当前片的 action_items 加进 final_actions
            pass 
        else:
            # 只有当标签合法时，才允许并入最终的标签池和待办事项池
            final_tags.update(valid_chunk_tags)
            for item in output.action_items:
                final_actions.add(item.strip())
        # ───────────────────────────────────────────────────────────────────
                
        # 无论如何保留核心摘要，让用户明白系统“为什么不打标签”
        summaries.append(output.summary)
        
    combined_summary = " | ".join(summaries)
    if len(combined_summary) > 150:
        combined_summary = combined_summary[:147] + "..."
        
    return FinalAggregatedOutput(
        summary=combined_summary,
        tags=list(final_tags),
        action_items=list(final_actions)
    )
