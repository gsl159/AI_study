# AI 知识工作台 — Level 0

基于**契约优先（Contract First）**原则构建的文本结构化精炼器。

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt


# 3. 启动网页界面
streamlit run app.py
```

## 文件说明

| 文件 | 职责 |
|------|------|
| `models.py` | 契约资产 — 用 Pydantic 锁死大模型的输出结构 |
| `llm.py` | 控制资产 — 调用 OpenAI Structured Outputs API |
| `app.py` | 界面资产 — Streamlit 极简前端 |

## 输出结构

每次精炼会产出三项结构化资产：

- **核心摘要** — 50 字内的本质提炼
- **分类标签** — 标签中选 1-2 个
- **可落地待办事项** — 必须以动词开头的明确行动
