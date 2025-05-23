import pygame
from typing import List, Tuple
from ui import draw_text

WIDTH, HEIGHT = 800, 600

white = (255, 255, 255)
green = (34, 139, 34)
wire_color_false = (100, 100, 100)
button_hover = (50, 200, 50)
button_bg = (40, 40, 40)

pygame.font.init()
gate_font = pygame.font.SysFont('arial', 20)
expected_font = pygame.font.SysFont('arial', 10)

default_gates = {"AND": ["images//AND.png", [[-20, -10], [-20, 10]], [20, 0, 0]],
                 "OR": ["images//OR.png", [[-20, -10], [-20, 10]], [20, 0, 0]],
                 "NOT": ["images//NOT.png", [[-20, 0]], [17, 0, 1]],
                 "XOR": ["images//XOR.png", [[-20, -10], [-20, 10]], [20, 0, 0]],
                 "XNOR": ["images//XNOR.png", [[-20, -10], [-20, 10]], [20, 0, 1]],
                 "NAND": ["images//NAND.png", [[-20, -10], [-20, 10]], [20, 0, 1]],
                 "NOR": ["images//NOR.png", [[-20, -10], [-20, 10]], [20, 0, 1]]}

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
            pos = (100, 100 + self.i * 60 + 3)
        elif self.type == "TERMINAL_O":
            pos = (WIDTH - 100, 100 + self.i * 60 + 3)
        return pos

    def __str__(self):
        return f"Terminal(i={self.i}, type={self.type}, pos={self.pos}, value={self.value}, isNot={self.isNot})"

class Gate:
    def __init__(self, gate_type: str, inputs: List[bool], outputs: List[bool], position: Tuple[int,int], color: Tuple[int,int,int]=button_bg):
        self.id = None
        self.type = gate_type.upper()
        self.inputs = [Terminal(i, "GATE_I", val) for i, val in enumerate(inputs)]
        self.outputs = [Terminal(i, "GATE_O", val) for i, val in enumerate(outputs)]
        self.position = position
        self.color = color
        self.radius = 30

        if self.type in ["NOT", "NAND", "NOR", "XNOR"]:
            self.outputs[0].isNot = True
    
    def copy(self):
        input_values = [term.value for term in self.inputs]
        output_values = [term.value for term in self.outputs]
        return Gate(gate_type=self.type, inputs=input_values, outputs=output_values, position=self.position, color=self.color)

    def draw(self, screen, x=-1, y=-1, selected=False):
        if x == -1 and y == -1:
            x, y = self.position
        if self.type in default_gates.keys():
            image = pygame.image.load(default_gates[self.type][0])
            image = pygame.transform.scale(image, (self.radius * 2, self.radius * 2))
            screen.blit(image, (x - self.radius, y - self.radius))
        else:
            rect_width, rect_height = 80, 60
            rect = pygame.Rect(self.position[0] - rect_width // 2, self.position[1] - rect_height // 2, rect_width, rect_height)
            pygame.draw.rect(screen, button_hover if selected else self.color, rect, border_radius=10)
            pygame.draw.rect(screen, white, rect, 2, border_radius=10)
            draw_text(screen, self.type, (self.position[0] - self.font.size(self.type)[0] // 2, self.position[1] - self.font.size(self.type)[1] // 2), self.font)
            
        # Draw input terminals
        input_positions = self.get_input_positions()
        for i, pos in input_positions:
            color = green if self.inputs[i].value else self.color
            pygame.draw.rect(screen, white, (pos[0] - 6, pos[1] - 6, 12, 12))
            pygame.draw.rect(screen, color, (pos[0] - 4, pos[1] - 4, 8, 8))

        # Draw output terminals
        output_positions = self.get_output_positions()
        for i, pos, circle_not in output_positions:
            color = green if self.outputs[i].value else self.color
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
    def __init__(self, name: str, inputs: List[bool], allowed_gates: List[str], function=None):
        self.name = name
        self.inputs = [Terminal(i, "TERMINAL_I", val) for i, val in enumerate(inputs)]
        self.expected = function(inputs)
        self.outputs = [Terminal(i, "TERMINAL_O") for i in range(len(self.expected))]
        self.allowed_gates = allowed_gates.copy()
        self.gates: dict[int, Gate] = {}
        self.wires: List[Wire] = []
        self.current_wire: Wire = None
        self.function = function
    
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

    def draw(self, screen, mouse_pos):
        self.expected = self.function(self.inputs)

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
            draw_text(screen, f"Expected: {term.value}", (term.pos[0] + 20, term.pos[1] + 5), expected_font)
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
            if wire.to_i[1] == "TERMINAL_I" and wire.to_i[0] == i:
                return True
        return False

    def gate_has_two_wires(self, gate_i, i):
        for wire in self.wires:
            if wire.to_i[1] == "GATE_I" and wire.to_i[0] == gate_i:
                if wire.to_i[2] == i:
                    return True
        return False
