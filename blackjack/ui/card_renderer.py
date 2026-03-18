import pygame
import core.settings as st  # Cambiado
from models.card import Card


def draw_suit_shape(
    surface: pygame.Surface,
    suit: str,
    x: float,
    y: float,
    scale: float = 1.0,
    color: tuple = None,  # Por defecto None para usar st.BLACK abajo
) -> None:
    if color is None:
        color = st.BLACK

    s = 10 * scale
    if suit == "♦":
        points = [(x, y - s * 1.2), (x + s, y), (x, y + s * 1.2), (x - s, y)]
        pygame.draw.polygon(surface, color, points)
    elif suit == "♥":
        r = s * 0.5
        pygame.draw.circle(surface, color, (int(x - r), int(y - r * 0.5)), int(r))
        pygame.draw.circle(surface, color, (int(x + r), int(y - r * 0.5)), int(r))
        points = [(x - s, y), (x + s, y), (x, y + s * 1.3)]
        pygame.draw.polygon(surface, color, points)
    elif suit == "♠":
        r = s * 0.5
        pygame.draw.circle(surface, color, (int(x - r), int(y + r * 0.2)), int(r))
        pygame.draw.circle(surface, color, (int(x + r), int(y + r * 0.2)), int(r))
        points = [(x - s, y + r * 0.5), (x + s, y + r * 0.5), (x, y - s)]
        pygame.draw.polygon(surface, color, points)
        stem = [(x, y - s * 0.2), (x - s * 0.2, y + s), (x + s * 0.2, y + s)]
        pygame.draw.polygon(surface, color, stem)
    elif suit == "♣":
        r = s * 0.45
        pygame.draw.circle(surface, color, (int(x), int(y - r)), int(r))
        pygame.draw.circle(surface, color, (int(x - r), int(y + r * 0.5)), int(r))
        pygame.draw.circle(surface, color, (int(x + r), int(y + r * 0.5)), int(r))
        stem = [(x, y), (x - s * 0.2, y + s), (x + s * 0.2, y + s)]
        pygame.draw.polygon(surface, color, stem)


def draw_card(surface: pygame.Surface, card: Card) -> None:
    rect = pygame.Rect(card.x, card.y, card.width, card.height)
    shadow_surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow_surf,
        (0, 0, 0, 100),
        (0, 0, card.width, card.height),
        border_radius=8,
    )
    surface.blit(shadow_surf, (card.x + 4, card.y + 4))

    if card.face_up:
        pygame.draw.rect(surface, st.WHITE, rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), rect, 2, border_radius=8)
        color = st.RED_SUIT if card.suit in ["♥", "♦"] else st.BLACK_SUIT
        rank_txt = st.FONT_CARD.render(card.rank, True, color)
        surface.blit(rank_txt, (card.x + 8, card.y + 5))
        draw_suit_shape(surface, card.suit, card.x + 20, card.y + 55, 0.8, color)
        draw_suit_shape(
            surface,
            card.suit,
            card.x + card.width / 2,
            card.y + card.height / 2,
            3.0,
            color,
        )
    else:
        pygame.draw.rect(surface, (150, 20, 20), rect, border_radius=8)
        pygame.draw.rect(
            surface,
            st.WHITE,
            (card.x + 5, card.y + 5, card.width - 10, card.height - 10),
            2,
            border_radius=6,
        )
