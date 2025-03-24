import pygame
from settings import *
import Box2D as box
from Box2D import b2
from bullet import Bullet

class Enemy:
    def __init__(self, world, x, y, width, height, speed, player):
        self.x = x
        self.y = y
        self.world = world
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = 1  # 1: right, -1: left
        self.y_velocity = 0
        self.gravity = 0.5
        self.on_ground = False
        self.target_platform = None
        self.current_platform = None
        self.player = player  # Assign the player object
        self.shoot_cooldown = 120  # Cooldown for shooting
        self.bullets = []  # List to store bullets
        self.desired_distance = 500  # New: Desired distance from player
        self.separation_distance = 20 # How far apart enemies should try to stay from each other
        self.max_separation_force = 10
        self.is_destroyed = False
        self.platform_edge_buffer = 20  # How close to get to platform edge
        self.platform_check_distance = 50

        # Animation system
        self.animations = {}
        self.current_animation = "walk_right"
        self.current_image = 0
        self.animation_frame = 0
        self.animation_speed = 8
        self.facing_right = True

        self.add_animation("walk_right", ["images/Enemies/WalkRight/WalkRight1.gif", "images/Enemies/WalkRight/WalkRight2.gif", "images/Enemies/WalkRight/WalkRight3.gif"])
        self.add_animation("walk_left", ["images/Enemies/WalkLeft/WalkLeft1.gif", "images/Enemies/WalkLeft/WalkLeft2.gif", "images/Enemies/WalkLeft/WalkLeft3.gif"])

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
        if self.is_destroyed:
            return
        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.animation_frame = 0
            self.current_image = (self.current_image + 1) % len(self.animations[self.current_animation])

    def create_body(self, world):
        """Create the Box2D body for this enemy."""
        body_def = b2.bodyDef()  # Define the body
        body_def.position = (self.x / PPM, self.y / PPM)  # Set the position (convert to Box2D units using PPM)
        body_def.type = b2.dynamicBody  # Set body type to dynamic (will move and be affected by physics)
        body_def.fixedRotation = True  # Ensure the enemy doesn't rotate (if you don't want them to flip)

        self.body = world.CreateBody(body_def)  # Create the body in the Box2D world
        
        # Create a fixture (shape) for the enemy
        fixture_def = b2.fixtureDef()
        fixture_def.shape = b2.polygonShape(box=(self.width / 2 / PPM, self.height / 2 / PPM))  # Shape is a rectangle based on width and height
        fixture_def.density = 1.0  # Set the density of the enemy (affects mass)
        fixture_def.friction = 0.3  # Set the friction for collision with other objects
        fixture_def.restitution = 0.1  # Set how much the enemy bounces when colliding with other objects
        
        self.body.CreateFixture(fixture_def)  # Attach the fixture to the body
        
        # Enable continuous collision detection (CCD) to prevent the enemy from passing through other objects at high speed
        self.body.bullet = True 

    def destroy(self):
        """Completely clean up this enemy"""
        # Clean up all bullets first
        for bullet in self.bullets[:]:
            if bullet.body and bullet.body.world == self.world:
                self.world.DestroyBody(bullet.body)
            self.bullets.remove(bullet)
        
        # Then destroy enemy body
        if not self.is_destroyed:
            self.is_destroyed = True
            if self.body:
                for fixture in self.body.fixtures:
                    self.body.DestroyFixture(fixture)
                self.world.DestroyBody(self.body)
                self.body = None

    def shoot(self):
        """Shoot a bullet toward the player."""
        if self.shoot_cooldown <= 0 and self.player is not None:  # Check if player exists
            # Calculate direction toward the player
            player_x = self.player.body.position.x * PPM
            player_y = self.player.body.position.y * PPM
            enemy_x = self.body.position.x * PPM
            enemy_y = self.body.position.y * PPM

            dx = player_x - enemy_x
            dy = player_y - enemy_y
            direction = pygame.math.Vector2(dx, dy).normalize()

            # Create a bullet
            bullet = Bullet(
                world=self.world,
                x=enemy_x,
                y=enemy_y,
                direction=(direction.x, direction.y),
                facing="right" if direction.x > 0 else "left",
                is_prone=False
            )
            self.bullets.append(bullet)

            # Reset shoot cooldown
            self.shoot_cooldown = 1800000  # 1 second cooldown (60 frames)
    
    def check_platform_edges(self, platforms):
        """Check if enemy is approaching a platform edge"""
        if not self.on_ground:
            return False
            
        # Raycast in front of enemy to detect platform edges
        ray_length = self.platform_check_distance / PPM
        ray_start = self.body.position
        ray_end = b2.vec2(
            ray_start.x + (self.direction * ray_length),
            ray_start.y + (self.height / PPM / 2)  # Check slightly below feet
        )
        
        # Perform the raycast
        callback = RayCastCallback()
        self.world.RayCast(callback, ray_start, ray_end)
        
        # If no platform detected ahead, we're at an edge
        return not callback.hit

    def update(self, platforms, logical_water, enemies):
        """Update the enemy's state."""
        if self.is_destroyed:
            return

        # Reset ground state
        self.on_ground = False

        # Check for ground/platform contact
        for contact_edge in self.body.contacts:
            contact = contact_edge.contact
            if not contact.touching:
                continue
                
            # Check if this is a platform contact
            for platform in platforms:
                if contact.fixtureA == platform.body.fixtures[0] or contact.fixtureB == platform.body.fixtures[0]:
                    # Check if contact is below the enemy (ground contact)
                    if contact.manifold.localNormal.y < -0.5:  # Mostly upward normal
                        self.on_ground = True
                        break

        # Check for approaching platform edges
        at_edge = self.check_platform_edges(platforms)
        
        # --- Movement Logic ---
        if self.player:
            player_x = self.player.body.position.x * PPM
            enemy_x = self.body.position.x * PPM
            distance_to_player = abs(player_x - enemy_x)

            # Only change direction if not at edge or if moving away from edge
            if not at_edge:
                if distance_to_player < self.desired_distance:  # Too close → Move away
                    self.direction = -1 if player_x > enemy_x else 1
                elif distance_to_player > self.desired_distance + 10:  # Too far → Move closer
                    self.direction = 1 if player_x > enemy_x else -1
            else:
                # At edge - turn around
                self.direction *= -1

        # Apply movement
        if self.on_ground and not at_edge:
            velocity = self.body.linearVelocity
            desired_velocity = self.direction * self.speed / PPM
            velocity_change = desired_velocity - velocity.x
            impulse = self.body.mass * velocity_change
            self.body.ApplyLinearImpulse(b2.vec2(impulse, 0), self.body.worldCenter, True)

        # Update facing direction and animation
        self.facing_right = self.direction == 1
        self.set_animation("walk_right" if self.facing_right else "walk_left")
        self.update_animation()

        # Shooting logic (same as before)
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.body.position.x * PPM < 0 or bullet.body.position.x * PPM > SCREEN_WIDTH:
                self.bullets.remove(bullet)
                self.world.DestroyBody(bullet.body)


    def draw(self, screen, camera):
        """Draw the enemy with the current animation frame and a bounding box."""
        if self.is_destroyed or self.body is None:
            return
        current_frame = self.animations[self.current_animation]
        if self.facing_right:
            offset_x = 120
        else:
            offset_x = 50
        offset_y = 130
        sprite_x = self.body.position.x * PPM - offset_x + camera.camera.x
        sprite_y = self.body.position.y * PPM - offset_y
        screen.blit(current_frame[self.current_image], (sprite_x, sprite_y))

        # Draw a bounding box around the enemy
        enemy_rect = pygame.Rect(
            self.body.position.x * PPM - self.width / 2 + camera.camera.x,
            self.body.position.y * PPM - self.height / 2,
            self.width,
            self.height
        )

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen, camera)

class RayCastCallback(b2.rayCastCallback):
    """Callback for raycasting to detect platform edges"""
    def __init__(self):
        super().__init__()
        self.hit = False
        
    def ReportFixture(self, fixture, point, normal, fraction):
        # Ignore sensors and non-solid fixtures
        if fixture.sensor:
            return -1
            
        self.hit = True
        self.point = b2.vec2(point)
        self.normal = b2.vec2(normal)
        return fraction  # Stop after first hit