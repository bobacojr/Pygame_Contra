import pygame

class Platform:
    def __init__(self, x, y, width, height, texture, kind=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.kind = kind

        self.animations = {}
        self.current_animation = "default"
        self.current_image = 0
        self.animation_frame = 0
        self.animation_speed = 8

        self.add_animation("default", texture)

    def add_animation(self, state, images):
        """Add an animation sequence for a specific state."""
        self.animations[state] = [pygame.image.load(img) for img in images]
        self.animations[state] = [pygame.transform.scale(frame, (self.rect.width, self.rect.height)) for frame in self.animations[state]]

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

    def draw(self, screen):
        """Draw the platform with the current animation frame."""
        current_frame = self.animations[self.current_animation][self.current_image]
        screen.blit(current_frame, self.rect.topleft)