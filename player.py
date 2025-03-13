import pygame as py
from settings import *

class Player:
    def __init__(self, x, y, width, height, color, speed):
        self.rect = py.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -11
        self.on_object = False
        self.target_platform = None
        self.current_platform = None

    def move(self, dx):
        """ Move the player horizontally by dx units """
        self.rect.x += dx * self.speed

    def jump(self):
        """ Let the player jump if they are grounded """
        if self.on_object: # If standing on something...
            self.y_velocity = self.jump_strength # Upwards velocity is now -10...
            self.on_object = False # Reset to false...

    def fall(self):
        """ Let the player fall through a platform if they are grounded """
        if self.on_object and self.current_platform:
            self.target_platform = self.current_platform # Player is targetting the platform they are standing on...
            self.on_object = False # Player is no longer on the platform...

    def update(self, platforms):
        self.y_velocity += self.gravity # Gravity slowly pulls player downwards after jumping...
        self.rect.y += self.y_velocity # Update y position to the new position...
        self.on_object = False # Reset the flag before checking for collisions...

        for platform in platforms:
            """ Snap the player ontop of platforms on collision """
            if platform == self.target_platform: # Continue if the platform is the target platform...
                continue

            if self.rect.colliderect(platform): # Player collided with a platform...
                if self.y_velocity >= 0 and self.rect.bottom >= platform.rect.top:
                    self.rect.bottom = platform.rect.top # Move the bottom of the player to the top of the platform...
                    self.y_velocity = 0
                    self.on_object = True
                    self.current_platform = platform # Track the current platform...
        
        if self.target_platform and not self.rect.colliderect(self.target_platform): # If player is not on the target_platform set it to None
            self.target_platform = None

        if self.rect.bottom > py.display.get_surface().get_height(): # Ensure the player can't fall through the canvas...
            self.rect.bottom = py.display.get_surface().get_height()
            self.y_velocity = 0
            self.on_object = True

    def draw(self, screen):
        """Draw the player on the screen."""
        py.draw.rect(screen, self.color, self.rect)
