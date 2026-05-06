"""game_ui.py — Snake Deluxe v2.0 rendering helpers.

Draw helpers for the Game class, extracted for modularisation.
Every public function receives the Game instance as its first argument
and is called from Game.draw() via the _ui module reference.
"""

import pygame
import math

from snake import (
    WINDOW,
    TILE_SIZE,
    GAME_MODES,
    SKINS,
    FRUITS,
    C_DIM,
    C_WHITE,
    C_BLACK,
    C_CYAN,
    C_RED,
    C_YELLOW,
    C_BG,
    C_GRID,
    lerp_color,
    rainbow_color,
    Fruit,
    Screen,
)

# Kept to avoid breaking callers that import C_BG / C_GRID via this module.
_ = C_BG, C_GRID


MODE_DESC = {
    "Clasico": "Velocidad incremental. Tocar muros = fin.",
    "Portal": "Las paredes teleportan al lado opuesto.",
    "Contrarreloj": "60 segundos. Maximo puntaje posible!",
    "Caos": "La fruta se mueve sola cada 4 segundos.",
    "Obstaculos": "Bloques en el mapa. Cuidado al girar!",
}


def overlay(game, alpha=160):
    """Blit a full-screen semi-transparent black rectangle onto *game.screen*.

    Args:
        game: The active Game instance.
        alpha: Opacity of the overlay (0 = invisible, 255 = opaque).

    """
    ov = pygame.Surface((WINDOW, WINDOW), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    game.screen.blit(ov, (0, 0))


def ctext(game, text, font, color, y):
    """Render *text* horizontally centred at vertical position *y* on *game.screen*.

    Args:
        game: The active Game instance.
        text: String to render.
        font: pygame Font object to use.
        color: RGB tuple for the text colour.
        y: Vertical pixel position of the text centre.

    """
    s = font.render(text, True, color)
    game.screen.blit(s, s.get_rect(center=(WINDOW // 2, y)))


def draw_grid(game):
    """Draw the background tile grid onto *game.screen*."""
    for x in range(0, WINDOW, TILE_SIZE):
        pygame.draw.line(game.screen, C_GRID, (x, 0), (x, WINDOW))
    for y in range(0, WINDOW, TILE_SIZE):
        pygame.draw.line(game.screen, C_GRID, (0, y), (WINDOW, y))


def draw_main_menu(game):
    """Render the main menu: title, mode/skin info, buttons, and audio toggles."""
    overlay(game, 170)
    t = math.sin(pygame.time.get_ticks() * 0.002) * 4
    title = game.f_title.render("SNAKE DELUXE", True, (0, 230, 120))
    game.screen.blit(title, title.get_rect(center=(WINDOW // 2, 188 + int(t))))
    ctext(game, "v2.0  Pruebas de Software", game.f_small, C_DIM, 244)
    ctext(
        game,
        f"Modo: {game.selected_mode}   Skin: {game.selected_skin}",
        game.f_small,
        C_CYAN,
        276,
    )
    for btn in game._main_btns:
        btn.draw(game.screen, game.f_med)
    ctext(
        game,
        "WASD/Flechas - mover  |  P - pausa  |  ESC - menu",
        game.f_tiny,
        C_DIM,
        WINDOW - 22,
    )
    if game.sm:
        sfx_col = (0, 200, 100) if game.sm.sfx_on else C_DIM
        mus_col = (0, 200, 100) if game.sm.music_on else C_DIM
        sfx_lbl = "SFX: ON" if game.sm.sfx_on else "SFX: OFF"
        mus_lbl = "MUS: ON" if game.sm.music_on else "MUS: OFF"
        game.screen.blit(
            game.f_tiny.render(sfx_lbl, True, sfx_col), (WINDOW - 80, WINDOW - 50)
        )
        game.screen.blit(
            game.f_tiny.render(mus_lbl, True, mus_col), (WINDOW - 80, WINDOW - 36)
        )
        tip = game.f_tiny.render("M=musica  N=sfx", True, C_DIM)
        game.screen.blit(tip, (WINDOW - 115, WINDOW - 22))


def draw_mode_select(game):
    """Render the game-mode selection screen with description under the active mode."""
    overlay(game, 175)
    ctext(game, "MODO DE JUEGO", game.f_big, C_CYAN, 158)
    game._back_btn.draw(game.screen, game.f_small)
    for btn, m in zip(game._mode_btns, GAME_MODES):
        btn.selected = m == game.selected_mode
        btn.draw(game.screen, game.f_med)
        if btn.selected:
            d = game.f_tiny.render(MODE_DESC.get(m, ""), True, C_DIM)
            game.screen.blit(d, d.get_rect(center=(WINDOW // 2, btn.rect.bottom + 11)))
    game._play_btn.draw(game.screen, game.f_med)


def draw_customize(game):
    """Render the skin customisation screen with a snake preview and fruit showcase."""
    overlay(game, 175)
    ctext(game, "PERSONALIZAR SERPIENTE", game.f_big, C_YELLOW, 156)
    ctext(game, "Elige tu skin:", game.f_small, C_DIM, 232)
    game._back_btn.draw(game.screen, game.f_small)

    for btn, name in zip(game._skin_btns, list(SKINS.keys())):
        btn.selected = name == game.selected_skin
        btn.draw(game.screen, game.f_med)
        info = SKINS[name]
        col = info[0] if info else rainbow_color(0, 1, game._bg_off)
        pr = pygame.Rect(btn.rect.right - 34, btn.rect.y + 15, 18, 18)
        pygame.draw.rect(game.screen, col, pr, border_radius=3)

    py = 475
    ctext(game, "Preview:", game.f_small, C_DIM, py - 28)
    n = 9
    for i in range(n):
        x = WINDOW // 2 - n * (TILE_SIZE // 2) + i * (TILE_SIZE - 2)
        r = pygame.Rect(x, py, TILE_SIZE - 4, TILE_SIZE - 4)
        if game.selected_skin == "Arcoiris":
            col = rainbow_color(i, n, game._bg_off)
        else:
            info = SKINS[game.selected_skin]
            col = lerp_color(info[1], info[0], i / max(n - 1, 1))
        pygame.draw.rect(game.screen, col, r, border_radius=5)

    ex = WINDOW // 2 - n * (TILE_SIZE // 2) + (n - 1) * (TILE_SIZE - 2) + 10
    ey = py + 10
    pygame.draw.circle(game.screen, C_WHITE, (ex, ey), 4)
    pygame.draw.circle(game.screen, C_BLACK, (ex, ey), 2)

    ctext(game, "Frutas disponibles:", game.f_small, C_DIM, py + 56)
    items = list(FRUITS.items())
    gap = 160
    start = WINDOW // 2 - gap * (len(items) - 1) // 2
    for i, (fname, (fc, fpts, _, frad)) in enumerate(items):
        demo_f = Fruit.__new__(Fruit)
        demo_f._pulse = pygame.time.get_ticks() * 0.005
        demo_f._angle = pygame.time.get_ticks() * 0.003
        demo_f.color = fc
        demo_f.kind = fname
        demo_f.radius = frad
        demo_f.rect = pygame.Rect(0, 0, TILE_SIZE - 2, TILE_SIZE - 2)
        demo_f.rect.center = (start + i * gap, py + 92)
        demo_f.draw(game.screen)
        lbl = game.f_tiny.render(f"{fname}  +{fpts}pt", True, C_DIM)
        game.screen.blit(lbl, lbl.get_rect(center=(start + i * gap, py + 122)))

    game._play_btn.draw(game.screen, game.f_med)


def draw_playing(game, scr):
    """Render the active gameplay view: obstacles, fruit, snake, HUD, and overlay."""
    if game.obstacle:
        game.obstacle.draw(game.screen)
    game.fruit.draw(game.screen)
    game.snake.draw(game.screen)
    draw_hud(game)
    if game.selected_mode == "Portal":
        for r in [
            pygame.Rect(0, 0, 4, WINDOW),
            pygame.Rect(WINDOW - 4, 0, 4, WINDOW),
            pygame.Rect(0, 0, WINDOW, 4),
            pygame.Rect(0, WINDOW - 4, WINDOW, 4),
        ]:
            pygame.draw.rect(game.screen, (100, 0, 230), r)
    if scr == Screen.PAUSED:
        overlay(game, 150)
        ctext(game, "PAUSADO", game.f_big, C_CYAN, WINDOW // 2 - 18)
        ctext(game, "P / ESC para continuar", game.f_small, C_DIM, WINDOW // 2 + 34)


def draw_hud(game):
    """Render the heads-up display: score, best, mode, fruit info, and countdown."""
    bar = pygame.Surface((WINDOW, 52), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 100))
    game.screen.blit(bar, (0, 0))
    score_s = game.f_big.render(str(game.scoreboard.score), True, (0, 230, 120))
    game.screen.blit(score_s, score_s.get_rect(center=(WINDOW // 2, 26)))
    hi_s = game.f_tiny.render(f"BEST {game.scoreboard.high_score}", True, C_DIM)
    game.screen.blit(hi_s, (8, 8))
    mode_s = game.f_tiny.render(game.selected_mode.upper(), True, C_CYAN)
    game.screen.blit(mode_s, mode_s.get_rect(topright=(WINDOW - 8, 8)))
    fruit_s = game.f_tiny.render(
        f"+{game.fruit.points}  {game.fruit.kind}", True, game.fruit.color
    )
    game.screen.blit(fruit_s, fruit_s.get_rect(topright=(WINDOW - 8, 24)))
    if game.selected_mode == "Contrarreloj":
        secs = int(game._countdown / 1000) + 1
        color = C_RED if secs <= 10 else C_YELLOW
        t_s = game.f_med.render(f"T: {secs}s", True, color)
        game.screen.blit(t_s, (8, 26))


def draw_dead(game):
    """Render the game-over screen: red snake, scores, history, and action buttons."""
    for seg in game.snake.segments:
        pygame.draw.rect(game.screen, C_RED, seg, border_radius=5)
    overlay(game, 160)
    cx = WINDOW // 2
    ctext(game, "GAME OVER", game.f_title, C_RED, 215)
    last = game.scoreboard.history[-1] if game.scoreboard.history else 0
    ctext(game, f"Puntaje: {last}", game.f_big, C_WHITE, 292)
    ctext(game, f"Record:  {game.scoreboard.high_score}", game.f_med, C_YELLOW, 336)
    ctext(
        game,
        f"Modo: {game.selected_mode}  |  Skin: {game.selected_skin}",
        game.f_small,
        C_DIM,
        372,
    )
    if game.scoreboard.history:
        hist = "  ".join(str(s) for s in reversed(game.scoreboard.history[-5:]))
        ctext(game, f"Historial: {hist}", game.f_tiny, C_DIM, 402)
    for rect, txt, col in [
        (pygame.Rect(cx - 120, 455, 240, 50), "Reintentar", (30, 100, 50)),
        (pygame.Rect(cx - 120, 515, 240, 50), "Menu principal", (60, 40, 90)),
    ]:
        pygame.draw.rect(game.screen, col, rect, border_radius=8)
        pygame.draw.rect(game.screen, (80, 95, 130), rect, 2, border_radius=8)
        s = game.f_med.render(txt, True, C_WHITE)
        game.screen.blit(s, s.get_rect(center=rect.center))
