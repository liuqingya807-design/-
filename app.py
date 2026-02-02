import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
from openai import OpenAI

# --- 1. 实验初始化配置 ---
st.set_page_config(page_title="生成式AI交互实验平台", layout="centered")

# 直接配置 DeepSeek 接口
client = OpenAI(
    api_key="sk-a05915657f7841b382145bc4c2e45749", 
    base_url="https://api.deepseek.com"
)

# 初始化实验数据记录
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'task_type' not in st.session_state:
    st.session_state.task_type = random.choice(['A', 'B']) # 随机分配任务验证 H2
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"User_{random.randint(1000, 9999)}"

# --- 2. 任务展示 (操控任务复杂度 H2) ---
st.title("生成式 AI 交互行为研究")
st.sidebar.info(f"**用户ID:** {st.session_state.user_id}")
st.sidebar.info(f"**当前组别:** {'低认知负荷组' if st.session_state.task_type == 'A' else '高认知负荷组'}")

if st.session_state.task_type == 'A':
    task_prompt = "【任务】请让 AI 为你写一段给朋友的生日祝福语，要求语气幽默，30字以内。"
else:
    task_prompt = "【任务】请让 AI 总结一段复杂的学术报告，并要求其将语气转换为“给5岁小孩解释”，且字数必须控制在80-100字之间。"

st.warning(f"**您的实验任务：** {task_prompt}")

# --- 3. AI 调用函数 (验证元认知监控 H1b) ---
def fetch_ai_response(chat_history):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 使用 DeepSeek 模型
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"接口连接失败，请检查网络或余额: {e}"

# --- 4. 聊天界面与客观指标埋点 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("在此输入指令..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("DeepSeek 正在思考..."):
            ai_content = fetch_ai_response(st.session_state.messages)
            st.markdown(ai_content)
    st.session_state.messages.append({"role": "assistant", "content": ai_content})

    # 自动计算验证假设所需的量化指标
    current_turn = len([m for m in st.session_state.messages if m['role'] == 'user'])
    revision_keywords = ["改", "长", "短", "语气", "重写", "调整", "精简", "不"]
    is_revision = any(k in prompt for k in revision_keywords)
    
    st.session_state.log_data.append({
        "UserID": st.session_state.user_id,
        "TaskType": st.session_state.task_type,
        "Turn": current_turn,
        "IsRevision": is_revision,
        "ResponseLength": len(ai_content)
    })

# --- 5. 实验结束与数据导出 ---
st.divider()
if st.button("完成实验并导出数据"):
    df = pd.DataFrame(st.session_state.log_data)
    first_turn = df[df['IsRevision'] == True]['Turn'].min() if df['IsRevision'].any() else "未干预"
    rev_rate = df['IsRevision'].mean() * 100
    
    st.success("### 实验客观指标")
    st.write(f"首次干预轮数: **{first_turn}** (对比预研均值 2.72轮)")
    st.write(f"修改指令频率: **{rev_rate:.2f}%** (对比预研均值 1.38%)")
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("下载 CSV 结果文件", csv, f"Result_{st.session_state.user_id}.csv", "text/csv")