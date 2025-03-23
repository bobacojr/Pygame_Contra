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

        # Animation system
        self.animations = {}
        self.current_animation = "idle_right"
        self.current_image = 0
        self.animation_frame = 0
        self.animation_speed = 8
        self.facing_right = True

    def add_animation(self, state, images):
        """Add an animation sequence for a specific state."""
        self.animations[state] = [pygame.image.load(img) for img in images]

    def set_animation(self, animation):
        """Set the current animation state."""
        if animation in self.animations and animation != self.current_animation:
            self.current_animation = animation
            self.current_image = 0

    def update_animation(self):
        """Update the animation frame."""
        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.animation_frame = 0
            self.current_image = (self.current_image + 1) % len(self.animations[self.current_animation])

    def update(self, platforms, delta_time):
        # Apply gravity
        if not self.on_ground:
            self.y_velocity += self.gravity * delta_time * 60  # Multiply by 60 to maintain similar gravity to before
        self.rect.y += self.y_velocity * delta_time * 60  # Multiply by 60 to maintain similar movement to before
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
        self.rect.x += self.direction * self.speed * delta_time * 60  # Multiply by 60 to maintain similar speed to before

        # Reverse direction at screen edges
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

        # Update facing direction
        if self.direction == 1:
            self.facing_right = True
        else:
            self.facing_right = False

        # Update animation
        if self.facing_right:
            self.set_animation("walk_right")
        else:
            self.set_animation("walk_left")

        self.update_animation()

    def draw(self, screen):
        """Draw the enemy with the current animation frame."""
        current_frame = self.animations[self.current_animation][self.current_image]
        if self.facing_right:
            offset_x = 90
        else:
            offset_x = 20
        offset_y = 80
        sprite_x = self.rect.x - offset_x
        sprite_y = self.rect.y - offset_y
        screen.blit(current_frame, (sprite_x, sprite_y))