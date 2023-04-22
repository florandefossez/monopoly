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

        rect = pygame.Rect(10,10,0,0)
        for player in [self.game.myself, *self.game.players]:
            self.sidebar.blit(player.image, rect)
            money = self.font.render(f"{player.money} $", True, pygame.Color(0,0,0))
            self.sidebar.blit(money, rect.move(player.image.get_height(), 0))
            rect.move_ip(0,player.image.get_height())
        self.game.screen.blit(
            self.sidebar, (0, 0)
        )
