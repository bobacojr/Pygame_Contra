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

player = Player(60, 500, 80, 100, 7, 5)
player.add_animation("idle_left", ["images/IdleLeft/IdleLeft_1.gif", "images/IdleLeft/IdleLeft_2.gif"])
player.add_animation("idle_right", ["images/IdleRight/IdleRight_1.gif", "images/IdleRight/IdleRight_2.gif"])
player.add_animation("walk_left", ["images/WalkLeft/WalkLeft_1.gif", "images/WalkLeft/WalkLeft_2.gif", "images/WalkLeft/WalkLeft_3.gif"])
player.add_animation("walk_right", ["images/WalkRight/WalkRight_1.gif", "images/WalkRight/WalkRight_2.gif", "images/walkRight/WalkRight_3.gif"])
player.add_animation("roll_left", ["images/RollLeft/RollLeft_1.gif", "images/RollLeft/RollLeft_2.gif", "images/RollLeft/RollLeft_3.gif", "images/RollLeft/RollLeft_4.gif"])
player.add_animation("roll_right", ["images/RollRight/RollRight_1.gif", "images/RollRight/RollRight_2.gif", "images/RollRight/RollRight_3.gif", "images/RollRight/RollRight_4.gif"])
player.add_animation("sprint_right", ["images/RunRight/RunRight_1.gif", "images/RunRight/RunRight_2.gif", "images/RunRight/RunRight_3.gif", "images/RunRight/RunRight_4.gif", "images/RunRight/RunRight_5.gif", "images/RunRight/RunRight_6.gif", ])
player.add_animation("sprint_left", ["images/RunLeft/RunLeft_1.gif", "images/RunLeft/RunLeft_2.gif", "images/RunLeft/RunLeft_3.gif", "images/RunLeft/RunLeft_4.gif", "images/RunLeft/RunLeft_5.gif", "images/RunLeft/RunLeft_6.gif", ])
player.add_animation("prone_left", ["images/ProneLeft/ProneLeft.gif"])
player.add_animation("prone_right", ["images/ProneRight/ProneRight.gif"])

# Platforms
platforms = [
    Platform(0, 600, SCREEN_WIDTH, 20, BLACK, "floor"),  # Ground platform
    Platform(200, 500, 200, 20, BLACK),  # Raised platform
    Platform(400, 400, 200, 20, BLACK),  # Another raised platform
    Platform(800, 200, 10, 600, BLACK),  # Tall platform
]

enemies = [
    Enemy(300, 300, 40, 80, GREEN, 2),
    Enemy(700, 400, 40, 80, GREEN, 2),
    Enemy(250, 400, 40, 80, GREEN, 0)
]

def draw_health():
    # Draw health text
    font = pygame.font.Font(None, 30)  # Create font object (size 30)
    health_text = font.render("Player Health:", True, BLACK)
    screen.blit(health_text, (10, 10))

    # Draw red circles (hearts)
    for i in range(player.health):
        pygame.draw.circle(screen, RED, (165 + i * 30, 20), 10)  # Spaced out


# Game loop
running = True
while running:
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

    player.move(dx)

    if player.rect.left < 0:
        player.rect.left = 0
    if player.rect.right > SCREEN_WIDTH:
        player.rect.right = SCREEN_WIDTH

    player.update(platforms)
    player.draw(screen)
    pygame.display.flip()

    for enemy in enemies[:]:
        if player.rect.colliderect(enemy.rect):
            if not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = pygame.time.get_ticks() + 1000  # 1 second

            # Bounce the enemy back
            enemy.rect.y -= 30  # Move enemy up slightly
            enemy.rect.x += enemy.direction * 20  # Move enemy away from player

            if player.health <= 0:
                print("Game Over")
                running = False

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

    screen.fill(WHITE)
    for enemy in enemies:
        enemy.update(platforms)

    for platform in platforms:
        pygame.draw.rect(screen, platform.color, platform)

    player.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)
    for bullet in player.bullets:
        bullet.draw(screen)

    draw_health()

    if not enemies:
        print("You Win!")
        pygame.quit()
        sys.exit()


    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()