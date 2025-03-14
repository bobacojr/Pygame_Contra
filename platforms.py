import pygame

class Platform:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.rect.top = y
        self.rect.bottom = y + height

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)