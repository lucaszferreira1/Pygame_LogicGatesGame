import pygame
import sys
from ui import Button, draw_background, draw_success_message, draw_failure_message, draw_run_button, draw_truth_table_button, draw_quit_button, draw_reset_button
from logic import Gate, Wire, Level, resource_path
import math
import time

# Criar o .exe
# pyinstaller --onefile --noconsole --add-data "images;images" main.py


# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_icon(pygame.image.load(resource_path("icon.ico")))
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
    sum_bit = inputs[0] ^ inputs[1]
    carry_out = inputs[0] and inputs[1]
    return [sum_bit, carry_out]

def level9_function(inputs):
    sum_bit = (inputs[0] ^ inputs[1]) ^ inputs[2]
    carry_out = (inputs[0] and inputs[1]) or (inputs[1] and inputs[2]) or (inputs[0] and inputs[2])
    return [sum_bit, carry_out]

def gate_half_adder(inputs):
    sum_bit = inputs[0] ^ inputs[1]
    carry_out = inputs[0] and inputs[1]
    return [sum_bit, carry_out]

def level10_function(inputs):
    diff = inputs[0] ^ inputs[1]
    borrow = (not inputs[0]) and inputs[1]
    return [diff, borrow]

def level11_function(inputs):
    diff = (inputs[0] ^ inputs[1]) ^ inputs[2]
    borrow = ((not inputs[0]) and inputs[1]) or ((not inputs[0]) and inputs[2]) or (inputs[1] and inputs[2])
    return [diff, borrow]


levels = [  Level("INTRO", 1, {}, level0_function, "Bem vindo ao jogo de Lógica Digital! Neste jogo, você irá aprender sobre portas lógicas e como elas funcionam. Para começar clique o botão direito do mouse no terminal de entrada e depois no de saída. Para finalizar o nível aperte Enter ou clique no botão de executar."),
            Level("NOT", 1, {'NOT': 1}, level1_function, "Agora vamos aprender sobre a porta NOT. Ela inverte o valor de entrada. Clique e arraste a porta NOT para o circuito, conecte-a ao terminal de entrada e depois ao terminal de saída. Para finalizar o nível aperte Enter ou clique no botão de executar."),
            Level("OR", 2, {'OR': 1}, level2_function, "A porta OR retorna verdadeiro se pelo menos uma entrada for verdadeira. Caso você queira saber a tabela verdade de uma porta lógica, aperte a tecla T ou clique no botão de tabela verdade."),
            Level("AND", 2, {'AND': 1}, level3_function, "A porta AND retorna verdadeiro se todas as entradas forem verdadeiras."),
            Level("NOR", 2, {'OR': 1, 'NOT': 1}, level4_function, "A porta NOR é a combinação da porta OR com a NOT. Ela retorna verdadeiro apenas se todas as entradas forem falsas."),
            Level("NAND", 2, {'AND': 1, 'NOT': 1}, level5_function, "A porta NAND é a combinação da porta AND com a NOT. Ela retorna verdadeiro se pelo menos uma entrada for falsa. Você pode usar a porta NAND para criar todas as outras portas lógicas."),
            Level("OR - NAND", 2, {'NAND': 3}, level2_function, "Neste nível, você deve usar apenas portas NAND para criar uma porta OR."),
            Level("XOR", 2, {'OR': 1, 'AND': 2, 'NOT': 2}, level6_function, "Agora vamos aprender sobre a porta XOR. Ela retorna verdadeiro se apenas uma das entradas for verdadeira."),
            Level("XNOR", 2, {'XOR': 1, 'NOT': 1}, level7_function, "A porta XNOR é a combinação da porta XOR com a NOT. Ela retorna verdadeiro se as entradas forem iguais."),
            Level("HALF ADDER", 2, {'XOR': 1, 'AND': 1}, level8_function, "Neste nível, você deve usar uma porta XOR e uma porta AND para criar um somador de meio bit (half adder). O somador de meio bit recebe duas entradas e retorna a soma e o carry."),
            Level("FULL ADDER", 3, {'XOR': 2, 'AND': 2, 'OR': 1}, level9_function, "Neste nível, você deve usar duas portas XOR, duas portas AND e uma porta OR para criar um somador completo (full adder). O somador completo recebe três entradas: A, B e Cin (carry in) e retorna a soma e o carry out."),
            Level("FULL ADDER 2", 3, {'OR': 1, 'HALF ADDER': 2}, level9_function, "Neste nível, você deve usar duas portas HALF ADDER e uma porta OR para criar um somador completo (full adder)."),
            Level("HALF SUBT", 2, {'XOR': 1, 'AND': 1, 'NOT': 1}, level10_function, "Neste nível, você deve usar uma porta XOR, uma porta AND e uma porta NOT para criar um subtrator de meio bit (half subtractor). O subtrator de meio bit recebe duas entradas e retorna a diferença e o borrow."),
            Level("FULL SUBT", 3, {'NOT': 2, 'XOR': 2, 'AND': 2, 'OR': 1}, level11_function, "Neste nível, você deve criar um subtrator completo (full subtractor). O subtrator completo recebe três entradas: A, B e Bin (borrow in) e retorna a diferença e o borrow out."),
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

    palette_height = int(height * 0.15)
    gate_radius = int(width * 0.01)
    terminal_radius = int(width * 0.015)
    button_size = 56

    truth_table = False

    quit_pos = (width * 0.025, height * 0.025)
    quit_btn_rect = pygame.Rect(quit_pos[0], quit_pos[1], button_size, button_size)
    if not level.isSimulator:
        reset_pos = (width - width * 0.3, height * 0.025)
    else:
        reset_pos = (width - width * 0.1, height * 0.025)
    reset_btn_rect = pygame.Rect(reset_pos[0], reset_pos[1], button_size, button_size)
    truth_pos = (width - width * 0.2, height * 0.025)
    truth_btn_rect = pygame.Rect(truth_pos[0], truth_pos[1], button_size, button_size)
    run_pos = (width - width * 0.1, height * 0.025)
    run_btn_rect = pygame.Rect(run_pos[0], run_pos[1], button_size, button_size)


    anim_start = time.time()
    while True:
        bg_offset = int((time.time() - anim_start) * 20) % height
        draw_background(screen, background_color, bg_offset)

        mouse_pos = pygame.mouse.get_pos()

        level.draw(screen, width, height, mouse_pos)

        quit_btn_hover = quit_btn_rect.collidepoint(mouse_pos)
        draw_quit_button(screen, quit_pos, (100, 25, 25), button_size, quit_btn_hover)

        reset_btn_hover = reset_btn_rect.collidepoint(mouse_pos)
        draw_reset_button(screen, reset_pos, (170, 170, 170), button_size, reset_btn_hover, resource_path("images//reset.png"))

        if not level.isSimulator:
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
                trash_img = pygame.image.load(resource_path("images/trash.png")).convert_alpha()
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
                if e.button == 1 :
                    if not dragging and not wiring:
                        if not level.isSimulator:
                            if run_btn_hover:
                                level.compile()
                                if level.evaluate():
                                    level.completed = True
                                    draw_success_message(screen, width, height, get_scaled_font('arial', 0.08), green)
                                    pygame.display.flip()
                                    pygame.time.wait(2500)
                                    return
                                else:
                                    draw_failure_message(screen, width, height, get_scaled_font('arial', 0.08), (200, 50, 50))
                                    pygame.display.flip()
                                    pygame.time.wait(2500)
                                    break
                            elif truth_btn_hover:
                                truth_table = not truth_table
                                break
                        if quit_btn_hover:
                            wiring = None
                            dragging = None
                            truth_table = False
                            return
                        elif reset_btn_hover:
                            level.reset()
                            wiring = None
                            dragging = None
                            truth_table = False
                            break
                        for gt, pos in level.palette:
                            if abs(mouse_pos[0] - pos[0]) < width * 0.05 and abs(mouse_pos[1] - pos[1]) < height * 0.05:
                                if level.allowed_gates[gt] == 0:
                                    continue
                                new_gate = logic_gates[gt].copy()
                                new_gate.position = mouse_pos
                                level.add_gate(new_gate)
                                level.allowed_gates[gt] -= 1
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
                    truth_table = False
                    if wiring:
                        wiring = None
                        level.current_wire = None
                    elif dragging:
                        dragging = None
                    else:
                        return
                elif e.key == pygame.K_t:
                    truth_table = not truth_table
                elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    level.cycle_inputs(False)
                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    level.cycle_inputs(True)
                elif e.key == pygame.K_r:
                    level.reset()
                elif (e.key == pygame.K_RETURN or e.key == pygame.K_SPACE) and not level.isSimulator:
                    wiring = None
                    dragging = None
                    truth_table = False
                    level.compile()
                    if level.evaluate():
                        level.completed = True
                        draw_success_message(screen, width, height, get_scaled_font('arial', 0.08), green)
                        pygame.display.flip()
                        pygame.time.wait(2500)
                        return
                    else:
                        draw_failure_message(screen, width, height, get_scaled_font('arial', 0.08), (200, 50, 50))
                        pygame.display.flip()
                        pygame.time.wait(2500)
                        break
                elif e.key == pygame.K_BACKSPACE or e.key == pygame.K_DELETE:
                    if level.gates:
                        last_gate_id = max(level.gates.keys())
                        last_gate = level.gates[last_gate_id]
                        level.remove_gate(last_gate)
                        level.allowed_gates[last_gate.type] += 1
                        
        clock.tick(240)


def history_menu():
    # Grid
    columns = 3
    x_spacing = WIDTH // (columns + 1)
    y_start = HEIGHT // 3
    y_spacing = HEIGHT // 1.9 // (len(levels) // columns + 1)

    # Smaller button height
    button_height = 32

    # Buttons
    level_buttons = []
    unlocked_levels = 1

    for idx, lvl in enumerate(levels):
        if idx == 0:
            continue
        if levels[idx - 1].completed:
            unlocked_levels = idx + 1
        else:
            break

    voltar_button = Button("Voltar", menu_font, WIDTH // 2, HEIGHT - (HEIGHT * 0.1), button_height, button_bg, hover_color)

    for idx, lvl in enumerate(levels[:unlocked_levels]):
        col = idx % columns
        row = idx // columns
        x = x_spacing * (col + 1)
        y = y_start + row * y_spacing
        level_buttons.append(Button(lvl.name, menu_font, x, y, button_height, button_bg, hover_color))

    selected = 1
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
                    if selected == unlocked_levels:
                        return None
                    elif selected < len(levels):
                        return play_level(screen, levels[selected])
                    return None
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if voltar_button.rect.collidepoint((mx, my)):
                    return None
                else:
                    return play_level(screen, levels[selected])
                

        clock.tick(60)


def simulator_menu():
    sim = Level("Simulador", 4, {"NOT": -1, "AND": -1, "OR": -1, "XOR": -1, "XNOR": -1, "NAND": -1, "NOR": -1}, isSim=True)
    play_level(screen, sim)


def options_menu():
    fullscreen = False
    anim_start = time.time()
    while True:
        bg_offset = int((time.time() - anim_start) * 20) % HEIGHT
        draw_background(screen, background_color, bg_offset)

        title_surf = title_font.render("Opções", True, white)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))

        mx, my = pygame.mouse.get_pos()
        buttons = [
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
                        fullscreen = not fullscreen
                        if fullscreen:
                            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        else:
                            pygame.display.set_mode((WIDTH, HEIGHT))
                    else:
                        return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and selected is not None:
                if selected == 0:
                    fullscreen = not fullscreen
                    if fullscreen:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT))
                elif selected == 1:
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        clock.tick(60)


def main_menu():
    options = ["Níveis", "Simulador", "Opções"]
    buttons = [Button(opt, title_font, WIDTH//2, HEIGHT // 3 + i*(HEIGHT * 0.2), 50, button_bg, hover_color) for i, opt in enumerate(options)]
    selected = 0

    button_offsets = [0 for _ in buttons]
    anim_start = time.time()

    while True:
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
                        history_menu()
                    elif selected == 1:
                        simulator_menu()
                    else:
                        options_menu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected == 0:
                    history_menu()
                elif selected == 1:
                    simulator_menu()
                else:
                    options_menu()

        clock.tick(60)


if __name__ == '__main__':
    main_menu()
