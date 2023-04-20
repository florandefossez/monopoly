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
            ((self.game.width - self.game.height) / 2, self.game.height),
        )
        self.sidebar.fill(pygame.Color(200, 0, 200))
        # i = 0
        # for box in Box.boxes:
        #     if hasattr(box, 'player') and box.player == self.game.myself:
        #         i += 1
        #         box_text = self.font.render(box.name, True, pygame.Color(255, 255, 255))
        #         self.sidebar.blit(box_text, (10, 50 + 20*i))

        word_surface = self.font.render(f"{self.game.myself.money} $", True, pygame.Color(255, 255, 255))
        self.sidebar.blit(word_surface, (10, 10))
        self.game.screen.blit(
            self.sidebar, (0, 0)
        )
