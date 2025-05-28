import pygame
from typing import List, Tuple
from ui import draw_text

WIDTH, HEIGHT = 800, 600

white = (255, 255, 255)
green = (34, 139, 34)
wire_color_false = (100, 100, 100)
button_hover = (50, 200, 50)
button_bg = (40, 40, 40)
panel_bg = (50, 50, 50)

pygame.font.init()
gate_font = pygame.font.SysFont('arial', 20)
quantity_font = pygame.font.SysFont('arial', 14)
expected_font = pygame.font.SysFont('arial', 10)

default_gates = {"AND": ["images//AND.png", [[-20, -10], [-20, 10]], [20, 0, 0]],
                 "OR": ["images//OR.png", [[-20, -10], [-20, 10]], [20, 0, 0]],
                 "NOT": ["images//NOT.png", [[-20, 0]], [17, 0, 1]],
                 "XOR": ["images//XOR.png", [[-20, -10], [-20, 10]], [20, 0, 0]],
                 "XNOR": ["images//XNOR.png", [[-20, -10], [-20, 10]], [20, 0, 1]],
                 "NAND": ["images//NAND.png", [[-20, -10], [-20, 10]], [20, 0, 1]],
                 "NOR": ["images//NOR.png", [[-20, -10], [-20, 10]], [20, 0, 1]]}

_image_cache = {}

def load_gate_image(gate_type: str):
    if gate_type in _image_cache:
        return _image_cache[gate_type]
    
    if gate_type in default_gates:
        image_path = default_gates[gate_type][0]
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (60, 60))
        _image_cache[gate_type] = image
        return image
    
    raise ValueError(f"Gate type '{gate_type}' not found.")


class Terminal:
    def __init__(self, i: int, type_: str, value: bool=False, isNot: bool=False):
        self.i: int = i
        self.type: str = type_
        self.pos: Tuple[int, int] = self.calculate_position()
        self.value: bool = value
        self.isNot: bool = isNot

    def calculate_position(self):
        pos = (0, 0)
        if self.type == "TERMINAL_I":
            pos = (WIDTH // 8, HEIGHT // 6 + self.i * HEIGHT // 10 + 3)
        elif self.type == "TERMINAL_O":
            pos = (WIDTH - WIDTH // 8, HEIGHT // 6 + self.i * HEIGHT // 10 + 3)
        return pos

    def __str__(self):
        return f"Terminal(i={self.i}, type={self.type}, pos={self.pos}, value={self.value}, isNot={self.isNot})"

class Gate:
    def __init__(self, gate_type: str, inputs: int, outputs: int, position: Tuple[int,int], function=None):
        self.id = None
        self.type = gate_type.upper()
        self.inputs = [Terminal(i, "GATE_I", False) for i in range(inputs)]
        self.outputs = [Terminal(i, "GATE_O", False) for i in range(outputs)]
        self.position = position
        self.radius = 30
        self.function = function

        if self.type in ["NOT", "NAND", "NOR", "XNOR"]:
            self.outputs[0].isNot = True
    
    def copy(self):
        return Gate(gate_type=self.type, inputs=len(self.inputs), outputs=len(self.outputs), position=self.position, function=self.function)

    def draw(self, screen, x=-1, y=-1, selected=False):
        if x == -1 and y == -1:
            x, y = self.position
            
        if self.type in default_gates.keys():
            image = load_gate_image(self.type)
            screen.blit(image, (x - self.radius, y - self.radius))
        else:
            rect_width, rect_height = 80, 60
            rect = pygame.Rect(self.position[0] - rect_width // 2, self.position[1] - rect_height // 2, rect_width, rect_height)
            pygame.draw.rect(screen, button_hover if selected else button_bg, rect, border_radius=10)
            pygame.draw.rect(screen, white, rect, 2, border_radius=10)

            type_len = len(self.type)
            if type_len <= 3:
                font = pygame.font.SysFont('arial', 20)
            elif type_len <= 4:
                font = pygame.font.SysFont('arial', 18)
            elif type_len <= 8:
                font = pygame.font.SysFont('arial', 14)
            else:
                font = pygame.font.SysFont('arial', 10)
            draw_text(screen, self.type, (self.position[0] - font.size(self.type)[0] // 2, self.position[1] - font.size(self.type)[1] // 2), font)
            
        # Draw input terminals
        input_positions = self.get_input_positions()
        for i, pos in input_positions:
            color = green if self.inputs[i].value else button_bg
            pygame.draw.rect(screen, white, (pos[0] - 6, pos[1] - 6, 12, 12))
            pygame.draw.rect(screen, color, (pos[0] - 4, pos[1] - 4, 8, 8))

        # Draw output terminals
        output_positions = self.get_output_positions()
        for i, pos, circle_not in output_positions:
            color = green if self.outputs[i].value else button_bg
            if circle_not:
                pygame.draw.circle(screen, white, pos, 6)
                pygame.draw.circle(screen, color, pos, 4)
            else:
                pygame.draw.rect(screen, white, (pos[0] - 6, pos[1] - 6, 12, 12))
                pygame.draw.rect(screen, color, (pos[0] - 4, pos[1] - 4, 8, 8))

    def update(self):
        self.evaluate()        

    def udpate_terminal_positions(self):
        for term in self.inputs:
            if self.type in default_gates.keys():
                term.pos = (self.position[0] + default_gates[self.type][1][term.i][0], self.position[1] + default_gates[self.type][1][term.i][1])
            else: 
                # Caso hajam gates personalizados
                break
        for term in self.outputs:
            if self.type in default_gates.keys():
                pos = (default_gates[self.type][2][0], default_gates[self.type][2][1])
                pos = (self.position[0] + pos[0], self.position[1] + pos[1])
                term.pos = pos
            else:
                # Caso hajam gates personalizados
                break

    def get_input_positions(self):
        positions = []
        if self.type in default_gates.keys():
            for term in self.inputs:
                positions.append((term.i, term.pos))
        else:
            rect_width, rect_height = 80, 60
            for i in range(len(self.inputs)):
                x_off = -rect_width // 2
                y_off = -rect_height // 2 + (i + 1) * (rect_height // (len(self.inputs) + 1))
                pos = (self.position[0] + x_off, self.position[1] + y_off)
                self.inputs[i].pos = pos
                positions.append((i, pos))
        return positions

    def get_output_positions(self):
        positions = []
        if self.type in default_gates.keys():
            term = self.outputs[0]
            positions.append((term.i, term.pos, term.isNot))
        else:
            rect_width, rect_height = 80, 60
            for i in range(len(self.outputs)):
                x_offset = rect_width // 2
                y_offset = -rect_height // 2 + (i + 1) * (rect_height // (len(self.outputs) + 1))
                pos = (self.position[0] + x_offset, self.position[1] + y_offset)
                self.outputs[i].pos = pos
                positions.append((i, pos, 0))
        return positions
    
    def evaluate(self):
        match self.type:
            case "AND":
                self.outputs[0].value = all([term.value for term in self.inputs])
            case "OR":
                self.outputs[0].value = any([term.value for term in self.inputs])
            case "NOT":
                self.outputs[0].value = not self.inputs[0].value
            case "NAND":
                self.outputs[0].value = not all([term.value for term in self.inputs])
            case "NOR":
                self.outputs[0].value = not any([term.value for term in self.inputs])
            case "XOR":
                self.outputs[0].value = self.inputs[0].value != self.inputs[1].value if len(self.inputs) == 2 else False
            case "XNOR":
                self.outputs[0].value = self.inputs[0].value == self.inputs[1].value if len(self.inputs) == 2 else False
            case _:
                if self.function:
                    input_values = [term.value for term in self.inputs]
                    for i, val in enumerate(self.function(input_values)):
                        self.outputs[i].value = val
                else:
                    raise ValueError(f"Unsupported gate type: {self.type}")
    
    def __str__(self):
        return (f"Gate(type={self.type}, inputs={self.inputs}, outputs={self.outputs}, "
                f"position={self.position}, color={self.color})")


class Wire:
    def __init__(self, from_i: Tuple[int, str, int], to_i: Tuple[int, str, int], value=False):
        self.from_i = from_i
        self.to_i = to_i
        self.value = value
        self.color = wire_color_false
    
    def draw(self, screen, ports):
        from_pos = self.get_port_pos(ports, False)
        to_pos = self.get_port_pos(ports, True)
        pygame.draw.line(screen, self.color, from_pos, to_pos, 5)
        
    def update(self, ports):
        self.update_own_value(ports)
        self.color = green if self.value else wire_color_false
        self.set_value_to_out(ports)
    
    def draw_one_point(self, screen, ports, mouse_pos):
        self.color = green if self.value else wire_color_false
        from_pos = self.get_port_pos(ports, False) if self.from_i else mouse_pos
        to_pos = self.get_port_pos(ports, True) if self.to_i else mouse_pos
        pygame.draw.line(screen, self.color, from_pos, to_pos, 5)

    def get_port_pos(self, ports, isTo):
        value = self.to_i if isTo else self.from_i
        if value[1] == "GATE_I":
            gate = ports["GATE"][value[0]]
            pos = gate.inputs[value[2]].pos
        elif value[1] == "GATE_O":
            gate = ports["GATE"][value[0]]
            pos = gate.outputs[value[2]].pos
        else:
            pos = ports[value[1]][value[0]].pos
        return pos
    
    def update_own_value(self, ports):
        if self.from_i[1] == "GATE_O":
            gate = ports["GATE"][self.from_i[0]]
            self.value = gate.outputs[self.from_i[2]].value
        elif self.from_i[1] == "TERMINAL_I":
            term = ports["TERMINAL_I"][self.from_i[0]]
            self.value = term.value

    def set_value_to_out(self, ports):
        if self.to_i[1] == "GATE_I":
            gate = ports["GATE"][self.to_i[0]]
            gate.inputs[self.to_i[2]].value = self.value
        elif self.to_i[1] == "TERMINAL_O":
            term = ports["TERMINAL_O"][self.to_i[0]]
            term.value = self.value

    def __str__(self):
        return f"Wire(from={self.from_i}, to={self.to_i}, value={self.value})"


class Level:
    def __init__(self, name: str, inputs: int, allowed_gates: dict[str, int], function=None):
        self.name = name
        self.inputs = [Terminal(i, "TERMINAL_I", False) for i in range(inputs)]
        self.expected = function([term.value for term in self.inputs])
        self.outputs = [Terminal(i, "TERMINAL_O") for i in range(len(self.expected))]
        self.allowed_gates = allowed_gates.copy()
        self.gates: dict[int, Gate] = {}
        self.wires: List[Wire] = []
        self.current_wire: Wire = None
        self.function = function
        self.palette = []
        self.current_function = None
        self.completed = False

    def add_gate(self, gate, id_gate):
        gate.id = id_gate
        self.gates[id_gate] = gate

    def remove_gate(self, gate):
        idx_gate = gate.id

        wires = [wire for wire in self.wires if (
            (wire.from_i[1] == "GATE_O" and wire.from_i[0] == idx_gate) or
            (wire.to_i[1] == "GATE_I" and wire.to_i[0] == idx_gate)
        )]
        
        for wire in wires:
            if wire.to_i[1] == "GATE_I":
                gate = self.gates[wire.to_i[0]]
                gate.inputs[wire.to_i[2]].value = False
            elif wire.to_i[1] == "TERMINAL_O":
                term = self.outputs[wire.to_i[0]]
                term.value = False
            self.wires.remove(wire)
        
        self.gates.pop(idx_gate)

    def draw_palette(self, screen, width, height):
        panel_height = int(height * 0.16)
        panel_y = height - panel_height

        if not self.palette or len(self.palette) != len(self.allowed_gates):
            self.palette = [(gt, (width // 8 + i * width // 8, panel_y + panel_height // 2)) for i, gt in enumerate(self.allowed_gates.keys())]

        pygame.draw.rect(screen, (30, 30, 30), (0, panel_y - 5, width, panel_height + 5))
        pygame.draw.rect(screen, panel_bg, (0, panel_y, width, panel_height), border_radius=15)
        pygame.draw.rect(screen, white, (0, panel_y, width, panel_height), 2, border_radius=15)

        font_cache = {}
        for gt, pos in self.palette:
            value = self.allowed_gates.get(gt, -1)

            rect_width, rect_height = width * 0.1, height * 0.1
            rect = pygame.Rect(pos[0] - rect_width // 2, pos[1] - rect_height // 2, rect_width, rect_height)
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, 12)
            pygame.draw.rect(screen, (60, 60, 60), highlight_rect, border_radius=8)
            pygame.draw.rect(screen, button_bg, rect, border_radius=10)

            border_color = (255, 0, 0) if value == 0 else white
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)

            type_len = len(gt)
            if type_len not in font_cache:
                if type_len <= 3:
                    font_cache[type_len] = gate_font
                elif type_len <= 4:
                    font_cache[type_len] = pygame.font.SysFont('arial', 18)
                elif type_len <= 8:
                    font_cache[type_len] = pygame.font.SysFont('arial', 14)
                else:
                    font_cache[type_len] = pygame.font.SysFont('arial', 10)
            font = font_cache[type_len]
            draw_text(screen, gt, (pos[0] - font.size(gt)[0] // 2, pos[1] - font.size(gt)[1] // 2), font,)

            if value > 0:
                num_text = str(value)
                num_pos = (rect.right - quantity_font.size(num_text)[0] - 6, rect.bottom - quantity_font.size(num_text)[1] - 4)
                draw_text(screen, num_text, num_pos, quantity_font)

    def draw_truth_table(self, screen, width, height):
        if not self.inputs or not self.expected:
            return

        n_inputs = len(self.inputs)
        n_outputs = len(self.outputs)
        table_width = 60 * (n_inputs + n_outputs)
        table_height = 30 * (2 ** n_inputs + 1)
        center_x = width // 2
        center_y = height // 2

        start_x = center_x - table_width // 2
        start_y = center_y - table_height // 2

        # Draw header
        header_font = pygame.font.SysFont('arial', 16)
        cell_w = 60
        cell_h = 30

        for i in range(n_inputs):
            draw_text(screen, f"In {i+1}", (start_x + i * cell_w + 10, start_y + 5), header_font)
        for i in range(n_outputs):
            draw_text(screen, f"Out {i+1}", (start_x + (n_inputs + i) * cell_w + 10, start_y + 5), header_font)

        # Rows
        row_font = pygame.font.SysFont('arial', 14)
        for row in range(2 ** n_inputs):
            y = start_y + (row + 1) * cell_h
            # Input
            bits = [(row >> (n_inputs - 1 - i)) & 1 for i in range(n_inputs)]
            for i, bit in enumerate(bits):
                draw_text(screen, str(bit), (start_x + i * cell_w + 25, y + 7), row_font)
            # Output
            expected = self.function([bool(b) for b in bits])
            for i, val in enumerate(expected):
                draw_text(screen, str(int(val)), (start_x + (n_inputs + i) * cell_w + 25, y + 7), row_font)

        # Grid
        for i in range(n_inputs + n_outputs + 1):
            x = start_x + i * cell_w
            pygame.draw.line(screen, white, (x, start_y), (x, start_y + table_height), 1)
        for i in range(2 ** n_inputs + 2):
            y = start_y + i * cell_h
            pygame.draw.line(screen, white, (start_x, y), (start_x + table_width, y), 1)


    def draw(self, screen, width, height, mouse_pos):
        self.expected = self.function([term.value for term in self.inputs])

        self.draw_palette(screen, width, height)

        for term in self.inputs:
            color = green if term.value else button_bg
            pygame.draw.circle(screen, white, term.pos, 12)
            pygame.draw.circle(screen, color, term.pos, 10)
            draw_text(screen, f"{term.value}", (30, term.pos[1] - 13), gate_font)
        for term in self.outputs:
            color = green if term.value else button_bg
            pygame.draw.circle(screen, white, term.pos, 12)
            pygame.draw.circle(screen, color, term.pos, 10)
            draw_text(screen, f"{term.value}", (term.pos[0] + 20, term.pos[1] - 13), gate_font)
            draw_text(screen, f"Expected: {self.expected[term.i]}", (term.pos[0] + 20, term.pos[1] + 5), expected_font)
        for gate in self.gates.values():
            gate.update()
            gate.draw(screen)
        
        ports = {"TERMINAL_I": self.inputs, "TERMINAL_O": self.outputs, "GATE": self.gates}
        for wire in self.wires:
            wire.update(ports)
            wire.draw(screen, ports)
        
        if self.current_wire:
            self.current_wire.draw_one_point(screen, ports, mouse_pos)
        

    def terminal_has_two_wires(self, i):
        for wire in self.wires:
            if wire.to_i[1] == "TERMINAL_O" and wire.to_i[0] == i:
                return True
        return False

    def gate_has_two_wires(self, gate_i, i):
        for wire in self.wires:
            if wire.to_i[1] == "GATE_I" and wire.to_i[0] == gate_i:
                if wire.to_i[2] == i:
                    return True
        return False
    
    def cycle_inputs(self, forward=True):
        n = len(self.inputs)
        if n == 0:
            return
        # Convert current input values to an integer
        current = 0
        for i, term in enumerate(self.inputs):
            if term.value:
                current |= (1 << (n - i - 1))
        # Cycle to next or previous value
        if forward:
            next_val = (current + 1) % (2 ** n)
        else:
            next_val = (current - 1) % (2 ** n)
        # Set input values according to next_val bits
        for i in range(n):
            self.inputs[i].value = bool((next_val >> (n - i - 1)) & 1)
    
    def evaluate(self):
        if self.current_function is None:
            return False
        n = len(self.inputs)
        for i in range(2 ** n):
            x = [(i >> bit) & 1 == 1 for bit in range(n)]
            expected = self.function(x)
            actual = self.current_function(x)
            if expected != actual:
                return False
        return True

    def compile(self):
        var_map = {}
        expr_map = {}

        for i, term in enumerate(self.inputs):
            var_map[("TERMINAL_I", i)] = f"x[{i}]"

        for gid, gate in self.gates.items():
            var_map[("GATE_O", gid, 0)] = f"g{gid}"

        for i, term in enumerate(self.outputs):
            var_map[("TERMINAL_O", i)] = f"y{i}"

        input_sources = {}
        for wire in self.wires:
            if wire.to_i[1] == "GATE_I":
                input_sources[(wire.to_i[0], wire.to_i[2])] = wire.from_i
            elif wire.to_i[1] == "TERMINAL_O":
                input_sources[("OUT", wire.to_i[0])] = wire.from_i

        def build_expr_for_gate(gid):
            gate = self.gates[gid]
            input_exprs = []
            for i, _ in enumerate(gate.inputs):
                src = input_sources.get((gid, i))
                if src is None:
                    input_exprs.append("False")
                elif src[1] == "TERMINAL_I":
                    input_exprs.append(var_map[(src[1], src[0])])
                elif src[1] == "GATE_O":
                    input_exprs.append(build_expr_for_gate(src[0]))
                else:
                    input_exprs.append("False")
            t = gate.type
            if t == "AND":
                expr = f"({' and '.join(input_exprs)})"
            elif t == "OR":
                expr = f"({' or '.join(input_exprs)})"
            elif t == "NOT":
                expr = f"(not {input_exprs[0]})"
            elif t == "NAND":
                expr = f"(not ({' and '.join(input_exprs)}))"
            elif t == "NOR":
                expr = f"(not ({' or '.join(input_exprs)}))"
            elif t == "XOR":
                expr = f"({input_exprs[0]} != {input_exprs[1]})"
            elif t == "XNOR":
                expr = f"({input_exprs[0]} == {input_exprs[1]})"
            else:
                expr = "False"
            expr_map[gid] = expr
            return expr

        output_exprs = []
        for i, _ in enumerate(self.outputs):
            src = input_sources.get(("OUT", i))
            if src is None:
                output_exprs.append("False")
            elif src[1] == "TERMINAL_I":
                output_exprs.append(var_map[(src[1], src[0])])
            elif src[1] == "GATE_O":
                output_exprs.append(build_expr_for_gate(src[0]))
            else:
                output_exprs.append("False")

        body = f"return [{', '.join(output_exprs)}]"
        func_str = f"def logic_func(x):\n    {body}"

        local_ns = {}
        exec(func_str, {}, local_ns)
        self.current_function = local_ns["logic_func"]
