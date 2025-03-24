import pygame
import Box2D as box
from Box2D import b2
from settings import *

class Bullet:
    def __init__(self, world, x, y, direction, facing, is_prone, speed=60):
        self.world = world
        self.speed = speed
        self.direction = direction
        self.facing = facing
        self.is_prone = is_prone
        self.landed_time = None
        self.landed = False

        # Adjust the initial position based on the player's state (prone or standing)
        if is_prone:
            if facing == 'right':
                self.start_x = x - 5
                self.start_y = y + 30
            else:
                self.start_x = x + 12
                self.start_y = y + 20
        else:
            if facing == 'right':
                self.start_x = x + 40
                self.start_y = y - 4
            else:
                self.start_x = x - 6
                self.start_y = y - 6

        # Create a Box2D body for the bullet
        body_def = b2.bodyDef()
        body_def.type = b2.dynamicBody
        body_def.position = b2.vec2(self.start_x / PPM, self.start_y / PPM)  # Convert to Box2D units
        body_def.bullet = True  # Enable continuous collision detection (CCD)
        self.body = self.world.CreateBody(body_def)

        # Create a Box2D fixture for the bullet
        fixture_def = b2.fixtureDef()
        fixture_def.shape = b2.polygonShape(box=(5 / PPM, 2.5 / PPM))  # Bullet size (10x5 pixels)
        fixture_def.density = 1.0
        fixture_def.friction = 0.0
        fixture_def.restitution = 0.0
        self.body.CreateFixture(fixture_def)

        # Set the bullet's initial velocity
        self.body.linearVelocity = b2.vec2(self.direction[0] * self.speed, self.direction[1] * self.speed)

    def update(self):
        """Update the bullet's position (handled by Box2D)."""
        pass  # Box2D handles the physics, so no need to manually update position

    def draw(self, screen, camera):
        """Draw the bullet."""
        # Get the bullet's position in pixels
        bullet_x = self.body.position.x * PPM
        bullet_y = self.body.position.y * PPM

        # Draw the bullet as a rectangle
        bullet_rect = pygame.Rect(
            bullet_x - 5,  # Adjust for bullet size
            bullet_y - 2.5,
            7,  # Bullet width
            6    # Bullet height
        )
        pygame.draw.rect(screen, (255, 255, 0), bullet_rect)  # Red bullet
    
    def destroy(self):
        """Safely remove bullet"""
        if self.body and self.body.world == self.world:
            for fixture in self.fixtures:
                self.body.DestroyFixture(fixture)
            self.world.DestroyBody(self.body)
        self.fixtures = []
        self.body = None

class BulletContactListener(b2.contactListener):
    def __init__(self, bullets, targets):
        super().__init__()
        self.bullets = bullets
        self.targets = targets

    def BeginContact(self, contact):
        """Called when two fixtures begin to collide."""
        fixture_a = contact.fixtureA
        fixture_b = contact.fixtureB
        body_a = fixture_a.body
        body_b = fixture_b.body

        for bullet in self.bullets:
            if body_a == bullet.body or body_b == bullet.body:
                other_body = body_a if body_b == bullet.body else body_b
                if other_body in self.targets:
                    bullet.landed = True
                    bullet.landed_time = pygame.time.get_ticks()