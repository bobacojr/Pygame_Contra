import pygame
from settings import *


class Enemy:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.direction = 1  # 1: right, -1: left
        self.y_velocity = 0
        self.gravity = 0.5
        self.on_ground = False

    def update(self, platforms):
        # Apply gravity
        if not self.on_ground:
            self.y_velocity += self.gravity
        self.rect.y += self.y_velocity
        self.on_ground = False  # Reset ground check

        # Platform collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_velocity > 0 and self.rect.bottom >= platform.rect.top and self.rect.bottom <= platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top
                    self.y_velocity = 0
                    self.on_ground = True

        # Ensure enemy does not fall below the screen
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y_velocity = 0
            self.on_ground = True

        # Horizontal movement
        self.rect.x += self.direction * self.speed

        # Reverse direction at screen edges
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)