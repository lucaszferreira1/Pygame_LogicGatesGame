import pygame
from typing import List, Tuple, Dict, Optional
from ui import draw_text

white = (255, 255, 255)
green = (34, 139, 34)
wire_color_false = (100, 100, 100)

class Gate:
    def __init__(self, gate_type: str, input_labels: List[str], output_label: str, position: Tuple[int,int], font, color: Tuple[int,int,int], values = [False]):
        self.type = gate_type.upper()
        self.input_labels = input_labels
        self.output_label = output_label
        self.position = position
        self.font = font
        self.color = color
        self.values = values
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
    def __init__(self, from_, to_ = None, io = "IN", value=False):
        self.from_ = from_
        self.to_ = to_
        self.io = io
        self.middle_points = []
        self.value = value
        self.color = wire_color_false
    
    def draw(self, screen, signal):
        self.color = green if signal else wire_color_false
        from_pos = self.from_.position
        to_pos = self.to_.position
        if len(self.middle_points) > 0:
            pygame.draw.line(screen, self.color, from_pos, self.middle_points[0], 5)
            if len(self.middle_points) > 1:
                for point in self.middle_points[1:]:
                    pygame.draw.circle(screen, white, point, 5)
            pygame.draw.line(screen, self.color, self.middle_points[-1], to_pos, 5)
        else:
            pygame.draw.line(screen, self.color, from_pos, to_pos, 5)

    def check_x_to_y(self):
        return True if self.io == "IN" else False


class Level:
    def __init__(self, name, inputs: Dict[str, bool], expected: Dict[str, bool], allowed_gates: List[str]):
        self.name = name
        self.inputs = inputs.copy()
        self.expected = expected.copy()
        self.allowed_gates = allowed_gates
        self.gates: List[Gate] = []
        self.wires: List[Wire] = []
        self.selected_terminal: Optional[Tuple[str, Tuple[int, int]]] = None

    
    def add_gate(self, gate: Gate):
        self.gates.append(gate)

    def draw(self, screen, width, height, button_bg, button_hover, gate_font):
        input_positions = self.get_input_terminals()
        for idx, (lab, val) in enumerate(self.inputs.items()):
            pygame.draw.circle(screen, white, input_positions[idx][1], 12)
            pygame.draw.circle(screen, button_bg, input_positions[idx][1], 10)
            draw_text(screen, f"{lab}: {val}", (10, input_positions[idx][1][1] - 13), gate_font)
        output_positions = self.get_output_terminals(width)
        for idx, (lab, val) in enumerate(self.expected.items()):
            pygame.draw.circle(screen, white, output_positions[idx][1], 12)
            pygame.draw.circle(screen, button_bg, output_positions[idx][1], 10)
            draw_text(screen, f"{lab}: {val}", (output_positions[idx][1][0] + 20, output_positions[idx][1][1] - 13), gate_font)
        for gate in self.gates:
            gate.draw(screen, button_hover)
    
    def get_input_terminals(self):
        positions = []
        for i in range(len(self.inputs.items())):
            pos = (100, 100 + i * 60 + 3)
            positions.append((i, pos))
        return positions

    def get_output_terminals(self, width):
        positions = []
        for i in range(len(self.expected.items())):
            pos = (width - 100, 100 + i * 60 + 3)
            positions.append((i, pos))
        return positions