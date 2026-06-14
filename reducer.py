from typing import List
from models import TextAnalysisOutput, FinalAggregatedOutput  # 引入新契约

def aggregate_and_deduplicate(chunk_outputs: List[TextAnalysisOutput]) -> FinalAggregatedOutput:
    """
    Reducer 节点：将多个 Chunk 吐出的结构化数据进行严格的去重和合并
    """
    final_tags = set()
    final_actions = set()
    summaries = []
    
    for output in chunk_outputs:
        for tag in output.tags:
            final_tags.add(tag)
        for item in output.action_items:
            final_actions.add(item.strip())
        summaries.append(output.summary)
        
    combined_summary = " | ".join(summaries)
    if len(combined_summary) > 150:
        combined_summary = combined_summary[:147] + "..."
        
    # ── 核心升级：拒绝返回字典，用强类型对象包裹 ────────────────────────────
    return FinalAggregatedOutput(
        summary=combined_summary,
        tags=list(final_tags),
        action_items=list(final_actions)
    )
