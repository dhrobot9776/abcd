import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import random

# ==========================================
# 1. 페이지 설정 (로봇 이모지 적용 🤖)
# ==========================================
st.set_page_config(
    page_title="🤖 로봇 무게중심 잡기 게임",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 로봇 무게중심(CoM) 직접 잡기 게임")
st.markdown("""
불규칙하게 불어오는 **바람(외란)**이 로봇을 계속 밀어냅니다!  
아래 **WASD 방향 버튼**을 눌러 **로봇 무게중심(🟢 CoM)**을 직접 이동시키고, **영모멘트점(❌ ZMP)**이 파란색 발바닥 경계 밖으로 나가지 않게 균형을 잡아주세요!
""")

# ==========================================
# 2. 게임 파라미터 및 세션 초기화
# ==========================================
FOOT_HALF = 0.20   # 발바닥 안전 영역 경계 [-0.2m, +0.2m]
STEP_SIZE = 0.03   # WASD 버튼 1회 클릭당 무게중심 이동 거리

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
# 3. 사이드바 및 컨트롤 패널
# ==========================================
st.sidebar.header("⚙️ 게임 난이도")
WIND_POWER = st.sidebar.slider("바람(외란) 세기", 1.0, 5.0, 2.5, 0.5)

col_start, col_reset, _ = st.columns([1, 1, 3])
with col_start:
    if st.button("▶️ 게임 시작 / 재개", use_container_width=True):
        st.session_state.running = True
with col_reset:
    if st.button("🔄 처음부터 다시하기", use_container_width=True):
        reset_game()
        st.rerun()

# WASD 무게중심 직접 조작 버튼 패드
st.subheader("🎯 WASD 무게중심(CoM) 직접 조작 패드")
pad_col1, pad_col2, pad_col3 = st.columns([1, 1, 1])

with pad_col2:
    if st.button("⬆️ W (앞으로)", use_container_width=True):
        st.session_state.y_com = min(FOOT_HALF, st.session_state.y_com + STEP_SIZE)
with pad_col1:
    if st.button("⬅️ A (왼쪽으로)", use_container_width=True):
        st.session_state.x_com = max(-FOOT_HALF, st.session_state.x_com - STEP_SIZE)
with pad_col2:
    if st.button("🎯 C (중앙 정렬)", use_container_width=True):
        st.session_state.x_com = 0.0
        st.session_state.y_com = 0.0
with pad_col3:
    if st.button("➡️ D (오른쪽으로)", use_container_width=True):
        st.session_state.x_com = min(FOOT_HALF, st.session_state.x_com + STEP_SIZE)
with pad_col2:
    if st.button("⬇️ S (뒤로)", use_container_width=True):
        st.session_state.y_com = max(-FOOT_HALF, st.session_state.y_com - STEP_SIZE)

# 메트릭 및 화면 출력 플레이스홀더
metrics_ph = st.empty()
plot_ph = st.empty()

# ==========================================
# 4. 게임 프레임 루프
# ==========================================
if st.session_state.running:
    # 바람(외란) 무작위 변동 계산
    if random.random() < 0.35:
        st.session_state.wind_x += (random.random() - 0.5) * WIND_POWER * 0.015
        st.session_state.wind_y += (random.random() - 0.5) * WIND_POWER * 0.015
    
    # 바람 저항 감쇠
    st.session_state.wind_x *= 0.93
    st.session_state.wind_y *= 0.93

    # ZMP 계산 = 사용자가 잡은 무게중심(CoM) + 바람 영향
    x_zmp = st.session_state.x_com + st.session_state.wind_x
    y_zmp = st.session_state.y_com + st.session_state.wind_y

    st.session_state.time += 0.1

    # 넘어짐 판정 (ZMP가 발바닥 범위 탈출)
    is_game_over = (abs(x_zmp) > FOOT_HALF or abs(y_zmp) > FOOT_HALF)

    # 메트릭 정보 업데이트
    with metrics_ph.container():
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⏱️ 버틴 시간", f"{st.session_state.time:.1f} 초")
        m2.metric("🟢 무게중심 (CoM)", f"X: {st.session_state.x_com:+.2f}, Y: {st.session_state.y_com:+.2f}")
        m3.metric("❌ 영모멘트점 (ZMP)", f"X: {x_zmp:+.2f}, Y: {y_zmp:+.2f}")
        m4.metric("💨 바람 밀림 영향", f"X: {st.session_state.wind_x:+.2f}, Y: {st.session_state.wind_y:+.2f}")

    # Plotly 2D 실시간 시각화
    fig = go.Figure()

    # 발바닥 안전 영역 (Blue Box)
    fig.add_shape(
        type="rect",
        x0=-FOOT_HALF, y0=-FOOT_HALF, x1=FOOT_HALF, y1=FOOT_HALF,
        fillcolor="rgba(0, 180, 255, 0.15)",
        line=dict(color="DeepSkyBlue", width=4)
    )

    # 🤖 사용자가 제어하는 로봇 무게중심 (CoM)
    fig.add_trace(go.Scatter(
        x=[st.session_state.x_com], y=[st.session_state.y_com],
        mode='markers+text', name='🟢 무게중심 (CoM)',
        text=['🤖 로봇'], textposition="top center",
        marker=dict(size=24, color='SpringGreen', symbol='circle')
    ))

    # ❌ 바람에 의해 밀리는 영모멘트점 (ZMP)
    fig.add_trace(go.Scatter(
        x=[x_zmp], y=[y_zmp],
        mode='markers+text', name='❌ 영모멘트점 (ZMP)',
        text=['❌ ZMP'], textposition="bottom center",
        marker=dict(size=20, color='Crimson', symbol='x')
    ))

    fig.update_layout(
        title="🤖 로봇 발바닥 내 ZMP 지키기 (파란 상자 이탈 시 게임 오버)",
        xaxis=dict(title="좌 / 우 (X축)", range=[-FOOT_HALF*1.5, FOOT_HALF*1.5]),
        yaxis=dict(title="뒤 / 앞 (Y축)", range=[-FOOT_HALF*1.5, FOOT_HALF*1.5]),
        width=600, height=500,
        showlegend=True
    )

    plot_ph.plotly_chart(fig, use_container_width=True)

    if is_game_over:
        st.session_state.running = False
        st.error(f"💥 로봇이 중심을 잃고 넘어졌습니다! (버틴 시간: {st.session_state.time:.1f}초)")
        st.info("💡 다시 도전하려면 상단의 **'🔄 처음부터 다시하기'** 버튼을 누르세요!")
    else:
        time.sleep(0.1)
        st.rerun()
