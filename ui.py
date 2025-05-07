import pygame

class Button:
    def __init__(self, text, font, x, y, padding, background_color, hover_color):
        self.text = text
        self.font = font
        self.padding = padding
        self.background_color = background_color
        self.hover_color = hover_color
        self.render_text()
        self.rect = self.text_surf.get_rect(center=(x, y))
        self.rect.inflate_ip(self.padding, self.padding)

    def render_text(self, color=(255, 255, 255)):
        self.text_surf = self.font.render(self.text, True, color)

    def draw(self, surface, is_selected, border_sel, dark_bg):
        bg_color = self.hover_color if is_selected else self.background_color
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        border_col = border_sel if is_selected else dark_bg
        pygame.draw.rect(surface, border_col, self.rect, width=3, border_radius=10)
        text_rect = self.text_surf.get_rect(center=self.rect.center)
        surface.blit(self.text_surf, text_rect)

    def is_mouse_over(self, pos):
        return self.rect.collidepoint(pos)

def draw_text(screen, text, pos, font, color=(255, 255, 255)):
    txt = font.render(text, True, color)
    screen.blit(txt, pos)