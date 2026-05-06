"""Snake Deluxe v2.0 — main game module with logic, entities, and input handling."""

import pygame
import os
import sys
import math
from random import randrange, random
from enum import Enum

try:
    from sound_manager import get_sound_manager as _get_sm

    _SOUND_AVAILABLE = True
except Exception:
    _SOUND_AVAILABLE = False

    def _get_sm():
        """Return None when sound is unavailable."""
        return None


_ui = None

WINDOW = 800
TILE_SIZE = 40
RANGE = (TILE_SIZE // 2, WINDOW - TILE_SIZE // 2, TILE_SIZE)
BASE_SPEED = 120
FPS = 60
MAX_HISTORY = 5
COUNTDOWN = 60
CHAOS_INTERVAL = 4000

C_BG = (8, 10, 20)
C_GRID = (18, 20, 35)
C_TEXT = (210, 215, 230)
C_DIM = (100, 110, 130)
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_RED = (255, 60, 80)
C_YELLOW = (255, 220, 50)
C_CYAN = (0, 220, 255)

SKINS = {
    "Verde": ((0, 230, 120), (0, 160, 70), (255, 255, 255)),
    "Fuego": ((255, 100, 20), (200, 40, 0), (255, 255, 100)),
    "Hielo": ((100, 200, 255), (30, 120, 200), (0, 0, 80)),
    "Arcoiris": None,
    "Dorado": ((255, 215, 0), (200, 160, 0), (80, 50, 0)),
    "Neon": ((200, 0, 255), (100, 0, 180), (0, 255, 200)),
}

FRUITS = {
    "Manzana": ((220, 40, 60), 1, 50, 8),
    "Uva": ((140, 60, 200), 2, 30, 6),
    "Sandia": ((60, 190, 80), 3, 15, 10),
    "Estrella": ((255, 220, 0), 5, 5, 10),
}

GAME_MODES = ["Clasico", "Portal", "Contrarreloj", "Caos", "Obstaculos"]


def random_pos():
    """Return a random grid-aligned [x, y] position within the playfield."""
    return [randrange(*RANGE), randrange(*RANGE)]


def random_pos_excluding(excluded):
    """Return a random position that does not overlap any position in *excluded*."""
    for _ in range(400):
        p = random_pos()
        if p not in excluded:
            return p
    return random_pos()


def snap_to_grid(v):
    """Snap pixel coordinate *v* to the nearest tile centre."""
    return (round((v - TILE_SIZE // 2) / TILE_SIZE) * TILE_SIZE) + TILE_SIZE // 2


def lerp_color(a, b, t):
    """Linearly interpolate between RGB tuples *a* and *b* by factor *t* (0-1)."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rainbow_color(index, total, offset=0.0):
    """Return an RGB colour from the rainbow spectrum.

    Uses *index* out of *total* steps, shifted by *offset*.
    """
    hue = (index / max(total - 1, 1) + offset) % 1.0
    h = hue * 6
    x = 1 - abs(h % 2 - 1)
    if h < 1:
        r, g, b = 1, x, 0
    elif h < 2:
        r, g, b = x, 1, 0
    elif h < 3:
        r, g, b = 0, 1, x
    elif h < 4:
        r, g, b = 0, x, 1
    elif h < 5:
        r, g, b = x, 0, 1
    else:
        r, g, b = 1, 0, x
    return (int(r * 255), int(g * 255), int(b * 255))


class Direction(Enum):
    """Cardinal movement directions for the snake, plus a stationary NONE state."""

    NONE = (0, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self):
        """Return the direction that is directly opposite to this one."""
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.NONE: Direction.NONE,
        }[self]

    def to_pixels(self):
        """Convert the direction unit vector to a pixel-delta tuple."""
        return (self.value[0] * TILE_SIZE, self.value[1] * TILE_SIZE)


class Screen(Enum):
    """Identifiers for the different screens / states of the game."""

    MAIN_MENU = "main_menu"
    CUSTOMIZE = "customize"
    MODE_SELECT = "mode_select"
    PLAYING = "playing"
    PAUSED = "paused"
    DEAD = "dead"


class Fruit:
    """Collectible fruit that spawns at a random tile and animates with a pulse/glow."""

    def __init__(self, excluded=None):
        """Spawn a new fruit avoiding positions listed in *excluded*."""
        self._pulse = 0.0
        self._angle = 0.0
        self._spawn(excluded or [])

    def _spawn(self, excluded):
        """Pick a random fruit type and position, avoiding *excluded* cells."""
        names = list(FRUITS.keys())
        weights = [FRUITS[n][2] for n in names]
        total_w = sum(weights)
        r = random() * total_w
        cum = 0
        self.kind = names[0]
        for n, w in zip(names, weights):
            cum += w
            if r <= cum:
                self.kind = n
                break
        color, pts, _, rad = FRUITS[self.kind]
        self.color = color
        self.points = pts
        self.radius = rad
        self.rect = pygame.Rect(0, 0, TILE_SIZE - 2, TILE_SIZE - 2)
        self.rect.center = random_pos_excluding(excluded)

    def reposition(self, excluded=None):
        """Relocate the fruit to a new random position outside *excluded*."""
        self._spawn(excluded or [])

    def update(self, dt):
        """Advance the pulse and rotation animations by *dt* milliseconds."""
        self._pulse = (self._pulse + dt * 0.005) % (2 * math.pi)
        self._angle = (self._angle + dt * 0.003) % (2 * math.pi)

    def draw(self, surface):
        """Render the fruit with a glow halo and kind-specific shape onto *surface*."""
        cx, cy = self.rect.center
        scale = 1.0 + 0.10 * math.sin(self._pulse)
        r = int(self.radius * scale)
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 45), (r * 2, r * 2), r * 2)
        surface.blit(glow, (cx - r * 2, cy - r * 2))
        if self.kind == "Manzana":
            self._draw_apple(surface, cx, cy, r)
        elif self.kind == "Uva":
            self._draw_grape(surface, cx, cy, r)
        elif self.kind == "Sandia":
            self._draw_watermelon(surface, cx, cy, r)
        elif self.kind == "Estrella":
            self._draw_star(surface, cx, cy, r)

    def _draw_apple(self, s, cx, cy, r):
        """Draw a stylised apple shape centred at (*cx*, *cy*) with radius *r*."""
        pygame.draw.circle(s, self.color, (cx, cy + 2), r)
        pygame.draw.circle(s, (255, 80, 80), (cx - r // 3, cy - r // 3), r // 3)
        pygame.draw.line(s, (80, 180, 40), (cx, cy - r + 2), (cx + 4, cy - r - 6), 2)

    def _draw_grape(self, s, cx, cy, r):
        """Draw a bunch-of-grapes shape centred at (*cx*, *cy*) with radius *r*."""
        off = [
            (-r // 2, -r // 2),
            (r // 2, -r // 2),
            (0, -r // 4),
            (-r // 3, r // 4),
            (r // 3, r // 4),
            (0, r // 2),
        ]
        for ox, oy in off:
            pygame.draw.circle(s, self.color, (cx + ox, cy + oy), r // 3 + 1)
            pygame.draw.circle(s, (180, 100, 230), (cx + ox - 1, cy + oy - 1), r // 6)

    def _draw_watermelon(self, s, cx, cy, r):
        """Draw a watermelon slice centred at (*cx*, *cy*) with radius *r*."""
        pygame.draw.circle(s, (60, 190, 80), (cx, cy), r)
        pygame.draw.circle(s, (40, 150, 50), (cx, cy), r, 2)
        pygame.draw.circle(s, (220, 50, 80), (cx, cy), int(r * 0.72))
        for i in range(4):
            a = i * math.pi / 2 + math.pi / 4
            pygame.draw.circle(
                s,
                (10, 10, 10),
                (int(cx + r * 0.35 * math.cos(a)), int(cy + r * 0.35 * math.sin(a))),
                2,
            )

    def _draw_star(self, s, cx, cy, r):
        """Draw a rotating 5-pointed star centred at (*cx*, *cy*) with radius *r*."""
        pts = []
        for i in range(10):
            a = math.pi / 2 + i * 2 * math.pi / 10 + self._angle
            ri = r if i % 2 == 0 else r // 2
            pts.append((int(cx + ri * math.cos(a)), int(cy - ri * math.sin(a))))
        pygame.draw.polygon(s, self.color, pts)
        pygame.draw.polygon(s, (255, 255, 200), pts, 1)


class Obstacle:
    """A set of static rectangular tiles that the snake must avoid."""

    def __init__(self, centers):
        """Build obstacle rects from a list of (cx, cy) centre coordinates."""
        self.rects = []
        for cx, cy in centers:
            r = pygame.Rect(0, 0, TILE_SIZE - 2, TILE_SIZE - 2)
            r.center = (cx, cy)
            self.rects.append(r)

    def collides_with(self, rect):
        """Return True if *rect* overlaps any obstacle tile."""
        return rect.collidelist(self.rects) != -1

    def get_centers(self):
        """Return a list of [x, y] centres for all obstacle tiles."""
        return [list(r.center) for r in self.rects]

    def draw(self, surface):
        """Render all obstacle tiles onto *surface*."""
        for r in self.rects:
            pygame.draw.rect(surface, (75, 85, 105), r, border_radius=4)
            pygame.draw.rect(surface, (100, 115, 140), r, 1, border_radius=4)


def make_obstacles():
    """Generate a grid of obstacle centre positions for the Obstaculos game mode."""
    centers = []
    step = TILE_SIZE * 3
    for x in range(RANGE[0] + step, RANGE[1] - step + 1, step * 2):
        for y in range(RANGE[0] + step, RANGE[1] - step + 1, step * 2):
            for dx, dy in [(0, 0), (TILE_SIZE, 0), (0, TILE_SIZE)]:
                nx, ny = x + dx, y + dy
                if RANGE[0] <= nx <= RANGE[1] and RANGE[0] <= ny <= RANGE[1]:
                    centers.append((nx, ny))
    return centers


class Snake:
    """Player-controlled snake: manages segments, movement, and collisions."""

    def __init__(self, skin="Verde"):
        """Initialise the snake with the given *skin* name and call reset()."""
        self.skin = skin
        self._rainbow_offset = 0.0
        self.reset()

    def reset(self):
        """Place the snake at a random position with length 1 and no direction."""
        head = pygame.Rect(0, 0, TILE_SIZE - 2, TILE_SIZE - 2)
        head.center = random_pos()
        self.segments = [head.copy()]
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.length = 1
        self.alive = True

    def set_direction(self, new_dir):
        """Queue *new_dir* as the next movement direction, ignoring reversal."""
        if self.direction == Direction.NONE:
            self.next_direction = new_dir
        elif new_dir != self.direction.opposite():
            self.next_direction = new_dir

    def move(self, portal=False):
        """Advance the snake one tile; wrap around the board when *portal* is True."""
        if not self.alive:
            return
        self.direction = self.next_direction
        if self.direction == Direction.NONE:
            return
        head = self.segments[-1].copy()
        dx, dy = self.direction.to_pixels()
        head.move_ip(dx, dy)
        if portal:
            if head.right <= 0:
                head.left = WINDOW
            elif head.left >= WINDOW:
                head.right = 0
            if head.bottom <= 0:
                head.top = WINDOW
            elif head.top >= WINDOW:
                head.bottom = 0
        self.segments.append(head)
        self.segments = self.segments[-self.length :]

    @property
    def head(self):
        """The leading (head) segment rect."""
        return self.segments[-1]

    @property
    def body(self):
        """All segments except the head."""
        return self.segments[:-1]

    def check_wall_collision(self):
        """Return True if the head has left the playfield boundaries."""
        h = self.head
        return h.left < 0 or h.right > WINDOW or h.top < 0 or h.bottom > WINDOW

    def check_self_collision(self):
        """Return True if the head overlaps any body segment (ignores short snakes)."""
        if len(self.segments) < 4:
            return False
        return self.head.collidelist(self.body) != -1

    def check_obstacle_collision(self, obstacle):
        """Return True if the head collides with *obstacle*, or False when None."""
        if obstacle is None:
            return False
        return obstacle.collides_with(self.head)

    def is_dead(self, portal=False, obstacle=None):
        """Return True if any lethal collision has occurred this frame."""
        wall = False if portal else self.check_wall_collision()
        return (
            wall
            or self.check_self_collision()
            or self.check_obstacle_collision(obstacle)
        )

    def eats_fruit(self, fruit):
        """Return True when the head rect overlaps the fruit rect."""
        return self.head.colliderect(fruit.rect)

    def grow(self):
        """Increase the snake's target length by one segment."""
        self.length += 1

    def get_segment_centers(self):
        """Return a list of [x, y] centres for every segment."""
        return [list(s.center) for s in self.segments]

    def update(self, dt):
        """Advance rainbow animation by *dt* ms; no-op for non-rainbow skins."""
        if self.skin == "Arcoiris":
            self._rainbow_offset = (self._rainbow_offset + dt * 0.0003) % 1.0

    def _segment_color(self, index, total):
        """Return the colour for segment at *index* out of *total*."""
        if self.skin == "Arcoiris":
            return rainbow_color(index, total, self._rainbow_offset)
        head_c, body_c, _ = SKINS[self.skin]
        t = index / max(total - 1, 1)
        return lerp_color(body_c, head_c, t)

    def draw(self, surface):
        """Render all segments and the directional eyes onto *surface*."""
        total = len(self.segments)
        for i, seg in enumerate(self.segments):
            col = self._segment_color(i, total)
            pygame.draw.rect(surface, col, seg, border_radius=6)
            hi = pygame.Rect(seg.x + 2, seg.y + 2, seg.width - 4, 3)
            pygame.draw.rect(
                surface, tuple(min(255, c + 55) for c in col), hi, border_radius=2
            )
        if self.direction != Direction.NONE and total > 0:
            self._draw_eyes(surface)

    def _draw_eyes(self, surface):
        """Draw two eyes on the head facing the current direction."""
        head = self.head
        cx, cy = head.center
        d = self.direction
        eo = 7
        if d == Direction.UP:
            e1, e2 = (cx - eo, cy - 4), (cx + eo, cy - 4)
        elif d == Direction.DOWN:
            e1, e2 = (cx - eo, cy + 4), (cx + eo, cy + 4)
        elif d == Direction.LEFT:
            e1, e2 = (cx - 4, cy - eo), (cx - 4, cy + eo)
        else:
            e1, e2 = (cx + 4, cy - eo), (cx + 4, cy + eo)
        skin_info = SKINS.get(self.skin)
        eye_color = skin_info[2] if skin_info else (255, 255, 255)
        for eye in (e1, e2):
            pygame.draw.circle(surface, eye_color, eye, 4)
            pygame.draw.circle(surface, C_BLACK, eye, 2)


class ScoreBoard:
    """Tracks the current score, all-time high score, and recent game history."""

    def __init__(self):
        """Initialise the scoreboard with zero scores and an empty history list."""
        self.score = 0
        self.high_score = 0
        self.history = []

    def add_points(self, pts):
        """Add *pts* to the current score and update the high score if needed."""
        self.score += pts
        if self.score > self.high_score:
            self.high_score = self.score

    def reset(self):
        """Archive the current score and reset it to zero for a new game."""
        self.history.append(self.score)
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)
        self.score = 0

    def get_score(self):
        """Return the current in-game score."""
        return self.score

    def get_high_score(self):
        """Return the all-time high score across all games."""
        return self.high_score


class Button:
    """A rectangular UI button that can be drawn and hit-tested."""

    def __init__(self, rect, text, bg=(40, 45, 65), sel=(70, 80, 110)):
        """Create a button from a *rect* tuple, display *text*, and optional colours."""
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg = bg
        self.sel = sel
        self.selected = False

    def draw(self, surface, font):
        """Render the button (highlighted if selected) onto *surface* using *font*."""
        col = self.sel if self.selected else self.bg
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, (80, 95, 130), self.rect, 2, border_radius=8)
        txt = font.render(self.text, True, C_WHITE if self.selected else C_TEXT)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos):
        """Return True if the mouse position *pos* falls inside this button."""
        return self.rect.collidepoint(pos)


class Game:
    """Top-level controller: owns game state, handles events, and drives the loop."""

    def __init__(self, headless=False):
        """Set up the game window, entities, and sound manager.

        When *headless* is True no pygame display or audio is initialised.
        """
        global _ui
        if _ui is None:
            import game_ui as _ui_mod

            _ui = _ui_mod

        self.headless = headless
        self.selected_skin = "Verde"
        self.selected_mode = "Clasico"

        if not headless:
            pygame.init()
            self.screen = pygame.display.set_mode([WINDOW, WINDOW])
            pygame.display.set_caption("Snake Deluxe v2.0")
            self.clock = pygame.time.Clock()
            # Cargar imagen del logo
            logo = pygame.image.load(os.path.join("snake", "img", "logo.png")).convert()
            pygame.display.set_icon(logo)
            self._init_fonts()
            self._build_ui()

        self.snake = Snake(self.selected_skin)
        self.fruit = Fruit()
        self.obstacle = None
        self.scoreboard = ScoreBoard()
        self.screen_id = Screen.MAIN_MENU

        self._move_timer = 0
        self._move_interval = BASE_SPEED
        self._countdown = COUNTDOWN * 1000
        self._chaos_timer = 0
        self._bg_off = 0.0
        self.frame_count = 0

        self.sm = _get_sm() if _SOUND_AVAILABLE and not headless else None
        if self.sm:
            self.sm.set_music_level(0)

    def _init_fonts(self):
        """Load monospace fonts at several sizes; fall back to default if needed."""
        try:
            self.f_title = pygame.font.SysFont("monospace", 56, bold=True)
            self.f_big = pygame.font.SysFont("monospace", 34, bold=True)
            self.f_med = pygame.font.SysFont("monospace", 22)
            self.f_small = pygame.font.SysFont("monospace", 17)
            self.f_tiny = pygame.font.SysFont("monospace", 13)
        except Exception:
            for attr, sz in [
                ("f_title", 56),
                ("f_big", 34),
                ("f_med", 22),
                ("f_small", 17),
                ("f_tiny", 13),
            ]:
                setattr(self, attr, pygame.font.Font(None, sz))

    def _build_ui(self):
        """Instantiate all Button objects used across the menu screens."""
        cx = WINDOW // 2
        self._main_btns = [
            Button((cx - 130, 310, 260, 44), "JUGAR"),
            Button((cx - 130, 364, 260, 44), "MODO DE JUEGO"),
            Button((cx - 130, 418, 260, 44), "PERSONALIZAR"),
            Button((cx - 130, 472, 260, 44), "SALIR"),
        ]
        self._mode_btns = [
            Button((cx - 160, 230 + i * 68, 320, 52), m)
            for i, m in enumerate(GAME_MODES)
        ]
        skins = list(SKINS.keys())
        sw, sh = 205, 52
        cols = 3
        gx = cx - (cols * sw + (cols - 1) * 10) // 2
        self._skin_btns = [
            Button((gx + (i % cols) * (sw + 10), 270 + (i // cols) * 65, sw, sh), name)
            for i, name in enumerate(skins)
        ]
        self._back_btn = Button((20, 16, 110, 36), "<- Volver")
        self._play_btn = Button(
            (cx - 110, WINDOW - 90, 220, 48),
            "JUGAR AHORA",
            bg=(30, 100, 50),
            sel=(50, 160, 80),
        )

    def _go_to_menu(self):
        """Switch to the main menu screen and restart menu music."""
        self.screen_id = Screen.MAIN_MENU
        if self.sm:
            self.sm.set_music_level(0)

    def _reset_game(self):
        """Rebuild snake, fruit, and timers then transition to the PLAYING screen."""
        self.snake = Snake(self.selected_skin)
        excluded = self.snake.get_segment_centers()
        self.obstacle = None
        if self.selected_mode == "Obstaculos":
            obs = make_obstacles()
            self.obstacle = Obstacle(obs)
            excluded += self.obstacle.get_centers()
        self.fruit = Fruit(excluded)
        self.scoreboard.reset()
        self._move_timer = 0
        self._move_interval = BASE_SPEED
        self._countdown = COUNTDOWN * 1000
        self._chaos_timer = 0
        self.screen_id = Screen.PLAYING
        if self.sm:
            mode_music = {
                "Clasico": 1,
                "Portal": 2,
                "Contrarreloj": 3,
                "Caos": 4,
                "Obstaculos": 5,
            }
            self.sm.set_music_level(mode_music.get(self.selected_mode, 1))

    def _is_portal(self):
        """Return True when the current mode uses wrap-around portal movement."""
        return self.selected_mode == "Portal"

    def handle_event(self, event):
        """Dispatch a single pygame *event* to the appropriate handler."""
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)
        if event.type == pygame.KEYDOWN:
            self._key(event.key)

    def _click(self, pos):
        """Handle a left-mouse-button click at screen position *pos*."""
        scr = self.screen_id
        if scr == Screen.MAIN_MENU:
            acts = ["play", "mode", "custom", "quit"]
            for btn, act in zip(self._main_btns, acts):
                if btn.hit(pos):
                    if act == "play":
                        self._reset_game()
                    elif act == "mode":
                        self.screen_id = Screen.MODE_SELECT
                    elif act == "custom":
                        self.screen_id = Screen.CUSTOMIZE
                    elif act == "quit":
                        pygame.quit()
                        sys.exit()
        elif scr == Screen.MODE_SELECT:
            if self._back_btn.hit(pos):
                self._go_to_menu()
            for btn, m in zip(self._mode_btns, GAME_MODES):
                if btn.hit(pos):
                    self.selected_mode = m
            if self._play_btn.hit(pos):
                self._reset_game()
        elif scr == Screen.CUSTOMIZE:
            if self._back_btn.hit(pos):
                self._go_to_menu()
            for btn, name in zip(self._skin_btns, list(SKINS.keys())):
                if btn.hit(pos):
                    self.selected_skin = name
            if self._play_btn.hit(pos):
                self._reset_game()
        elif scr == Screen.DEAD:
            cx = WINDOW // 2
            if pygame.Rect(cx - 120, 455, 240, 50).collidepoint(pos):
                self._reset_game()
            if pygame.Rect(cx - 120, 515, 240, 50).collidepoint(pos):
                self._go_to_menu()

    def _key(self, key):
        """Handle a key-down event identified by pygame key constant *key*."""
        km = {
            pygame.K_w: Direction.UP,
            pygame.K_UP: Direction.UP,
            pygame.K_s: Direction.DOWN,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_a: Direction.LEFT,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_d: Direction.RIGHT,
            pygame.K_RIGHT: Direction.RIGHT,
        }
        scr = self.screen_id
        if key in (pygame.K_p, pygame.K_ESCAPE):
            if scr == Screen.PLAYING:
                self.screen_id = Screen.PAUSED
            elif scr == Screen.PAUSED:
                self.screen_id = Screen.PLAYING
            elif scr in (Screen.MODE_SELECT, Screen.CUSTOMIZE):
                self._go_to_menu()
            elif scr == Screen.DEAD:
                self._go_to_menu()
        if key == pygame.K_m and self.sm:
            self.sm.toggle_music()
        if key == pygame.K_n and self.sm:
            self.sm.toggle_sfx()
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            if scr == Screen.MAIN_MENU:
                self._reset_game()
            elif scr == Screen.DEAD:
                self._reset_game()
            elif scr == Screen.PAUSED:
                self.screen_id = Screen.PLAYING
        if scr == Screen.PLAYING and key in km:
            self.snake.set_direction(km[key])

    def update(self, dt):
        """Advance all game logic by *dt* milliseconds for the current screen."""
        self._bg_off = (self._bg_off + dt * 0.00005) % 1.0
        if not self.headless:
            self.fruit.update(dt)
            self.snake.update(dt)
        if self.screen_id == Screen.PLAYING:
            self._update_playing(dt)
        self.frame_count += 1

    def _update_playing(self, dt):
        """Run per-frame gameplay logic: timers, movement, collision, and scoring."""
        if self.selected_mode == "Contrarreloj":
            self._countdown -= dt
            if self._countdown <= 0:
                self._countdown = 0
                self.scoreboard.reset()
                self.screen_id = Screen.DEAD
                return
        if self.selected_mode == "Caos":
            self._chaos_timer += dt
            if self._chaos_timer >= CHAOS_INTERVAL:
                self._chaos_timer = 0
                self.fruit.reposition(self.snake.get_segment_centers())
        self._move_timer += dt
        if self._move_timer < self._move_interval:
            return
        self._move_timer = 0
        portal = self._is_portal()
        self.snake.move(portal=portal)
        if self.snake.is_dead(portal=portal, obstacle=self.obstacle):
            self.scoreboard.reset()
            self.screen_id = Screen.DEAD
            if self.sm:
                self.sm.play("wall_hit")
                self.sm.play("die")
                self.sm.set_music_level(0)
            return
        if self.snake.eats_fruit(self.fruit):
            pts = self.fruit.points
            self.snake.grow()
            self.scoreboard.add_points(pts)
            excluded = self.snake.get_segment_centers()
            if self.obstacle:
                excluded += self.obstacle.get_centers()
            self.fruit.reposition(excluded)
            if self.selected_mode != "Contrarreloj":
                self._move_interval = max(45, BASE_SPEED - self.scoreboard.score * 2)
            if self.sm:
                self.sm.play("eat_rare" if pts >= 5 else "eat")

    def draw(self):
        """Render the current screen state to the pygame display."""
        if self.headless:
            return
        self.screen.fill(C_BG)
        _ui.draw_grid(self)
        scr = self.screen_id
        if scr == Screen.MAIN_MENU:
            _ui.draw_main_menu(self)
        elif scr == Screen.MODE_SELECT:
            _ui.draw_mode_select(self)
        elif scr == Screen.CUSTOMIZE:
            _ui.draw_customize(self)
        elif scr in (Screen.PLAYING, Screen.PAUSED):
            _ui.draw_playing(self, scr)
        elif scr == Screen.DEAD:
            _ui.draw_dead(self)
        pygame.display.flip()

    def _overlay(self, alpha=160):
        """Delegate a semi-transparent overlay draw to the UI module."""
        _ui.overlay(self, alpha)

    def _ctext(self, text, font, color, y):
        """Delegate centred text rendering to the UI module."""
        _ui.ctext(self, text, font, color, y)

    def _draw_hud(self):
        """Delegate HUD rendering to the UI module."""
        _ui.draw_hud(self)

    def run(self):
        """Enter the main loop: tick clock, process events, update, and draw."""
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
