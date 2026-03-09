import pygame
import sys
from core.settings import *
from models.shoe import Shoe
from models.player import Player, Dealer
from models.hand import calculate_score, organize_hands, get_strategy_advice
from ui.button import Button
from ui.table import draw_table_base, draw_scores, draw_chips, draw_coach, draw_simulation_results
from ui.overlay import draw_result_overlay
from ui.card_renderer import draw_card

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Blackjack Engineering Simulator")
        self.clock = pygame.time.Clock()
        self.shoe = Shoe()
        self.player = Player()
        self.dealer = Dealer()
        self.state = "BETTING"
        self.running_count = 0
        self.anim_counter = 0
        self.coach_enabled = True
        self.sim_stats = None
        self.init_ui()

    def init_ui(self):
        # Botones de juego
        self.btn_deal = Button("DEAL", WIDTH//2 - 60, HEIGHT - 120, 120, 50, 'deal')
        self.btn_hit = Button("HIT", WIDTH//2 - 200, HEIGHT - 120, 120, 50, 'hit')
        self.btn_stand = Button("STAND", WIDTH//2 - 60, HEIGHT - 120, 120, 50, 'stand')
        self.btn_double = Button("DOUBLE", WIDTH//2 + 80, HEIGHT - 120, 120, 50, 'double')
        self.btn_reset = Button("NEW HAND", WIDTH//2 - 75, HEIGHT - 120, 150, 50, 'reset')
        
        # Botones de utilidad y simulación
        self.btn_sim = Button("SIM 10K", 20, HEIGHT - 120, 150, 50, 'simulate')
        self.btn_add = Button("+ $1000", WIDTH - 120, HEIGHT - 60, 100, 40, 'add') # <-- CORREGIDO
        self.btn_toggle_coach = Button("COACH: ON", WIDTH - 180, HEIGHT - 110, 160, 40, 'toggle_coach')
        
        # Fichas (subidas un poco para que no tapen botones)
        self.chip_rects = [(pygame.Rect(50 + i*90, HEIGHT - 220, 80, 80), v) for i,v in enumerate([10, 50, 100, 500])]

    def run_simulation(self):
        total_hands = 10000
        sim_shoe = Shoe()
        wins, losses, pushes, bjs = 0, 0, 0, 0
        total_bet, total_profit = 0, 0
        fixed_bet = 10

        for _ in range(total_hands):
            if len(sim_shoe.cards) < 52: sim_shoe.build()
            total_bet += fixed_bet
            p_hand = [sim_shoe.draw_card(), sim_shoe.draw_card()]
            d_hand = [sim_shoe.draw_card(), sim_shoe.draw_card()]
            
            p_score = calculate_score(p_hand)
            d_score = calculate_score(d_hand)
            
            if p_score == 21:
                if d_score == 21: pushes += 1
                else: wins += 1; bjs += 1; total_profit += fixed_bet * 1.5
                continue

            playing = True
            advice = "HIT"
            while playing:
                advice = get_strategy_advice(p_hand, d_hand[0])
                if advice == "HIT":
                    p_hand.append(sim_shoe.draw_card())
                    if calculate_score(p_hand) > 21:
                        losses += 1; total_profit -= fixed_bet; playing = False
                elif advice == "DOUBLE":
                    total_bet += fixed_bet
                    p_hand.append(sim_shoe.draw_card())
                    if calculate_score(p_hand) > 21:
                        losses += 1; total_profit -= (fixed_bet * 2); playing = False
                    else: playing = False
                else: playing = False
            
            if calculate_score(p_hand) <= 21:
                while calculate_score(d_hand) < 17: d_hand.append(sim_shoe.draw_card())
                f_p, f_d = calculate_score(p_hand), calculate_score(d_hand)
                m = 2 if advice == "DOUBLE" else 1
                if f_d > 21 or f_p > f_d: wins += 1; total_profit += (fixed_bet * m)
                elif f_p < f_d: losses += 1; total_profit -= (fixed_bet * m)
                else: pushes += 1

        self.sim_stats = {
            'profit': int(total_profit),
            'win_rate': (wins / total_hands) * 100,
            'ev': total_profit / total_bet,
            'edge': abs(total_profit / total_bet) * 100 if total_profit < 0 else 0,
            'bjs': bjs
        }
        self.state = "SIM_RESULT"

    def run(self):
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and self.state == "BETTING":
                    for r, v in self.chip_rects:
                        if r.collidepoint(e.pos) and self.player.money >= v:
                            self.player.money -= v; self.player.current_bet += v
            self.update(events)
            self.draw()
            self.clock.tick(FPS)

    def update(self, events):
        if self.btn_toggle_coach.update(events) == 'toggle_coach':
            self.coach_enabled = not self.coach_enabled
            self.btn_toggle_coach.text = f"COACH: {'ON' if self.coach_enabled else 'OFF'}"

        if self.state == "BETTING":
            if self.btn_sim.update(events) == 'simulate': self.run_simulation()
            if self.btn_add.update(events) == 'add': self.player.money += 1000
            if self.btn_deal.update(events) == 'deal' and self.player.current_bet > 0:
                self.state = "PLAYING"
                for i in range(2):
                    p_c = self.shoe.draw_card(); self.player.hand.append(p_c); self.update_count(p_c)
                    d_c = self.shoe.draw_card(); self.dealer.hand.append(d_c)
                    if i == 0: self.update_count(d_c)
                self.dealer.hand[1].face_up = False
                organize_hands(self.player.hand, self.dealer.hand)
        
        elif self.state == "SIM_RESULT":
            if self.btn_reset.update(events) == 'reset': self.state = "BETTING"

        elif self.state == "PLAYING":
            if self.btn_hit.update(events) == 'hit':
                c = self.shoe.draw_card(); self.player.hand.append(c); self.update_count(c)
                organize_hands(self.player.hand, self.dealer.hand)
                if calculate_score(self.player.hand) > 21: self.handle_result("BUST")
            if self.btn_stand.update(events) == 'stand': self.state = "DEALER_ANIM"
            if self.btn_double.update(events) == 'double' and self.player.money >= self.player.current_bet:
                self.player.money -= self.player.current_bet; self.player.current_bet *= 2
                c = self.shoe.draw_card(); self.player.hand.append(c); self.update_count(c)
                organize_hands(self.player.hand, self.dealer.hand)
                if calculate_score(self.player.hand) > 21: self.handle_result("BUST")
                else: self.state = "DEALER_ANIM"

        elif self.state == "DEALER_ANIM":
            self.dealer.hand[1].face_up = True
            if calculate_score(self.dealer.hand) < 17:
                c = self.shoe.draw_card(); self.dealer.hand.append(c); self.update_count(c)
                organize_hands(self.player.hand, self.dealer.hand); pygame.time.wait(300)
            else:
                s, ps = calculate_score(self.dealer.hand), calculate_score(self.player.hand)
                if s > 21 or ps > s: self.handle_result("WIN")
                elif ps < s: self.handle_result("LOSE")
                else: self.handle_result("PUSH")

        elif self.state == "RESULT":
            if self.btn_reset.update(events) == 'reset': 
                self.player.reset_hand(); self.dealer.reset_hand(); self.state = "BETTING"
        
        for c in self.player.hand + self.dealer.hand: c.update()

    def update_count(self, c):
        if c.rank in ['10','J','Q','K','A']: self.running_count -= 1
        elif c.rank in ['2','3','4','5','6']: self.running_count += 1

    def get_true_count(self):
        dl = len(self.shoe.cards)/52
        return self.running_count/dl if dl > 0 else 0

    def handle_result(self, r):
        self.state = "RESULT"; self.update_count(self.dealer.hand[1])
        b = self.player.current_bet
        if r == "LOSE" or r == "BUST": self.msg_main, self.msg_sub, self.msg_color = "DEALER WINS", f"- ${b}", LOSE_RED
        elif r == "WIN": self.player.money += b*2; self.msg_main, self.msg_sub, self.msg_color = "YOU WIN!", f"+ ${b}", WIN_GREEN
        elif r == "PUSH": self.player.money += b; self.msg_main, self.msg_sub, self.msg_color = "PUSH", "+ $0", PUSH_GRAY

    def draw(self):
        draw_table_base(self.screen, self.player.money, self.player.current_bet, len(self.shoe.cards), self.running_count, self.get_true_count())
        for c in self.dealer.hand + self.player.hand: 
            draw_card(self.screen, c)
        draw_scores(self.screen, self.player.hand, self.dealer.hand)
        if self.state == "PLAYING" and self.coach_enabled: draw_coach(self.screen, self.player.hand, self.dealer.hand)
        self.btn_toggle_coach.draw(self.screen)
        if self.state == "BETTING":
            self.btn_deal.draw(self.screen); self.btn_sim.draw(self.screen); self.btn_add.draw(self.screen); draw_chips(self.screen, self.chip_rects)
        elif self.state == "PLAYING":
            self.btn_hit.draw(self.screen); self.btn_stand.draw(self.screen); self.btn_double.draw(self.screen)
        elif self.state == "RESULT":
            draw_result_overlay(self.screen, self.msg_main, self.msg_sub, self.msg_color, self.anim_counter); self.btn_reset.draw(self.screen)
        elif self.state == "SIM_RESULT":
            draw_simulation_results(self.screen, self.sim_stats); self.btn_reset.draw(self.screen)
        pygame.display.flip()
