import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width  # Total map width
        self.height = height  # Total map height

    def update(self, target):
        # Fixed position, no scrolling. You can set this to any fixed location or keep it at the top-left corner.
        self.camera.x = 0
        self.camera.y = 0  # You can adjust this if you want to keep the vertical position fixed.

    def apply(self, rect):
        # No movement, so the apply function doesn't need to modify the rect.
        return rect

    def apply_pos(self, pos):
        # No movement, so the apply_pos function doesn't need to modify the position.
        return pos
