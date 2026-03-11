import sys
import pygame
from game_logic import (
    Card, SUIT_SYMBOLS,
    PokerGame, GamePhase, GameResult,
)

C_FELT        = (27, 94, 32)
C_FELT_LIGHT  = (46, 125, 50)
C_FELT_DARK   = (18, 65, 22)
C_GOLD        = (212, 175, 55)
C_GOLD_DIM    = (160, 130, 40)
C_WHITE       = (255, 255, 255)
C_OFF_WHITE   = (245, 240, 220)
C_BLACK       = (10, 10, 10)
C_RED         = (198, 40, 40)
C_RED_SUIT    = (200, 30, 30)
C_BTN_GREEN   = (56, 142, 60)
C_BTN_GREEN_H = (76, 175, 80)
C_BTN_RED     = (183, 28, 28)
C_BTN_RED_H   = (229, 57, 53)
C_BTN_BLUE    = (21, 101, 192)
C_BTN_BLUE_H  = (30, 136, 229)
C_BTN_GOLD    = (160, 120, 20)
C_BTN_GOLD_H  = (200, 160, 40)
C_CHIP        = (220, 180, 50)
C_CARD_BACK   = (25, 60, 130)

SCREEN_W  = 1100
SCREEN_H  = 780

CARD_W    = 80
CARD_H    = 115
FPS       = 60

TITLE_H       = 58    
DEALER_Y      = 68    
COMMUNITY_Y   = 232   
PLAYER_Y      = 400   
INFO_Y        = 530  
MESSAGE_Y     = 592   
HINT_Y        = 628   
DIVIDER_Y     = 652   
BUTTON_Y      = 664   
BOTTOM_EDGE   = 722   



def draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_card(surface, card: Card, x: int, y: int, fonts: dict, face_up=True):
    rect = pygame.Rect(x, y, CARD_W, CARD_H)

    shadow = pygame.Surface((CARD_W + 4, CARD_H + 4), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 80), shadow.get_rect(), border_radius=10)
    surface.blit(shadow, (x + 3, y + 3))

    if not face_up:
        draw_rounded_rect(surface, C_CARD_BACK, rect, radius=10,
                          border=2, border_color=C_GOLD)
        for i in range(0, CARD_W, 10):
            pygame.draw.line(surface, (35, 80, 160), (x + i, y), (x, y + i), 1)
            pygame.draw.line(surface, (35, 80, 160),
                             (x + CARD_W - i, y + CARD_H),
                             (x + CARD_W, y + CARD_H - i), 1)
        return

    draw_rounded_rect(surface, C_WHITE, rect, radius=10,
                      border=2, border_color=(200, 200, 200))

    sc  = C_RED_SUIT if card.suit in ("Hearts", "Diamonds") else C_BLACK
    sym = SUIT_SYMBOLS[card.suit]

    rank_surf   = fonts["card_rank"].render(card.rank, True, sc)
    suit_surf   = fonts["card_suit"].render(sym,       True, sc)
    center_suit = fonts["card_center"].render(sym,     True, sc)

    surface.blit(rank_surf, (x + 5, y + 4))
    surface.blit(suit_surf, (x + 5, y + 4 + rank_surf.get_height()))
    surface.blit(center_suit, (
        x + CARD_W // 2 - center_suit.get_width()  // 2,
        y + CARD_H // 2 - center_suit.get_height() // 2,
    ))
    r2 = pygame.transform.rotate(rank_surf, 180)
    s2 = pygame.transform.rotate(suit_surf, 180)
    surface.blit(r2, (x + CARD_W - r2.get_width() - 5,
                      y + CARD_H - r2.get_height() - 4))
    surface.blit(s2, (x + CARD_W - s2.get_width() - 5,
                      y + CARD_H - r2.get_height() - s2.get_height() - 4))



class Button:
    def __init__(self, rect, label, color, hover_color, font):
        self.rect        = pygame.Rect(rect)
        self.label       = label
        self.color       = color
        self.hover_color = hover_color
        self.font        = font
        self.enabled     = True
        self._hovered    = False

    def update(self, mouse_pos):
        self._hovered = self.rect.collidepoint(mouse_pos) and self.enabled

    def draw(self, surface):
        col = self.hover_color if self._hovered else self.color
        if not self.enabled:
            col = (72, 72, 72)
        draw_rounded_rect(surface, col, self.rect, radius=8,
                          border=2,
                          border_color=C_GOLD if self.enabled else (50, 50, 50))
        lbl = self.font.render(self.label, True,
                               C_WHITE if self.enabled else (110, 110, 110))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event) -> bool:
        return (self.enabled
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))



class CasinoPokerApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Casino Poker — Ante Game")
        self.clock  = pygame.time.Clock()

        self.fonts = {
            "title":       pygame.font.SysFont("Georgia", 34, bold=True),
            "subtitle":    pygame.font.SysFont("Georgia", 17, italic=True),
            "card_rank":   pygame.font.SysFont("Georgia", 20, bold=True),
            "card_suit":   pygame.font.SysFont("Segoe UI Symbol", 18),
            "card_center": pygame.font.SysFont("Segoe UI Symbol", 34),
            "ui":          pygame.font.SysFont("Georgia", 18),
            "ui_bold":     pygame.font.SysFont("Georgia", 18, bold=True),
            "result":      pygame.font.SysFont("Georgia", 23, bold=True),
            "small":       pygame.font.SysFont("Georgia", 14),
            "btn":         pygame.font.SysFont("Georgia", 16, bold=True),
        }

        self.game       = PokerGame()
        self.ante_input = "25"
        self.message    = "Welcome!  Set your ante and press DEAL."
        self.msg_color  = C_GOLD

        bw = 148   
        bh = 44
        gap = (SCREEN_W - 40 - 5 * bw) // 4  

        def bx(i):
            return 20 + i * (bw + gap)

        self.btn_deal     = Button((bx(0), BUTTON_Y, bw,      bh), "DEAL",            C_BTN_BLUE,  C_BTN_BLUE_H,  self.fonts["btn"])
        self.btn_bet      = Button((bx(1), BUTTON_Y, bw,      bh), "BET",             C_BTN_GREEN, C_BTN_GREEN_H, self.fonts["btn"])
        self.btn_fold     = Button((bx(2), BUTTON_Y, bw,      bh), "FOLD",            C_BTN_RED,   C_BTN_RED_H,   self.fonts["btn"])
        self.btn_next     = Button((bx(3), BUTTON_Y, bw,      bh), "NEW ROUND",       C_BTN_BLUE,  C_BTN_BLUE_H,  self.fonts["btn"])
        self.btn_recharge = Button((bx(4), BUTTON_Y, bw + 10, bh), "RECHARGE ($500)", C_BTN_GOLD,  C_BTN_GOLD_H,  self.fonts["btn"])

        nudge_y = INFO_Y + 8
        self.btn_minus = Button((SCREEN_W - 224, nudge_y, 32, 32), "−", C_GOLD_DIM, C_GOLD, self.fonts["btn"])
        self.btn_plus  = Button((SCREEN_W - 56,  nudge_y, 32, 32), "+", C_GOLD_DIM, C_GOLD, self.fonts["btn"])

        self._action_buttons = [
            self.btn_deal, self.btn_bet, self.btn_fold,
            self.btn_next, self.btn_recharge,
        ]
        self._all_buttons = self._action_buttons + [self.btn_minus, self.btn_plus]


    def _update_buttons(self, mouse_pos):
        phase = self.game.phase
        self.btn_deal.enabled     = phase == GamePhase.WAITING_FOR_BET
        self.btn_bet.enabled      = phase == GamePhase.FLOP
        self.btn_fold.enabled     = phase == GamePhase.FLOP
        self.btn_next.enabled     = phase == GamePhase.SHOWDOWN
        self.btn_recharge.enabled = phase == GamePhase.GAME_OVER
        self.btn_minus.enabled    = phase == GamePhase.WAITING_FOR_BET
        self.btn_plus.enabled     = phase == GamePhase.WAITING_FOR_BET
        for b in self._all_buttons:
            b.update(mouse_pos)


    def _draw_background(self):
        self.screen.fill(C_FELT)

        for i in range(10):
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, 14),
                             pygame.Rect(i * 4, i * 4,
                                         SCREEN_W - i * 8, SCREEN_H - i * 8),
                             width=10, border_radius=22)
            self.screen.blit(s, (0, 0))

        pygame.draw.rect(self.screen, C_GOLD,
                         pygame.Rect(10, 10, SCREEN_W - 20, BOTTOM_EDGE),
                         2, border_radius=18)

        title = self.fonts["title"].render("♠  CASINO POKER  ♠", True, C_GOLD)
        self.screen.blit(title, title.get_rect(centerx=SCREEN_W // 2, top=14))

        pygame.draw.line(self.screen, C_GOLD_DIM,
                         (28, TITLE_H), (SCREEN_W - 28, TITLE_H), 1)

        pygame.draw.line(self.screen, C_GOLD_DIM,
                         (28, DIVIDER_Y), (SCREEN_W - 28, DIVIDER_Y), 1)

    def _draw_info_bar(self):
        chip_txt = self.fonts["ui_bold"].render(
            f"Chips:  ${self.game.chips}", True, C_CHIP)
        self.screen.blit(chip_txt, (28, INFO_Y))

        if self.game.ante > 0:
            ante_txt = self.fonts["ui"].render(
                f"Ante: ${self.game.ante}   •   Call: ${self.game.ante}",
                True, C_OFF_WHITE)
            self.screen.blit(ante_txt, (28, INFO_Y + 26))

        if self.game.phase == GamePhase.WAITING_FOR_BET:
            try:
                val = int(self.ante_input) if self.ante_input else 0
            except ValueError:
                val = 0

            lbl = self.fonts["ui"].render("Ante bet:", True, C_OFF_WHITE)
            self.screen.blit(lbl, (SCREEN_W - 278, INFO_Y + 10))

            box = pygame.Rect(SCREEN_W - 188, INFO_Y + 4, 56, 34)
            draw_rounded_rect(self.screen, C_FELT_DARK, box, radius=6,
                              border=2, border_color=C_GOLD)
            v = self.fonts["ui_bold"].render(str(val), True, C_GOLD)
            self.screen.blit(v, v.get_rect(center=box.center))

            self.btn_minus.draw(self.screen)
            self.btn_plus.draw(self.screen)

    def _draw_hand_label(self, text, cx, top):
        lbl = self.fonts["subtitle"].render(text, True, C_GOLD_DIM)
        self.screen.blit(lbl, lbl.get_rect(centerx=cx, top=top))

    def _draw_cards_row(self, cards, x0, y, face_up=True, n_total=2):
        gap = CARD_W + 14
        for i in range(n_total):
            cx = x0 + i * gap
            if i < len(cards):
                draw_card(self.screen, cards[i], cx, y, self.fonts, face_up=face_up)
            else:
                ph = pygame.Rect(cx, y, CARD_W, CARD_H)
                draw_rounded_rect(self.screen, C_FELT_LIGHT, ph, radius=10,
                                  border=2, border_color=(60, 110, 65))

    def _draw_dealer_hand(self):
        cx = SCREEN_W // 2
        x0 = cx - (CARD_W + 7)   
        self._draw_hand_label("Dealer's Hand", cx, DEALER_Y - 20)
        face_up = self.game.phase == GamePhase.SHOWDOWN
        self._draw_cards_row(self.game.dealer_hand, x0, DEALER_Y,
                             face_up=face_up, n_total=2)

    def _draw_community(self):
        cx  = SCREEN_W // 2
        gap = CARD_W + 14
        x0  = cx - (5 * gap - 14) // 2
        self._draw_hand_label("Community Cards", cx, COMMUNITY_Y - 20)

        revealed = self.game.flop + self.game.turn_river
        for i in range(5):
            px = x0 + i * gap
            if i < len(revealed):
                draw_card(self.screen, revealed[i], px, COMMUNITY_Y,
                          self.fonts, face_up=True)
            else:
                ph = pygame.Rect(px, COMMUNITY_Y, CARD_W, CARD_H)
                draw_rounded_rect(self.screen, C_FELT_LIGHT, ph, radius=10,
                                  border=2, border_color=(60, 110, 65))

    def _draw_player_hand(self):
        cx = SCREEN_W // 2
        x0 = cx - (CARD_W + 7)
        self._draw_hand_label("Your Hand", cx, PLAYER_Y - 20)
        self._draw_cards_row(self.game.player_hand, x0, PLAYER_Y,
                             face_up=True, n_total=2)

    def _draw_message(self):
        strip = pygame.Surface((SCREEN_W - 24, 34), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 55))
        self.screen.blit(strip, (12, MESSAGE_Y - 4))

        shadow = self.fonts["result"].render(self.message, True, C_BLACK)
        msg    = self.fonts["result"].render(self.message, True, self.msg_color)
        self.screen.blit(shadow, shadow.get_rect(centerx=SCREEN_W // 2 + 2, top=MESSAGE_Y + 1))
        self.screen.blit(msg,       msg.get_rect(centerx=SCREEN_W // 2,     top=MESSAGE_Y))

    def _draw_hint(self):
        hints = {
            GamePhase.WAITING_FOR_BET: "Use − / + or type a number to set your ante, then press DEAL.",
            GamePhase.PRE_FLOP:        "Cards dealt.  The flop is being revealed…",
            GamePhase.FLOP:            "BET to see the turn & river (costs one ante), or FOLD to surrender.",
            GamePhase.SHOWDOWN:        "Round complete.  Press NEW ROUND to continue.",
            GamePhase.GAME_OVER:       "Out of chips!  Press RECHARGE ($500) to keep playing.",
        }
        text  = hints.get(self.game.phase, "")
        hint  = self.fonts["small"].render(text, True, (168, 212, 168))
        self.screen.blit(hint, hint.get_rect(centerx=SCREEN_W // 2, top=HINT_Y))


    def _handle_events(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        self._update_buttons(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

            # Keyboard ante input
            if event.type == pygame.KEYDOWN and self.game.phase == GamePhase.WAITING_FOR_BET:
                if event.key == pygame.K_BACKSPACE:
                    self.ante_input = self.ante_input[:-1]
                elif event.unicode.isdigit():
                    raw = (self.ante_input + event.unicode).lstrip("0")
                    self.ante_input = raw or "0"

            # Nudge buttons
            if self.btn_minus.clicked(event):
                try:
                    self.ante_input = str(max(5, int(self.ante_input) - 5))
                except ValueError:
                    self.ante_input = "5"

            if self.btn_plus.clicked(event):
                try:
                    self.ante_input = str(min(self.game.chips, int(self.ante_input) + 5))
                except ValueError:
                    self.ante_input = "5"

            # DEAL
            if self.btn_deal.clicked(event):
                try:
                    amt = int(self.ante_input)
                except ValueError:
                    amt = 0
                if self.game.place_ante(amt):
                    self.game.reveal_flop()
                    self.message   = "Flop revealed!  Bet to see the turn & river, or fold."
                    self.msg_color = C_OFF_WHITE
                else:
                    self.message   = "Invalid ante — must be at least 5 and no more than your chips."
                    self.msg_color = C_RED

            # BET
            if self.btn_bet.clicked(event):
                result = self.game.player_bet()
                self.message   = self.game.result_message
                self.msg_color = self._result_color(result)

            # FOLD
            if self.btn_fold.clicked(event):
                self.game.player_fold()
                self.message   = self.game.result_message
                self.msg_color = C_RED

            # NEW ROUND
            if self.btn_next.clicked(event):
                self.game.new_round()
                self.message   = "New round!  Set your ante and press DEAL."
                self.msg_color = C_GOLD

            # RECHARGE  (only active on GAME_OVER)
            if self.btn_recharge.clicked(event):
                self.game.chips = PokerGame.STARTING_CHIPS
                self.game.new_round()
                self.message   = "Chips recharged to $500.  Good luck!"
                self.msg_color = C_GOLD

        return True

    def _result_color(self, result: GameResult) -> tuple:
        return {
            GameResult.PLAYER_WINS:       (100, 220, 100),
            GameResult.TIE:               C_GOLD,
            GameResult.DEALER_NO_QUALIFY: (150, 220, 255),
            GameResult.DEALER_WINS:       C_RED,
        }.get(result, C_OFF_WHITE)


    def run(self):
        while True:
            if not self._handle_events():
                break

            self._draw_background()

            if self.game.phase not in (GamePhase.WAITING_FOR_BET, GamePhase.GAME_OVER):
                self._draw_dealer_hand()
                self._draw_community()
                self._draw_player_hand()

            self._draw_info_bar()
            self._draw_message()
            self._draw_hint()

            for btn in self._action_buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    CasinoPokerApp().run()