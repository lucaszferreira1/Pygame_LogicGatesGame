import pygame
import sys
from ui import Button, draw_text
from logic import Gate, Wire, Level

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

def level1_function(inputs):
    return [inputs[0] or inputs[1]]

def level2_function(inputs):
    return [inputs[0] and inputs[1]]

def level3_function(inputs):
    return [inputs[0] ^ inputs[1]]


levels = [Level("Nível 1", [True, False], ['AND', 'OR', 'NOT', 'XOR', 'NAND', 'NOR', 'XNOR'], level1_function),
            Level("Nível 2", [False, False, True], ['AND', 'NOT', 'OR'], level2_function),
            Level("Nível 3", [True, True], ['XOR', 'NOT'], level3_function)]

logic_gates = {
    'AND': Gate('AND', [False, False], [False], (0, 0), button_bg),
    'OR': Gate('OR', [False, False], [False], (0, 0), button_bg),
    'NOT': Gate('NOT', [False], [True], (0, 0), button_bg),
    'XOR': Gate('XOR', [False, False], [False], (0, 0), button_bg),
    'NAND': Gate('NAND', [False, False], [False], (0, 0), button_bg),
    'NOR': Gate('NOR', [False, False], [False], (0, 0), button_bg),
    "XNOR": Gate("XNOR", [False, False], [False], (0, 0), button_bg),
}

def play_level(level):
    palette = [(gt, (100 + i * 100, HEIGHT - 50)) for i, gt in enumerate(level.allowed_gates)]
    mouse_pos = (0, 0)
    dragging = None
    wiring = None
    offset = (0, 0)
    count_gates = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(dark_bg)

        pygame.draw.rect(screen, panel_bg, (0, HEIGHT - 100, WIDTH, 100))
        for gt, pos in palette:
            rect_width, rect_height = 80, 60
            rect = pygame.Rect(pos[0] - rect_width // 2, pos[1] - rect_height // 2, rect_width, rect_height)
            pygame.draw.rect(screen, button_bg, rect, border_radius=10)
            pygame.draw.rect(screen, white, rect, 2, border_radius=10)
            draw_text(screen, gt, (pos[0] - gate_font.size(gt)[0] // 2, pos[1] - gate_font.size(gt)[1] // 2), gate_font)

        level.draw(screen, WIDTH, HEIGHT, button_bg, hover_color, mouse_pos)

        if dragging:
            dragging.position = (mouse_pos[0] + offset[0], mouse_pos[1] + offset[1])
            dragging.draw(screen, hover_color, selected=True)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                # Left Click
                if e.button == 1 and not dragging and not wiring:
                    for gt, pos in palette:
                        if abs(mouse_pos[0] - pos[0]) < 40 and abs(mouse_pos[1] - pos[1]) < 30:
                            new_gate = logic_gates[gt].copy()
                            new_gate.position = mouse_pos
                            level.add_gate(new_gate, count_gates)
                            count_gates += 1
                            dragging = new_gate
                            offset = (new_gate.position[0] - mouse_pos[0], new_gate.position[1] - mouse_pos[1])
                            break
                    for gate in level.gates.values():
                        if (mouse_pos[0] - gate.position[0])**2 + (mouse_pos[1] - gate.position[1])**2 < gate.radius**2:
                            dragging = gate
                            offset = (gate.position[0] - mouse_pos[0], gate.position[1] - mouse_pos[1])
                            break
                # Right Click
                elif e.button == 3 and not dragging:
                    clicked = False
                    for i, pos, val in level.get_input_terminals():
                        if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < 12**2:
                            if not wiring:
                                wiring = Wire((i, "TERMINAL_O", 0), None, level.inputs[i])
                                level.current_wire = wiring
                            elif not wiring.from_i:
                                wiring.from_i = (i, "TERMINAL_O", 0)
                                wiring.value = val
                            clicked = True
                            break
                    if not clicked:
                        for i, pos, val in level.get_output_terminals(WIDTH):
                            if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < 12**2:
                                has_two = level.terminal_has_two_wires(i)
                                if not has_two:
                                    if not wiring:
                                        wiring = Wire(None, (i, "TERMINAL_I", 0), level.expected[i])
                                        level.current_wire = wiring
                                    elif not wiring.to_i:
                                        wiring.to_i = (i, "TERMINAL_I", 0)
                                clicked = True
                                break
                    if not clicked:
                        for gate in level.gates.values():
                            input_terminals = gate.get_input_positions()
                            for i, pos in input_terminals:
                                if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < 8**2:
                                    has_two = level.gate_has_two_wires(gate.id, i)
                                    if not has_two:
                                        if not wiring:
                                            wiring = Wire(None, (gate.id, "GATE_I", i))
                                            level.current_wire = wiring
                                        elif not wiring.to_i:
                                            wiring.to_i = (gate.id, "GATE_I", i)
                                    clicked = True
                                    break
                            if clicked:
                                break
                            output_terminals = gate.get_output_positions()
                            for i, pos, ignore in output_terminals:
                                if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < 8**2:
                                    if not wiring:
                                        wiring = Wire((gate.id, "GATE_O", i), None, gate.outputs[i])
                                        level.current_wire = wiring
                                    elif not wiring.from_i:
                                        wiring.from_i = (gate.id, "GATE_O", i, gate.outputs[i])
                                    clicked = True
                                    break
                            if clicked:
                                break
                    if not clicked and wiring:
                        wiring = None
                        level.current_wire = None
                        break
                    if wiring:
                        if wiring.from_i and wiring.to_i:
                            level.wires.append(wiring)
                            wiring = None
                            level.current_wire = None
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    if dragging and dragging.position[1] > HEIGHT - 100:
                        level.remove_gate(dragging)
                    dragging = None
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if wiring:
                        wiring = None
                        level.current_wire = None
                    elif dragging:
                        dragging = None
                    else:
                        return

        clock.tick(240)


def history_menu():
    labels = [lvl.name for lvl in levels]

    # Grid
    columns = 3
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
    options = ["Níveis", "Sem Fim", "Opções"]
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
