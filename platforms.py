import pygame
import Box2D as box
from Box2D import b2
from settings import *

class Platform:
    def __init__(self, world, x, y, width, height, texture, kind=None):
        self.width = width
        self.height = height
        self.kind = kind

        # Create a Box2D static body for the platform
        body_def = b2.bodyDef()
        body_def.position = ((x + width / 2) / PPM, (y + height / 2) / PPM)
        body_def.type = b2.staticBody
        self.body = world.CreateBody(body_def)

        # Define the fixture (shape) for the platform
        fixture_def = b2.fixtureDef()
        fixture_def.shape = b2.polygonShape(box=(width / 2 / PPM, height / 2 / PPM * 0.8))
        fixture_def.density = 0.0
        fixture_def.friction = 0.5
        self.body.CreateFixture(fixture_def)

        self.animations = {}
        self.current_animation = "default"
        self.current_image = 0
        self.animation_frame = 0
        self.animation_speed = 8

        self.add_animation("default", texture)

    def add_animation(self, state, images):
        """Add an animation sequence for a specific state."""
        self.animations[state] = [pygame.image.load(img) for img in images]
        self.animations[state] = [pygame.transform.scale(frame, (self.width, self.height)) for frame in self.animations[state]]

    def set_animation(self, animation):
        """Set the current animation state."""
        if animation in self.animations and animation != self.current_animation:
            self.current_animation = animation
            self.current_image = 0

    def update(self):
        """Update the animation frame."""
        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.animation_frame = 0
            self.current_image = (self.current_image + 1) % len(self.animations[self.current_animation])

    def draw(self, screen, camera):
        """Draw the platform with the current animation frame."""
        current_frame = self.animations[self.current_animation][self.current_image]
        pixel_x = self.body.position.x * PPM - self.width / 2 + camera.camera.x
        pixel_y = self.body.position.y * PPM - self.height / 2
        screen.blit(current_frame, (pixel_x, pixel_y))