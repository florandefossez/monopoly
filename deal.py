import pygame
from inputText import InputText
from inputProperty import InputProperty
from popup import OkPopup


class Deal:
    def __init__(self, game):
        self.game = game
        self.inputOffererMoney = InputText(
            self.game, None, pygame.Color(195, 195, 195), True
        )
        self.inputOffererMoney.text = ""
        self.inputRecipientMoney = InputText(
            self.game, None, pygame.Color(195, 195, 195), True
        )
        self.inputRecipientMoney.text = ""

        self.inputOffererProperty = InputProperty(self.game, self.game.myself)
        self.recipient = 0
        self.inputRecipientProperty = InputProperty(
            self.game, self.game.players[self.recipient]
        )
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
        self.close_image = pygame.transform.smoothscale(
            pygame.image.load("assets/close.png"), self.closeRect.size
        )

        self.dealRect = pygame.Rect(
            0.28 * self.game.height,
            0.47 * self.game.height,
            0.13 * self.game.height,
            0.06 * self.game.height,
        ).move(*self.closeRect.topleft)
        self.deal_image = pygame.transform.smoothscale(
            pygame.image.load("assets/deal_button.png"), self.dealRect.size
        )

        self.recipientRect = pygame.Rect(
            0.4915 * self.game.height,
            0.04 * self.game.height,
            0.052 * self.game.height,
            0.052 * self.game.height,
        ).move(*self.closeRect.topleft)

        self.inputOffererMoney.update(
            pygame.Rect(
                0.0975 * self.game.height,
                0.125 * self.game.height,
                0.15 * self.game.height,
                0.052 * self.game.height,
            ).move(*self.closeRect.topleft)
        )
        self.inputRecipientMoney.update(
            self.inputOffererMoney.rect.move(0.345 * self.game.height, 0)
        )

        self.inputOffererProperty.update(
            pygame.Rect(
                0.08625 * self.game.height,
                0.2 * self.game.height,
                0.1725 * self.game.height,
                0.23 * self.game.height,
            ).move(*self.closeRect.topleft)
        )
        self.inputRecipientProperty.update(
            self.inputOffererProperty.rect.move(0.345 * self.game.height, 0)
        )

    def draw(self):
        # image
        self.game.screen.blit(self.image, self.closeRect)
        # close
        self.game.screen.blit(self.close_image, self.closeRect)
        # offerer image
        self.game.screen.blit(
            self.game.myself.image,
            self.recipientRect.move(-0.345 * self.game.height, 0),
        )
        # recipient image
        self.game.screen.blit(
            self.game.players[self.recipient].image, self.recipientRect
        )
        pygame.draw.rect(
            self.game.screen,
            InputText.color_inactive,
            self.recipientRect.inflate(8, 8),
            2,
            5,
        )
        # money
        self.inputOffererMoney.draw()
        self.inputRecipientMoney.draw()
        # property
        self.inputOffererProperty.draw()
        self.inputRecipientProperty.draw()
        # deal_button
        self.game.screen.blit(self.deal_image, self.dealRect)

    def handle_event(self, event):
        self.inputOffererMoney.handle_event(event)
        self.inputRecipientMoney.handle_event(event)
        self.inputOffererProperty.handle_event(event)
        self.inputRecipientProperty.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.recipientRect.collidepoint(event.pos):
                self.recipient = (self.recipient + 1) % len(self.game.players)
                self.inputRecipientProperty = InputProperty(
                    self.game, self.game.players[self.recipient]
                )
                self.update()
            if self.closeRect.collidepoint(event.pos):
                self.game.popups.remove(self)
            if self.dealRect.collidepoint(event.pos):
                self.game.popups.remove(self)
                self.send()

    def send(self):
        if self.game.players[self.recipient].position is None:
            self.game.popups.append(OkPopup(self.game, f"{self.game.players[self.recipient].name} n'est plus joueur, vous ne pouvez pas le soumttre de proposition !"))
            return
        deal = {
            "type": "deal",
            "offerer": self.game.myself.name,
            "recipient": self.game.players[self.recipient].name,
            "offer": {
                "money": self.inputOffererMoney.get_value(),
                "property": self.inputOffererProperty.get_value(),
            },
            "request": {
                "money": self.inputRecipientMoney.get_value(),
                "property": self.inputRecipientProperty.get_value(),
            },
        }
        print(deal)
        self.game.socket_manager.send_deal(deal)
