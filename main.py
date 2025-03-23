import pygame
import sys
from player import Player
from platforms import Platform
from settings import *
from enemy import Enemy

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
background_texture = pygame.image.load("images/Background.gif")
background_texture = pygame.transform.scale(background_texture, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Player
player = Player(60, 300, 80, 100, 7, 4)
player.add_animation("idle_left", ["images/Player/IdleLeft/IdleLeft_1.gif", "images/Player/IdleLeft/IdleLeft_2.gif"])
player.add_animation("idle_right", ["images/Player/IdleRight/IdleRight_1.gif", "images/Player/IdleRight/IdleRight_2.gif"])
player.add_animation("walk_left", ["images/Player/WalkLeft/WalkLeft_1.gif", "images/Player/WalkLeft/WalkLeft_2.gif", "images/Player/WalkLeft/WalkLeft_3.gif"])
player.add_animation("walk_right", ["images/Player/WalkRight/WalkRight_1.gif", "images/Player/WalkRight/WalkRight_2.gif", "images/Player/walkRight/WalkRight_3.gif"])
player.add_animation("roll_left", ["images/Player/RollLeft/RollLeft_1.gif", "images/Player/RollLeft/RollLeft_2.gif", "images/Player/RollLeft/RollLeft_3.gif", "images/Player/RollLeft/RollLeft_4.gif"])
player.add_animation("roll_right", ["images/Player/RollRight/RollRight_1.gif", "images/Player/RollRight/RollRight_2.gif", "images/Player/RollRight/RollRight_3.gif", "images/Player/RollRight/RollRight_4.gif"])
player.add_animation("sprint_right", ["images/Player/RunRight/RunRight_1.gif", "images/Player/RunRight/RunRight_2.gif", "images/Player/RunRight/RunRight_3.gif", "images/Player/RunRight/RunRight_4.gif", "images/Player/RunRight/RunRight_5.gif", "images/Player/RunRight/RunRight_6.gif", ])
player.add_animation("sprint_left", ["images/Player/RunLeft/RunLeft_1.gif", "images/Player/RunLeft/RunLeft_2.gif", "images/Player/RunLeft/RunLeft_3.gif", "images/Player/RunLeft/RunLeft_4.gif", "images/Player/RunLeft/RunLeft_5.gif", "images/Player/RunLeft/RunLeft_6.gif", ])
player.add_animation("prone_left", ["images/Player/ProneLeft/ProneLeft.gif"])
player.add_animation("prone_right", ["images/Player/ProneRight/ProneRight.gif"])
player.add_animation("water_left", ["images/Player/WaterMovement/WaterLeft.gif"])
player.add_animation("water_right", ["images/Player/WaterMovement/WaterRight.gif"])

# Platforms
platforms = [
    Platform(0, 400, SCREEN_WIDTH, 261, ["images/Platforms/MainPlatform/MainPlatform1.gif", "images/Platforms/MainPlatform/MainPlatform2.gif"]),  # Ground platform
    Platform(248, 480, 200, 158, ['images/200x158yPlatform.png']),
    Platform(-12, 636, 200, 51, ["images/Platforms/SmallGrass/SmallGrass1.gif", "images/Platforms/SmallGrass/SmallGrass2.gif"]),
]

# Decorations
MainPlatformFlora = pygame.image.load("images/Platforms/MainPlatform/MainPlatformFlora.gif")
MainPlatformFlora_position = (0, 266)

visual_water_y = 660
visual_water_height = SCREEN_HEIGHT - visual_water_y
visual_water = pygame.Rect(0, visual_water_y, SCREEN_WIDTH, visual_water_height)

logical_water_y = 700
logical_water_height = SCREEN_HEIGHT - logical_water_y
logical_water = pygame.Rect(0, logical_water_y, SCREEN_WIDTH, logical_water_height)


# Enemies
enemies = [
    Enemy(300, 300, 80, 100, GREEN, 2),
    Enemy(700, 400, 40, 80, GREEN, 2),
    Enemy(250, 400, 40, 80, GREEN, 2)
]

for enemy in enemies:
    enemy.add_animation("walk_right", ["images/Enemies/WalkRight/WalkRight1.gif", "images/Enemies/WalkRight/WalkRight2.gif", "images/Enemies/WalkRight/WalkRight3.gif"])
    enemy.add_animation("walk_left", ["images/Enemies/WalkLeft/WalkLeft1.gif", "images/Enemies/WalkLeft/WalkLeft2.gif", "images/Enemies/WalkLeft/WalkLeft3.gif"])

def draw_health():
    # Draw health text
    font = pygame.font.Font(None, 30)  # Create font object (size 30)
    health_text = font.render("Player Health:", True, WHITE)
    screen.blit(health_text, (10, 10))

    # Draw red circles (hearts)
    for i in range(player.health):
        pygame.draw.circle(screen, RED, (165 + i * 30, 20), 10)  # Spaced out

# Game loop
running = True
while running:
    # Calculate delta time in seconds
    delta_time = clock.tick(60) / 1000.0  # Convert milliseconds to seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_s:
                player.fall()
            if event.key == pygame.K_k:
                player.shoot()

    # Horizontal movement events
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_a]:
        dx = -1
    if keys[pygame.K_d]:
        dx = 1

    player.is_sprinting = keys[pygame.K_LSHIFT]
    player.is_prone = keys[pygame.K_LCTRL]
    player.move(dx, delta_time)

    if player.rect.left < 0:
        player.rect.left = 0
    if player.rect.right > SCREEN_WIDTH:
        player.rect.right = SCREEN_WIDTH

    player.update(platforms, logical_water, delta_time)

    for platform in platforms:
        platform.update(delta_time)

    for enemy in enemies:
        enemy.update(platforms, delta_time)

    for enemy in enemies[:]:
        if player.rect.colliderect(enemy.rect):
            if not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = pygame.time.get_ticks() + 1000  # 1 second

            # Bounce the enemy back
            enemy.rect.y -= 30  # Move enemy up slightly
            enemy.rect.x += enemy.direction * 20  # Move enemy away from player

            #if player.health <= 0:
               #print("Game Over")
                #running = False

    for bullet in player.bullets[:]:
        bullet.update()
        if (bullet.rect.right < 0 or
                bullet.rect.left > SCREEN_WIDTH or
                bullet.rect.bottom < 0 or
                bullet.rect.top > SCREEN_HEIGHT):
            player.bullets.remove(bullet)
        else:
            # Check bullet-enemy collisions
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemies.remove(enemy)
                    player.bullets.remove(bullet)
                    break

    screen.blit(background_texture, (0, 0))
    screen.blit(MainPlatformFlora, MainPlatformFlora_position)

    pygame.draw.rect(screen, (0, 78, 152), visual_water)

    for platform in platforms:
        platform.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

    player.draw(screen)

    for bullet in player.bullets:
        bullet.draw(screen)

    draw_health()

    if not enemies:
        print("You Win!")
        pygame.quit()
        sys.exit()

    pygame.display.update()

pygame.quit()
sys.exit()