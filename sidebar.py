import pygame
from box import Box


class Sidebar():
    def __init__(self, game):
        self.game = game
        self.update()
    
    def update(self):
        self.font = pygame.font.Font(None, 32)
    
    def draw(self):
        self.sidebar = pygame.Surface(
            (self.game.width - self.game.height, self.game.height),
        )
        self.sidebar.fill(pygame.Color(218, 233, 212))

        word_surface = self.font.render(f"{self.game.myself.money} $", True, pygame.Color(0,0,0))
        self.sidebar.blit(word_surface, (10, 10))
        self.game.screen.blit(
            self.sidebar, (0, 0)
        )
