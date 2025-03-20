import pygame

class Platform:
    def __init__(self, x, y, width, height, texture, kind=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.texture = pygame.image.load(texture)  # Load the texture image
        self.texture = pygame.transform.scale(self.texture, (width, height))
        self.kind = kind

    def draw(self, screen):
        screen.blit(self.texture, self.rect.topleft)