import pygame
from box import Box
from deal import Deal
from popup import OkPopup, YesNoPopup


class Sidebar:
    def __init__(self, game):
        self.game = game
        self.update()

    def update(self):
        # background
        self.sidebar = pygame.Surface(
            (self.game.width - self.game.height, self.game.height),
        )
        self.sidebar.fill(pygame.Color(218, 233, 212))

        # deal
        self.deal_rect = pygame.Rect(
            (self.game.width - self.game.height) / 2 - 25, self.game.height - 20, 50, 15
        )

        # title
        self.title = pygame.font.SysFont("widelatin", self.game.height//20).render(f"MONOPOLY", True, pygame.Color(0,0,0))
        self.titleRect = pygame.Rect(max((self.game.width - self.game.height)/2 - self.title.get_width()/2,0), self.game.height/30,0,0)

        # players
        self.font = pygame.font.SysFont("calibri", self.game.height//20)
    
    def draw(self):
        # background
        self.game.screen.blit(self.sidebar, (0,0))
        # left bar
        pygame.draw.rect(self.game.screen, pygame.Color(0,0,0), pygame.Rect(0.99*self.game.width - self.game.height, 0, 0.012*self.game.width, self.game.height))
        # title
        self.game.screen.blit(self.title, self.titleRect)

        # player money
        draw_bar = len(self.game.players)
        l = self.game.myself.image.get_height()
        rect = pygame.Rect((self.game.width - self.game.height)/2 - 3.5*l, self.game.height//10, 7*l, self.game.height/200)
        for player in [self.game.myself, *self.game.players]:
            self.game.screen.blit(player.green_image if player.his_turn else player.image, rect.move(0.5*l,0))
            money = self.font.render(
                f"{player.money} $", True, pygame.Color(31,165,76) if player.his_turn else pygame.Color(0, 0, 0)
            )
            self.game.screen.blit(money, rect.move(6.5*l - money.get_width(), 0))
            rect.move_ip(0, 1.05*l)
            if draw_bar:
                pygame.draw.rect(self.game.screen, pygame.Color(0, 0, 0), rect)
                rect.move_ip(0, 0.2*l)
                draw_bar -= 1

        # deal button
        s = pygame.Surface(self.deal_rect.size)
        s.fill(pygame.Color(0, 0, 0))
        self.game.screen.blit(s, self.deal_rect)

    
    def handle_event(self, event):
        if not event.type == pygame.MOUSEBUTTONDOWN:
            return
        if self.deal_rect.collidepoint(event.pos) and self.game.players and self.game.myself.his_turn:
            self.game.popups.append(Deal(self.game))
        elif not self.game.myself.his_turn:
            self.game.popups.append(OkPopup(self.game, "Attendez votre tour pour émettre une proposition d'échange."))

