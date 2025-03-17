import pygame as py
from settings import *

class Player:
    def __init__(self, x, y, width, height, speed):
        self.rect = py.Rect(x, y, width, height)
        self.is_sprinting = False
        self.speed = speed
        self.sprint_speed = speed * 1.4
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -11
        self.on_object = False
        self.target_platform = None
        self.current_platform = None
        self.current_wall = None
        self.wall_jump_used = False
        self.on_wall = False

        # Player sprites
        self.animations = {}
        self.current_animation = "idle_right"
        self.facing_right = True
        self.current_image = 0
        self.animation_frame = 0
        self.animation_speed = 8
        self.is_moving = False
        self.is_jumping = False
        self.is_prone = False

    def add_animation(self, state, images):
        """Add an animation sequence for a specific state."""
        self.animations[state] = [py.image.load(img) for img in images]

    def set_animation(self, animation):
        """Set the current animation state."""
        if animation in self.animations and animation != self.current_animation:
            self.current_animation = animation
            self.current_image = 0

    def move(self, dx):
        """ Move the player horizontally by dx units """
        if self.is_prone:
            current_speed = 0
        elif self.is_sprinting:
            current_speed = self.sprint_speed
        else:
            current_speed = self.speed

        self.rect.x += dx * current_speed

        if dx != 0:
            self.is_moving = True
            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False
        else:
            self.is_moving = False
    
    def update_animation(self):
        if self.is_prone:
            if self.facing_right:
                self.set_animation('prone_right')
            else:
                self.set_animation('prone_left')
        elif self.is_jumping:
            if self.facing_right:
                self.set_animation('roll_right')
            else:
                self.set_animation('roll_left')
        elif self.is_moving:
            if self.is_sprinting:
                if self.facing_right:
                    self.set_animation('sprint_right')
                else:
                    self.set_animation('sprint_left')
            else:
                if self.facing_right:
                    self.set_animation('walk_right')
                else:
                    self.set_animation('walk_left')
        else:
            if self.facing_right:
                self.set_animation('idle_right')
            else:
                self.set_animation('idle_left')

    def jump(self):
        """ Let the player jump if they are grounded """
        if self.on_object: # If standing on something...
            self.y_velocity = self.jump_strength # Upwards velocity is now -10...
            self.on_object = False # Reset to false...
            self.wall_jump_used = False # Reset to false...
            self.is_jumping = True
        elif self.on_wall and not self.wall_jump_used:
            self.y_velocity = self.jump_strength
            self.on_wall = False
            self.wall_jump_used = True
            self.is_jumping = True

    def fall(self):
        """ Let the player fall through a platform if they are grounded """
        if self.on_object and self.current_platform:
            self.target_platform = self.current_platform # Player is targetting the platform they are standing on...
            self.on_object = False # Player is no longer on the platform...

    def update(self, platforms):
        self.y_velocity += self.gravity # Gravity slowly pulls player downwards after jumping...
        self.rect.y += self.y_velocity # Update y position to the new position...
        self.on_object = False # Reset the flag before checking for collisions...
        self.on_wall = False

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
                    self.is_jumping = False # Reset jump tracker...
                elif self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.bottom:
                    self.on_wall = True
                    self.current_wall = platform
        
        if self.target_platform and not self.rect.colliderect(self.target_platform): # If player is not on the target_platform set it to None
            self.target_platform = None

        if self.rect.bottom > py.display.get_surface().get_height(): # Ensure the player can't fall through the canvas...
            self.rect.bottom = py.display.get_surface().get_height()
            self.y_velocity = 0
            self.on_object = True
            self.is_jumping = False

        self.update_animation()

        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.animation_frame = 0
            self.current_image = (self.current_image + 1) % len(self.animations[self.current_animation])

    def draw(self, screen):
        """Draw the player on the screen."""
        current_state = self.animations[self.current_animation]
        sprite_height = current_state[self.current_image].get_height()
        if self.facing_right:
            offset_x = 90
        else:
            offset_x = 20
        sprite_x = self.rect.x - offset_x
        sprite_y = self.rect.y - (sprite_height - self.rect.height)
        screen.blit(current_state[self.current_image], (sprite_x, sprite_y))
        #py.draw.rect(screen, (255, 0, 0), self.rect, 2)
