import pygame as py
from settings import *
from bullet import Bullet

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
        self.current_wall = None
        self.wall_jump_used = False
        self.on_wall = False
        self.facing = "right"
        self.bullets = []
        self.health = 3
        self.invincible = False
        self.invincibility_timer = 0

    def shoot(self):
        keys = py.key.get_pressed()

        # Get direction from pressed keys
        dx, dy = 0, 0
        if keys[py.K_d]: dx += 1
        if keys[py.K_a]: dx -= 1
        if keys[py.K_w]: dy -= 1
        if keys[py.K_s]: dy += 1

        if dx == 0 and dy == 0:
            dx = 1 if self.facing == "right" else -1

        bullet = Bullet(self.rect.centerx, self.rect.centery, (dx, dy))
        self.bullets.append(bullet)

    def move(self, dx):
        """ Move the player horizontally by dx units """
        self.rect.x += dx * self.speed
        if dx < 0:
            self.facing = "left"
        elif dx > 0:
            self.facing = "right"

    def jump(self):
        """ Let the player jump if they are grounded """
        if self.on_object: # If standing on something...
            self.y_velocity = self.jump_strength # Upwards velocity is now -10...
            self.on_object = False # Reset to false...
            self.wall_jump_used = False # Reset to false...
        elif self.on_wall and not self.wall_jump_used:
            self.y_velocity = self.jump_strength
            self.on_wall = False
            self.wall_jump_used = True
            if self.rect.left < self.current_wall.rect.left:
                self.move(-2)
            else: 
                self.move(2)

    def fall(self):
        """ Let the player fall through a platform if they are grounded """
        if self.on_object and self.current_platform and self.current_platform.kind != "floor":
            self.target_platform = self.current_platform # Player is targeting the platform they are standing on...
            self.on_object = False # Player is no longer on the platform...

    def update(self, platforms):
        self.y_velocity += self.gravity # Gravity slowly pulls player downwards after jumping...
        self.rect.y += self.y_velocity # Update y position to the new position...
        self.on_object = False # Reset the flag before checking for collisions...

        if self.invincible and py.time.get_ticks() > self.invincibility_timer:
            self.invincible = False

        for platform in platforms:
            """ Snap the player ontop of platforms on collision """
            if platform == self.target_platform: # Continue if the platform is the target platform...
                continue

            if self.rect.colliderect(platform.rect): # Player collided with a platform...
                if self.y_velocity >= 0 and self.rect.bottom >= platform.rect.top and self.rect.bottom <= platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top # Move the bottom of the player to the top of the platform...
                    self.y_velocity = 0
                    self.on_object = True
                    self.current_platform = platform # Track the current platform...
                    self.target_platform = None # Reset the target_platform...
                    self.wall_jump_used = False # Reset wall jump...
                elif self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.bottom:
                    self.on_wall = True
                    self.current_wall = platform
        
        if self.target_platform and not self.rect.colliderect(self.target_platform): # If player is not on the target_platform set it to None
            self.target_platform = None

        if self.rect.bottom > py.display.get_surface().get_height(): # Ensure the player can't fall through the canvas...
            self.rect.bottom = py.display.get_surface().get_height()
            self.y_velocity = 0
            self.on_object = True

    def draw(self, screen):
        """Draw the player on the screen."""
        py.draw.rect(screen, self.color, self.rect)
