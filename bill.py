import pygame


class Entrie:
    def __init__(self, amount, text, font, game):
        self.text = text
        self.amount = amount
        self.game = game
        self.update(font)

    def update(self, font):
        self.text_surface = font.render(self.text, True, "black")
        self.amount_surface = font.render(
            f"{self.amount} $",
            True,
            pygame.Color(31, 165, 76) if self.amount >= 0 else pygame.Color(227, 1, 15),
            pygame.Color(218, 233, 212),
        )

    def draw(self, rect):
        self.game.screen.blit(self.text_surface, rect)
        self.game.screen.blit(
            self.amount_surface, rect.move(-self.amount_surface.get_width(), 0).topright
        )


class Bill:
    def __init__(self, game):
        self.game = game
        self.l = 10
        self.bills = [None] * self.l
        self.last = self.l - 1
        self.update()

    def update(self):
        self.font = pygame.font.Font("assets/custom.otf", int(self.game.height // 35))
        self.rect = pygame.Rect(
            (self.game.width - self.game.height) / 4,
            0,
            (self.game.width - self.game.height) / 2,
            int(self.game.height // 35),
        )
        for i in range(self.l):
            if self.bills[i] is not None:
                self.bills[i].update(self.font)  # type: ignore

    def add(self, amount, text):
        self.last = (self.last + 1) % self.l
        self.bills[self.last] = Entrie(amount, text, self.font, self.game)  # type: ignore

    def draw(self, rect):
        i = 0
        while self.bills[(self.last - i) % self.l] is not None and i < self.l:
            self.bills[(self.last - i) % self.l].draw(self.rect.move(0, rect.y + (i + 2) * self.rect.h))  # type: ignore
            i += 1
