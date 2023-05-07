import pygame
from inputText import InputText
from card import Card
from box import Box


class ReceiveDeal:
    def __init__(self, game, deal):
        self.game = game
        self.deal = deal
        self.offerer = [p for p in self.game.players if p.name == deal["offerer"]][0]
        self.update()

    def update(self):
        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/popup.png"),
            (0.69 * self.game.height, 0.5 * self.game.height),
        )
        self.closeRect = pygame.Rect(
            self.game.width - 0.843 * self.game.height,
            0.25 * self.game.height,
            0.05 * self.game.height,
            0.05 * self.game.height,
        )
        self.norect = pygame.Rect(
            0.135 * self.game.height,
            0.4625 * self.game.height,
            0.075 * self.game.height,
            0.075 * self.game.height,
        ).move(*self.closeRect.topleft)
        self.no = pygame.transform.smoothscale(
            pygame.image.load("assets/cancel.png"), self.norect.size
        )
        self.yesrect = pygame.Rect(
            0.48 * self.game.height,
            0.4625 * self.game.height,
            0.075 * self.game.height,
            0.075 * self.game.height,
        ).move(*self.closeRect.topleft)
        self.yes = pygame.transform.smoothscale(
            pygame.image.load("assets/valid.png"), self.yesrect.size
        )

        self.recipientRect = pygame.Rect(
            self.game.width - 0.3554 * self.game.height,
            0.292 * self.game.height,
            0.052 * self.game.height,
            0.052 * self.game.height,
        )

        font = pygame.font.Font(None, int(self.game.height / 10))
        self.inputOffererMoney = font.render(
            str(self.deal["offer"]["money"]) + " $", True, pygame.color.Color(0, 0, 0)
        )
        self.inputRecipientMoney = font.render(
            str(self.deal["request"]["money"]) + " $", True, pygame.color.Color(0, 0, 0)
        )

        self.inputOffererPropertyRect = pygame.Rect(
            self.game.width - 0.7855 * self.game.height,
            0.442 * self.game.height,
            0.207 * self.game.height,
            0.276 * self.game.height,
        )
        self.inputRecipientPropertyRect = pygame.Rect(
            self.game.width - 0.4405 * self.game.height,
            0.442 * self.game.height,
            0.207 * self.game.height,
            0.276 * self.game.height,
        )

        if (i := self.deal["offer"]["property"]) is not None:
            self.inputOffererProperty = Card(self.game, Box.boxes[i], False).card
        else:
            self.inputOffererProperty = pygame.image.load("assets/card.png")
        self.inputOffererProperty = pygame.transform.smoothscale(
            self.inputOffererProperty, self.inputOffererPropertyRect.size
        )

        if (i := self.deal["request"]["property"]) is not None:
            self.inputRecipientProperty = Card(self.game, Box.boxes[i], False).card
        else:
            self.inputRecipientProperty = pygame.image.load("assets/card.png")
        self.inputRecipientProperty = pygame.transform.smoothscale(
            self.inputRecipientProperty, self.inputRecipientPropertyRect.size
        )

    def draw(self):
        # image
        self.game.screen.blit(self.image, self.closeRect)
        # offerer image
        self.game.screen.blit(
            self.offerer.image, self.recipientRect.move(-1.37 * self.game.height / 4, 0)
        )
        # recipient image
        self.game.screen.blit(self.game.myself.image, self.recipientRect)
        # money
        self.game.screen.blit(
            self.inputOffererMoney,
            (
                self.game.width - 0.7855 * self.game.height,
                0.367 * self.game.height,
            ),
        )
        self.game.screen.blit(
            self.inputRecipientMoney,
            (
                self.game.width - 0.4405 * self.game.height,
                0.367 * self.game.height,
            ),
        )
        # property
        self.game.screen.blit(self.inputOffererProperty, self.inputOffererPropertyRect)
        self.game.screen.blit(
            self.inputRecipientProperty, self.inputRecipientPropertyRect
        )

        # buttons
        self.game.screen.blit(self.yes, self.yesrect)
        self.game.screen.blit(self.no, self.norect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.norect.collidepoint(event.pos):
                self.game.popups.remove(self)
                self.game.socket_manager.send_private_msg(
                    f"{self.game.myself.name} a décliné votre offre !",
                    self.offerer.name,
                )

            if self.yesrect.collidepoint(event.pos):
                self.game.popups.remove(self)
                if self.deal["request"]["money"]:
                    self.game.myself.pay(
                        self.deal["request"]["money"], f"Deal with {self.offerer.name}"
                    )
                    self.offerer.earn(
                        self.deal["request"]["money"],
                        f"Deal with {self.game.myself.name}",
                    )
                if self.deal["offer"]["money"]:
                    self.game.myself.earn(
                        self.deal["offer"]["money"], f"Deal with {self.offerer.name}"
                    )
                    self.offerer.pay(
                        self.deal["offer"]["money"],
                        f"Deal with {self.game.myself.name}",
                    )

                self.game.socket_manager.send_player(self.game.myself)
                self.game.socket_manager.send_player(self.offerer)

                if self.deal["offer"]["property"]:
                    box = Box.boxes[self.deal["offer"]["property"]]
                    box.player = self.game.myself
                    self.game.socket_manager.send_box(box)

                if self.deal["request"]["property"]:
                    box = Box.boxes[self.deal["request"]["property"]]
                    box.player = self.offerer
                    self.game.socket_manager.send_box(box)

                self.game.socket_manager.send_private_msg(
                    f"{self.game.myself.name} a accepté votre offre !",
                    self.offerer.name,
                )
