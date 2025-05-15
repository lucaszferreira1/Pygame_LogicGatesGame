import pygame
from typing import List, Tuple
from ui import draw_text

white = (255, 255, 255)
green = (34, 139, 34)
wire_color_false = (100, 100, 100)

class Gate:
    def __init__(self, gate_type: str, inputs: List[bool], outputs: List[bool], position: Tuple[int,int], font, color: Tuple[int,int,int]):
        self.id = None
        self.type = gate_type.upper()
        self.inputs = inputs
        self.outputs = outputs
        self.position = position
        self.font = font
        self.color = color
        self.radius = 30
    
    def copy(self):
        return Gate(gate_type=self.type, inputs=self.inputs[:], outputs=self.outputs, position=self.position, font=self.font, color=self.color)

    def draw(self, screen, hover_color, x=-1, y=-1, selected=False):
        if x == -1 and y == -1:
            x, y = self.position
        rect_width, rect_height = 80, 60
        rect = pygame.Rect(self.position[0] - rect_width // 2, self.position[1] - rect_height // 2, rect_width, rect_height)
        pygame.draw.rect(screen, hover_color if selected else self.color, rect, border_radius=10)
        pygame.draw.rect(screen, white, rect, 2, border_radius=10)
        draw_text(screen, self.type, (self.position[0] - self.font.size(self.type)[0] // 2, self.position[1] - self.font.size(self.type)[1] // 2), self.font)
        
        # Draw input terminals
        input_positions = self.get_input_positions()
        for i, pos in input_positions:
            color = green if self.inputs[i] else self.color
            pygame.draw.circle(screen, white, pos, 6)
            pygame.draw.circle(screen, color, pos, 4)

        # Draw output terminals
        output_positions = self.get_output_positions()
        for i, pos in output_positions:
            color = green if self.outputs[i] else self.color
            pygame.draw.circle(screen, white, pos, 6)
            pygame.draw.circle(screen, color, pos, 4)
    
    def update(self):
        self.evaluate()

    def get_input_positions(self):
        positions = []
        rect_width, rect_height = 80, 60
        for i in range(len(self.inputs)):
            x_off = -rect_width // 2
            y_off = -rect_height // 2 + (i + 1) * (rect_height // (len(self.inputs) + 1))
            pos = (self.position[0] + x_off, self.position[1] + y_off)
            positions.append((i, pos))
        return positions

    def get_output_positions(self):
        positions = []
        rect_width, rect_height = 80, 60
        for i in range(len(self.outputs)):
            x_offset = rect_width // 2
            y_offset = -rect_height // 2 + (i + 1) * (rect_height // (len(self.outputs) + 1))
            pos = (self.position[0] + x_offset, self.position[1] + y_offset)
            positions.append((i, pos))
        return positions
    
    def evaluate(self):
        match self.type:
            case "AND":
                self.outputs = [all(self.inputs)]
            case "OR":
                self.outputs = [any(self.inputs)]
            case "NOT":
                if len(self.inputs) == 1:
                    self.outputs = [not self.inputs[0]]
            case "NAND":
                self.outputs = [not all(self.inputs)]
            case "NOR":
                self.outputs = [not any(self.inputs)]
            case "XOR":
                self.outputs = [self.inputs[0] != self.inputs[1]] if len(self.inputs) == 2 else [False]
            case "XNOR":
                self.outputs = [self.inputs[0] == self.inputs[1]] if len(self.inputs) == 2 else [False]
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
            pos = gate.get_input_positions()[value[2]][1]
        elif value[1] == "GATE_O":
            gate = ports["GATE"][value[0]]
            pos = gate.get_output_positions()[value[2]][1]
        else:
            pos = ports[value[1]][value[0]][1]
        return pos
    
    def update_own_value(self, ports):
        if self.from_i[1] == "GATE_O":
            gate = ports["GATE"][self.from_i[0]]
            self.value = gate.outputs[self.from_i[2]]
        elif self.from_i[1] == "TERMINAL_O":
            term = ports["TERMINAL_O"][self.from_i[0]]
            self.value = term[2]

    def set_value_to_out(self, ports):
        if self.to_i[1] == "GATE_I":
            gate = ports["GATE"][self.to_i[0]]
            gate.inputs[self.to_i[2]] = self.value
        elif self.from_i[1] == "TERMINAL_I":
            pass # Alterar o valor do terminal da esquerda

    def __str__(self):
        return f"Wire(from={self.from_i}, to={self.to_i}, value={self.value})"


class Level:
    def __init__(self, name: str, inputs: List[bool], expected: List[bool], allowed_gates: List[str]):
        self.name = name
        self.inputs = inputs.copy()
        self.expected = expected.copy()
        self.allowed_gates = allowed_gates.copy()
        self.gates: dict[int, Gate] = {}
        self.wires: List[Wire] = []
        self.current_wire: Wire = None
    
    def add_gate(self, gate, id_gate):
        gate.id = id_gate
        self.gates[id_gate] = gate

    def remove_gate(self, gate):
        idx_gate = gate.id
        self.wires = [wire for wire in self.wires if not (
            (wire.from_i[1] == "GATE_O" and wire.from_i[0] == idx_gate) or
            (wire.to_i[1] == "GATE_I" and wire.to_i[0] == idx_gate)
        )]
        self.gates.pop(idx_gate)

    def draw(self, screen, width, height, button_bg, button_hover, gate_font, mouse_pos):
        input_positions = self.get_input_terminals()
        for i, val in enumerate(self.inputs):
            pygame.draw.circle(screen, white, input_positions[i][1], 12)
            pygame.draw.circle(screen, button_bg, input_positions[i][1], 10)
            draw_text(screen, f"{i}: {val}", (10, input_positions[i][1][1] - 13), gate_font)
        output_positions = self.get_output_terminals(width)
        for i, val in enumerate(self.expected):
            pygame.draw.circle(screen, white, output_positions[i][1], 12)
            pygame.draw.circle(screen, button_bg, output_positions[i][1], 10)
            draw_text(screen, f"{i}: {val}", (output_positions[i][1][0] + 20, output_positions[i][1][1] - 13), gate_font)
        for gate in self.gates.values():
            gate.update()
            gate.draw(screen, button_hover)
        
        ports = {"TERMINAL_O": input_positions, "TERMINAL_I": output_positions, "GATE": self.gates}
        for wire in self.wires:
            wire.update(ports)
            wire.draw(screen, ports)
        
        if self.current_wire:
            self.current_wire.draw_one_point(screen, ports, mouse_pos)

    def get_input_terminals(self):
        positions = []
        for i in range(len(self.inputs)):
            pos = (100, 100 + i * 60 + 3)
            positions.append((i, pos, self.inputs[i]))
        return positions

    def get_output_terminals(self, width):
        positions = []
        for i in range(len(self.expected)):
            pos = (width - 100, 100 + i * 60 + 3)
            positions.append((i, pos, self.inputs[i]))
        return positions

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
