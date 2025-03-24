import pygame as py
import Box2D as box
from Box2D import b2
from settings import *
from bullet import Bullet

class Player:
    def __init__(self, world, x, y, width, height, speed, jump_strength):
        #self.rect = py.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.world = world
        self.is_sprinting = False
        self.speed = speed
        self.sprint_speed = speed * 1.4
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = jump_strength
        self.on_object = False
        self.target_platform = None
        self.current_platform = None
        self.in_water = False
        self.invincible = False
        self.bullets = []
        self.health = 3
        self.facing = "right"
        self.is_falling = False

        # Box2D Body
        body_def = b2.bodyDef()
        body_def.type = b2.dynamicBody
        body_def.position = b2.vec2(x / PPM, y / PPM)
        body_def.fixedRotation = True
        self.body = self.world.CreateBody(body_def)

        # Box2D fixture definition
        fixture_def = b2.fixtureDef()
        fixture_def.shape = b2.polygonShape(box=(width / 2 / PPM, height / 2 / PPM))
        fixture_def.density = 1.0
        fixture_def.friction = 0.3
        fixture_def.restitution = 0.1
        self.body.CreateFixture(fixture_def)

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

        self.add_animation("idle_left", ["images/Player/IdleLeft/IdleLeft_1.gif", "images/Player/IdleLeft/IdleLeft_2.gif"])
        self.add_animation("idle_right", ["images/Player/IdleRight/IdleRight_1.gif", "images/Player/IdleRight/IdleRight_2.gif"])
        self.add_animation("walk_left", ["images/Player/WalkLeft/WalkLeft_1.gif", "images/Player/WalkLeft/WalkLeft_2.gif", "images/Player/WalkLeft/WalkLeft_3.gif"])
        self.add_animation("walk_right", ["images/Player/WalkRight/WalkRight_1.gif", "images/Player/WalkRight/WalkRight_2.gif", "images/Player/WalkRight/WalkRight_3.gif"])
        self.add_animation("roll_left", ["images/Player/RollLeft/RollLeft_1.gif", "images/Player/RollLeft/RollLeft_2.gif", "images/Player/RollLeft/RollLeft_3.gif", "images/Player/RollLeft/RollLeft_4.gif"])
        self.add_animation("roll_right", ["images/Player/RollRight/RollRight_1.gif", "images/Player/RollRight/RollRight_2.gif", "images/Player/RollRight/RollRight_3.gif", "images/Player/RollRight/RollRight_4.gif"])
        self.add_animation("sprint_right", ["images/Player/RunRight/RunRight_1.gif", "images/Player/RunRight/RunRight_2.gif", "images/Player/RunRight/RunRight_3.gif", "images/Player/RunRight/RunRight_4.gif", "images/Player/RunRight/RunRight_5.gif", "images/Player/RunRight/RunRight_6.gif", ])
        self.add_animation("sprint_left", ["images/Player/RunLeft/RunLeft_1.gif", "images/Player/RunLeft/RunLeft_2.gif", "images/Player/RunLeft/RunLeft_3.gif", "images/Player/RunLeft/RunLeft_4.gif", "images/Player/RunLeft/RunLeft_5.gif", "images/Player/RunLeft/RunLeft_6.gif", ])
        self.add_animation("prone_left", ["images/Player/ProneLeft/ProneLeft.gif"])
        self.add_animation("prone_right", ["images/Player/ProneRight/ProneRight.gif"])
        self.add_animation("water_left", ["images/Player/WaterMovement/WaterLeft.gif"])
        self.add_animation("water_right", ["images/Player/WaterMovement/WaterRight.gif"])

    def create_fixture(self):
        """Creates the player fixture based on the current size."""
        fixture_def = b2.fixtureDef()
        fixture_def.shape = b2.polygonShape(box=(self.width / 2 / PPM, self.height / 2 / PPM))
        fixture_def.density = 1.0
        fixture_def.friction = 0.3
        fixture_def.restitution = 0.1
        self.body.CreateFixture(fixture_def)

    def enter_prone(self):
        """Shrink the player when entering the prone position."""
        self.is_prone = True
        self.height = self.original_height / 2  # Shrink height
        self.width = self.original_width / 2  # Optionally shrink width as well
        self.body.DestroyFixture(self.body.fixtures[0])  # Remove the current fixture
        self.create_fixture()  # Create a new fixture with the smaller size

    def exit_prone(self):
        """Revert the player to their original size."""
        self.is_prone = False
        self.height = self.original_height
        self.width = self.original_width
        self.body.DestroyFixture(self.body.fixtures[0])  # Remove the current fixture
        self.create_fixture()  # Create a new fixture with the original size

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
            return
        
        velocity = self.body.linearVelocity
        desired_velocity = dx * (self.sprint_speed if self.is_sprinting else self.speed) / PPM
        velocity_change = desired_velocity - velocity.x
        impulse = self.body.mass * velocity_change
        self.body.ApplyLinearImpulse(b2.vec2(impulse, 0), self.body.worldCenter, True)

        if dx != 0:
            self.is_moving = True
            if dx > 0:
                self.facing_right = True
                self.facing = "right"
            elif dx < 0:
                self.facing_right = False
                self.facing = "left"
        else:
            self.is_moving = False

    def update_animation(self):
        if self.in_water:
            if self.facing_right:
                self.set_animation('water_right')
            else:
                self.set_animation('water_left')
        elif self.is_prone:
            keys = py.key.get_pressed()
            if keys[py.K_a]:
                self.facing_right = False
                self.set_animation('prone_left')
            if keys[py.K_d]:
                self.facing_right = True
                self.set_animation('prone_right')
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
        if self.on_object or self.in_water:  # If standing on something...
            self.body.ApplyLinearImpulse(b2.vec2(0, -self.jump_strength), self.body.worldCenter, True)
            self.on_object = False
            self.is_jumping = True
            print("Player jumped!")

    def shoot(self):
        keys = py.key.get_pressed()

        # Get direction from pressed keys
        dx, dy = 0, 0
        if keys[py.K_d]: dx += 1
        if keys[py.K_a]: dx -= 1
        if keys[py.K_w]: dy -= 1

        if dx == 0:
            dx = 1 if self.facing == 'right' else -1

        direction = py.math.Vector2(dx, dy).normalize()

        # Create a Box2D bullet
        bullet = Bullet(
            world=self.world,  # Pass the Box2D world
            x=self.body.position.x * PPM,  # Convert Box2D position to pixels
            y=self.body.position.y * PPM,  # Convert Box2D position to pixels
            direction=(direction.x, direction.y),  # Normalized direction
            facing=self.facing,  # Player's facing direction
            is_prone=self.is_prone  # Player's prone state
        )

        # Add the bullet to the player's bullet list
        self.bullets.append(bullet)

    def fall(self):
        """ Let the player fall through a platform if they are grounded """
        if self.on_object and self.current_platform:
            self.target_platform = self.current_platform # Player is targeting the platform they are standing on...
            self.on_object = False # Player is no longer on the platform...

            platform_aabb = self.current_platform.body.fixtures[0].GetAABB(0)
            self.body.position = b2.vec2(
                self.body.position.x,  # Keep the same x position
                platform_aabb.lowerBound.y + 0.9  # Move slightly below the platform
            )

    def update(self, platforms, logical_water):
        self.on_object = False

        # Get the player's AABB
        player_fixture = self.body.fixtures[0]
        player_aabb = player_fixture.GetAABB(0)

        # Check for collisions with platforms
        for platform in platforms:
            if platform == self.target_platform:  # Skip the target platform
                continue

            # Get the platform's AABB
            platform_fixture = platform.body.fixtures[0]
            platform_aabb = platform_fixture.GetAABB(0)

            # Check for overlap
            if (player_aabb.lowerBound.x < platform_aabb.upperBound.x and
            player_aabb.upperBound.x > platform_aabb.lowerBound.x and
            player_aabb.lowerBound.y < platform_aabb.upperBound.y and
            player_aabb.upperBound.y > platform_aabb.lowerBound.y):

            # Only snap to the platform if the player is falling (moving down) and their feet are above the platform
                if self.body.linearVelocity.y >= 0:  # Player is moving downward or stationary
                    if player_aabb.upperBound.y > platform_aabb.lowerBound.y:  # Check if player's feet are above the platform
                    
                        self.body.linearVelocity.y = 0  # Stop vertical movement

                        self.on_object = True
                        self.current_platform = platform
                        self.target_platform = None  # Reset the target platform
                        self.is_jumping = False

        # Handle smooth falling when going below a platform
        if self.on_object and self.current_platform:
            platform_aabb = self.current_platform.body.fixtures[0].GetAABB(0)
            if player_aabb.upperBound.y < platform_aabb.lowerBound.y:  # Player falling below the platform
                self.body.position = b2.vec2(
                    self.body.position.x,  # Keep the player's x position unchanged
                    platform_aabb.lowerBound.y + 0.1  # Apply a small offset to avoid instant falling
                )

        # Check for water collision
        water_fixture = logical_water.fixtures[0]
        water_aabb = water_fixture.GetAABB(0)

        if (player_aabb.lowerBound.x < water_aabb.upperBound.x and  # player left < water right
            player_aabb.upperBound.x > water_aabb.lowerBound.x and  # player right > water left
            player_aabb.lowerBound.y < water_aabb.upperBound.y and  # player bottom < water top
            player_aabb.upperBound.y > water_aabb.lowerBound.y):    # player top > water bottom
            self.in_water = True
        else:
            self.in_water = False

        # Update invincibility timer
        if self.invincible and py.time.get_ticks() > self.invincibility_timer:
            self.invincible = False

        # Update animation
        self.update_animation()

        # Update animation frame
        self.animation_frame += 1
        if self.animation_frame >= self.animation_speed:
            self.animation_frame = 0
            self.current_image = (self.current_image + 1) % len(self.animations[self.current_animation])

    def draw(self, screen, camera):
        """Draw the player on the screen."""
        current_state = self.animations[self.current_animation]
        if self.facing_right:
            offset_x = 120
        else:
            offset_x = 50
        offset_y = 130
        sprite_x = self.body.position.x * PPM - offset_x
        sprite_y = self.body.position.y * PPM - offset_y
        screen.blit(current_state[self.current_image], (sprite_x, sprite_y))