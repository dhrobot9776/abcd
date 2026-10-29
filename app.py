import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random

# ==========================================
# 1. 페이지 및 타이틀 설정 🤖
# ==========================================
st.set_page_config(
    page_title="🤖 3D 휴머노이드 로봇 중심 잡기 게임",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 3D 휴머노이드 로봇 균형 제어 시뮬레이터 (하드모드)")

# ==========================================
# 2. 튜토리얼 / 안내
# ==========================================
with st.expander("📖 **[3D 게임 조작법 및 안내] (클릭해서 열기/접기)**", expanded=False):
    st.markdown("""
    ### 🎮 3D 시뮬레이션 주요 안내
    1. **경고**: 가만히 서 있으면 불어오는 바람에 의해 **3~5초 안에 무조건 넘어집니다!**
    2. **3D 로봇 관절**: 로봇이 몸(무게중심)을 기울이면 **머리, 팔, 다리 관절이 3D 공간상에서 함께 실시간으로 기울어집니다.**
    3. **게임 승리 조건**: 바람에 밀려나는 **바닥의 🔴 3D ZMP(영모멘트점)**가 **🟦 3D 파란색 발바닥 영역** 밖으로 나가지 않도록 바람 반대 방향으로 빠르게 WASD를 눌러 균형을 잡으세요!
    """)

st.divider()

# ==========================================
# 3. 세션 및 난이도 초기화
# ==========================================
st.sidebar.header("⚙️ 난이도 선택")
DIFFICULTY = st.sidebar.selectbox(
    "게임 모드 선택",
    ["🍃 쉬움", "💨 보통", "🌪️ 어려움", "💥 지옥 (강풍+가속)", "🔥 극한 (외발 서기)", "🧊 빙판길 (관성 미끄러짐)"]
)

FOOT_HALF = 0.20
STEP_SIZE = 0.04
is_ice_mode = False

if "🔥 극한" in DIFFICULTY:
    FOOT_HALF = 0.10
if "🧊 빙판길" in DIFFICULTY:
    is_ice_mode = True
    STEP_SIZE = 0.015

diff_power_map = {
    "🍃 쉬움": 2.0,
    "💨 보통": 3.5,
    "🌪️ 어려움": 5.0,
    "💥 지옥 (강풍+가속)": 7.0,
    "🔥 극한 (외발 서기)": 4.0,
    "🧊 빙판길 (관성 미끄러짐)": 3.5
}
BASE_WIND_POWER = diff_power_map[DIFFICULTY]

if 'running' not in st.session_state:
    st.session_state.running = False
if 'is_game_over' not in st.session_state:
    st.session_state.is_game_over = False
if 'time' not in st.session_state:
    st.session_state.time = 0.0
if 'x_com' not in st.session_state:
    st.session_state.x_com = 0.0
if 'y_com' not in st.session_state:
    st.session_state.y_com = 0.0
if 'vx_com' not in st.session_state:
    st.session_state.vx_com = 0.0
if 'vy_com' not in st.session_state:
    st.session_state.vy_com = 0.0
if 'wind_x' not in st.session_state:
    st.session_state.wind_x = 0.0
if 'wind_y' not in st.session_state:
    st.session_state.wind_y = 0.0

def reset_game():
    st.session_state.running = True
    st.session_state.is_game_over = False
    st.session_state.time = 0.0
    st.session_state.x_com = 0.0
    st.session_state.y_com = 0.0
    st.session_state.vx_com = 0.0
    st.session_state.vy_com = 0.0
    
    # 게임 시작 즉시 기습 바람 밀림 발생!
    angle = random.uniform(0, 2 * np.pi)
    st.session_state.wind_x = np.cos(angle) * 0.08
    st.session_state.wind_y = np.sin(angle) * 0.08

# ==========================================
# 4. 상단 컨트롤 패널 및 WASD 리모컨
# ==========================================
col_s1, col_s2, _ = st.columns([1.5, 1.5, 3])
with col_s1:
    if st.button("▶️ 게임 시작!", use_container_width=True, type="primary"):
        reset_game()
with col_s2:
    if st.button("🔄 다시 하기", use_container_width=True):
        reset_game()

st.subheader("🎮 3D 로봇 관절 조종 리모컨")
p_col1, p_col2, p_col3 = st.columns([1, 1, 1])

if not is_ice_mode:
    with p_col2:
        if st.button("⬆️ W (앞으로 기울이기)", use_container_width=True):
            st.session_state.y_com = min(FOOT_HALF, st.session_state.y_com + STEP_SIZE)
    with p_col1:
        if st.button("⬅️ A (왼쪽으로)", use_container_width=True):
            st.session_state.x_com = max(-FOOT_HALF, st.session_state.x_com - STEP_SIZE)
    with p_col2:
        if st.button("🎯 C (중앙 정렬)", use_container_width=True):
            st.session_state.x_com, st.session_state.y_com = 0.0, 0.0
    with p_col3:
        if st.button("➡️ D (오른쪽으로)", use_container_width=True):
            st.session_state.x_com = min(FOOT_HALF, st.session_state.x_com + STEP_SIZE)
    with p_col2:
        if st.button("⬇️ S (뒤로 기울이기)", use_container_width=True):
            st.session_state.y_com = max(-FOOT_HALF, st.session_state.y_com - STEP_SIZE)
else:
    with p_col2:
        if st.button("⬆️ W (앞 추진력)", use_container_width=True):
            st.session_state.vy_com += STEP_SIZE
    with p_col1:
        if st.button("⬅️ A (좌 추진력)", use_container_width=True):
            st.session_state.vx_com -= STEP_SIZE
    with p_col2:
        if st.button("🛑 C (긴급 브레이크)", use_container_width=True):
            st.session_state.vx_com, st.session_state.vy_com = 0.0, 0.0
    with p
