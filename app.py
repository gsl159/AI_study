# app.py
import streamlit as st
import asyncio
from llm import analyze_large_knowledge_text_async

st.set_page_config(page_title="AI 知识工作台", layout="centered")
st.title("📚 AI 知识工作台 (Level 1 - 完全体)")
st.caption("基于 Asyncio 信号量并发锁 + 零信任代码双向过滤的企业级长文本精炼器")

# 前端输入平面
user_input = st.text_area("请输入或粘贴你今天看到的任何长篇技术文章、博客或聊天记录：", height=200)

if st.button("开始精炼资产", type="primary"):
    if user_input.strip() == "":
        st.warning("请输入内容后再提交。")
    else:
        with st.spinner("异步流水线并发请求中，代码闸门防御拦截已就绪..."):
            # 利用 asyncio.run 驱动后端的异步总控面
            result = asyncio.run(analyze_large_knowledge_text_async(user_input))
            
            st.success("长文本资产完美精炼成功！数据零丢失，未知标签已在代码层无感拦截。")
            
            # ── 优雅的点号属性访问，绝不暴露 Bug 给运行期 ──────────────────────
            st.subheader("💡 核心摘要")
            st.info(result.summary)
            
            st.subheader("🏷️ 命中核心技术标签")
            if result.tags:
                # 漂亮地用 Markdown 格式展示过滤去重后的标签
                st.write(" ".join([f"`{tag}`" for tag in result.tags]))
            else:
                st.caption("⚠️ 本文内容未命中任何官方 18 个核心技术标签，代码层已执行断路保护。")
            
            st.subheader("🏃 可落地待办事项")
            if result.action_items:
                for item in result.action_items:
                    st.markdown(f"- `{item}`")
            else:
                st.caption("暂无可提取的明确待办动作。")
