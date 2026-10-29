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
    with p_col3:
        if st.button("➡️ D (우 추진력)", use_container_width=True):
            st.session_state.vx_com += STEP_SIZE
    with p_col2:
        if st.button("⬇️ S (뒤 추진력)", use_container_width=True):
            st.session_state.vy_com -= STEP_SIZE

# ==========================================
# 5. 프래그먼트 엔진 (@st.fragment)
# ==========================================
@st.fragment(run_every=0.1)
def render_game_fragment():
    if not st.session_state.running:
        if st.session_state.is_game_over:
            st.error(f"💥 3D 로봇이 중심을 잃고 넘어졌습니다! (최종 생존 시간: {st.session_state.time:.1f}초)")
            if st.session_state.time >= 15.0:
                st.balloons()
                st.success(f"🎉 대단합니다! {st.session_state.time:.1f}초 동안 성공적으로 균형을 잡으셨습니다!")
            else:
                st.info("💡 다시 도전하려면 상단의 **'▶️ 게임 시작!'** 버튼을 누르세요!")
        else:
            st.info("💡 상단의 **'▶️ 게임 시작!'** 버튼을 누르면 3D 시뮬레이션이 시작됩니다.")
        return

    st.session_state.time += 0.1

    # 시간이 지날수록 바람 가속
    time_factor = 1.0 + (st.session_state.time * 0.03)
    current_wind_power = BASE_WIND_POWER * time_factor

    # 강한 지속 바람 누적 계산
    st.session_state.wind_x += (random.random() - 0.48) * current_wind_power * 0.025
    st.session_state.wind_y += (random.random() - 0.48) * current_wind_power * 0.025
    
    # 바람 감소율을 0.98로 낮추어 바람 밀림 지속력 대폭 상승
    st.session_state.wind_x *= 0.98
    st.session_state.wind_y *= 0.98

    if is_ice_mode:
        st.session_state.x_com += st.session_state.vx_com
        st.session_state.y_com += st.session_state.vy_com
        st.session_state.vx_com *= 0.88
        st.session_state.vy_com *= 0.88

    x_zmp = st.session_state.x_com + st.session_state.wind_x
    y_zmp = st.session_state.y_com + st.session_state.wind_y

    # 넘어짐 판정
    if abs(x_zmp) > FOOT_HALF or abs(y_zmp) > FOOT_HALF:
        st.session_state.running = False
        st.session_state.is_game_over = True

    # 수치 전광판
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ 버틴 시간", f"{st.session_state.time:.1f} 초")
    m2.metric("🌪️ 바람 세기", f"{current_wind_power:.2f}x")
    m3.metric("🟢 로봇 무게중심(CoM)", f"X: {st.session_state.x_com:+.2f} | Y: {st.session_state.y_com:+.2f}")
    m4.metric("🔴 3D ZMP 위치", f"X: {x_zmp:+.2f} | Y: {y_zmp:+.2f}")

    # 3D 관절 연산
    xc, yc = st.session_state.x_com, st.session_state.y_com
    z_foot, z_hip, z_chest, z_head = 0.0, 0.35, 0.55, 0.70

    left_foot, right_foot = [-0.07, 0, z_foot], [0.07, 0, z_foot]
    hip_center, hip_left, hip_right = [xc, yc, z_hip], [xc - 0.06, yc, z_hip], [xc + 0.06, yc, z_hip]
    chest, head = [xc * 1.25, yc * 1.25, z_chest], [xc * 1.45, yc * 1.45, z_head]

    shoulder_left, shoulder_right = [xc * 1.25 - 0.12, yc * 1.25, z_chest], [xc * 1.25 + 0.12, yc * 1.25, z_chest]
    hand_left, hand_right = [xc * 1.35 - 0.18, yc * 1.35 - 0.08, z_chest - 0.12], [xc * 1.35 + 0.18, yc * 1.35 - 0.08, z_chest - 0.12]

    fig = go.Figure()

    # 3D 발바닥 영역
    bx = [-FOOT_HALF, FOOT_HALF, FOOT_HALF, -FOOT_HALF, -FOOT_HALF]
    by = [-FOOT_HALF, -FOOT_HALF, FOOT_HALF, FOOT_HALF, -FOOT_HALF]
    bz = [0, 0, 0, 0, 0]
    fig.add_trace(go.Scatter3d(
        x=bx, y=by, z=bz, mode='lines', name='🟦 3D 발바닥 영역',
        line=dict(color='DeepSkyBlue', width=8)
    ))

    # 3D 뼈대
    skeleton_lines = [
        [left_foot, hip_left], [right_foot, hip_right], [hip_left, hip_right],
        [hip_center, chest], [chest, head],
        [shoulder_left, shoulder_right], [shoulder_left, hand_left], [shoulder_right, hand_right]
    ]

    for line in skeleton_lines:
        fig.add_trace(go.Scatter3d(
            x=[line[0][0], line[1][0]], y=[line[0][1], line[1][1]], z=[line[0][2], line[1][2]],
            mode='lines', showlegend=False, line=dict(color='Turquoise', width=7)
        ))

    # 3D 관절
    joints_x = [head[0], chest[0], hip_center[0], hand_left[0], hand_right[0], left_foot[0], right_foot[0]]
    joints_y = [head[1], chest[1], hip_center[1], hand_left[1], hand_right[1], left_foot[1], right_foot[1]]
    joints_z = [head[2], chest[2], hip_center[2], hand_left[2], hand_right[2], left_foot[2], right_foot[2]]
    
    fig.add_trace(go.Scatter3d(
        x=joints_x, y=joints_y, z=joints_z, mode='markers', name='🤖 3D 로봇 관절',
        marker=dict(size=[16, 10, 12, 8, 8, 10, 10], color='SpringGreen', symbol='circle')
    ))

    # 3D ZMP
    fig.add_trace(go.Scatter3d(
        x=[x_zmp], y=[y_zmp], z=[0], mode='markers+text', name='🔴 3D ZMP (영모멘트점)',
        text=['🔴 ZMP'], textposition="top center",
        marker=dict(size=12, color='Crimson', symbol='diamond')
    ))

    fig.update_layout(
        title=f"🤖 [{DIFFICULTY}] 3D 휴머노이드 로봇 시뮬레이터",
        scene=dict(
            xaxis=dict(title="X축 (좌/우)", range=[-0.35, 0.35]),
            yaxis=dict(title="Y축 (뒤/앞)", range=[-0.35, 0.35]),
            zaxis=dict(title="Z축 (높이)", range=[0, 0.85]),
            aspectmode='cube',
            camera=dict(eye=dict(x=1.3, y=-1.4, z=0.9))
        ),
        height=550,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    st.plotly_chart(fig, use_container_width=True)

render_game_fragment()
