import pygame
import sys
from ui import Button, draw_background
from logic import Gate, Wire, Level
import math
import time

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Logic Gate Puzzle")
clock = pygame.time.Clock()

# Colors & Fonts
background_color = (80, 80, 80)
dark_bg = (25, 25, 25)
white = (255, 255, 255)
green = (34, 139, 34)
hover_color = (50, 200, 50)
button_bg = (40, 40, 40)
panel_bg = (50, 50, 50)

def get_scaled_font(name, size_ratio):
    return pygame.font.SysFont(name, int(HEIGHT * size_ratio))

title_font = get_scaled_font('arialrounded', 0.1)
menu_font = get_scaled_font('arial', 0.04)
gate_font = get_scaled_font('arial', 0.035)
terminal_font = get_scaled_font('arial', 0.015)

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
    'AND': Gate('AND', [False, False], [False], (0, 0)),
    'OR': Gate('OR', [False, False], [False], (0, 0)),
    'NOT': Gate('NOT', [False], [True], (0, 0)),
    'XOR': Gate('XOR', [False, False], [False], (0, 0)),
    'NAND': Gate('NAND', [False, False], [False], (0, 0)),
    'NOR': Gate('NOR', [False, False], [False], (0, 0)),
    "XNOR": Gate("XNOR", [False, False], [False], (0, 0)),
}

def play_level(screen, level):
    width, height = pygame.display.get_window_size()
    mouse_pos = (0, 0)
    dragging = None
    wiring = None
    offset = (0, 0)
    count_gates = 0

    palette_height = int(height * 0.15)
    gate_radius = int(width * 0.01)
    terminal_radius = int(width * 0.015)

    anim_start = time.time()
    while True:
        bg_offset = int((time.time() - anim_start) * 20) % height
        draw_background(screen, background_color, bg_offset)

        mouse_pos = pygame.mouse.get_pos()

        level.draw(screen, width, height, mouse_pos)

        if dragging:
            # Blank out the palette area
            palette_rect = pygame.Rect(0, height - palette_height, width, palette_height)
            pygame.draw.rect(screen, background_color, palette_rect)
            image = pygame.image.load("images/trash.png").convert_alpha()
            image = pygame.transform.scale(image, (width // 8, width // 8))
            screen.blit(image, (width // 2 - width // 16, height - palette_height))

            dragging.position = (mouse_pos[0] + offset[0], mouse_pos[1] + offset[1])
            dragging.udpate_terminal_positions()
            dragging.draw(screen, selected=True)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                # Left Click
                if e.button == 1 and not dragging and not wiring:
                    for gt, pos in level.palette:
                        if abs(mouse_pos[0] - pos[0]) < width * 0.05 and abs(mouse_pos[1] - pos[1]) < height * 0.05:
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
                    for term in level.inputs:
                        if (mouse_pos[0] - term.pos[0])**2 + (mouse_pos[1] - term.pos[1])**2 < terminal_radius**2:
                            if not wiring:
                                wiring = Wire((term.i, "TERMINAL_I", 0), None, term.value)
                                level.current_wire = wiring
                            elif not wiring.from_i:
                                wiring.from_i = (term.i, "TERMINAL_I", 0)
                                wiring.value = term.value
                            clicked = True
                            break
                    if not clicked:
                        for term in level.outputs:
                            if (mouse_pos[0] - term.pos[0])**2 + (mouse_pos[1] - term.pos[1])**2 < terminal_radius**2:
                                has_two = level.terminal_has_two_wires(term.i)
                                if not has_two:
                                    if not wiring:
                                        wiring = Wire(None, (term.i, "TERMINAL_O", 0), term.value)
                                        level.current_wire = wiring
                                    elif not wiring.to_i:
                                        wiring.to_i = (term.i, "TERMINAL_O", 0)
                                clicked = True
                                break
                    if not clicked:
                        for gate in level.gates.values():
                            input_terminals = gate.get_input_positions()
                            for i, pos in input_terminals:
                                if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < gate_radius**2:
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
                                if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < gate_radius**2:
                                    if not wiring:
                                        wiring = Wire((gate.id, "GATE_O", i), None, gate.outputs[i].value)
                                        level.current_wire = wiring
                                    elif not wiring.from_i:
                                        wiring.from_i = (gate.id, "GATE_O", i, gate.outputs[i].value)
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
                    if dragging and dragging.position[1] > height - palette_height:
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
    y_start = HEIGHT // 3
    y_spacing = HEIGHT // (len(labels) // columns + 1)

    # Buttons
    level_buttons = []
    for idx, lvl in enumerate(labels):
        col = idx % columns
        row = idx // columns
        x = x_spacing * (col + 1)
        y = y_start + row * y_spacing
        level_buttons.append(Button(lvl, menu_font, x, y, 50, button_bg, hover_color))

    voltar_button = Button("Voltar", menu_font, WIDTH // 2, HEIGHT - (HEIGHT * 0.1), 50, button_bg, hover_color)
    selected = 0
    total_items = len(level_buttons) + 1
    anim_start = time.time()
    while True:
        bg_offset = int((time.time() - anim_start) * 20) % HEIGHT
        draw_background(screen, background_color, bg_offset)

        title_surf = title_font.render("História", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, HEIGHT * 0.1)))

        mx, my = pygame.mouse.get_pos()
        t = time.time()
        for i, btn in enumerate(level_buttons):
            is_sel = (i == selected) or btn.is_mouse_over((mx, my))
            offset = (0, int(4 * math.sin(t * 4 + i))) if btn.is_mouse_over((mx, my)) else (0, 0)
            btn.draw(screen, is_sel, hover_color, dark_bg, offset)
            if btn.is_mouse_over((mx, my)):
                selected = i

        v_idx = len(level_buttons)
        is_v_sel = (selected == v_idx) or voltar_button.is_mouse_over((mx, my))
        v_offset = (0, int(4 * math.sin(t * 4 + v_idx))) if voltar_button.is_mouse_over((mx, my)) else (0, 0)
        voltar_button.draw(screen, is_v_sel, hover_color, dark_bg, v_offset)
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
                if event.key == pygame.K_ESCAPE:
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
    anim_start = time.time()
    while True:
        bg_offset = int((time.time() - anim_start) * 20) % HEIGHT
        draw_background(screen, background_color, bg_offset)

        title_surf = title_font.render("Opções", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))

        mx, my = pygame.mouse.get_pos()
        buttons = [
            Button(f"Som: {'On' if sound_on else 'Off'}", menu_font, WIDTH//2, HEIGHT // 3, 50, button_bg, hover_color),
            Button(f"Tela Cheia: {'On' if fullscreen else 'Off'}", menu_font, WIDTH//2, HEIGHT // 3 + (HEIGHT * 0.15), 50, button_bg, hover_color),
            Button("Voltar", menu_font, WIDTH//2, HEIGHT // 3 + (HEIGHT * 0.3), 50, button_bg, hover_color)
        ]
        selected = None
        t = time.time() - anim_start
        for i, btn in enumerate(buttons):
            is_selected = btn.is_mouse_over((mx, my))
            offset = (0, int(4 * math.sin(t * 4 + i))) if is_selected else (0, 0)
            btn.draw(screen, is_selected, hover_color, dark_bg, offset)
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
                elif selected == 2:
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        clock.tick(60)


def main_menu():
    options = ["Níveis", "Sem Fim", "Opções"]
    buttons = [Button(opt, title_font, WIDTH//2, HEIGHT // 3 + i*(HEIGHT * 0.2), 50, button_bg, hover_color) for i, opt in enumerate(options)]
    selected = 0

    button_offsets = [0 for _ in buttons]
    anim_start = time.time()

    while True:
        # Animate background offset slowly going up
        bg_offset = int((time.time() - anim_start) * 20) % HEIGHT
        draw_background(screen, background_color, bg_offset)

        title_surf = title_font.render("Menu", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT // 8)))

        mx, my = pygame.mouse.get_pos()
        t = time.time() - anim_start

        for i, btn in enumerate(buttons):
            if (i == selected) or btn.is_mouse_over((mx, my)):
                offset = (0, int(4 * math.sin(t * 4 + i)))
            else:
                offset = (0, 0)
            button_offsets[i] = offset
            btn.draw(screen, (i == selected) or btn.is_mouse_over((mx, my)), hover_color, dark_bg, offset)
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
                            play_level(screen, level)
                    elif selected == 1:
                        print("Error: Endless mode not implemented yet.")
                    else:
                        options_menu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected == 0:
                    level = history_menu()
                    if level:
                        play_level(screen, level)
                elif selected == 1:
                    print("Error: Endless mode not implemented yet.")
                else:
                    options_menu()

        clock.tick(60)


if __name__ == '__main__':
    main_menu()
