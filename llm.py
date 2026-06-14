# llm.py
import json
import asyncio
import time
import logging
import openai
from models import TextAnalysisOutput, FinalAggregatedOutput
from reducer import aggregate_and_deduplicate

# ── 监控配置：让控制台日志带上精确时间戳 ─────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AI-Systems-Monitor")

DEEPSEEK_API_KEY  = "sk-68901eb2d2894926bb24442944c1eb23"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL    = "deepseek-chat"

# ── 确定性的18个官方小标签名单（作为静态资产沉淀） ──────────────────────────
ALLOWED_TAGS = {
    "LLM", "Agent", "RAG", "LangChain", "LangGraph", "MCP", 
    "Prompt工程", "模型部署", "推理优化", "AI工程化", "多模态", 
    "向量数据库", "知识图谱", "数据处理", "论文解读", "框架更新", 
    "最佳实践", "性能优化"
}

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """物理字符串切片算法，带重叠区"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

async def async_extract_single_chunk(client: openai.AsyncOpenAI, chunk: str, chunk_id: int, semaphore: asyncio.Semaphore) -> TextAnalysisOutput:
    """单个 Chunk 的异步抽取任务"""
    # ── 贯彻你的意志：不强制选择，不符则输出空列表，降低确定性幻觉 ─────────────
    system_prompt = (
        "你是一个严谨的 AI 技术知识整理专家。请阅读用户输入的文字片段，严格按照要求输出 JSON。\n"
        f"允许使用的官方标签列表严格限制为：{list(ALLOWED_TAGS)}\n"
        "【关键规则】：如果文本内容不属于上述官方标签列表中的任何一个领域（例如属于纯粹的通用软件工程 Git、SSH、前端等），"
        "则 tags 字段必须输出为空列表 []，绝对禁止自行发明任何新标签。\n"
        "JSON 结构：{ 'summary': '50字内', 'tags': ['符合的官方标签'], 'action_items': ['动词开头'] }"
    )
    
    async with semaphore:
        start_time = time.time()
        logger.info(f"🚀 [Chunk-{chunk_id}] 进入并发队列，正在向 DeepSeek 发起 HTTP 请求...")
        
        try:
            response = await client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": chunk}],
                temperature=0.1, # 极低温度，锁死大模型的确定性
            )
            raw = response.choices[0].message.content.strip()
            
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
                raw = raw.strip()
                
            latency = time.time() - start_time
            logger.info(f"✅ [Chunk-{chunk_id}] 请求成功返回！单片耗时: {latency:.2f} 秒")
            
            data = json.loads(raw)
            return TextAnalysisOutput(**data)
        except Exception as e:
            logger.error(f"❌ [Chunk-{chunk_id}] 运行时异常! 原因: {str(e)}")
            return TextAnalysisOutput(summary="当前分片解析失败", tags=[], action_items=[])

async def analyze_large_knowledge_text_async(user_text: str) -> FinalAggregatedOutput:
    """Level 1 异步总控运行时：并发抽取系统"""
    client = openai.AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    
    chunks = chunk_text(user_text)
    total_chunks = len(chunks)
    
    logger.info(f"📝 [系统启动] 成功将长文本切分为 {total_chunks} 个物理切片，准备并发交火...")
    global_start_time = time.time()
    
    # 信号量控制器：最多允许 3 个任务同时向 DeepSeek 开火，防止 429 限流
    sem = asyncio.Semaphore(3)
    
    # 使用 enumerate 确保元组正确解包，避开 ValueError 暗雷
    tasks = [async_extract_single_chunk(client, chunk, i+1, sem) for i, chunk in enumerate(chunks)]
    
    # 并发等待所有网络 IO 返回
    chunk_results = await asyncio.gather(*tasks)
    
    io_duration = time.time() - global_start_time
    logger.info(f"📊 [Map阶段结束] 所有异步网络请求全部收拢。网络层总耗时: {io_duration:.2f} 秒")
    
    logger.info("⚙️ [Reduce阶段启动] 正在将多片数据丢进去重聚合引擎...")
    final_output = aggregate_and_deduplicate(chunk_results, ALLOWED_TAGS)
    
    total_duration = time.time() - global_start_time
    logger.info(f"🏁 [系统完成] 全链路执行结束。总系统耗时: {total_duration:.2f} 秒")
    
    return final_output
