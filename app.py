import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import time
import random
import math

# ==========================================
# 1. 스트림릿 페이지 설정 및 기본 레이아웃
# ==========================================
st.set_page_config(
    page_title="ZMP 휴머노이드 로봇 균형 제어 시뮬레이터",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 2-DOF ZMP 휴머노이드 로봇 균형 제어 웹 시뮬레이터")
st.markdown("""
**로봇동역학 핵심 원리**: 로봇의 영모멘트점(ZMP)이 발바닥 지지 영역(Support Polygon) 범위 내부(**파란색 사각형**)에 위치해야 넘어지지 않고 균형을 유지합니다.
""")

# ==========================================
# 2. 사이드바 설정 (물리 파라미터 & 제어 옵션)
# ==========================================
st.sidebar.header("⚙️ 시뮬레이션 설정")

control_mode = st.sidebar.radio("제어 모드 선택", ["PID 자동 제어 모드", "수동 방향키 제어 모드"])

st.sidebar.subheader("📐 로봇 물리 파라미터")
MASS = st.sidebar.slider("로봇 질량 (m, kg)", 5.0, 20.0, 10.0, 0.5)
LEG_L = st.sidebar.slider("다리 길이 (L, m)", 0.5, 1.5, 1.0, 0.1)
FOOT_HALF = st.sidebar.slider("발바닥 반폭 (m)", 0.10, 0.30, 0.20, 0.02)
GRAVITY = 9.81
DT = 0.05

st.sidebar.subheader("💨 환경 변수 (바람 외란)")
WIND_STRENGTH = st.sidebar.slider("최대 바람 세기 (N)", 0.0, 40.0, 20.0, 2.0)

# PID 제어 파라미터 (자동 제어 모드용)
if control_mode == "PID 자동 제어 모드":
    st.sidebar.subheader("🕹️ PID 제어 게인")
    KP = st.sidebar.slider("비례 게인 (Kp)", 0.0, 500.0, 220.0, 10.0)
    KD = st.sidebar.slider("미분 게인 (Kd)", 0.0, 100.0, 35.0, 2.0)

# ==========================================
# 3. 세션 상태(Session State) 초기화
# ==========================================
if 'running' not in st.session_state:
    st.session_state.running = False
if 'time' not in st.session_state:
    st.session_state.time = 0.0
if 'theta_x' not in st.session_state:
    st.session_state.theta_x = 0.03
if 'omega_x' not in st.session_state:
    st.session_state.omega_x = 0.0
if 'theta_y' not in st.session_state:
    st.session_state.theta_y = 0.02
if 'omega_y' not in st.session_state:
    st.session_state.omega_y = 0.0
if 'history' not in st.session_state:
    st.session_state.history = []

def reset_simulation():
    st.session_state.running = False
    st.session_state.time = 0.0
    st.session_state.theta_x = 0.03
    st.session_state.omega_x = 0.0
    st.session_state.theta_y = 0.02
    st.session_state.omega_y = 0.0
    st.session_state.history = []

# ==========================================
# 4. 제어 버튼 레이아웃
# ==========================================
col_btn1, col_btn2, _ = st.columns([1, 1, 4])
with col_btn1:
    if st.button("▶️ 시뮬레이션 시작 / 재개"):
        st.session_state.running = True
with col_btn2:
    if st.button("🔄 초기화"):
        reset_simulation()
        st.rerun()

# 수동 제어 시 입력 슬라이더/버튼
manual_tau_x, manual_tau_y = 0.0, 0.0
if control_mode == "수동 방향키 제어 모드":
    st.subheader("🎮 수동 복원 토크 제어")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        manual_tau_x = st.slider("좌/우 복원 토크 (A/D)", -30.0, 30.0, 0.0, 1.0)
    with col_m2:
        manual_tau_y = st.slider("전/후 복원 토크 (W/S)", -30.0, 30.0, 0.0, 1.0)

# 시각화용 플레이스홀더 설정
metrics_placeholder = st.empty()
plot_placeholder = st.empty()
chart_placeholder = st.empty()

# ==========================================
# 5. 시뮬레이션 대시보드 루프 Engine
# ==========================================
if st.session_state.running:
    # 물리 상태 복원
    t = st.session_state.time
    tx, ox = st.session_state.theta_x, st.session_state.omega_x
    ty, oy = st.session_state.theta_y, st.session_state.omega_y

    # 무작위 외란(바람) 발생
    f_ext_x = (random.random() - 0.5) * WIND_STRENGTH
    f_ext_y = (random.random() - 0.5) * WIND_STRENGTH

    # 복원 토크 산출
    if control_mode == "PID 자동 제어 모드":
        # PID 피드백 제어: 기울기 각도 및 각속도를 줄이는 방향으로 토크 생성
        tau_x = - (KP * tx + KD * ox)
        tau_y = - (KP * ty + KD * oy)
    else:
        tau_x = manual_tau_x
        tau_y = manual_tau_y

    # 수치해석 동역학 계산 (오일러 방법)
    alpha_x = (MASS * GRAVITY * LEG_L * math.sin(tx) + tau_x + f_ext_x * LEG_L * math.cos(tx)) / (MASS * LEG_L**2)
    ox += alpha_x * DT
    tx += ox * DT

    alpha_y = (MASS * GRAVITY * LEG_L * math.sin(ty) + tau_y + f_ext_y * LEG_L * math.cos(ty)) / (MASS * LEG_L**2)
    oy += alpha_y * DT
    ty += oy * DT

    # CoM 및 ZMP 위치 산출
    x_com = LEG_L * math.sin(tx)
    y_com = LEG_L * math.sin(ty)
    z_com = LEG_L * math.cos(tx) * math.cos(ty)

    x_com_ddot = LEG_L * (alpha_x * math.cos(tx) - (ox**2) * math.sin(tx))
    y_com_ddot = LEG_L * (alpha_y * math.cos(ty) - (oy**2) * math.sin(ty))

    x_zmp = x_com - (z_com / GRAVITY) * x_com_ddot
    y_zmp = y_com - (z_com / GRAVITY) * y_com_ddot

    t += DT

    # 상태 저장
    st.session_state.time = t
    st.session_state.theta_x, st.session_state.omega_x = tx, ox
    st.session_state.theta_y, st.session_state.omega_y = ty, oy
    st.session_state.history.append({
        'time': t, 'x_zmp': x_zmp, 'y_zmp': y_zmp, 
        'x_com': x_com, 'y_com': y_com, 'roll_deg': math.degrees(tx), 'pitch_deg': math.degrees(ty)
    })

    # 넘어짐 판정
    is_fallen = abs(x_zmp) > FOOT_HALF or abs(y_zmp) > FOOT_HALF or abs(tx) > 0.8 or abs(ty) > 0.8
    if is_fallen:
        st.session_state.running = False

    # 1) 메트릭 카드 출력
    with metrics_placeholder.container():
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("생존 시간", f"{t:.2f} 초")
        m2.metric("기울기 (Roll / Pitch)", f"{math.degrees(tx):+.1f}° / {math.degrees(ty):+.1f}°")
        m3.metric("ZMP 위치 (X, Y)", f"{x_zmp:+.3f}m, {y_zmp:+.3f}m")
        m4.metric("바람 외란 (X, Y)", f"{f_ext_x:+.1f}N, {f_ext_y:+.1f}N")

    # 2) 2D 발바닥 지지 영역 및 ZMP Plotly 시각화
    fig = go.Figure()

    # 발바닥 지지 다각형 (Support Polygon)
    fig.add_shape(
        type="rect",
        x0=-FOOT_HALF, y0=-FOOT_HALF, x1=FOOT_HALF, y1=FOOT_HALF,
        fillcolor="rgba(0, 150, 255, 0.15)",
        line=dict(color="DeepSkyBlue", width=3)
    )

    # 궤적 이력 추적
    if len(st.session_state.history) > 0:
        df_hist = pd.DataFrame(st.session_state.history)
        fig.add_trace(go.Scatter(
            x=df_hist['x_zmp'], y=df_hist['y_zmp'],
            mode='lines', name='ZMP 궤적 이력',
            line=dict(color='rgba(255, 99, 132, 0.4)', width=2)
        ))

    # CoM 및 ZMP 현재 점
    fig.add_trace(go.Scatter(
        x=[x_com], y=[y_com], mode='markers', name='CoM (무게중심)',
        marker=dict(size=14, color='MediumSpringGreen', symbol='circle')
    ))
    fig.add_trace(go.Scatter(
        x=[x_zmp], y=[y_zmp], mode='markers', name='ZMP (영모멘트점)',
        marker=dict(size=16, color='Crimson', symbol='x')
    ))

    fig.update_layout(
        title="2D 발바닥 영역 내 ZMP / CoM 위치 변화",
        xaxis=dict(title="X축 (Roll, m)", range=[-FOOT_HALF*1.6, FOOT_HALF*1.6]),
        yaxis=dict(title="Y축 (Pitch, m)", range=[-FOOT_HALF*1.6, FOOT_HALF*1.6]),
        width=700, height=500,
        showlegend=True
    )
    plot_placeholder.plotly_chart(fig, use_container_width=True)

    # 3) 시간에 따른 ZMP 시계열 그래프
    if len(st.session_state.history) > 1:
        df_hist = pd.DataFrame(st.session_state.history)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df_hist['time'], y=df_hist['x_zmp'], name='X_ZMP (좌우)', line=dict(color='LightSkyBlue')))
        fig_line.add_trace(go.Scatter(x=df_hist['time'], y=df_hist['y_zmp'], name='Y_ZMP (전후)', line=dict(color='Orange')))
        fig_line.add_hline(y=FOOT_HALF, line_dash="dash", line_color="red", annotation_text="+상한 경계")
        fig_line.add_hline(y=-FOOT_HALF, line_dash="dash", line_color="red", annotation_text="-하한 경계")
        fig_line.update_layout(title="시간에 따른 ZMP 좌표 수렴 특성 그래프", xaxis_title="시간 (s)", yaxis_title="위치 (m)", height=300)
        chart_placeholder.plotly_chart(fig_line, use_container_width=True)

    if is_fallen:
        st.error(f"💥 로봇이 균형을 잃고 넘어졌습니다! (생존 시간: {t:.2f}초)")
    else:
        time.sleep(DT)
        st.rerun()
