import pygame
import math
from core.settings import *

def draw_result_overlay(screen, msg_main, msg_sub, msg_color, anim_counter):
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.set_alpha(150)
    bg.fill(BLACK)
    screen.blit(bg, (0, 0))
    main_s = FONT_BIG.render(msg_main, True, WHITE)
    screen.blit(main_s, main_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
    offset = math.sin(anim_counter * 0.1) * 15
    sub_s = FONT_HUGE.render(msg_sub, True, msg_color)
    shadow_s = FONT_HUGE.render(msg_sub, True, BLACK)
    screen.blit(shadow_s, shadow_s.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 + 54 - offset)))
    screen.blit(sub_s, sub_s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50 - offset)))
