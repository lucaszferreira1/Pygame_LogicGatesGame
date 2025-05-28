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
    screen.blit(txt, (int(pos[0]), int(pos[1])))

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

def draw_success_message(screen, width, height, font, color):
    backboard_rect = pygame.Rect(width // 4, height // 2 - height // 8, width - width // 2, height // 4)
    pygame.draw.rect(screen, (30, 30, 30), backboard_rect, border_radius=20)
    pygame.draw.rect(screen, (60, 60, 60), backboard_rect, 4, border_radius=20)
    success_text = font.render("Nível Completo!", True, color)
    screen.blit(success_text, success_text.get_rect(center=(width // 2, height // 2)))

def draw_run_button(screen, pos, color, button_size=56, hover=True):
    rect = pygame.Rect(pos[0], pos[1], button_size, button_size)

    # Change colors if hovered
    bg_color = (40, 180, 90)
    if hover:
        border_color = (40, 120, 60)
        triangle_color = (color[0], color[1], color[2], 200)
    else:
        border_color = (20, 90, 45)
        triangle_color = color

    pygame.draw.rect(screen, bg_color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, 4, border_radius=14)

    triangle_width = button_size * 0.45
    triangle_height = button_size * 0.38
    cx, cy = rect.center

    triangle = [
        (cx - triangle_width * 0.5, cy - triangle_height),  # top left
        (cx - triangle_width * 0.5, cy + triangle_height),  # bottom left
        (cx + triangle_width * 0.6, cy)                    # right (tip)
    ]

    shadow_offset = 1
    shadow_triangle = [(x + shadow_offset, y + shadow_offset) for (x, y) in triangle]
    pygame.draw.polygon(screen, (0, 0, 0, 60), shadow_triangle)

    pygame.draw.polygon(screen, triangle_color, triangle)

def draw_truth_table_button(screen, pos, color, button_size=56, hover=True):
    rect = pygame.Rect(pos[0], pos[1], button_size, button_size)

    # Change colors if hovered
    bg_color = (40, 180, 90)
    if hover:
        border_color = (40, 120, 60)
        icon_color = (color[0], color[1], color[2], 200)
    else:
        border_color = (20, 90, 45)
        icon_color = color

    pygame.draw.rect(screen, bg_color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, 4, border_radius=14)

    # Draw the truth table icon
    cell_width = button_size // 4
    cell_height = button_size // 4
    grid_size = 3 * cell_width
    # Calculate top-left corner to center the grid inside the button
    grid_x = rect.x + (button_size - grid_size) // 2
    grid_y = rect.y + (button_size - grid_size) // 2
    for i in range(3):
        for j in range(3):
            cell_rect = pygame.Rect(
                grid_x + i * cell_width + 2,
                grid_y + j * cell_height + 2,
                cell_width - 4,
                cell_height - 4
            )
            pygame.draw.rect(screen, icon_color, cell_rect)