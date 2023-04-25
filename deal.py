import pygame


class Deal:
    def __init__(self, game):
        self.game = game
        self.update()
    

    def update(self):
        self.window = pygame.image.load("assets/deal.png")
    

    def draw(self):
        self.game.screen.blit(
            self.window,
            (
                self.game.width - self.game.height / 2 - self.window.get_width() / 2,
                self.game.height / 2 - self.window.get_height() / 2,
            ),
        )
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # if self.okrect.collidepoint(event.pos):
            #     if self.resolve_ok is not None:
            #         self.resolve_ok()
            self.game.popups.remove(self)



