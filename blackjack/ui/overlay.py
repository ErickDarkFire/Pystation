import pygame
import math
import core.settings as st  # Cambiado


def draw_result_overlay(screen, msg_main, msg_sub, msg_color, anim_counter):
    bg = pygame.Surface((st.WIDTH, st.HEIGHT))
    bg.set_alpha(150)
    bg.fill(st.BLACK)
    screen.blit(bg, (0, 0))

    main_s = st.FONT_BIG.render(msg_main, True, st.WHITE)
    screen.blit(main_s, main_s.get_rect(center=(st.WIDTH // 2, st.HEIGHT // 2 - 50)))

    offset = math.sin(anim_counter * 0.1) * 15
    sub_s = st.FONT_HUGE.render(msg_sub, True, msg_color)
    shadow_s = st.FONT_HUGE.render(msg_sub, True, st.BLACK)

    screen.blit(
        shadow_s,
        shadow_s.get_rect(center=(st.WIDTH // 2 + 4, st.HEIGHT // 2 + 54 - offset)),
    )
    screen.blit(
        sub_s,
        sub_s.get_rect(center=(st.WIDTH // 2, st.HEIGHT // 2 + 50 - offset)),
    )
