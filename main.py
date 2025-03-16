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
    Platform(0, 600, SCREEN_WIDTH, 20, BLACK),  # Ground platform
    Platform(200, 500, 200, 20, BLACK),  # Raised platform
    Platform(400, 400, 200, 20, BLACK),  # Another raised platform
    Platform(800, 200, 10, 600, BLACK),  # Tall platform
]

enemies = [
    Enemy(300, 550, 40, 40, GREEN, 3),
    Enemy(700, 300, 40, 40, GREEN, 2)
]

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

# Update enemies (before screen.fill())
    for enemy in enemies:
        enemy.update(platforms)

    screen.fill(WHITE)
    for platform in platforms:
        pygame.draw.rect(screen, platform.color, platform)

    player.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)
    for bullet in player.bullets:
        bullet.draw(screen)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()