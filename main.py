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
player = Player(60, 500, 40, 40, RED, 5)

# Platforms
platforms = [
    Platform(0, 600, SCREEN_WIDTH, 20, BLACK, "floor"),  # Ground platform
    Platform(200, 500, 200, 20, BLACK),  # Raised platform
    Platform(400, 400, 200, 20, BLACK),  # Another raised platform
    Platform(800, 200, 10, 600, BLACK),  # Tall platform
]

enemies = [
    Enemy(300, 550, 40, 40, GREEN, 2),
    Enemy(700, 300, 40, 40, GREEN, 2)
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
    if keys[pygame.K_a]:
        player.move(-1)
    if keys[pygame.K_d]:
        player.move(1)

    if player.rect.left < 0:
        player.rect.left = 0
    if player.rect.right > SCREEN_WIDTH:
        player.rect.right = SCREEN_WIDTH

    player.update(platforms)

    for enemy in enemies[:]:
        if player.rect.colliderect(enemy.rect):
            if not player.invincible:
                player.health -= 1
                player.invincible = True
                player.invincibility_timer = pygame.time.get_ticks() + 1000  # 1 second

            # Bounce the enemy back
            enemy.direction *= -1  # Reverse direction
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

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()