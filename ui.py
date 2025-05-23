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

    def draw(self, surface, is_selected, border_sel, dark_bg, offset=(0, 0)):
        bg_color = self.hover_color if is_selected else self.background_color
        rect = self.rect.move(offset)

        # Use rounded corners always
        border_radius = min(rect.width, rect.height) // 2  # Make it as round as possible

        # Draw a shadow for depth
        shadow_offset = (4, 4)
        shadow_rect = rect.move(shadow_offset)
        shadow_surf = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (30, 30, 30, 120), shadow_surf.get_rect(), border_radius=border_radius)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Draw gradient background with rounded corners
        gradient_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        for y in range(rect.height):
            alpha = 255
            r = int(bg_color[0] * (1 - y / rect.height) + 40 * (y / rect.height))
            g = int(bg_color[1] * (1 - y / rect.height) + 40 * (y / rect.height))
            b = int(bg_color[2] * (1 - y / rect.height) + 40 * (y / rect.height))
            pygame.draw.line(gradient_surf, (r, g, b, alpha), (0, y), (rect.width, y))
        
        # Mask the gradient with a rounded rectangle
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=border_radius)
        gradient_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(gradient_surf, rect.topleft)

        # Draw border with a thicker, rounded look
        border_col = border_sel if is_selected else dark_bg
        pygame.draw.rect(surface, border_col, rect, width=5, border_radius=border_radius)

        # Draw the text with a slight shadow
        text_rect = self.text_surf.get_rect(center=rect.center)
        shadow_offset = (1, 2)
        shadow_pos = (text_rect.x + shadow_offset[0], text_rect.y + shadow_offset[1])
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(shadow_surf, shadow_pos)
        surface.blit(self.text_surf, text_rect)

    def is_mouse_over(self, pos):
        return self.rect.collidepoint(pos)

def draw_text(screen, text, pos, font, color=(255, 255, 255)):
    txt = font.render(text, True, color)
    screen.blit(txt, pos)

def draw_background(screen, color, pattern_offset=0):
    # Fill with a vertical gradient from color to a darker shade
    width, height = screen.get_size()
    for y in range(height):
        # Interpolate between the base color and a darker version
        factor = y / height
        r = int(color[0] * (1 - factor) + (color[0] // 2) * factor)
        g = int(color[1] * (1 - factor) + (color[1] // 2) * factor)
        b = int(color[2] * (1 - factor) + (color[2] // 2) * factor)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # Overlay a subtle diagonal pattern for texture
    pattern_color = (255, 255, 255, 18)  # Low alpha for subtlety
    pattern_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    spacing = 32
    # Move the pattern by pattern_offset (wraps around spacing)
    offset = int(pattern_offset) % spacing
    for x in range(-height, width, spacing):
        pygame.draw.line(pattern_surf, pattern_color, (x + offset, 0), (x + height + offset, height), 2)
    screen.blit(pattern_surf, (0, 0))