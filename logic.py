import pygame
from typing import List, Tuple, Dict, Optional
from ui import draw_text

white = (255, 255, 255)
green = (34, 139, 34)
wire_color_false = (100, 100, 100)

class Gate:
    def __init__(self, gate_type: str, input_labels: List[str], output_label: str, position: Tuple[int,int], font, color: Tuple[int,int,int]):
        self.type = gate_type.upper()
        self.input_labels = input_labels
        self.output_label = output_label
        self.position = position
        self.font = font
        self.color = color
        self.radius = 30

    def evaluate(self, inputs: List[bool]) -> bool:
        if self.type == 'AND': return inputs[0] and inputs[1]
        if self.type == 'OR': return inputs[0] or inputs[1]
        if self.type == 'NOT': return not inputs[0]
        if self.type == 'XOR': return inputs[0] ^ inputs[1]
        if self.type == 'NAND': return not (inputs[0] and inputs[1])
        if self.type == 'NOR': return not (inputs[0] or inputs[1])
        return False

    def draw(self, screen, hover_color, x=-1, y=-1, selected=False):
        if x == -1 and y == -1:
            x, y = self.position
        rect_width, rect_height = 80, 60
        rect = pygame.Rect(self.position[0] - rect_width // 2, self.position[1] - rect_height // 2, rect_width, rect_height)
        pygame.draw.rect(screen, hover_color if selected else self.color, rect, border_radius=10)
        pygame.draw.rect(screen, white, rect, 2, border_radius=10)
        draw_text(screen, self.type[0], (self.position[0] - 7, self.position[1] - 10), self.font)
        
        # Draw input terminals
        for i, label in enumerate(self.input_labels):
            x_offset = -rect_width // 2 - 10
            y_offset = -rect_height // 2 + (i + 1) * (rect_height // (len(self.input_labels) + 1))
            pos = (self.position[0] + x_offset, self.position[1] + y_offset)
            pygame.draw.circle(screen, self.color, pos, 6)
            draw_text(screen, label, (pos[0] - 7, pos[1] - 10), self.font)
        
        # Draw output terminals
        x_offset = rect_width // 2 + 10
        for i, label in enumerate(self.output_label):
            y_offset = -rect_height // 2 + (i + 1) * (rect_height // (len(self.output_label) + 1))
            pos = (self.position[0] + x_offset, self.position[1] + y_offset)
            pygame.draw.circle(screen, self.color, pos, 6)
            draw_text(screen, label, (pos[0] - 7, pos[1] - 10), self.font)
    

class Wire:
    def __init__(self, from_, to_):
        self.from_ = from_
        self.to_ = to_
        self.middle_points = []
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
        for idx, (lab, val) in enumerate(self.inputs.items()):
            pygame.draw.circle(screen, button_bg, (50, 100 + idx * 60), 10)
            draw_text(screen, f"{lab}: {val}", (70, 90 + idx * 60), gate_font)
        for idx, (lab, val) in enumerate(self.expected.items()):
            pygame.draw.circle(screen, button_bg, (width - 50, 100 + idx * 60), 10)
            draw_text(screen, f"{lab}: {val}", (width - 70, 90 + idx * 60), gate_font)
        for gate in self.gates:
            gate.draw(screen, button_hover)