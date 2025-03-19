import pygame

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x - 5, y - 2, 10, 5)
        self.direction = pygame.math.Vector2(direction).normalize() if direction != (0,0) else pygame.math.Vector2(1, 0)
        self.speed = 20

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)