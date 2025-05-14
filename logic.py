import pygame
from typing import List, Tuple, Dict, Optional
from ui import draw_text

white = (255, 255, 255)
green = (34, 139, 34)
wire_color_false = (100, 100, 100)

class Gate:
    def __init__(self, gate_type: str, input_labels: List[str], output_label: str, position: Tuple[int,int], font, color: Tuple[int,int,int], value=False):
        self.type = gate_type.upper()
        self.input_labels = input_labels
        self.output_label = output_label
        self.position = position
        self.font = font
        self.color = color
        self.value = value
        self.radius = 30
    
    def copy(self):
        return Gate(gate_type=self.type, input_labels=self.input_labels[:], output_label=self.output_label, position=self.position, font=self.font, color=self.color)

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
            pygame.draw.circle(screen, white, pos, 6)
            pygame.draw.circle(screen, self.color, pos, 3)

        # Draw output terminals
        output_positions = self.get_output_positions()
        for i, pos in output_positions:
            pygame.draw.circle(screen, white, pos, 6)
            pygame.draw.circle(screen, self.color, pos, 3)
    
    def get_input_positions(self):
        positions = []
        rect_width, rect_height = 80, 60
        for i in range(len(self.input_labels)):
            x_off = -rect_width // 2
            y_off = -rect_height // 2 + (i + 1) * (rect_height // (len(self.input_labels) + 1))
            pos = (self.position[0] + x_off, self.position[1] + y_off)
            positions.append((i, pos))
        return positions

    def get_output_positions(self):
        positions = []
        rect_width, rect_height = 80, 60
        for i in range(len(self.output_label)):
            x_offset = rect_width // 2
            y_offset = -rect_height // 2 + (i + 1) * (rect_height // (len(self.output_label) + 1))
            pos = (self.position[0] + x_offset, self.position[1] + y_offset)
            positions.append((i, pos))
        return positions


class Wire:
    def __init__(self, from_i: Tuple[int, str, int], to_i: Tuple[int, str, int], value=False):
        self.from_i = from_i
        self.to_i = to_i
        self.middle_points = []
        self.value = value
        self.color = wire_color_false
    
    def draw(self, screen, ports):
        self.color = green if self.value else wire_color_false
        from_pos = self.get_port_pos(ports, False)
        to_pos = self.get_port_pos(ports, True)
        
        if len(self.middle_points) > 0:
            pygame.draw.line(screen, self.color, from_pos, self.middle_points[0], 5)
            if len(self.middle_points) > 1:
                for point in self.middle_points[1:]:
                    pygame.draw.circle(screen, white, point, 5)
            pygame.draw.line(screen, self.color, self.middle_points[-1], to_pos, 5)
        else:
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


class Level:
    def __init__(self, name: str, inputs: List[bool], expected: List[bool], allowed_gates: List[str]):
        self.name = name
        self.inputs = inputs.copy()
        self.expected = expected.copy()
        self.allowed_gates = allowed_gates.copy()
        self.gates: List[Gate] = []
        self.wires: List[Wire] = []
        self.selected_terminal: Optional[Tuple[str, Tuple[int, int]]] = None

    
    def add_gate(self, gate: Gate):
        self.gates.append(gate)

    def draw(self, screen, width, height, button_bg, button_hover, gate_font):
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
        for gate in self.gates:
            gate.draw(screen, button_hover)
        
        ports = {"TERMINAL_I": input_positions, "TERMINAL_O": output_positions, "GATE": self.gates}
        for wire in self.wires:
            wire.draw(screen, ports)

    
    def get_input_terminals(self):
        positions = []
        for i in range(len(self.inputs)):
            pos = (100, 100 + i * 60 + 3)
            positions.append((i, pos))
        return positions

    def get_output_terminals(self, width):
        positions = []
        for i in range(len(self.expected)):
            pos = (width - 100, 100 + i * 60 + 3)
            positions.append((i, pos))
        return positions