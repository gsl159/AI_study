# state_machine_agent.py
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from agent_models import AgentState, Hypothesis, ExecutionPlan

logger = logging.getLogger("RAG-Agent-Core")

class EnterpriseDiagnosticAgent:
    """
    企业级可验证决策 Agent
    遵循架构师第一原则：由状态机驱动行为，拒绝 random walk（随机游走）。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model_name
        self.current_state = AgentState.INIT
        self.plan: Optional[ExecutionPlan] = None
        self.diagnostic_history: List[str] = []

    def _transit_state(self, next_state: AgentState):
        """严格控制状态机的物理流转日志"""
        logger.info(f"🔄 [状态机转移] 【{self.current_state.value}】 ───> 【{next_state.value}】")
        self.current_state = next_state

    def _call_llm_json(self, system_prompt: str, user_prompt: str) -> dict:
        """纯净的 JSON 提取器底座"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())

    def execute_diagnostic_loop(self, problem_description: str, mock_environment_tools: Dict[str, Any]) -> str:
        """主运行控制面：状态机强力接管循环"""
        logger.info(f"🚀 [Agent Brain] 接收到硬核排障任务: '{problem_description}'")
        self.diagnostic_history.append(f"原始问题: {problem_description}")
        
        while self.current_state not in [AgentState.SUCCESS, AgentState.FAILED]:
            
            # ── [STATE: INIT -> GENERATE_HYPOTHESIS] ──────────────────────────
            if self.current_state == AgentState.INIT:
                self._transit_state(AgentState.GENERATE_HYPOTHESIS)
                
                system_prompt = (
                    "你是一个资深数据库专家 Planner。面对用户的故障，请生成 3 个排障假设，并按排查优先级排序。\n"
                    "你必须返回以下格式的 JSON，绝对禁止包含任何多余文字：\n"
                    "{ 'hypotheses': [ { 'id': 'H1', 'description': '假设原因', 'target_tool': '检查方法' } ] }"
                )
                user_prompt = f"当前故障: {problem_description}\n可动用的验证工具/知识库: {list(mock_environment_tools.keys())}"
                
                raw_plan = self._call_llm_json(system_prompt, user_prompt)
                # 利用 Pydantic 锁死结构，强制将 LLM 转化为有纪律的排障计划书
                self.plan = ExecutionPlan(hypotheses=[Hypothesis(**h) for h in raw_plan['hypotheses']])
                logger.info(f"📋 [Planner] 执行计划生成完毕！排查队列长度: {len(self.plan.hypotheses)}")
                for h in self.plan.hypotheses:
                    logger.info(f"  - [{h.id}] 假设: {h.description} | 预动用工具: {h.target_tool}")

            # ── [STATE: GENERATE_HYPOTHESIS -> COLLECT_EVIDENCE] ──────────────
            elif self.current_state == AgentState.GENERATE_HYPOTHESIS:
                if self.plan.current_hypothesis_index >= len(self.plan.hypotheses):
                    logger.error("❌ 计划书中所有的假设都验证失败，未找到根因。")
                    self._transit_state(AgentState.FAILED)
                    break
                    
                self._transit_state(AgentState.COLLECT_EVIDENCE)
                current_hyp = self.plan.hypotheses[self.plan.current_hypothesis_index]
                logger.info(f"🛡️ [Executor] 开始锁定并进攻当前核心假设: {current_hyp.id} -> {current_hyp.description}")
                
                # 模拟工具或二级 Level 2 RAG 知识库的确定性结果回填
                tool_name = current_hyp.target_tool
                if tool_name in mock_environment_tools:
                    evidence_result = mock_environment_tools[tool_name]
                    logger.info(f"🛠️ [Tool Execution] 成功调用底层工具 [{tool_name}]，捕获硬核证据: '{evidence_result}'")
                else:
                    evidence_result = "工具未找到，无法搜集证据"
                    logger.warning(f"⚠️ 工具 {tool_name} 不存在")

                # ── [STATE: COLLECT_EVIDENCE -> VERIFY_HYPOTHESIS] ────────────
                self._transit_state(AgentState.VERIFY_HYPOTHESIS)
                
                system_prompt = (
                    "你是一个严谨的排障自省器 Reflection。\n"
                    "请根据当前的【故障假设】和【工具返回的物理证据】，进行严密的逻辑推导，判断该假设是否成立。\n"
                    "你必须返回以下 JSON 格式：\n"
                    "{ 'is_verified': true/false, 'reasoning': '你的推导证据和反思逻辑' }"
                )
                user_prompt