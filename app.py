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
    1. **입체 휴머노이드 모델**: 가슴 장갑, 머리 헬멧, 무릎/팔꿈치 2단 관절, LED 바이저 센서를 탑재한 3D 입체 메카닉 로봇 모델이 적용되었습니다.
    2. **C 버튼 제한**: C 버튼(중앙 정렬)은 **게임당 딱 3번만 사용 가능한 긴급 스킬**입니다.
    3. **게임 승리 조건**: 바람에 밀려나는 **바닥의 🔴 3D ZMP(영모멘트점)**가 **🟦 3D 파란색 발바닥 영역** 밖으로 나가지 않도록 빠르게 WASD를 눌러 균형을 잡으세요!
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
if 'c_uses' not in st.session_state:
    st.session_state.c_uses = 3

def reset_game():
    st.session_state.running = True
    st.session_state.is_game_over = False
    st.session_state.time = 0.0
    st.session_state.x_com = 0.0
    st.session_state.y_com = 0.0
    st.session_state.vx_com = 0.0
    st.session_state.vy_com = 0.0
    st.session_state.c_uses = 3
    
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

st.subheader("🎮 3D 휴머노이드 조종 리모컨")
p_col1, p_col2, p_col3 = st.columns([1, 1, 1])

if not is_ice_mode:
    with p_col2:
        if st.button("⬆️ W (앞으로 기울이기)", use_container_width=True):
            st.session_state.y_com = min(FOOT_HALF, st.session_state.y_com + STEP_SIZE)
    with p_col1:
        if st.button("⬅️ A (왼쪽으로)", use_container_width=True):
            st.session_state.x_com = max(-FOOT_HALF, st.session_state.x_com - STEP_SIZE)
    with p_col2:
        c_label = f"🎯 C (스킬 남은 횟수: {st.session_state.c_uses})"
        if st.button(c_label, use_container_width=True, disabled=(st.session_state.c_uses <= 0)):
            if st.session_state.c_uses > 0:
                st.session_state.x_com, st.session_state.y_com = 0.0, 0.0
                st.session_state.c_uses -= 1
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
        c_label = f"🛑 C (브레이크 남은 횟수: {st.session_state.c_uses})"
        if st.button(c_label, use_container_width=True, disabled=(st.session_state.c_uses <= 0)):
            if st.session_state.c_uses > 0:
                st.session_state.vx_com, st.session_state.vy_com = 0.0, 0.0
                st.session_state.c_uses -= 1
    with p_col3:
        if st.button("➡️ D (우 추진력)", use_container_width=True):
            st.session_state.vx_com += STEP_SIZE
    with p_col2:
        if st.button("⬇️ S (뒤 추진력)", use_container_width=True):
            st.session_state.vy_com -= STEP_SIZE

# 3D 입체 장갑 박스 생성 함수
def create_3d_box(cx, cy, cz, dx, dy, dz, color, opacity=0.85, name=""):
    x = [cx-dx, cx+dx, cx+dx, cx-dx, cx-dx, cx+dx, cx+dx, cx-dx]
    y = [cy-dy, cy-dy, cy+dy, cy+dy, cy-dy, cy-dy, cy+dy, cy+dy]
    z = [cz-dz, cz-dz, cz-dz, cz-dz, cz+dz, cz+dz, cz+dz, cz+dz]
    i = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
    j = [1, 2, 5, 6, 1, 5, 2, 6, 4, 7, 5, 6]
    k = [2, 3, 6, 7, 5, 4, 6, 7, 7, 3, 6, 2]
    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=opacity, name=name, showlegend=False)

# ==========================================
# 5. 프래그먼트 엔진 (@st.fragment)
# ==========================================
@st.fragment(run_every=0.2)
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

    st.session_state.time += 0.2

    time_factor = 1.0 + (st.session_state.time * 0.03)
    current_wind_power = BASE_WIND_POWER * time_factor

    st.session_state.wind_x += (random.random() - 0.48) * current_wind_power * 0.035
    st.session_state.wind_y += (random.random() - 0.48) * current_wind_power * 0.035
    
    st.session_state.wind_x *= 0.98
    st.session_state.wind_y *= 0.98

    if is_ice_mode:
        st.session_state.x_com += st.session_state.vx_com
        st.session_state.y_com += st.session_state.vy_com
        st.session_state.vx_com *= 0.88
        st.session_state.vy_com *= 0.88

    x_zmp = st.session_state.x_com + st.session_state.wind_x
    y_zmp = st.session_state.y_com + st.session_state.wind_y

    if abs(x_zmp) > FOOT_HALF or abs(y_zmp) > FOOT_HALF:
        st.session_state.running = False
        st.session_state.is_game_over = True

    # 전광판
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ 버틴 시간", f"{st.session_state.time:.1f} 초")
    m2.metric("🌪️ 바람 세기", f"{current_wind_power:.2f}x")
    m3.metric("🟢 로봇 무게중심(CoM)", f"X: {st.session_state.x_com:+.2f} | Y: {st.session_state.y_com:+.2f}")
    m4.metric("🔴 3D ZMP 위치", f"X: {x_zmp:+.2f} | Y: {y_zmp:+.2f}")

    # ==========================================
    # 6. 정밀 3D 휴머노이드 Kinematics 좌표 연산
    # ==========================================
    xc, yc = st.session_state.x_com, st.session_state.y_com
    
    # 1) 발바닥 및 무릎 (2단 다리 관절)
    left_foot = [-0.08, 0.0, 0.01]
    right_foot = [0.08, 0.0, 0.01]
    
    left_knee = [-0.075 + xc * 0.4, yc * 0.4, 0.18]
    right_knee = [0.075 + xc * 0.4, yc * 0.4, 0.18]

    # 2) 골반 및 상체 (무게중심 기울임)
    hip_center = [xc, yc, 0.36]
    hip_left = [xc - 0.07, yc, 0.36]
    hip_right = [xc + 0.07, yc, 0.36]

    chest = [xc * 1.3, yc * 1.3, 0.58]
    shoulder_left = [xc * 1.3 - 0.13, yc * 1.3, 0.58]
    shoulder_right = [xc * 1.3 + 0.13, yc * 1.3, 0.58]

    # 3) 팔 관절 (어깨 -> 팔꿈치 -> 손)
    elbow_left = [xc * 1.4 - 0.17, yc * 1.4 - 0.04, 0.45]
    elbow_right = [xc * 1.4 + 0.17, yc * 1.4 - 0.04, 0.45]
    hand_left = [xc * 1.5 - 0.20, yc * 1.5 - 0.09, 0.35]
    hand_right = [xc * 1.5 + 0.20, yc * 1.5 - 0.09, 0.35]

    # 4) 머리 및 LED 센서 바이저
    head = [xc * 1.45, yc * 1.45, 0.73]
    visor = [xc * 1.50, yc * 1.50 + 0.03, 0.73]

    fig = go.Figure()

    # 🟦 A. 지면 3D 발바닥 영역 (Support Polygon)
    bx = [-FOOT_HALF, FOOT_HALF, FOOT_HALF, -FOOT_HALF, -FOOT_HALF]
    by = [-FOOT_HALF, -FOOT_HALF, FOOT_HALF, FOOT_HALF, -FOOT_HALF]
    bz = [0, 0, 0, 0, 0]
    fig.add_trace(go.Scatter3d(
        x=bx, y=by, z=bz, mode='lines', name='🟦 3D 발바닥 영역',
        line=dict(color='DeepSkyBlue', width=8)
    ))

    # 🤖 B. 3D 휴머노이드 솔리드 장갑 (Mesh3D 메쉬 파트)
    # B-1) 가슴 체스트 장갑 (시안 블루 메탈)
    fig.add_trace(create_3d_box(chest[0], chest[1], chest[2], 0.09, 0.06, 0.07, color='#00D2FF', opacity=0.9, name='가슴 장갑'))
    # B-2) 골반 장갑 (다크 스틸)
    fig.add_trace(create_3d_box(hip_center[0], hip_center[1], hip_center[2], 0.07, 0.05, 0.04, color='#34495E', opacity=0.95, name='골반 메쉬'))
    # B-3) 머리 헬멧 (화이트 메탈)
    fig.add_trace(create_3d_box(head[0], head[1], head[2], 0.05, 0.05, 0.05, color='#ECEFF1', opacity=0.95, name='머리 헬멧'))
    # B-4) 양발 3D 신발 플레이트
    fig.add_trace(create_3d_box(left_foot[0], left_foot[1], left_foot[2], 0.03, 0.07, 0.015, color='#1A252F', opacity=1.0))
    fig.add_trace(create_3d_box(right_foot[0], right_foot[1], right_foot[2], 0.03, 0.07, 0.015, color='#1A252F', opacity=1.0))

    # 🦾 C. 3D 프레임 관절 뼈대 (Double Segment Limbs)
    skeleton_lines = [
        # 왼다리 (발목 -> 무릎 -> 골반)
        [left_foot, left_knee], [left_knee, hip_left],
        # 오른다리 (발목 -> 무릎 -> 골반)
        [right_foot, right_knee], [right_knee, hip_right],
        # 골반 프레임 & 척추
        [hip_left, hip_right], [hip_center, chest], [chest, head],
        # 어깨 & 왼팔/오른팔 (어깨 -> 팔꿈치 -> 손)
        [shoulder_left, shoulder_right],
        [shoulder_left, elbow_left], [elbow_left, hand_left],
        [shoulder_right, elbow_right], [elbow_right, hand_right]
    ]

    for line in skeleton_lines:
        fig.add_trace(go.Scatter3d(
            x=[line[0][0], line[1][0]], y=[line[0][1], line[1][1]], z=[line[0][2], line[1][2]],
            mode='lines', showlegend=False, line=dict(color='#00F5FF', width=7)
        ))

    # 🟢 D. 관절 노드 & LED 센서
    # 관절 볼 마커 (어깨, 팔꿈치, 무릎, 손)
    joint_nodes_x = [shoulder_left[0], shoulder_right[0], elbow_left[0], elbow_right[0], left_knee[0], right_knee[0], hand_left[0], hand_right[0]]
    joint_nodes_y = [shoulder_left[1], shoulder_right[1], elbow_left[1], elbow_right[1], left_knee[1], right_knee[1], hand_left[1], hand_right[1]]
    joint_nodes_z = [shoulder_left[2], shoulder_right[2], elbow_left[2], elbow_right[2], left_knee[2], right_knee[2], hand_left[2], hand_right[2]]

    fig.add_trace(go.Scatter3d(
        x=joint_nodes_x, y=joint_nodes_y, z=joint_nodes_z, mode='markers', name='🤖 관절 노드',
        marker=dict(size=7, color='#10B981', symbol='circle')
    ))

    # 머리 붉은색 LED 탐지 바이저 (Eye Sensor)
    fig.add_trace(go.Scatter3d(
        x=[visor[0]], y=[visor[1]], z=[visor[2]], mode='markers', name='🔴 LED 바이저',
        marker=dict(size=9, color='#FF1744', symbol='diamond')
    ))

    # 🔴 E. 바닥 투영 ZMP (영모멘트점)
    fig.add_trace(go.Scatter3d(
        x=[x_zmp], y=[y_zmp], z=[0], mode='markers+text', name='🔴 3D ZMP (영모멘트점)',
        text=['🔴 ZMP'], textposition="top center",
        marker=dict(size=12, color='Crimson', symbol='diamond')
    ))

    fig.update_layout(
        title=f"🤖 [{DIFFICULTY}] 입체 휴머노이드 로봇 시뮬레이터",
        scene=dict(
            xaxis=dict(title="X축 (좌/우)", range=[-0.35, 0.35]),
            yaxis=dict(title="Y축 (뒤/앞)", range=[-0.35, 0.35]),
            zaxis=dict(title="Z축 (높이)", range=[0, 0.85]),
            aspectmode='cube',
            camera=dict(eye=dict(x=1.3, y=-1.4, z=0.9))
        ),
        height=580,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    st.plotly_chart(fig, use_container_width=True)

render_game_fragment()
