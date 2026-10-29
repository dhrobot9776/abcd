import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import random

# ==========================================
# 1. 페이지 및 타이틀 설정 🤖
# ==========================================
st.set_page_config(
    page_title="🤖 3D 휴머노이드 로봇 중심 잡기 게임",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 3D 휴머노이드 로봇 균형 제어 시뮬레이터")

# ==========================================
# 2. 튜토리얼 / 안내
# ==========================================
with st.expander("📖 **[3D 게임 조작법 및 안내] (클릭해서 열기/접기)**", expanded=False):
    st.markdown("""
    ### 🎮 3D 시뮬레이션 주요 안내
    1. **3D 로봇 관절**: 로봇이 몸(무게중심)을 기울이면 **머리, 팔, 다리 관절이 3D 공간상에서 함께 실시간으로 기울어집니다!**
    2. **3D 시점 조절**: 오른쪽 3D 화면을 마우스로 **드래그하여 3D 카메라 회전 및 확대/축소**가 가능합니다.
    3. **게임 승리 조건**: 바람(외란)에 밀리는 **바닥의 🔴 3D ZMP(영모멘트점)**가 **🟦 3D 파란색 발바닥 영역** 밖으로 나가지 않도록 **WASD 리모컨**으로 3D 로봇의 몸을 제어하세요!
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

# 모드별 기본 설정값
FOOT_HALF = 0.20
STEP_SIZE = 0.04
is_ice_mode = False

if "🔥 극한" in DIFFICULTY:
    FOOT_HALF = 0.10  # 발바닥 축소
if "🧊 빙판길" in DIFFICULTY:
    is_ice_mode = True
    STEP_SIZE = 0.015

diff_power_map = {
    "🍃 쉬움": 1.2,
    "💨 보통": 2.2,
    "🌪️ 어려움": 3.5,
    "💥 지옥 (강풍+가속)": 5.0,
    "🔥 극한 (외발 서기)": 3.0,
    "🧊 빙판길 (관성 미끄러짐)": 2.5
}
BASE_WIND_POWER = diff_power_map[DIFFICULTY]

if 'running' not in st.session_state:
    st.session_state.running = False
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
    st.session_state.time = 0.0
    st.session_state.x_com = 0.0
    st.session_state.y_com = 0.0
    st.session_state.vx_com = 0.0
    st.session_state.vy_com = 0.0
    st.session_state.wind_x = 0.0
    st.session_state.wind_y = 0.0

# ==========================================
# 4. 상단 컨트롤 패널 및 WASD 조종판
# ==========================================
col_s1, col_s2, _ = st.columns([1.5, 1.5, 3])
with col_s1:
    if st.button("▶️ 게임 시작!", use_container_width=True, type="primary"):
        reset_game()
        st.rerun()
with col_s2:
    if st.button("🔄 다시 하기", use_container_width=True):
        reset_game()
        st.rerun()

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
    with p_col3:
        if st.button("➡️ D (우 추진력)", use_container_width=True):
            st.session_state.vx_com += STEP_SIZE
    with p_col2:
        if st.button("⬇️ S (뒤 추진력)", use_container_width=True):
            st.session_state.vy_com -= STEP_SIZE

metrics_ph = st.empty()
plot_ph = st.empty()

# ==========================================
# 5. 게임 엔진 및 3D 그래픽 렌더링
# ==========================================
if st.session_state.running:
    st.session_state.time += 0.1

    time_factor = 1.0 + (st.session_state.time * 0.02)
    current_wind_power = BASE_WIND_POWER * time_factor

    gust_x, gust_y = 0.0, 0.0
    if random.random() < 0.08:
        gust_x = (random.random() - 0.5) * current_wind_power * 0.08
        gust_y = (random.random() - 0.5) * current_wind_power * 0.08

    if random.random() < 0.45:
        st.session_state.wind_x += (random.random() - 0.5) * current_wind_power * 0.018 + gust_x
        st.session_state.wind_y += (random.random() - 0.5) * current_wind_power * 0.018 + gust_y
    
    st.session_state.wind_x *= 0.91
    st.session_state.wind_y *= 0.91

    if is_ice_mode:
        st.session_state.x_com += st.session_state.vx_com
        st.session_state.y_com += st.session_state.vy_com
        st.session_state.vx_com *= 0.88
        st.session_state.vy_com *= 0.88

    x_zmp = st.session_state.x_com + st.session_state.wind_x
    y_zmp = st.session_state.y_com + st.session_state.wind_y

    is_game_over = (abs(x_zmp) > FOOT_HALF or abs(y_zmp) > FOOT_HALF)

    with metrics_ph.container():
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⏱️ 버틴 시간", f"{st.session_state.time:.1f} 초")
        m2.metric("🌪️ 바람 세기", f"{current_wind_power:.2f}x")
        m3.metric("🟢 로봇 무게중심(CoM)", f"X: {st.session_state.x_com:+.2f} | Y: {st.session_state.y_com:+.2f}")
        m4.metric("🔴 3D ZMP 위치", f"X: {x_zmp:+.2f} | Y: {y_zmp:+.2f}")

    # ==========================================
    # 6. 3D 로봇 동역학 뼈대 및 관절 좌표 연산
    # ==========================================
    xc, yc = st.session_state.x_com, st.session_state.y_com
    
    # 3D 관절 좌표 정의 (Height Z)
    z_foot = 0.0
    z_hip = 0.35
    z_chest = 0.55
    z_head = 0.70

    # 발바닥 고정 위치 (왼발, 오른발)
    left_foot = [-0.07, 0, z_foot]
    right_foot = [0.07, 0, z_foot]

    # 골반/허리 (무게중심 연동)
    hip_center = [xc, yc, z_hip]
    hip_left = [xc - 0.06, yc, z_hip]
    hip_right = [xc + 0.06, yc, z_hip]

    # 가슴 및 머리 (상체 기울임 연동)
    chest = [xc * 1.25, yc * 1.25, z_chest]
    head = [xc * 1.45, yc * 1.45, z_head]

    # 어깨 및 손 관절
    shoulder_left = [xc * 1.25 - 0.12, yc * 1.25, z_chest]
    shoulder_right = [xc * 1.25 + 0.12, yc * 1.25, z_chest]
    hand_left = [xc * 1.35 - 0.18, yc * 1.35 - 0.08, z_chest - 0.12]
    hand_right = [xc * 1.35 + 0.18, yc * 1.35 - 0.08, z_chest - 0.12]

    fig = go.Figure()

    # 1) 3D 발바닥 지지 영역 (바닥 파란 상자)
    bx = [-FOOT_HALF, FOOT_HALF, FOOT_HALF, -FOOT_HALF, -FOOT_HALF]
    by = [-FOOT_HALF, -FOOT_HALF, FOOT_HALF, FOOT_HALF, -FOOT_HALF]
    bz = [0, 0, 0, 0, 0]
    fig.add_trace(go.Scatter3d(
        x=bx, y=by, z=bz,
        mode='lines',
        name='🟦 3D 발바닥 영역',
        line=dict(color='DeepSkyBlue', width=8)
    ))

    # 2) 3D 로봇 뼈대 (선 연결)
    skeleton_lines = [
        # 왼다리, 오른다리, 골반
        [left_foot, hip_left], [right_foot, hip_right], [hip_left, hip_right],
        # 척추 (골반 -> 가슴 -> 머리)
        [hip_center, chest], [chest, head],
        # 어깨 및 팔
        [shoulder_left, shoulder_right], [shoulder_left, hand_left], [shoulder_right, hand_right]
    ]

    for line in skeleton_lines:
        fig.add_trace(go.Scatter3d(
            x=[line[0][0], line[1][0]],
            y=[line[0][1], line[1][1]],
            z=[line[0][2], line[1][2]],
            mode='lines',
            showlegend=False,
            line=dict(color='Turquoise', width=7)
        ))

    # 3) 3D 로봇 주요 관절 및 머리 (구형 마커)
    joints_x = [head[0], chest[0], hip_center[0], hand_left[0], hand_right[0], left_foot[0], right_foot[0]]
    joints_y = [head[1], chest[1], hip_center[1], hand_left[1], hand_right[1], left_foot[1], right_foot[1]]
    joints_z = [head[2], chest[2], hip_center[2], hand_left[2], hand_right[2], left_foot[2], right_foot[2]]
    
    fig.add_trace(go.Scatter3d(
        x=joints_x, y=joints_y, z=joints_z,
        mode='markers',
        name='🤖 3D 로봇 관절',
        marker=dict(size=[16, 10, 12, 8, 8, 10, 10], color='SpringGreen', symbol='circle')
    ))

    # 4) 3D ZMP (바닥에 투영된 영모멘트점)
    fig.add_trace(go.Scatter3d(
        x=[x_zmp], y=[y_zmp], z=[0],
        mode='markers+text',
        name='🔴 3D ZMP (영모멘트점)',
        text=['🔴 ZMP'], textposition="top center",
        marker=dict(size=12, color='Crimson', symbol='diamond')
    ))

    # 3D 카메라 및 레이아웃 설정
    fig.update_layout(
        title=f"🤖 [{DIFFICULTY}] 3D 휴머노이드 로봇 시뮬레이터",
        scene=dict(
            xaxis=dict(title="X축 (좌/우)", range=[-0.35, 0.35]),
            yaxis=dict(title="Y축 (뒤/앞)", range=[-0.35, 0.35]),
            zaxis=dict(title="Z축 (높이)", range=[0, 0.85]),
            aspectmode='cube',
            camera=dict(
                eye=dict(x=1.3, y=-1.4, z=0.9)  # 3D 입체 카메라 시점
            )
        ),
        height=550,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    plot_ph.plotly_chart(fig, use_container_width=True)

    if is_game_over:
        st.session_state.running = False
        st.error(f"💥 3D 로봇이 균형을 잃고 넘어졌습니다! (버틴 시간: {st.session_state.time:.1f}초)")
        if st.session_state.time > 20.0:
            st.balloons()
            st.success("🎉 대단합니다! 3D 시뮬레이션에서 20초 이상 생존하셨습니다!")
    else:
        time.sleep(0.1)
        st.rerun()
