import pygame
from box import Box
from deal import Deal


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

        # deal & abandon
        self.deal_rect = pygame.Rect(
            0.06 * self.game.height,
            0.90 * self.game.height,
            0.13 * self.game.height,
            0.06 * self.game.height,
        )
        self.abandon_rect = self.deal_rect.move(0.2 * self.game.height, 0)
        self.deal = pygame.transform.smoothscale(
            pygame.image.load("assets/deal_button.png"), self.deal_rect.size
        )
        self.abandon = pygame.transform.smoothscale(
            pygame.image.load("assets/abandon.png"), self.deal_rect.size
        )

        # title
        self.title = pygame.font.SysFont("widelatin", self.game.height // 20).render(
            f"MONOPOLY", True, pygame.Color(0, 0, 0)
        )
        self.titleRect = pygame.Rect(
            max(
                (self.game.width - self.game.height) / 2 - self.title.get_width() / 2, 0
            ),
            self.game.height / 30,
            0,
            0,
        )

        # players money font
        self.font = pygame.font.SysFont("calibri", self.game.height // 20)

        # get out of jail
        self.get_out_of_jail_rect = pygame.Rect(
            2/3*(self.game.width - self.game.height),
            -2/9*self.game.width + 11/9*self.game.height,
            1/4*(self.game.width - self.game.height),
            1/6*(self.game.width - self.game.height)
        )
        self.get_out_of_jail = pygame.transform.smoothscale(
            pygame.image.load("assets/get_out_of_jail.png"),
            self.get_out_of_jail_rect.size
        )

    def draw(self):
        # background
        self.game.screen.blit(self.sidebar, (0, 0))
        # left bar
        pygame.draw.rect(
            self.game.screen,
            pygame.Color(0, 0, 0),
            pygame.Rect(
                0.99 * self.game.width - self.game.height,
                0,
                0.012 * self.game.width,
                self.game.height,
            ),
        )
        # title
        self.game.screen.blit(self.title, self.titleRect)

        # player money
        draw_bar = len(self.game.players)
        l = self.game.myself.image.get_height()
        rect = pygame.Rect(
            (self.game.width - self.game.height) / 2 - 3.5 * l,
            self.game.height // 10,
            7 * l,
            self.game.height / 200,
        )
        for player in [self.game.myself, *self.game.players]:
            if player.his_turn:
                self.game.screen.blit(player.green_image, rect.move(0.5 * l, 0))
            elif player.position is None:
                self.game.screen.blit(player.red_image, rect.move(0.5 * l, 0))
            else:
                self.game.screen.blit(player.image, rect.move(0.5 * l, 0))
            money = self.font.render(
                f"{player.money} $",
                True,
                pygame.Color(31, 165, 76) if player.his_turn else pygame.Color(0, 0, 0),
            )
            self.game.screen.blit(money, rect.move(6.5 * l - money.get_width(), 0))
            rect.move_ip(0, 1.05 * l)
            if draw_bar:
                pygame.draw.rect(self.game.screen, pygame.Color(0, 0, 0), rect)
                rect.move_ip(0, 0.2 * l)
                draw_bar -= 1

        self.game.bill.draw(rect)

        # deal button
        self.game.screen.blit(self.deal, self.deal_rect)
        self.game.screen.blit(self.abandon, self.abandon_rect)

        # jet out of jail
        if self.game.myself.get_out_of_prison_card:
            self.game.screen.blit(self.get_out_of_jail, self.get_out_of_jail_rect)

        self.game.screen.blit(self.font.render(str(self.game.parc), True, "black"), (0,0))

    def handle_event(self, event):
        if not event.type == pygame.MOUSEBUTTONDOWN:
            return
        if self.deal_rect.collidepoint(event.pos) and self.game.players:
            if self.game.myself.his_turn:
                self.game.popups.append(Deal(self.game))
            else:
                self.game.okpopup(
                    "Attendez votre tour pour émettre une proposition d'échange."
                )
        if self.abandon_rect.collidepoint(event.pos):
            self.game.yesnopopup(
                "Etes-vous sûr de vouloir abodonner la partie ?",
                resolve_no=lambda: None,
                resolve_yes=self.game.end,
            )
