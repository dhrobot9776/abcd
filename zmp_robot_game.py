import sys
import math
import random
import pygame

# ==========================================
# 1. 공학적 물리 상수 및 시뮬레이션 설정
# ==========================================
GRAVITY = 9.81         # 중력 가속도 (m/s^2)
LEG_L = 1.0            # 로봇 다리 길이 (m)
MASS = 10.0            # 로봇 질량 (kg)
FOOT_X_HALF = 0.20     # 좌우 발바닥 반폭 (m)  -> [-0.2m, +0.2m]
FOOT_Y_HALF = 0.20     # 전후 발바닥 반길이 (m) -> [-0.2m, +0.2m]
DT = 0.02              # 시뮬레이션 타임스텝 (50 FPS)

# 화면 및 그래픽 관련 설정
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
CENTER_X = 450
CENTER_Y = 320
SCALE = 700            # 미터(m)를 피셀(px)로 변환하는 스케일 비율

# 색상 정의
COLOR_BG = (20, 24, 33)
COLOR_FOOT = (40, 50, 70)
COLOR_FOOT_BORDER = (0, 200, 255)
COLOR_COM = (0, 255, 120)     # 무게중심 (초록색)
COLOR_ZMP = (255, 50, 80)     # 영모멘트점 (빨간색)
COLOR_TEXT = (220, 225, 235)
COLOR_GRID = (35, 42, 58)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2-DOF ZMP Humanoid Balance Simulator")
    clock = pygame.time.Clock()

    # 폰트 설정
    font_large = pygame.font.SysFont("malgungothic", 28, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 16)

    # 상태 변수 초기화 (Roll: X축, Pitch: Y축)
    theta_x, omega_x = 0.03, 0.0
    theta_y, omega_y = 0.02, 0.0
    
    f_ext_x, f_ext_y = 0.0, 0.0
    time_survived = 0.0
    frame_count = 0
    game_over = False

    while True:
        # ==========================================
        # 2. 이벤트 처리 및 WASD 키 입력
        # ==========================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # 재시작
                    main()
                    return

        tau_x, tau_y = 0.0, 0.0
        keys = pygame.key.get_pressed()
        
        if not game_over:
            if keys[pygame.K_a]: tau_x = -18.0  # 좌측 복원 토크
            if keys[pygame.K_d]: tau_x = 18.0   # 우측 복원 토크
            if keys[pygame.K_w]: tau_y = 18.0   # 전방 복원 토크
            if keys[pygame.K_s]: tau_y = -18.0  # 후방 복원 토크

            # 주기적인 불규칙 2D 외란(바람) 발생
            frame_count += 1
            if frame_count % 40 == 0:
                f_ext_x = (random.random() - 0.5) * 26.0
                f_ext_y = (random.random() - 0.5) * 26.0
            else:
                f_ext_x *= 0.95
                f_ext_y *= 0.95

            # ==========================================
            # 3. 2자유도 수치해석 동역학 계산 Engine
            # ==========================================
            # Roll (X축) 각가속도 계산
            alpha_x = (MASS * GRAVITY * LEG_L * math.sin(theta_x) + tau_x + f_ext_x * LEG_L * math.cos(theta_x)) / (MASS * LEG_L ** 2)
            omega_x += alpha_x * DT
            theta_x += omega_x * DT

            # Pitch (Y축) 각가속도 계산
            alpha_y = (MASS * GRAVITY * LEG_L * math.sin(theta_y) + tau_y + f_ext_y * LEG_L * math.cos(theta_y)) / (MASS * LEG_L ** 2)
            omega_y += alpha_y * DT
            theta_y += omega_y * DT

            # 무게중심 (CoM) 및 2D ZMP 위치 계산
            x_com = LEG_L * math.sin(theta_x)
            y_com = LEG_L * math.sin(theta_y)
            z_com = LEG_L * math.cos(theta_x) * math.cos(theta_y)

            x_com_ddot = LEG_L * (alpha_x * math.cos(theta_x) - (omega_x ** 2) * math.sin(theta_x))
            y_com_ddot = LEG_L * (alpha_y * math.cos(theta_y) - (omega_y ** 2) * math.sin(theta_y))

            # 핵심 ZMP 방정식 적용
            x_zmp = x_com - (z_com / GRAVITY) * x_com_ddot
            y_zmp = y_com - (z_com / GRAVITY) * y_com_ddot

            # 넘어짐 조건 판정 (지지 영역 탈출 또는 과도한 기울기)
            if (abs(x_zmp) > FOOT_X_HALF or abs(y_zmp) > FOOT_Y_HALF or 
                abs(theta_x) > 0.8 or abs(theta_y) > 0.8):
                game_over = True

            time_survived += DT

        # ==========================================
        # 4. 렌더링 (화면 그리기)
        # ==========================================
        screen.fill(COLOR_BG)

        # 1) 백그라운드 그리드
        for i in range(-5, 6):
            pygame.draw.line(screen, COLOR_GRID, (CENTER_X + i * 50, 0), (CENTER_X + i * 50, SCREEN_HEIGHT), 1)
            pygame.draw.line(screen, COLOR_GRID, (0, CENTER_Y + i * 50), (SCREEN_WIDTH, CENTER_Y + i * 50), 1)

        # 2) 발바닥 지지 다각형 (Support Polygon)
        foot_w_px = int(FOOT_X_HALF * 2 * SCALE)
        foot_h_px = int(FOOT_Y_HALF * 2 * SCALE)
        foot_rect = pygame.Rect(CENTER_X - foot_w_px // 2, CENTER_Y - foot_h_px // 2, foot_w_px, foot_h_px)
        pygame.draw.rect(screen, COLOR_FOOT, foot_rect)
        pygame.draw.rect(screen, COLOR_FOOT_BORDER, foot_rect, 3)

        # 3) CoM 및 ZMP 위치를 픽셀 좌표로 변환 (Y축은 화면상 아래쪽이 +이므로 반전)
        com_px = (int(CENTER_X + x_com * SCALE), int(CENTER_Y - y_com * SCALE))
        zmp_px = (int(CENTER_X + x_zmp * SCALE), int(CENTER_Y - y_zmp * SCALE))

        # CoM (무게중심 - 초록 원)
        pygame.draw.circle(screen, COLOR_COM, com_px, 8)
        pygame.draw.circle(screen, (255, 255, 255), com_px, 10, 1)

        # ZMP (영모멘트점 - 빨간 십자가)
        pygame.draw.circle(screen, COLOR_ZMP, zmp_px, 6)
        pygame.draw.line(screen, COLOR_ZMP, (zmp_px[0] - 12, zmp_px[1]), (zmp_px[0] + 12, zmp_px[1]), 2)
        pygame.draw.line(screen, COLOR_ZMP, (zmp_px[0], zmp_px[1] - 12), (zmp_px[0], zmp_px[1] + 12), 2)

        # 4) 정보 UI 출력
        title = font_large.render("2-DOF ZMP Humanoid Balance Control", True, COLOR_TEXT)
        screen.blit(title, (20, 15))

        info_texts = [
            f"생존 시간: {time_survived:.2f} 초",
            f"조작 (WASD): W(전) S(후) A(좌) D(우)",
            f"바람 외란 (X, Y): {f_ext_x:+5.1f} N, {f_ext_y:+5.1f} N",
            f"기울기 Roll (X) : {math.degrees(theta_x):+5.1f} deg",
            f"기울기 Pitch (Y): {math.degrees(theta_y):+5.1f} deg",
            f"ZMP 위치 (X, Y) : ({x_zmp:+5.3f}m, {y_zmp:+5.3f}m)",
        ]

        for idx, text in enumerate(info_texts):
            txt_surface = font_small.render(text, True, COLOR_TEXT)
            screen.blit(txt_surface, (20, 60 + idx * 24))

        # 범례 표시
        pygame.draw.circle(screen, COLOR_COM, (SCREEN_WIDTH - 150, 30), 6)
        screen.blit(font_small.render("CoM (무게중심)", True, COLOR_TEXT), (SCREEN_WIDTH - 135, 22))
        pygame.draw.circle(screen, COLOR_ZMP, (SCREEN_WIDTH - 150, 55), 6)
        screen.blit(font_small.render("ZMP (영모멘트점)", True, COLOR_TEXT), (SCREEN_WIDTH - 135, 47))

        # 5) Game Over 화면
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((10, 10, 15))
            screen.blit(overlay, (0, 0))

            over_txt = font_large.render("ROBOT FALLEN! (GAME OVER)", True, (255, 70, 70))
            sub_txt = font_small.render("ZMP가 지지 영역을 이탈했습니다. 'R' 키를 눌러 재시작하세요.", True, COLOR_TEXT)
            
            screen.blit(over_txt, (SCREEN_WIDTH // 2 - over_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(int(1 / DT))

if __name__ == "__main__":
    main()
