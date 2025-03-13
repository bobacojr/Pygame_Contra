import pygame as py
from settings import *

class Player:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = py.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.on_object = False

    def move(self, dx):
        """ Move the player horizontally by dx units """
        self.rect.x += dx * self.speed

    def jump(self):
        """ Let the player jump if they are grounded """
        if self.on_object: # If standing on something...
            self.y_velocity = self.jump_strength # Upwards velocity is now -10...
            self.on_object = False # Reset to false...

    def update(self, platforms):
        self.y_velocity += self.gravity # Gravity slowly pulls player downwards after jumping...
        self.rect.y += self.y_velocity # Update y position to the new position...
        self.on_object = False # Reset the flag before checking for collisions...

        for platform in platforms:
            """ Snap the player ontop of platforms on collision """
            if self.rect.colliderect(platform) and self.y_velocity >= 0:
                self.rect.bottom = platform.rect.top
                self.y_velocity = 0
                self.on_object = True
        if self.rect.bottom > py.display.get_surface().get_height():
            self.rect.bottom = py.display.get_surface().get_height()
            self.velocity_y = 0
            self.on_object = True

    def draw(self, screen):
        """Draw the player on the screen."""
        py.draw.rect(screen, self.color, self.rect)
