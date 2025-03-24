import pygame
import sys
import Box2D as box
from Box2D import b2
from player import Player
from platforms import Platform
from settings import *
from enemy import Enemy
from camera import Camera
from bullet import BulletContactListener

""" Initialize game instance """
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set the games screen
clock = pygame.time.Clock()  # Set the games clock

""" Load assets """
# Background image
background_texture = pygame.image.load("images/Background.gif")
background_texture = pygame.transform.scale(background_texture, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Decorations
MainPlatformFlora = pygame.image.load("images/Platforms/MainPlatform/MainPlatformFlora.gif")
MainPlatformFlora_position = (0, 280)

# Load the background image
main_bg = pygame.image.load("images/Platforms/MainBG1.gif")
main_bg = pygame.transform.scale(main_bg, (SCREEN_WIDTH, 250))  # Set the height to 210

# Define the position of the background image
main_bg_position = (0, MainPlatformFlora_position[1] + MainPlatformFlora.get_height())

""" Initialize Box2D world """
world = b2.world(gravity=(0, 9.8))  # Create a Box2D world with gravity

""" Initialize game objects """
player = None
platforms = []
enemies = []
visual_water = None  # The water seen in the game
logical_water = None  # Invisible water used for animation purposes

def initialize_game():
    """ Initialize game objects and variables """
    global player, platforms, enemies, visual_water, logical_water, camera, current_section_index, current_section, main_bg, map_sections, contact_listener, game_state, current_level

    game_state = "playing"
    current_level = 0

    # Camera
    camera = Camera(2000, SCREEN_HEIGHT)

    # Player
    player = Player(world, 80, 300, 50, 60, 240, 30)

    # Define map sections
    map_sections = [
        {
            "platforms": [
                Platform(world, 200, 540, 237, 129, ["images/Platforms/Wall3.gif"]),
                Platform(world, -40, 410, 237, 52, ["images/Platforms/Wall1.gif"]),
                Platform(world, 520, 410, 624, 52, ["images/Platforms/Wall2.gif"]),
                Platform(world, 470, 636, 573, 63, ["images/Platforms/LongGrass1.gif", "images/Platforms/LongGrass2.gif"]),
                Platform(world, -12, 636, 200, 51, ["images/Platforms/SmallGrass/SmallGrass1.gif", "images/Platforms/SmallGrass/SmallGrass2.gif"]),
            ],
            "decorations": [
                {"image": MainPlatformFlora, "position": (0, 280)},
            ],
            "enemies": [
                Enemy(world, 500, 635, 80, 100, 200, player),
                #Enemy(world, 30, 634, 80, 80, 200, player),
                Enemy(world, 250, 200, 80, 100, 200, player)
            ],
        },
        {
            "platforms": [
                Platform(world, 200, 540, 237, 129, ["images/Platforms/Wall3.gif"]),
                Platform(world, -40, 410, 237, 52, ["images/Platforms/Wall1.gif"]),
                Platform(world, 520, 410, 624, 52, ["images/Platforms/Wall2.gif"]),
                Platform(world, 470, 636, 573, 63, ["images/Platforms/LongGrass1.gif", "images/Platforms/LongGrass2.gif"]),
                Platform(world, -12, 636, 200, 51, ["images/Platforms/SmallGrass/SmallGrass1.gif", "images/Platforms/SmallGrass/SmallGrass2.gif"]),
            ],
            "decorations": [
                {"image": MainPlatformFlora, "position": (0, 280)},
            ],
            "enemies": [
                Enemy(world, 500, 635, 80, 100, 200, player),
                Enemy(world, 550, 635, 80, 100, 200, player),
                #Enemy(world, 30, 634, 80, 80, 200, player),
                Enemy(world, 250, 200, 80, 100, 200, player)
            ],
        },
        
    ]

    current_level = 0
    load_level(current_level)

    # Map Section
    current_section_index = 0
    current_section = map_sections[current_section_index]
    platforms = current_section["platforms"]
    enemies = current_section["enemies"]

    # Water
    visual_water_y = 660
    visual_water_height = SCREEN_HEIGHT - visual_water_y
    visual_water = pygame.Rect(0, visual_water_y, SCREEN_WIDTH, visual_water_height)

    # Create a Box2D body for logical water
    logical_water_y = 700 / PPM  # Convert to meters
    logical_water_height = (SCREEN_HEIGHT - 700) / PPM  # Convert to meters
    water_body_def = b2.bodyDef()
    water_body_def.position = (SCREEN_WIDTH / 2 / PPM, logical_water_y + logical_water_height / 2)
    water_body_def.type = b2.staticBody  # Water is static
    logical_water = world.CreateBody(water_body_def)

    # Create a fixture for the water body
    water_fixture_def = b2.fixtureDef()
    water_fixture_def.shape = b2.polygonShape(box=(SCREEN_WIDTH / 2 / PPM, logical_water_height / 2))
    logical_water.CreateFixture(water_fixture_def)

    targets = [logical_water]
    for platform in platforms:
        targets.append(platform.body)
    for enemy in enemies:
        targets.append(enemy.body)

    # Contact Listener
    contact_listener = BulletContactListener(player.bullets, targets)
    world.contactListener = contact_listener

def load_level(level_index):
    """Load a specific level from the map_sections"""
    global current_section, platforms, enemies
    
    if level_index < 0 or level_index >= len(map_sections):
        return False
    
    # Clear existing platforms and enemies
    platforms = []
    enemies = []
    
    # Load the new level
    current_section = map_sections[level_index]
    platforms = current_section["platforms"]
    enemies = current_section["enemies"].copy()  # Create a copy of the enemy list
    
    # Create Box2D bodies for the new enemies
    for enemy in enemies:
        enemy.create_body(world)  # Assuming your Enemy class has this method
    
    return True

def handle_events():
    """ Handle user input events """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # Game is not running

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            #if event.key == pygame.K_s:
               # player.fall()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.shoot()

    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_a]:
        dx -= 1
    if keys[pygame.K_d]:
        dx += 1

    player.is_sprinting = keys[pygame.K_LSHIFT]
    player.is_prone = keys[pygame.K_LCTRL]
    player.move(dx)

    return True  # Game is running

def update_game():
    """Update the game state."""
    global current_level, platforms, enemies, game_state

    # Step the Box2D world
    world.Step(1 / 60, 6, 2)

    player.update(platforms, logical_water)  # Update player
    camera.update(player)  # Update camera

    if not enemies:
        # Current level completed
        if current_level < len(map_sections) - 1:
            # More levels to go - advance to next level
            current_level += 1
            load_level(current_level)
        else:
            # Game won!
            game_state = "game_won"

    for platform in platforms:  # Update platforms
        platform.update()

    for enemy in enemies[:]:  # Create a copy of the list for iteration
        if enemy.is_destroyed:
            enemies.remove(enemy)
            continue
        enemy.update(platforms, logical_water, enemies)
        # Keep enemies within screen bounds
        enemy_x = enemy.body.position.x * PPM
        enemy_y = enemy.body.position.y * PPM

        if enemy_x < 0:
            enemy.body.position.x = 0 / PPM
        if enemy_x > SCREEN_WIDTH - enemy.width:
            enemy.body.position.x = (SCREEN_WIDTH - enemy.width) / PPM
        if enemy_y < 0:
            enemy.body.position.y = 0 / PPM
        if enemy_y > SCREEN_HEIGHT - enemy.height:
            enemy.body.position.y = (SCREEN_HEIGHT - enemy.height) / PPM

    # Check for collisions between player and enemies
    for enemy in enemies[:]:
        if enemy.is_destroyed:
            continue
        # Get the player's AABB
        player_fixture = player.body.fixtures[0]
        player_aabb = player_fixture.GetAABB(0)

        # Get the enemy's AABB
        enemy_fixture = enemy.body.fixtures[0]
        enemy_aabb = enemy_fixture.GetAABB(0)

        # Check for overlap
        if (player_aabb.lowerBound.x < enemy_aabb.upperBound.x and  # player left < enemy right
            player_aabb.upperBound.x > enemy_aabb.lowerBound.x and  # player right > enemy left
            player_aabb.lowerBound.y < enemy_aabb.upperBound.y and  # player bottom < enemy top
            player_aabb.upperBound.y > enemy_aabb.lowerBound.y):    # player top > enemy bottom
            if not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = pygame.time.get_ticks() + 1000  # 1 second

            # Bounce the enemy back
            enemy.body.position.y -= 60 / PPM  # Move enemy up slightly
            enemy.body.position.x += enemy.direction * 20 / PPM

    for bullet in player.bullets[:]:
        # Check if the bullet is off-screen
        bullet_x = bullet.body.position.x * PPM
        if bullet_x < 0 or bullet_x > SCREEN_WIDTH:
            player.bullets.remove(bullet)
            world.DestroyBody(bullet.body)  # Clean up the Box2D body
        elif bullet.landed and pygame.time.get_ticks() - bullet.landed_time > 1000:
            player.bullets.remove(bullet)
            world.DestroyBody(bullet.body)
        else:
            for enemy in enemies[:]:
                if enemy.is_destroyed:
                    continue
                if enemy.body.fixtures:
                    # Check for bullet-enemy collisions
                    bullet_fixture = bullet.body.fixtures[0]
                    enemy_fixture = enemy.body.fixtures[0]

                    if bullet_fixture and enemy_fixture:  # Ensure the fixtures exist
                        bullet_aabb = bullet_fixture.GetAABB(0)
                        enemy_aabb = enemy_fixture.GetAABB(0)

                        if (bullet_aabb.lowerBound.x < enemy_aabb.upperBound.x and
                            bullet_aabb.upperBound.x > enemy_aabb.lowerBound.x and
                            bullet_aabb.lowerBound.y < enemy_aabb.upperBound.y and
                            bullet_aabb.upperBound.y > enemy_aabb.lowerBound.y):
                            enemy.destroy()
                            player.bullets.remove(bullet)
                            world.DestroyBody(bullet.body)
                            enemies.remove(enemy)
                            break  # Stop checking for this bullet

    for enemy in enemies[:]:
        
        for bullet in enemy.bullets[:]:
            # Check if the bullet is off-screen
            bullet_x = bullet.body.position.x * PPM
            if bullet_x < 0 or bullet_x > SCREEN_WIDTH:
                enemy.bullets.remove(bullet)
                world.DestroyBody(bullet.body)  # Clean up the Box2D body
            elif bullet.landed and pygame.time.get_ticks() - bullet.landed_time > 1000:
                enemy.bullets.remove(bullet)
                world.DestroyBody(bullet.body)
            else:
                if player.body.fixtures:
                    # Check for bullet-enemy collisions
                    bullet_fixture = bullet.body.fixtures[0]
                    player_fixture = player.body.fixtures[0]

                    if bullet_fixture and player_fixture:  # Ensure the fixtures exist
                        bullet_aabb = bullet_fixture.GetAABB(0)
                        player_aabb = player_fixture.GetAABB(0)

                        if (bullet_aabb.lowerBound.x < player_aabb.upperBound.x and
                            bullet_aabb.upperBound.x > player_aabb.lowerBound.x and
                            bullet_aabb.lowerBound.y < player_aabb.upperBound.y and
                            bullet_aabb.upperBound.y > player_aabb.lowerBound.y):
                            enemy.bullets.remove(bullet)
                            world.DestroyBody(bullet.body)
                            break  # Stop checking for this bullet

def draw_game(camera):
    screen.blit(background_texture, (0, 0))
    screen.blit(main_bg, (main_bg_position[0] + camera.camera.x, main_bg_position[1]))
    for decoration in current_section["decorations"]:
        screen.blit(decoration["image"], (decoration["position"][0] + camera.camera.x, decoration["position"][1]))
    pygame.draw.rect(screen, (0, 78, 152), visual_water)

    for platform in platforms:
        platform.draw(screen, camera)
        #draw_aabb(screen, camera, platform.body, platform.width, platform.height, (255, 0, 0))

    for enemy in enemies:
        if not enemy.is_destroyed:
            enemy.draw(screen, camera)
        #draw_aabb(screen, camera, enemy.body, platform.width, platform.height, (255, 0, 0))

    player.draw(screen, camera)
    draw_aabb(screen, camera, player.body, player.width, player.height, (0, 255, 0))

    for bullet in player.bullets:
        bullet.update()
        bullet.draw(screen, camera)

    draw_health()
    font = pygame.font.Font(None, 36)
    level_text = font.render(f"Level: {current_level + 1}/3", True, BLACK)
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
    
    # Draw game state messages
    if game_state == "game_won":
        draw_message("You Win! Press ENTER to restart", 48, GREEN)
    elif game_state == "game_over":
        draw_message("Game Over - Press ENTER to restart", 48, RED)
    draw_fixtures(screen, camera)

def draw_message(text, size, color):
    """Draw a centered message on the screen"""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text_surface, text_rect)

def draw_aabb(screen, camera, body, width, height, color):
    """
    Draw a box around a Box2D body.
    """
    # Convert Box2D position to screen coordinates
    x = body.position.x * PPM - width / 2 + camera.camera.x
    y = body.position.y * PPM - height / 2

    # Draw the rectangle
    pygame.draw.rect(screen, color, (x, y, width, height), 2)  # 2 is the line thickness

def draw_health():
    # Draw health text
    font = pygame.font.Font(None, 30)  # Create font object (size 30)
    health_text = font.render("Player Health:", True, BLACK)
    screen.blit(health_text, (10, 10))

    # Draw red circles (hearts)
    for i in range(player.health):
        pygame.draw.circle(screen, RED, (165 + i * 30, 20), 10)  # Spaced out

def draw_fixtures(screen, camera):
    """Draw AABBs for all fixtures in the world."""
    for body in world.bodies:
        for fixture in body.fixtures:
            aabb = fixture.GetAABB(0)
            lower_bound = aabb.lowerBound * PPM
            upper_bound = aabb.upperBound * PPM

            # Convert Box2D coordinates to screen coordinates
            x = lower_bound.x + camera.camera.x
            y = lower_bound.y
            width = upper_bound.x - lower_bound.x
            height = upper_bound.y - lower_bound.y

            # Draw the AABB
            pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height), 2)

def main():
    initialize_game()

    running = True
    while running:
        running = handle_events()
        
        if game_state == "game_won" or game_state == "game_over":
            # Show end game screen
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                initialize_game()  # Restart game
        else:
            update_game()
        
        camera.update(player)
        draw_game(camera)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()