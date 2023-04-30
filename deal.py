import pygame
from inputText import InputText
from inputProperty import InputProperty

class Deal:
    def __init__(self, game):
        self.game = game
        self.inputOffererMoney = InputText(self.game, None, pygame.Color(195,195,195), True)
        self.inputOffererMoney.text = '0'
        self.inputRecipientMoney = InputText(self.game, None, pygame.Color(195,195,195), True)
        self.inputRecipientMoney.text = '0'

        self.inputOffererProperty = InputProperty(self.game, self.game.myself)
        self.recipient = 0
        self.inputRecipientProperty = InputProperty(self.game, self.game.players[self.recipient])
        self.update()
    

    def update(self):
        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/deal.png"),
            (0.69 * self.game.height, 0.5 * self.game.height)
        )
        self.closeRect = pygame.Rect(
            self.game.width - 0.843 * self.game.height,
            0.5 * self.game.height - 0.25 * self.game.height,
            0.05 * self.game.height,
            0.05 * self.game.height
        )
        self.dealRect = pygame.Rect(
            self.game.width - 0.565 * self.game.height,
            0.68 * self.game.height,
            0.13 * self.game.height,
            0.06 * self.game.height
        )
        self.recipientRect = pygame.Rect(
            self.game.width - 0.3554 * self.game.height,
            0.292 * self.game.height,
            0.052 * self.game.height,
            0.052 * self.game.height
        )

        self.inputOffererMoney.update(pygame.Rect(
            self.game.width - 0.843 * self.game.height + 0.69 * self.game.height/2/6,
            0.292 * self.game.height + 0.15*0.5 * self.game.height,
            0.15 * self.game.height,
            0.052 * self.game.height
        ))
        self.inputRecipientMoney.update(pygame.Rect(
            self.game.width - 0.843 * self.game.height + 0.69 * self.game.height/2/6 + 0.69 * self.game.height/2,
            0.292 * self.game.height + 0.15*0.5 * self.game.height,
            0.15 * self.game.height,
            0.052 * self.game.height
        ))

        self.inputOffererProperty.update(pygame.Rect(
            self.game.width - 0.843 * self.game.height + 0.69 * self.game.height/2/6,
            0.292 * self.game.height + 0.30*0.5 * self.game.height,
            3*0.69/10*self.game.height,
            3*0.69/10*4/3 * self.game.height
        ))
        self.inputRecipientProperty.update(pygame.Rect(
            self.game.width - 0.843 * self.game.height + 0.69 * self.game.height/2/6 + 0.69 * self.game.height/2,
            0.292 * self.game.height + 0.30*0.5 * self.game.height,
            3*0.69/10*self.game.height,
            3*0.69/10*4/3 * self.game.height
        ))

    def draw(self):
        # image
        self.game.screen.blit(
            self.image,
            self.closeRect
        )
        # offerer image
        self.game.screen.blit(
            self.game.myself.image,
            self.recipientRect.move(- 1.37*self.game.height/4, 0)
        )
        # recipient image
        self.game.screen.blit(
            self.game.players[self.recipient].image,
            self.recipientRect
        )
        # money
        self.inputOffererMoney.draw()
        self.inputRecipientMoney.draw()
        # property
        self.inputOffererProperty.draw()
        self.inputRecipientProperty.draw()


        # close = pygame.Surface(self.dealRect.size)
        # close.fill(pygame.Color(50,50,50,10))
        # self.game.screen.blit(close, self.dealRect)
    
    def handle_event(self, event):
        self.inputOffererMoney.handle_event(event)
        self.inputRecipientMoney.handle_event(event)
        self.inputOffererProperty.handle_event(event)
        self.inputRecipientProperty.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.recipientRect.collidepoint(event.pos):
                self.recipient = (self.recipient + 1)%len(self.game.players)
                self.inputRecipientProperty = InputProperty(self.game, self.game.players[self.recipient])
                self.update()
            if self.closeRect.collidepoint(event.pos):
                self.game.popups.remove(self)
            if self.dealRect.collidepoint(event.pos):
                self.game.popups.remove(self)
                self.send()
    
    def send(self):
        deal = {
            "type": "deal",
            "offerer": self.game.myself.name,
            "recipient": self.game.players[self.recipient].name,
            "offer": {
                "money": self.inputOffererMoney.get_value(),
                "property": self.inputOffererProperty.get_value()
            },
            "request": {
                "money": self.inputRecipientMoney.get_value(),
                "property": self.inputRecipientProperty.get_value()
            }
        }
        print(deal)
        self.game.socket_manager.send_deal(deal)
