import streamlit as st
import pandas as pd
import random
from datetime import datetime
from openai import OpenAI

st.set_page_config(page_title="人-AI协作实验", layout="centered")

client = OpenAI(
    api_key="sk-a05915657f7841b382145bc4c2e45749", 
    base_url="https://api.deepseek.com"
)

if 'group' not in st.session_state:
    st.session_state.group = random.choice(['Control', 'A', 'B'])
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"User_{random.randint(1000, 9999)}"

st.title("人-AI 协作元认知唤醒实验")
st.sidebar.info(f"用户ID: {st.session_state.user_id}")
st.sidebar.info(f"实验组别: {st.session_state.group}")

task_prompt = "【高难度任务】请提供一段学术论文摘要，要求 AI 将其改写为“面向非专业人士”的科普短文。要求：逻辑严密、字数严格控制在 100-120 字之间。"
st.warning(task_prompt)

def render_nudge(last_ai_response):
    if st.session_state.group == 'A':
        if len(last_ai_response) > 150:
            st.toast("检测到回复较长，需要为你切换为精简模式吗？", icon="⚠️")
            if st.button("点此尝试一键精简"):
                return "请将上述内容精简到 100 字以内。"
    elif st.session_state.group == 'B':
        st.help("提示：若想提高协作质量，您可以点击‘精简’或要求 AI 使用‘通俗语气’。专业语气会使用更多术语。")
    return None

def get_ai_response(chat_history):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"错误: {e}"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("在此输入指令..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        ai_content = get_ai_response(st.session_state.messages)
        st.markdown(ai_content)
    st.session_state.messages.append({"role": "assistant", "content": ai_content})

    current_turn = len([m for m in st.session_state.messages if m['role'] == 'user'])
    rev_keywords = ["改", "短", "换", "重写", "调整", "不", "精简"]
    is_revision = any(k in prompt for k in rev_keywords)

    st.session_state.log_data.append({
        "UserID": st.session_state.user_id,
        "Group": st.session_state.group,
        "Turn": current_turn,
        "IsRevision": is_revision,
        "ResponseLen": len(ai_content)
    })

    if nudge_prompt := render_nudge(ai_content):
        st.info(f"建议指令: {nudge_prompt}")

st.divider()
if st.button("下载实验数据"):
    if st.session_state.log_data:
        df = pd.DataFrame(st.session_state.log_data)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="点击下载CSV",
            data=csv,
            file_name=f"Data_{st.session_state.user_id}.csv",
            mime="text/csv"
        )
