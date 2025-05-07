import pygame
import sys
from ui import Button, draw_text
from logic import Gate, Level

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Logic Gate Puzzle")
clock = pygame.time.Clock()

# Colors & Fonts
dark_bg = (25, 25, 25)
white = (255, 255, 255)
green = (34, 139, 34)
hover_color = (50, 200, 50)
button_bg = (40, 40, 40)
panel_bg = (50, 50, 50)

title_font = pygame.font.SysFont('arialrounded', 64)
menu_font = pygame.font.SysFont('arial', 24)
gate_font = pygame.font.SysFont('arial', 20)
terminal_font = pygame.font.SysFont('arial', 8)

logic_gates = {
    'AND': Gate('AND', ['in1', 'in2'], ['out1'], (0, 0), gate_font, button_bg),
    'OR': Gate('OR', ['in1', 'in2'], ['out1'], (0, 0), gate_font, button_bg),
    'NOT': Gate('NOT', ['in1'], ['out1'], (0, 0), gate_font, button_bg),
    'XOR': Gate('XOR', ['in1', 'in2'], ['out1'], (0, 0), gate_font, button_bg),
    'NAND': Gate('NAND', ['in1', 'in2'], ['out1'], (0, 0), gate_font, button_bg),
    'NOR': Gate('NOR', ['in1', 'in2'], ['out1'], (0, 0), gate_font, button_bg),
}

def play_level(level):
    palette = [(gt, (100 + i * 100, HEIGHT - 50)) for i, gt in enumerate(level.allowed_gates)]
    dragging = None
    offset = (0, 0)

    while True:
        screen.fill(dark_bg)
        pygame.draw.rect(screen, panel_bg, (0, HEIGHT - 100, WIDTH, 100))
        for gt, pos in palette:
            pygame.draw.circle(screen, button_bg, pos, 30)
            pygame.draw.circle(screen, white, pos, 30, 2)
            draw_text(screen, gt[0], (pos[0] - 7, pos[1] - 10), gate_font)

        level.draw(screen, WIDTH, HEIGHT, button_bg, hover_color, gate_font)

        if dragging:
            dragging.position = (pygame.mouse.get_pos()[0] + offset[0], pygame.mouse.get_pos()[1] + offset[1])
            dragging.draw(screen, hover_color, selected=True)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    for gt, pos in palette:
                        if (e.pos[0] - pos[0])**2 + (e.pos[1] - pos[1])**2 < 900:
                            new_gate = logic_gates[gt].copy()
                            new_gate.position = e.pos
                            level.add_gate(new_gate)
                            dragging = new_gate
                            offset = (new_gate.position[0] - e.pos[0], new_gate.position[1] - e.pos[1])
                            break
                    for gate in level.gates:
                        if (e.pos[0] - gate.position[0])**2 + (e.pos[1] - gate.position[1])**2 < gate.radius**2:
                            dragging = gate
                            offset = (gate.position[0] - e.pos[0], gate.position[1] - e.pos[1])
                            break
            elif e.type == pygame.MOUSEBUTTONUP:
                if dragging and dragging.position[1] > HEIGHT - 100:
                    level.gates.remove(dragging)
                dragging = None
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return

        clock.tick(60)


def history_menu():
    levels = [Level("Nível 1", {'A': True, 'B': False}, {'X': True}, ['AND', 'OR', 'NOT']),
              Level("Nível 2", {'A': False, 'B': False, 'C': True}, {'Y': False}, ['AND', 'NOT', 'OR']),
              Level("Nível 3", {'A': True, 'B': True}, {'Z': False}, ['XOR', 'NOT'])]
    labels = [lvl.name for lvl in levels]

    # Grid
    columns = 2
    x_spacing = WIDTH // (columns + 1)
    y_start = 200
    y_spacing = 80

    # Buttons
    level_buttons = []
    for idx, lvl in enumerate(labels):
        col = idx % columns
        row = idx // columns
        x = x_spacing * (col + 1)
        y = y_start + row * y_spacing
        level_buttons.append(Button(lvl, menu_font, x, y, 50, button_bg, hover_color))

    voltar_button = Button("Voltar", menu_font, WIDTH // 2, HEIGHT - 80, 50, button_bg, hover_color)
    selected = 0
    total_items = len(level_buttons) + 1

    while True:
        screen.fill(dark_bg)
        title_surf = title_font.render("História", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 80)))

        mx, my = pygame.mouse.get_pos()
        for i, btn in enumerate(level_buttons):
            is_sel = (i == selected) or btn.is_mouse_over((mx, my))
            btn.draw(screen, is_sel, hover_color, dark_bg)
            if btn.is_mouse_over((mx, my)):
                selected = i

        v_idx = len(level_buttons)
        is_v_sel = (selected == v_idx) or voltar_button.is_mouse_over((mx, my))
        voltar_button.draw(screen, is_v_sel, hover_color, dark_bg)
        if voltar_button.is_mouse_over((mx, my)):
            selected = v_idx

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % total_items
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % total_items
                elif event.key == pygame.K_RETURN:
                    if selected < len(levels):
                        return levels[selected]
                    else:
                        return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected < len(levels):
                    return levels[selected]
                else:
                    return None

        clock.tick(60)


def options_menu():
    sound_on = True
    fullscreen = False
    while True:
        screen.fill(dark_bg)
        title_surf = title_font.render("Opções", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))

        mx, my = pygame.mouse.get_pos()
        buttons = [Button(f"Som: {'On' if sound_on else 'Off'}", menu_font, WIDTH//2, 200, 50, button_bg, hover_color),
                   Button(f"Tela Cheia: {'On' if fullscreen else 'Off'}", menu_font, WIDTH//2, 280, 50, button_bg, hover_color),
                   Button("Voltar", menu_font, WIDTH//2, 360, 50, button_bg, hover_color)]
        selected = None
        for i, btn in enumerate(buttons):
            is_selected = btn.is_mouse_over((mx, my))
            btn.draw(screen, is_selected, hover_color, dark_bg)
            if is_selected:
                selected = i

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and selected is not None:
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        sound_on = not sound_on
                    elif selected == 1:
                        fullscreen = not fullscreen
                        if fullscreen:
                            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        else:
                            pygame.display.set_mode((WIDTH, HEIGHT))
                    else:
                        return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and selected is not None:
                if selected == 0:
                    sound_on = not sound_on
                elif selected == 1:
                    fullscreen = not fullscreen
                    if fullscreen:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT))
                else:
                    return

        clock.tick(60)


def main_menu():
    options = ["História", "Sem Fim", "Opções"]
    buttons = [Button(opt, title_font, WIDTH//2, 200 + i*100, 50, button_bg, hover_color) for i, opt in enumerate(options)]
    selected = 0

    while True:
        screen.fill(dark_bg)
        title_surf = title_font.render("Menu", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))

        mx, my = pygame.mouse.get_pos()
        for i, btn in enumerate(buttons):
            is_selected = (i == selected) or btn.is_mouse_over((mx, my))
            btn.draw(screen, is_selected, hover_color, dark_bg)
            if btn.is_mouse_over((mx, my)):
                selected = i

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(buttons)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        level = history_menu()
                        if level:
                            play_level(level)
                    elif selected == 1:
                        print("Endless mode selected")
                    else:
                        options_menu()
                        print("Returned from options.")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected == 0:
                    level = history_menu()
                    if level:
                        play_level(level)
                elif selected == 1:
                    print("Endless mode selected")
                else:
                    options_menu()
                    print("Returned from options.")

        clock.tick(60)


if __name__ == '__main__':
    main_menu()
