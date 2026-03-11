import pygame

WIDTH, HEIGHT = 1280, 800
FPS = 60
FELT_COLOR = (0, 80, 0)
WOOD_COLOR = (85, 53, 25)
GOLD = (218, 165, 32)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED_SUIT = (200, 20, 40)
BLACK_SUIT = (20, 20, 20)
BUTTON_BG = (40, 40, 40)
BUTTON_HOVER = (60, 60, 60)
WIN_GREEN = (0, 255, 0)
LOSE_RED = (255, 0, 0)
PUSH_GRAY = (200, 200, 200)
ADVICE_COLOR = (0, 200, 255)
STATS_COLOR = (255, 255, 100)

pygame.font.init()


def get_font(size, bold=False):
    fonts = ["arial", "helvetica", "calibri", "verdana"]
    return pygame.font.SysFont(pygame.font.match_font(fonts) or None, size, bold=bold)


FONT_UI = get_font(28, True)
FONT_CARD = get_font(36, True)
FONT_BIG = get_font(70, True)
FONT_HUGE = get_font(100, True)
FONT_SMALL = get_font(20, True)
