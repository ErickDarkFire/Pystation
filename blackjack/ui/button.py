import pygame
import core.settings as st  # Cambiado para evitar F403/F405


class Button:
    def __init__(self, text, x, y, w, h, func_id):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.func_id = func_id
        self.enabled = True
        self.hover = False

    def draw(self, surface):
        # Usamos el prefijo st. para acceder a las constantes
        col = (
            (st.BUTTON_HOVER if self.hover else st.BUTTON_BG)
            if self.enabled
            else (50, 50, 50)
        )
        txt_col = st.WHITE if self.enabled else (100, 100, 100)
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, st.GOLD, self.rect, 2, border_radius=8)
        txt_surf = st.FONT_UI.render(self.text, True, txt_col)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def update(self, event_list):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.enabled and self.hover:
            for e in event_list:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    return self.func_id
        return None
