import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import random

# ==========================================
# 1. 페이지 및 타이틀 설정 🤖
# ==========================================
st.set_page_config(
    page_title="🤖 아슬아슬! 로봇 균형 잡기 게임",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 아슬아슬! 로봇 중심 잡기 시뮬레이터")

# ==========================================
# 2. 초등학생 눈높이 튜토리얼 / 게임 설명서
# ==========================================
with st.expander("📖 **[필독] 초간단 게임 설명서 & 튜토리얼 (클릭해서 열기/접기)**", expanded=True):
    st.markdown("""
    ### 🎯 게임 목표
    바람이 쌩쌩 불어서 🤖 **로봇**이 흔들려요!  
    **WASD 버튼**을 눌러 로봇의 몸을 반대 방향으로 기울여서, **❌ 빨간 십자가**가 **🟦 파란 발바닥 상자** 밖으로 나가지 않게 지켜주세요!

    ---
    ### 🎨 화면에 나오는 그림 뜻 알아보기
    * 🟦 **파란색 상자**: 로봇의 **발바닥 영역**이에요. (이 밖으로 나가면 꽈당! 넘어져요)
    * 🟢 **초록색 동그라미**: 여러분이 WASD 버튼으로 조종하는 **로봇의 몸(무게중심)**이에요.
    * ❌ **빨간색 십자가**: 바람 때문에 흔들리는 **진짜 중심점(ZMP)**이에요.

    ---
    ### 💡 고수가 되는 꿀팁!
    * 💨 바람이 **오른쪽**으로 밀면? ➡️ **⬅️ A 버튼 (왼쪽)**을 눌러서 로봇 몸을 반대로 기울이세요!
    * 💨 바람이 **앞(위)**으로 밀면? ⬆️ **⬇️ S 버튼 (뒤)**을 누르세요!
    * 🎯 중심을 완전히 잃었다면 **C 버튼 (중앙 정렬)**을 누르면 빠르게 되돌아와요!
    """)

st.divider()

# ==========================================
# 3. 게임 변수 및 세션 초기화
# ==========================================
FOOT_HALF = 0.20   # 발바닥 영역 경계
STEP_SIZE = 0.04   # 버튼 클릭당 로봇 이동 거리

if 'running' not in st.session_state:
    st.session_state.running = False
if 'time' not in st.session_state:
    st.session_state.time = 0.0
if 'x_com' not in st.session_state:
    st.session_state.x_com = 0.0
if 'y_com' not in st.session_state:
    st.session_state.y_com = 0.0
if 'wind_x' not in st.session_state:
    st.session_state.wind_x = 0.0
if 'wind_y' not in st.session_state:
    st.session_state.wind_y = 0.0

def reset_game():
    st.session_state.running = True
    st.session_state.time = 0.0
    st.session_state.x_com = 0.0
    st.session_state.y_com = 0.0
    st.session_state.wind_x = 0.0
    st.session_state.wind_y = 0.0

# ==========================================
# 4. 사이드바 및 게임 시작 제어판
# ==========================================
st.sidebar.header("⚙️ 난이도 설정")
WIND_LEVEL = st.sidebar.select_slider(
    "바람 세기 (난이도)",
    options=["쉬움 🍃", "보통 💨", "어려움 🌪️", "지옥 💥"],
    value="보통 💨"
)

wind_power_map = {"쉬움 🍃": 1.2, "보통 💨": 2.2, "어려움 🌪️": 3.5, "지옥 💥": 5.0}
WIND_POWER = wind_power_map[WIND_LEVEL]

col_s1, col_s2, _ = st.columns([1.5, 1.5, 3])
with col_s1:
    if st.button("▶️ 게임 시작!", use_container_width=True, type="primary"):
        reset_game()
        st.rerun()
with col_s2:
    if st.button("🔄 다시 하기", use_container_width=True):
        reset_game()
        st.rerun()

# ==========================================
# 5. 알록달록 WASD 조종 리모컨
# ==========================================
st.subheader("🎮 로봇 조종 리모컨")
p_col1, p_col2, p_col3 = st.columns([1, 1, 1])

with p_col2:
    if st.button("⬆️ W (앞으로 기울이기)", use_container_width=True):
        st.session_state.y_com = min(FOOT_HALF, st.session_state.y_com + STEP_SIZE)
with p_col1:
    if st.button("⬅️ A (왼쪽으로)", use_container_width=True):
        st.session_state.x_com = max(-FOOT_HALF, st.session_state.x_com - STEP_SIZE)
with p_col2:
    if st.button("🎯 C (제자리 제어)", use_container_width=True):
        st.session_state.x_com = 0.0
        st.session_state.y_com = 0.0
with p_col3:
    if st.button("➡️ D (오른쪽으로)", use_container_width=True):
        st.session_state.x_com = min(FOOT_HALF, st.session_state.x_com + STEP_SIZE)
with p_col2:
    if st.button("⬇️ S (뒤로 기울이기)", use_container_width=True):
        st.session_state.y_com = max(-FOOT_HALF, st.session_state.y_com - STEP_SIZE)

# 플레이스홀더
metrics_ph = st.empty()
plot_ph = st.empty()

# ==========================================
# 6. 게임 루프 Engine
# ==========================================
if st.session_state.running:
    # 바람 흔들림 계산
    if random.random() < 0.4:
        st.session_state.wind_x += (random.random() - 0.5) * WIND_POWER * 0.015
        st.session_state.wind_y += (random.random() - 0.5) * WIND_POWER * 0.015
    
    st.session_state.wind_x *= 0.92
    st.session_state.wind_y *= 0.92

    # ZMP 위치 = 로봇 몸 위치 + 바람 영향
    x_zmp = st.session_state.x_com + st.session_state.wind_x
    y_zmp = st.session_state.y_com + st.session_state.wind_y

    st.session_state.time += 0.1

    # 게임 오버 조건 (발바닥 이탈)
    is_game_over = (abs(x_zmp) > FOOT_HALF or abs(y_zmp) > FOOT_HALF)

    # 전광판 점수 및 정보
    with metrics_ph.container():
        m1, m2, m3 = st.columns(3)
        m1.metric("⏱️ 버틴 시간", f"{st.session_state.time:.1f} 초")
        m2.metric("🟢 로봇 몸 위치", f"좌우: {st.session_state.x_com:+.2f} | 앞뒤: {st.session_state.y_com:+.2f}")
        m3.metric("❌ 실제 흔들림", f"좌우: {x_zmp:+.2f} | 앞뒤: {y_zmp:+.2f}")

    # Plotly 그래프 시각화
    fig = go.Figure()

    # 🟦 발바닥 안전 구역
    fig.add_shape(
        type="rect",
        x0=-FOOT_HALF, y0=-FOOT_HALF, x1=FOOT_HALF, y1=FOOT_HALF,
        fillcolor="rgba(0, 180, 255, 0.2)",
        line=dict(color="DeepSkyBlue", width=4)
    )

    # 🟢 로봇 몸통
    fig.add_trace(go.Scatter(
        x=[st.session_state.x_com], y=[st.session_state.y_com],
        mode='markers+text', name='🟢 로봇 몸',
        text=['🤖 로봇'], textposition="top center",
        marker=dict(size=26, color='SpringGreen', symbol='circle')
    ))

    # ❌ 흔들리는 중심점 (ZMP)
    fig.add_trace(go.Scatter(
        x=[x_zmp], y=[y_zmp],
        mode='markers+text', name='❌ 흔들리는 중심(ZMP)',
        text=['❌ 중심점'], textposition="bottom center",
        marker=dict(size=22, color='Crimson', symbol='x')
    ))

    fig.update_layout(
        title="🤖 로봇 발바닥을 지켜라! (❌가 파란 박스를 나가면 패배)",
        xaxis=dict(title="왼쪽 (A) <--- 위치 ---> 오른쪽 (D)", range=[-FOOT_HALF*1.5, FOOT_HALF*1.5]),
        yaxis=dict(title="뒤쪽 (S) <--- 위치 ---> 앞쪽 (W)", range=[-FOOT_HALF*1.5, FOOT_HALF*1.5]),
        width=600, height=500,
        showlegend=True
    )

    plot_ph.plotly_chart(fig, use_container_width=True)

    if is_game_over:
        st.session_state.running = False
        st.error(f"💥 꽈당! 로봇이 중심을 잃고 넘어졌어요! (최종 기록: {st.session_state.time:.1f}초)")
        st.balloons() if st.session_state.time > 15.0 else None
        st.info("💡 **'▶️ 게임 시작!'** 버튼을 눌러서 다시 도전해보세요!")
    else:
        time.sleep(0.1)
        st.rerun()
