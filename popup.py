import pygame


class Popup:
    def __init__(self, game, text):
        self.game = game
        self.image = pygame.transform.scale(
            pygame.image.load("assets/popup.png"),
            (0.5 * game.height, 0.3 * game.height),
        )
        self.blit_text(text)

    def blit_text(self, text):
        margin = 0.1
        font = pygame.font.Font(None, 32)
        space = font.size(" ")[0]
        width, height = self.image.get_size()
        x = margin * width
        y = margin * height
        for word in text.split(" "):
            word_surface = font.render(word, True, pygame.Color(255, 255, 255))
            word_width, word_height = word_surface.get_size()
            if x + word_width >= width * (1 - margin):
                x = margin * width
                y += word_height
            self.image.blit(word_surface, (x, y))
            x += word_width + space

    def draw(self):
        self.game.screen.blit(
            self.image,
            (
                self.game.width - self.game.height / 2 - self.image.get_width() / 2,
                self.game.height / 2 - self.image.get_height() / 2,
            ),
        )
    
    def update(self):
        pass


class YesNoPopup(Popup):
    def __init__(self, game, text, resolve_yes, resolve_no):
        super().__init__(game, text)
        self.resolve_yes = resolve_yes
        self.resolve_no = resolve_no
        self.update()

    def update(self):
        width, height = self.image.get_size()
        length = width * 0.15
        yes = pygame.transform.scale(
            pygame.image.load("assets/valid.png"), (length, length)
        )
        no = pygame.transform.scale(
            pygame.image.load("assets/cancel.png"), (length, length)
        )
        self.image.blit(yes, (length, height - 1.2 * length))
        self.image.blit(no, (width - 2 * length, height - 1.2 * length))
        self.yesrect = yes.get_rect()
        self.yesrect.move_ip(
            length + self.game.width - self.game.height/2 - self.image.get_width() / 2,
            height - 1.2 * length + self.game.height / 2 - self.image.get_height() / 2,
        )
        self.norect = no.get_rect()
        self.norect.move_ip(
            self.game.width - self.game.height/2 - self.image.get_width() / 2 + width - 2 * length,
            self.game.height / 2 - self.image.get_height() / 2 + height - 1.2 * length,
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.yesrect.collidepoint(event.pos):
                self.resolve_yes()
                self.game.popups.remove(self)
            elif self.norect.collidepoint(event.pos):
                self.resolve_no()
                self.game.popups.remove(self)


class OkPopup(Popup):
    def __init__(self, game, text, resolve_ok=None):
        super().__init__(game, text)
        self.resolve_ok = resolve_ok
        self.update()

    def update(self):
        width, height = self.image.get_size()
        length = width * 0.15
        ok = pygame.transform.scale(
            pygame.image.load("assets/valid.png"), (length, length)
        )
        self.image.blit(ok, (width / 2 - length / 2, height - 1.2 * length))

        self.okrect = ok.get_rect()
        self.okrect.move_ip(
            self.game.width - self.game.height/2 - self.image.get_width() / 2 + width / 2 - length / 2,
            self.game.height / 2 - self.image.get_height() / 2 + height - 1.2 * length,
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.okrect.collidepoint(event.pos):
                if self.resolve_ok is not None:
                    self.resolve_ok()
                self.game.popups.remove(self)


class SelectPlayer(Popup):
    def __init__(self, game, text, resolve):
        super().__init__(game, text)
        self.resolve = resolve
        self.rects = []
        self.update()
    
    def update(self):
        width, height = self.image.get_size()
        length = width * 0.15

        for i, player in enumerate(self.game.players):
            p = pygame.transform.scale(
                pygame.image.load("assets/popup.png"), (length, length)
            )
            p.blit(pygame.font.Font(None, 32).render(player.address, True, pygame.Color(255, 255, 255)), (0,0))
            self.image.blit(p, (width - (i+1) * length, height - 1.2 * length))
            rect = p.get_rect()
            rect.move_ip(
                self.game.width - self.game.height/2 - self.image.get_width() / 2 + width - i * length,
                self.game.height / 2 - self.image.get_height() / 2 + height - 1.2 * length,
            )
            self.rects.append(rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect in self.rects:
                if rect.collidepoint(event.pos):
                    self.resolve(self.game.players[self.rects.index(rect)])
                    self.game.popups.remove(self)
