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
# 初始化nudge_prompt会话状态，防止首次访问时报错
if "nudge_prompt" not in st.session_state:
    st.session_state.nudge_prompt = None
resume_images = {
    "候选人1": "https://i.imgur.com/hfRjQTI.jpeg",  # 替换为你的公开Imgur链接
    "候选人2": "https://i.imgur.com/dDM6Mt2.jpeg",
    "候选人3": "https://i.imgur.com/O5cvFL9.jpeg",
    "候选人4": "https://i.imgur.com/cyRqMzM.jpeg"
}

st.title("人-AI 协作元认知唤醒实验")
st.sidebar.info(f"用户ID: {st.session_state.user_id}")
st.sidebar.info(f"实验组别: {st.session_state.group}")

task_prompt = """【高难度任务】请你以企业HR身份，结合下方4份AI算法工程师简历，要求AI生成面向非专业人士的招聘筛选标准：
1. 至少3条筛选标准，每条严格控制在100-120字之间，整合成表格形式
2. 逻辑严密，贴合企业真实招聘需求
3. 语言通俗，非专业人士也能理解筛选要求"""
st.warning(task_prompt)
col_resume, col_chat = st.columns([2, 1.5], gap="large")

with col_resume:
    st.header("📄 AI算法工程师候选人简历（共4份）")
    # 候选人1
    with st.expander("候选人1 简历", expanded=True):
        try:
            st.image(
                resume_images["候选人1"],
                caption="候选人1 - AI算法工程师简历",
                use_column_width=True,
                clamp=True
            )
        except Exception as e:
            st.error(f"❌ 简历加载失败：{str(e)}")
            st.warning("请检查Imgur链接是否为公开可访问状态")
    # 候选人2
    with st.expander("候选人2 简历", expanded=True):
        try:
            st.image(
                resume_images["候选人2"],
                caption="候选人2 - AI算法工程师简历",
                use_column_width=True,
                clamp=True
            )
        except Exception as e:
            st.error(f"❌ 简历加载失败：{str(e)}")
    # 候选人3
    with st.expander("候选人3 简历", expanded=True):
        try:
            st.image(
                resume_images["候选人3"],
                caption="候选人3 - AI算法工程师简历",
                use_column_width=True,
                clamp=True
            )
        except Exception as e:
            st.error(f"❌ 简历加载失败：{str(e)}")
    # 候选人4
    with st.expander("候选人4 简历", expanded=True):
        try:
            st.image(
                resume_images["候选人4"],
                caption="候选人4 - AI算法工程师简历",
                use_column_width=True,
                clamp=True
            )
        except Exception as e:
            st.error(f"❌ 简历加载失败：{str(e)}")

with col_chat:
    # ---------------------- 原有render_nudge函数适配HR任务 ----------------------
    def render_nudge(last_ai_response):
        if st.session_state.group == 'A':  # A组：情景提示组（动态弹窗）
            if len(last_ai_response) > 150:  # 检测筛选标准字数过多
                st.toast("⚠️ 检测到筛选标准较长，需要为你切换为精简模式吗？", icon="📏")
                if st.button("点此一键精简为100-120字/条"):
                    return "请将上述筛选标准每条精简到100-120字，保留核心招聘要求，语言通俗"
        elif st.session_state.group == 'B':  # B组：解释性说明组（功能按钮）
            st.info("提示：可点击下方按钮快速调整AI生成的筛选标准")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📝", help="调整为专业HR语气"):
                    st.session_state.nudge_prompt = "请将筛选标准调整为专业HR招聘语气，突出核心评估维度，语言严谨规范"
                    st.toast("已触发专业语气调整！", icon="📝")
            with col2:
                if st.button("📏", help="限定100-120字/条"):
                    st.session_state.nudge_prompt = "请将每条筛选标准精简/扩充到100-120字，保留核心招聘信息"
                    st.toast("已触发字数调整！", icon="📏")
            with col3:
                if st.button("🧠", help="优化逻辑清晰度"):
                    st.session_state.nudge_prompt = "请按「算法能力→项目经验→专业背景」排序优化筛选标准，条理更清晰"
                    st.toast("已触发逻辑优化！", icon="🧠")
        # Control组无任何提示，直接返回None
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

if prompt := st.chat_input("在此输入HR筛选指令，例如：帮我生成3条AI算法工程师筛选标准 / 调整这条标准的语气"):
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
