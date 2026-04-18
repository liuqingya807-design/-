import streamlit as st
import pandas as pd
import random
from openai import OpenAI

# --- 1. 实验初始化配置 ---
st.set_page_config(page_title="Seed AI", layout="centered")

# 直接配置 DeepSeek 接口
client = OpenAI(
    api_key="sk-f9fd213424cf41d29cf7c564be6ac48d",  # 你自己填写 API Key
    base_url="https://api.deepseek.com"
)

# 简历图片链接（你自己填写 Imgur 链接）
RESUME_IMAGES = [
    "https://i.imgur.com/hfRjQTI.jpeg",  # 替换为你的公开Imgur链接
    "https://i.imgur.com/dDM6Mt2.jpeg",
    "https://i.imgur.com/O5cvFL9.jpeg",
    "https://i.imgur.com/cyRqMzM.jpeg"
]

# 初始化实验数据
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'task_type' not in st.session_state:
    st.session_state.task_type = random.choice(['low', 'high'])
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{random.randint(100000, 999999)}"
if 'first_intervene' not in st.session_state:
    st.session_state.first_intervene = None
if 'total_intervene' not in st.session_state:
    st.session_state.total_intervene = 0

# --- 2. 页面标题 ---
st.title("🤖 Seed AI")

# --- 3. 侧边栏 ---
st.sidebar.info(f"**用户ID:** {st.session_state.user_id}")
st.sidebar.info(f"**实验组:** {st.session_state.task_type}")

# --- 4. 简历图片 ---
st.subheader("📄 简历材料")
cols = st.columns(4)
for i, img in enumerate(RESUME_IMAGES):
    if img:
        cols[i].image(img, caption=f"简历{i+1}")

st.divider()

# ==============================================
# 【任务说明 100% 还原你的文档】
# ==============================================
task_type = st.session_state.task_type
user_task_input = ""

if task_type == "low":
    st.markdown("### 低负荷任务：求职者")
    st.markdown("""
**你是一名求职者，拟应聘一家公司的“AI算法工程师”岗位。**
请结合岗位关注提示、面试者简历，以求职者身份编写1份自我介绍，为将来的面试做准备。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 负责公司核心产品中机器学习/深度学习算法的开发与优化；
- 跟踪前沿 AI 技术，将其转化为可落地的业务方案；
- 参与模型性能评估，确保持续提升算法输出的准确度。

【任职要求】
- 计算机、统计学或数学相关专业本科及以上学历；
- 熟悉 Python/C++ 等编程语言，熟练使用 PyTorch 或 TensorFlow 框架；
- 核心关注：具备良好的算法优化能力，有实际的项目应用经验者优先。

【自我介绍编写提示】
该岗位中，招聘方关注候选人是否具有算法优化与应用经验，请你围绕这一要点编写自我介绍。
自我介绍稿中可以补充JD中未提及的相关内容。
""")
    user_task_input = st.text_area("✍️ 请在此编写你的自我介绍：", height=200)

else:
    st.markdown("### 高负荷任务：人力资源经理（HR）")
    st.markdown("""
**你是一名人力资源经理（HR），你所在的公司拟招聘1名AI算法工程师。**
请梳理你目前收到的4份简历，结合岗位招聘标准，为“AI算法工程师”岗位选择1名合适的候选人。
并请给出您选择时参考的岗位招聘标准（至少3个方面，每个方面不超过200字）。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 负责公司核心产品中机器学习/深度学习算法的开发与优化；
- 跟踪前沿 AI 技术，将其转化为可落地的业务方案；
- 参与模型性能评估，确保持续提升算法输出的准确度。

【任职要求】
- 计算机、统计学或数学相关专业本科及以上学历；
- 熟悉 Python/C++ 等编程语言，熟练使用 PyTorch 或 TensorFlow 框架；
- 核心关注：具备良好的算法优化能力，有实际的项目应用经验者优先。
""")
    choice = st.radio("✅ 请选择录取的候选人：", ["候选人1", "候选人2", "候选人3", "候选人4"])
    q1 = st.text_input("① 专业匹配度评价（≤200字）：")
    q2 = st.text_input("② 算法优化能力评价（≤200字）：")
    q3 = st.text_input("③ 项目经验评价（≤200字）：")
    user_task_input = f"录取：{choice} | 专业：{q1} | 算法能力：{q2} | 项目经验：{q3}"

st.divider()

# --- AI 调用函数 ---
def fetch_ai_response(chat_history):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API调用失败: {e}"

# --- 扩充后的干预关键词 ---
revision_keywords = [
    "改", "重写", "调整", "不对", "换", "重新", "不要", "修改", "优化",
    "太长", "太短", "长一点", "短一点", "精简", "扩写", "缩写", "字数",
    "语气", "风格", "幽默", "专业", "严肃", "通俗", "正式", "口语化",
    "表格", "列表", "分点", "条理", "结构", "清晰", "替换", "纠正",
    "错", "不好", "不够", "重新生成", "换一种", "再来", "重做", "修正"
]

# --- 聊天界面 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入指令（可修改/干预意图）..."):
    current_turn = len([m for m in st.session_state.messages if m['role'] == 'user']) + 1
    is_revision = any(keyword in prompt for keyword in revision_keywords)

    if is_revision and st.session_state.first_intervene is None:
        st.session_state.first_intervene = current_turn
    if is_revision:
        st.session_state.total_intervene += 1

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 思考中..."):
            ai_content = fetch_ai_response(st.session_state.messages)
            st.markdown(ai_content)
    st.session_state.messages.append({"role": "assistant", "content": ai_content})

# --- 导出数据（含完整对话）---
st.divider()
if st.button("✅ 导出实验数据"):
    first_intervene_turn = st.session_state.first_intervene if st.session_state.first_intervene else 0
    total_intervene_count = st.session_state.total_intervene
    total_turns = len([m for m in st.session_state.messages if m["role"] == "user"])

    full_dialogue = ""
    for msg in st.session_state.messages:
        role = "用户" if msg["role"] == "user" else "AI"
        full_dialogue += f"[{role}]: {msg['content']}\n\n"

    final_data = {
        "user_id": [st.session_state.user_id],
        "group": [st.session_state.task_type],
        "total_turns": [total_turns],
        "first_intervene_turn": [first_intervene_turn],
        "total_intervene_count": [total_intervene_count],
        "user_answer": [user_task_input],
        "deepseek_response": [st.session_state.messages[-1]["content"] if len(st.session_state.messages) > 0 else ""],
        "full_dialogue": [full_dialogue]
    }

    final_df = pd.DataFrame(final_data)
    csv = final_df.to_csv(index=False, encoding="utf-8-sig")
    
    st.download_button(
        "📥 点击下载 CSV 文件",
        csv,
        f"SeedAI_{st.session_state.user_id}.csv",
        "text/csv"
    )
