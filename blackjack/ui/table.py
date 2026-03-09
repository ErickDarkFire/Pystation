import pygame
from core.settings import *
from models.hand import calculate_score, get_strategy_advice

def draw_table_base(screen, money, current_bet, shoe_count, running_count, true_count):
    screen.fill(FELT_COLOR)
    pygame.draw.rect(screen, WOOD_COLOR, (0, 0, WIDTH, 20))
    pygame.draw.line(screen, GOLD, (0, 100), (WIDTH, 100), 2)
    screen.blit(FONT_UI.render(f"BANK: ${int(money)}", True, GOLD), (20, 30))
    screen.blit(FONT_UI.render(f"BET: ${current_bet}", True, WHITE), (WIDTH - 200, 30))
    count_txt = f"RC: {running_count} | TC: {true_count:.1f}"
    screen.blit(FONT_SMALL.render(count_txt, True, (200, 200, 200)), (20, HEIGHT - 40))
    decks = round(shoe_count / 52, 1)
    screen.blit(FONT_SMALL.render(f"Decks: {decks}", True, (150, 150, 150)), (WIDTH//2 - 40, 10))

def draw_simulation_results(screen, stats):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))
    screen.blit(overlay, (0,0))
    
    y_offset = 150
    title = FONT_BIG.render("SIMULATION REPORT (10,000 Hands)", True, GOLD)
    screen.blit(title, title.get_rect(center=(WIDTH//2, y_offset)))
    
    rows = [
        (f"Total Won: ${stats['profit']}", WHITE),
        (f"Win Rate: {stats['win_rate']:.2f}%", WIN_GREEN),
        (f"EV per Hand: {stats['ev']:.4f}", STATS_COLOR),
        (f"House Edge: {stats['edge']:.2f}%", LOSE_RED),
        (f"Blackjacks: {stats['bjs']}", GOLD)
    ]
    
    for i, (text, color) in enumerate(rows):
        surf = FONT_UI.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, 300 + i * 50)))

def draw_coach(screen, p_hand, d_hand):
    if len(p_hand) >= 2 and len(d_hand) >= 2:
        advice = get_strategy_advice(p_hand, d_hand[0])
        txt = FONT_UI.render(f"COACH: {advice}", True, ADVICE_COLOR)
        rect = txt.get_rect(center=(WIDTH//2, 440))
        bg_rect = rect.inflate(20, 10)
        pygame.draw.rect(screen, (0,0,0,150), bg_rect, border_radius=5)
        screen.blit(txt, rect)

def draw_scores(screen, player_hand, dealer_hand):
    if len(dealer_hand) > 0 and dealer_hand[1].face_up:
        d_val = calculate_score(dealer_hand)
        screen.blit(FONT_UI.render(str(d_val), True, WHITE), (WIDTH // 2 - 20, 120))
    if len(player_hand) > 0:
        p_val = calculate_score(player_hand)
        screen.blit(FONT_UI.render(str(p_val), True, WHITE), (WIDTH // 2 - 20, 470))

def draw_chips(screen, chip_rects):
    for rect, val in chip_rects:
        color = RED_SUIT if val == 10 else (0, 0, 150) if val == 50 else BLACK if val == 100 else GOLD
        pygame.draw.circle(screen, color, rect.center, 38)
        pygame.draw.circle(screen, WHITE, rect.center, 38, 3)
        txt = FONT_SMALL.render(str(val), True, WHITE if val != 500 else BLACK)
        screen.blit(txt, txt.get_rect(center=rect.center))
