import streamlit as st
import pandas as pd
import random
from datetime import datetime
from openai import OpenAI

# --- 1. 实验初始化与分组控制 (研究2核心逻辑) ---
st.set_page_config(page_title="元认知唤醒交互实验平台", layout="centered")

# DeepSeek API 配置
client = OpenAI(
    api_key="sk-a05915657f7841b382145bc4c2e45749", 
    base_url="https://api.deepseek.com"
)

# 随机分配三组实验水平 (验证 H3) 
if 'group' not in st.session_state:
    # Control: 控制组 | A: 情景化提示组 | B: 解释性说明组
    st.session_state.group = random.choice(['Control', 'A', 'B'])
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"User_{random.randint(1000, 9999)}"

# --- 2. 实验任务显示 (统一采用高复杂度任务以验证唤醒效果) ---
st.title("人-AI 协作元认知唤醒实验")
st.sidebar.info(f"用户ID: {st.session_state.user_id}")
st.sidebar.info(f"实验组别: {st.session_state.group}")

task_prompt = "【高难度任务】请提供一段学术论文摘要，要求 AI 将其改写为“面向非专业人士”的科普短文。要求：逻辑严密、字数严格控制在 100-120 字之间。" 
st.warning(task_prompt)

# --- 3. 不同组别的差异化 UI (助推设计) ---
def render_nudge(last_ai_response):
    """根据分组渲染助推组件"""
    if st.session_state.group == 'A':
        # 实验组 A: 情景化提示 (主动唤醒监控) 
        if len(last_ai_response) > 150:
            st.toast("检测到回复可能字数超标，需要为您切换精简模式吗？", icon="⚠️")
            if st.button("点此尝试一键精简"):
                return "请将上述内容精简到 100 字以内。"
                
    elif st.session_state.group == 'B':
        # 实验组 B: 解释性说明 (补充元认知知识) 
        st.help("提示：若想提高协作质量，您可以点击‘精简’或要求 AI 使用‘通俗语气’。专业语气会使用更多术语。")
    
    return None

# --- 4. AI 对话核心逻辑 ---
def get_ai_response(chat_history):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"连接失败: {e}"

# 显示对话历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("在此输入指令..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考..."):
            ai_content = get_ai_response(st.session_state.messages)
            st.markdown(ai_content)
    st.session_state.messages.append({"role": "assistant", "content": ai_content})

    # --- 数据埋点 (为 SPSS 分析准备指标) ---
    current_turn = len([m for m in st.session_state.messages if m['role'] == 'user'])
    # 识别是否打破默认选项 (IsRevision)
    rev_keywords = ["改", "短", "换", "重写", "调整", "不", "精简"]
    is_revision = any(k in prompt for k in rev_keywords)

    st.session_state.log_data.append({
        "UserID": st.session_state.user_id,
        "Group": st.session_state.group,
        "Turn": current_turn,
        "Content": prompt,
        "IsRevision": is_revision,
        "ResponseLen": len(ai_content),
        "Timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # 渲染助推组件并检查是否产生新指令
    if nudge_prompt := render_nudge(ai_content):
        st.info(f"系统建议指令: {nudge_prompt}")

# --- 5. 实验结束与多维度数据导出 ---
st.divider()
if st.button("完成实验并下载交互数据"):
    if st.session_state.log_data:
        df = pd.DataFrame(st.session_state.log_data)
        
        # 计算核心量化指标
        rev_rate = df['IsRevision'].mean() * 100
        first_turn = df[df['IsRevision'] == True]['Turn'].min() if df['IsRevision'].any() else "未干预"
        
        st.success("### 实验结果摘要 (研究2)")
        c1, c2, c3 = st.columns(3)
        c1.metric("所属组别", st.session_state.group)
        c2.metric("指令迭代率", f"{rev_rate:.1f}%")
        c3.metric("首次干预轮数", first_turn)
        
        # 提供 CSV 下载用于 SPSS [cite: 18]
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载 CSV 轨迹文件",
            data=csv,
            file_name=f"Study2_{st.session_state.group}_{st.session_state.user_id}.csv",
            mime="text/csv"
        )
        st.info("请将被试最终满意的 AI 回复复制保存，以便专家评分。")
    else:
        st.error("暂无交互数据。")
