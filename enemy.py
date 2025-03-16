import pygame
from settings import *


class Enemy:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.direction = 1  # 1: right, -1: left

    def update(self, platforms):
        self.rect.x += self.direction * self.speed

        # Reverse direction at screen edges
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)