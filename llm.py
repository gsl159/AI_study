import json
import openai
from models import TextAnalysisOutput
from reducer import aggregate_and_deduplicate

DEEPSEEK_API_KEY  = "sk-68901eb2d2894926bb24442944c1eb23"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL    = "deepseek-chat"

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """极简的物理字符串切片算法，带重叠区"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def analyze_large_knowledge_text(user_text: str) -> dict:
    """Level 1 核心运行时：长文本分布式抽取系统"""
    client = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    
    # 1. 物理切片
    chunks = chunk_text(user_text)
    chunk_results = []
    
    system_prompt = (
    "你是一个严谨的 AI 技术知识整理专家。请阅读用户输入的文字，"
    "并严格按照要求输出结构化数据。\n\n"
    "你必须只返回一个合法的 JSON 对象，不要有任何多余的文字、解释或 markdown 代码块。\n"
    "JSON 结构如下：\n"
    "{\n"
    '  "summary": "用一句话高度概括输入文本的核心内容，字数控制在50字以内",\n'
    '  "tags": ["从以下选择1-3个：LLM、Agent、RAG、LangChain、LangGraph、MCP、Prompt工程、模型部署、推理优化、AI工程化、多模态、向量数据库、知识图谱、数据处理、论文解读、框架更新、最佳实践、性能优化"],\n'
    '  "action_items": ["必须以动词开头，从以下选择1-3个：阅读、整理、记录、实现、编写、测试、验证、部署、复现、优化、调研、实验、分析、对比、总结、集成、封装、评估"]\n'
    "}"
)
    
    # 2. 循环调用（Map 阶段）
    for chunk in chunks:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk},
            ],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        
        # 兼容 Markdown 外壳
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
            raw = raw.strip()
            
        try:
            data = json.loads(raw)
            # 通过 Pydantic 校验单点契约
            validated_output = TextAnalysisOutput(**data)
            chunk_results.append(validated_output)
        except Exception as e:
            # 基础防御：单片失败跳过，保证系统不整体雪崩
            continue
            
    # 3. 聚合去重（Reduce 阶段）
    return aggregate_and_deduplicate(chunk_results)
