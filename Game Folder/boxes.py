import pygame

YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

class Box(pygame.sprite.Sprite):
    def __init__(self, area, width, height):
        super().__init__()

        # create a surface for the box
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)  # transparent
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def drawOutline(self, screen):
        pygame.draw.rect(self.image, YELLOW, self.image.get_rect(), 5)  #d raw a yellow outline
        screen.blit(self.image, self.rect.topleft)  