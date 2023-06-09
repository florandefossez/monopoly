import pygame


class Popup:
    def __init__(self, game, text):
        self.game = game
        self.text = text
        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/popup.png"),
            (0.5 * game.height, 0.3 * game.height),
        )
        self.font = pygame.font.Font("assets/custom.otf", 8 * self.game.height // 233)
        self.blit_text()

    def blit_text(self):
        margin = 0.1
        space = self.font.size(" ")[0]
        width, height = self.image.get_size()
        x = margin * width
        y = margin * height
        for word in self.text.split(" "):
            word_surface = self.font.render(word, True, pygame.Color(0, 0, 0))
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
        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/popup.png"),
            (0.5 * self.game.height, 0.3 * self.game.height),
        )
        self.font = pygame.font.Font("assets/custom.otf", 8 * self.game.height // 233)
        self.blit_text()


class YesNoPopup(Popup):
    def __init__(self, game, text, resolve_yes, resolve_no):
        super().__init__(game, text)
        self.resolve_yes = resolve_yes
        self.resolve_no = resolve_no
        self.update()

    def update(self):
        super().update()
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
            length
            + self.game.width
            - self.game.height / 2
            - self.image.get_width() / 2,
            height - 1.2 * length + self.game.height / 2 - self.image.get_height() / 2,
        )
        self.norect = no.get_rect()
        self.norect.move_ip(
            self.game.width
            - self.game.height / 2
            - self.image.get_width() / 2
            + width
            - 2 * length,
            self.game.height / 2 - self.image.get_height() / 2 + height - 1.2 * length,
        )

    def handle_event(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.yesrect.collidepoint(event.pos)
        ) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            self.resolve_yes()
            self.game.popups.remove(self)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.norect.collidepoint(
            event.pos
        ):
            self.resolve_no()
            self.game.popups.remove(self)


class OkPopup(Popup):
    def __init__(self, game, text, resolve_ok=None):
        super().__init__(game, text)
        self.resolve_ok = resolve_ok
        self.update()

    def update(self):
        super().update()
        width, height = self.image.get_size()
        length = width * 0.15
        ok = pygame.transform.scale(
            pygame.image.load("assets/valid.png"), (length, length)
        )
        self.image.blit(ok, (width / 2 - length / 2, height - 1.2 * length))

        self.okrect = ok.get_rect()
        self.okrect.move_ip(
            self.game.width
            - self.game.height / 2
            - self.image.get_width() / 2
            + width / 2
            - length / 2,
            self.game.height / 2 - self.image.get_height() / 2 + height - 1.2 * length,
        )

    def handle_event(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN and self.okrect.collidepoint(event.pos)
        ) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            if self.resolve_ok is not None:
                self.resolve_ok()
            self.game.popups.remove(self)
