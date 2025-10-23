import pygame

BLACK = (0, 0, 0)

class Square(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()

        self.color = color
        # create a surface for the square
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)  # transparent

        # rectangle on the surface
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        # define the rectangle area for positioning and collisions
        self.rect = self.image.get_rect()