import pygame


class InputText:
    color_inactive = pygame.Color("lightskyblue3")
    color_active = pygame.Color("dodgerblue2")

    def __init__(self, game, rect, background, force_numeric=False):
        self.game = game
        self.is_active = False
        self.background = background
        self.color = InputText.color_inactive
        self.text = ""
        self.force_numeric = force_numeric
        if rect:
            self.update(rect)

    def update(self, rect):
        self.rect = rect
        self.font = pygame.font.Font(None, int(0.9 * rect.h))
        self.input_box = pygame.Surface(self.rect.size)

    def get_value(self):
        if self.force_numeric:
            return int(self.text) if self.text else 0
        return self.text

    def draw(self):
        self.input_box.fill(self.background)
        txt_surface = self.font.render(self.text, True, pygame.Color(0, 0, 0))
        self.input_box.blit(txt_surface, (0.3 * self.rect.w, 0.2 * self.rect.h))
        self.game.screen.blit(self.input_box, self.rect)
        pygame.draw.rect(self.game.screen, self.color, self.rect.inflate(2, 2), 2, 5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_active = not self.is_active
            else:
                self.is_active = False
            self.color = (
                InputText.color_active if self.is_active else InputText.color_inactive
            )
        if event.type == pygame.KEYDOWN:
            if self.is_active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif (
                    self.force_numeric and event.unicode.isdecimal()
                ) or not self.force_numeric:
                    self.text += event.unicode
