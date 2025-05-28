import pygame
import sys
from ui import Button, draw_background, draw_success_message, draw_run_button, draw_truth_table_button, draw_quit_button
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

def level0_function(inputs):
    return [inputs[0]]

def level1_function(inputs):
    return [not inputs[0]]

def level2_function(inputs):
    return [inputs[0] or inputs[1]]

def level3_function(inputs):
    return [inputs[0] and inputs[1]]

def level4_function(inputs):
    return [not(inputs[0] or inputs[1])]

def level5_function(inputs):
    return [not(inputs[0] and inputs[1])]

def level6_function(inputs):
    return [True if inputs[0] != inputs[1] else False]

def level7_function(inputs):
    return [False if inputs[0] != inputs[1] else True]

def level8_function(inputs):
    # 1-bit half adder: inputs[0]=A, inputs[1]=B
    sum_bit = inputs[0] ^ inputs[1]
    carry_out = inputs[0] and inputs[1]
    return [sum_bit, carry_out]

def level9_function(inputs):
    # 1-bit full adder: inputs[0]=A, inputs[1]=B, inputs[2]=Cin
    sum_bit = (inputs[0] ^ inputs[1]) ^ inputs[2]
    carry_out = (inputs[0] and inputs[1]) or (inputs[1] and inputs[2]) or (inputs[0] and inputs[2])
    return [sum_bit, carry_out]

def gate_half_adder(inputs):
    # 1-bit half adder: inputs[0]=A, inputs[1]=B
    sum_bit = inputs[0] ^ inputs[1]
    carry_out = inputs[0] and inputs[1]
    return [sum_bit, carry_out]

levels = [  Level("INTRO", 1, {}, level0_function),
            Level("NOT", 1, {'NOT': 1}, level1_function),
            Level("OR", 2, {'OR': 1}, level2_function),
            Level("AND", 2, {'AND': 1}, level3_function),
            Level("NOR", 2, {'OR': 1, 'NOT': 1}, level4_function),
            Level("NAND", 2, {'AND': 1, 'NOT': 1}, level5_function),
            Level("OR - NAND", 2, {'NAND': 3}, level2_function),
            Level("XOR", 2, {'OR': 1, 'AND': 2, 'NOT': 2}, level6_function),
            Level("XNOR", 2, {'XOR': 1, 'NOT': 1}, level7_function),
            Level("HALF ADDER", 2, {'XOR': 1, 'AND': 1}, level8_function),
            Level("FULL ADDER", 3, {'XOR': 2, 'AND': 2, 'OR': 1}, level9_function),
        ]

logic_gates = {
    'AND': Gate('AND', 2, 1, (0, 0)),
    'OR': Gate('OR', 2, 1, (0, 0)),
    'NOT': Gate('NOT', 1, 1, (0, 0)),
    'XOR': Gate('XOR', 2, 1, (0, 0)),
    'NAND': Gate('NAND', 2, 1, (0, 0)),
    'NOR': Gate('NOR', 2, 1, (0, 0)),
    "XNOR": Gate("XNOR", 2, 1, (0, 0)),
    'HALF ADDER': Gate('HALF ADDER', 2, 2, (0, 0), gate_half_adder),
}

def play_level(screen, level):
    width, height = pygame.display.get_window_size()
    mouse_pos = (0, 0)
    dragging = None
    wiring = None
    offset = (0, 0)
    count_gates = len(level.gates)

    palette_height = int(height * 0.15)
    gate_radius = int(width * 0.01)
    terminal_radius = int(width * 0.015)
    button_size = 56

    truth_table = False


    quit_pos = (width * 0.025, height * 0.025)
    quit_btn_rect = pygame.Rect(quit_pos[0], quit_pos[1], button_size, button_size)
    truth_pos = (width - width * 0.2, height * 0.025)
    truth_btn_rect = pygame.Rect(truth_pos[0], truth_pos[1], button_size, button_size)
    run_pos = (width - width * 0.1, height * 0.025)
    run_btn_rect = pygame.Rect(run_pos[0], run_pos[1], button_size, button_size)


    anim_start = time.time()
    while True:
        fps = clock.get_fps()
        pygame.display.set_caption(f"Logic Gate Puzzle - FPS: {fps:.1f}")
        bg_offset = int((time.time() - anim_start) * 20) % height
        draw_background(screen, background_color, bg_offset)

        mouse_pos = pygame.mouse.get_pos()

        level.draw(screen, width, height, mouse_pos)

        quit_btn_hover = quit_btn_rect.collidepoint(mouse_pos)
        draw_quit_button(screen, quit_pos, (100, 25, 25), button_size, quit_btn_hover)

        truth_btn_hover = truth_btn_rect.collidepoint(mouse_pos)
        draw_truth_table_button(screen, truth_pos, (170, 170, 170), button_size, truth_btn_hover)
        if truth_table:
            level.draw_truth_table(screen, width, height)
        
        run_btn_hover = run_btn_rect.collidepoint(mouse_pos)
        draw_run_button(screen, run_pos, green, button_size, run_btn_hover)

        if dragging:
            palette_rect = pygame.Rect(0, height - palette_height, width, palette_height)
            pygame.draw.rect(screen, background_color, palette_rect)

            if not hasattr(play_level, "_trash_icon") or play_level._trash_icon_size != width // 8:
                trash_img = pygame.image.load("images/trash.png").convert_alpha()
                trash_img = pygame.transform.scale(trash_img, (width // 8, width // 8))
                play_level._trash_icon = trash_img
                play_level._trash_icon_size = width // 8
            else:
                trash_img = play_level._trash_icon
            
            screen.blit(trash_img, (width // 2 - width // 16, height - palette_height))

            dragging.position = (mouse_pos[0] + offset[0], mouse_pos[1] + offset[1])
            dragging.udpate_terminal_positions()
            dragging.draw(screen, selected=True)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = e.w, e.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1 and not dragging and not wiring:
                    if run_btn_hover:
                        level.compile()
                        if level.evaluate():
                            level.completed = True
                            draw_success_message(screen, width, height, get_scaled_font('arial', 0.08), green)
                            pygame.display.flip()
                            pygame.time.wait(2500)
                            return
                        else:
                            break
                    elif truth_btn_hover:
                        truth_table = not truth_table
                        break
                    elif quit_btn_hover:
                        return
                    for gt, pos in level.palette:
                        if abs(mouse_pos[0] - pos[0]) < width * 0.05 and abs(mouse_pos[1] - pos[1]) < height * 0.05:
                            if level.allowed_gates[gt] == 0:
                                continue
                            new_gate = logic_gates[gt].copy()
                            new_gate.position = mouse_pos
                            level.add_gate(new_gate, count_gates)
                            level.allowed_gates[gt] -= 1
                            count_gates += 1
                            dragging = new_gate
                            offset = (new_gate.position[0] - mouse_pos[0], new_gate.position[1] - mouse_pos[1])
                            break
                    for gate in level.gates.values():
                        if (mouse_pos[0] - gate.position[0])**2 + (mouse_pos[1] - gate.position[1])**2 < gate.radius**2:
                            dragging = gate
                            offset = (gate.position[0] - mouse_pos[0], gate.position[1] - mouse_pos[1])
                            break
                    for term in level.inputs:
                        if (mouse_pos[0] - term.pos[0])**2 + (mouse_pos[1] - term.pos[1])**2 < terminal_radius**2:
                            term.value = not term.value
                            break
                elif e.button == 3 and not dragging:
                    def check_terminal(term, kind, idx, attr):
                        if (mouse_pos[0] - term.pos[0])**2 + (mouse_pos[1] - term.pos[1])**2 < terminal_radius**2:
                            if not wiring:
                                wire = Wire((term.i, kind, idx), None, getattr(term, attr, None))
                                level.current_wire = wire
                                return wire
                            elif not wiring.from_i:
                                wiring.from_i = (term.i, kind, idx)
                                wiring.value = getattr(term, attr, None)
                                return wiring
                            return wiring
                        return None

                    clicked = False
                    # Input terminals
                    for term in level.inputs:
                        if check_terminal(term, "TERMINAL_I", 0, "value"):
                            wiring = level.current_wire
                            clicked = True
                            break
                    # Output terminals
                    if not clicked:
                        for term in level.outputs:
                            if (mouse_pos[0] - term.pos[0])**2 + (mouse_pos[1] - term.pos[1])**2 < terminal_radius**2:
                                if not level.terminal_has_two_wires(term.i):
                                    if not wiring:
                                        wiring = Wire(None, (term.i, "TERMINAL_O", 0), term.value)
                                        level.current_wire = wiring
                                    elif not wiring.to_i:
                                        wiring.to_i = (term.i, "TERMINAL_O", 0)
                                clicked = True
                                break
                    # Gate terminals
                    if not clicked:
                        for gate in level.gates.values():
                            # Inputs
                            for i, pos in gate.get_input_positions():
                                if (mouse_pos[0] - pos[0])**2 + (mouse_pos[1] - pos[1])**2 < gate_radius**2:
                                    if not level.gate_has_two_wires(gate.id, i):
                                        if not wiring:
                                            wiring = Wire(None, (gate.id, "GATE_I", i))
                                            level.current_wire = wiring
                                        elif not wiring.to_i:
                                            wiring.to_i = (gate.id, "GATE_I", i)
                                        clicked = True
                                        break
                            if clicked:
                                break
                            # Outputs
                            for i, pos, _ in gate.get_output_positions():
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
                    if wiring and wiring.from_i and wiring.to_i:
                        level.wires.append(wiring)
                        wiring = None
                        level.current_wire = None
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1 and dragging and dragging.position[1] > height - palette_height:
                    level.remove_gate(dragging)
                    level.allowed_gates[dragging.type] += 1
                    dragging = None
                elif e.button == 1:
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
                elif e.key == pygame.K_t:
                    truth_table = not truth_table
                elif e.key == pygame.K_LEFT:
                    level.cycle_inputs(False)
                elif e.key == pygame.K_RIGHT:
                    level.cycle_inputs(True)
                elif e.key == pygame.K_RETURN:
                    level.compile()
                    if level.evaluate():
                        level.completed = True
                        draw_success_message(screen, width, height, get_scaled_font('arial', 0.08), green)
                        pygame.display.flip()
                        pygame.time.wait(2500)
                        return

        clock.tick(240)


def history_menu():
    # Grid
    columns = 3
    x_spacing = WIDTH // (columns + 1)
    y_start = HEIGHT // 3
    y_spacing = HEIGHT // 1.9 // (len(levels) // columns + 1)

    # Buttons
    level_buttons = []
    unlocked_levels = 50 # Trocar o valor para 1 na entrega

    for idx, lvl in enumerate(levels):
        if idx == 0:
            continue
        if levels[idx - 1].completed:
            unlocked_levels = idx + 1
        else:
            break

    for idx, lvl in enumerate(levels[:unlocked_levels]):
        col = idx % columns
        row = idx // columns
        x = x_spacing * (col + 1)
        y = y_start + row * y_spacing
        level_buttons.append(Button(lvl.name, menu_font, x, y, 50, button_bg, hover_color))

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
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    selected = (selected + 1) % total_items
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    selected = (selected - 1) % total_items
                elif event.key == pygame.K_DOWN:
                    selected = (selected + columns) % total_items
                elif event.key == pygame.K_UP:
                    selected = (selected - columns) % total_items
                elif event.key == pygame.K_RETURN:
                    if selected < len(levels):
                        return levels[selected]
                    else:
                        return None
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected < unlocked_levels:
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
    options = ["Níveis", "Opções"]
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
                    elif selected == -1:
                        print("Error: Endless mode not implemented yet.")
                    else:
                        options_menu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected == 0:
                    level = history_menu()
                    if level:
                        play_level(screen, level)
                elif selected == -1:
                    print("Error: Endless mode not implemented yet.")
                else:
                    options_menu()

        clock.tick(60)


if __name__ == '__main__':
    main_menu()
