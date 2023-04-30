import pygame
from box import Box, Street, Gare, Company, Special


class Card:
    def __new__(cls, game, box, close):
        if isinstance(box, Street):
            obj = object.__new__(StreetCard)
        elif isinstance(box, Gare):
            obj = object.__new__(GareCard)
        elif isinstance(box, Company):
            obj = object.__new__(CompanyCard)
        else:
            obj = object.__new__(SpecialCard)
        return obj

    def __init__(self, game, box, close):
        self.game = game
        self.box = box
        self.image = None
        self.close = close

    def update(self):
        if self.image is None:
            raise Exception("Image card is not loaded")
        self.card = pygame.transform.scale(
            self.image , (self.game.height / 3, 4 * self.game.height / 9)
        )
        self.closeRect = pygame.Rect(
            self.game.width - self.game.height / 2 - self.card.get_width() / 2,
            self.game.height / 2 - self.card.get_height() / 2,
            0.15 * self.game.height / 3,
            0.15 * self.game.height / 3,
        )
        self.close_image = pygame.transform.scale(pygame.image.load("assets/close.png"), self.closeRect.size)
        self.blit_title(self.box.name)

    def blit_title(self, name):
        margin = 0.25
        font = pygame.font.SysFont("calibri", 25*self.card.get_width()//233)

        width, height = self.card.get_size()
        y = 0.05 * height
        words = name.split(" ")
        while words:
            line = []
            line.append(words.pop(0))
            line_surface = font.render(" ".join(line), True, pygame.Color(0, 0, 0))
            while line_surface.get_width() <= width * (1 - margin) and words:
                line.append(words.pop(0))
                line_surface = font.render(" ".join(line), True, pygame.Color(0, 0, 0))
            if line_surface.get_width() > width * (1 - margin) and len(line) > 1:
                words.insert(0, line.pop())
            line_surface = font.render(" ".join(line), True, pygame.Color(0, 0, 0))
            x = (width - line_surface.get_width()) / 2
            self.card.blit(line_surface, (x, y))
            y += line_surface.get_height()

    def draw(self):
        self.game.screen.blit(
            self.card,
            (
                self.game.width - self.game.height / 2 - self.card.get_width() / 2,
                self.game.height / 2 - self.card.get_height() / 2,
            ),
        )
        if self.close:
            self.game.screen.blit(self.close_image, self.closeRect.move(-5,-5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.closeRect.collidepoint(event.pos):
                self.game.popups.pop(0)
                return False  # do not execute subClass methode
            return True
        else:
            return False


class StreetCard(Card):
    def __init__(self, game, box, close):
        super().__init__(game, box, close)
        self.image = pygame.image.load(f"assets/street/card{box.color}.png")
        self.update()
        

    def update(self):
        # card, title, closeRect
        super().update()
        width, height = self.card.get_size()
        font = pygame.font.Font(None, 30*width//233)
        # display prices
        i = 0
        for price in self.box.rent:
            word_surface = font.render(str(price), True, pygame.Color(0, 0, 0))
            self.card.blit(
                word_surface,
                (0.7 * width, 0.25 * height + word_surface.get_height() * i),
            )
            i += 1
        i += 1
        for price in (self.box.house_price, self.box.base_price // 2):
            word_surface = font.render(str(price), True, pygame.Color(0, 0, 0))
            self.card.blit(
                word_surface,
                (0.7 * width, 0.20 * height + word_surface.get_height() * i),
            )
            i += 1

        # manage bottom buttons
        a = 0.15 * width
        space = (width - 4 * a) / 5
        self.addHouseRect = pygame.Rect(space, height - a * 1.4, a, a)
        self.addHouseRect.move_ip(self.closeRect.topleft)
        self.removeHouseRect = self.addHouseRect.move(space + self.closeRect.width, 0)
        self.sellRect = self.addHouseRect.move(2 * space + 2 * self.closeRect.width, 0)
        self.mortgageRect = self.addHouseRect.move(
            3 * space + 3 * self.closeRect.width, 0
        )

    def handle_event(self, event):
        if super().handle_event(event):
            if self.addHouseRect.collidepoint(event.pos):
                self.box.add_house()
            elif self.removeHouseRect.collidepoint(event.pos):
                self.box.remove_house()
            elif self.sellRect.collidepoint(event.pos):
                self.box.sell()
            elif self.mortgageRect.collidepoint(event.pos):
                self.box.mortgage()

    def draw(self):
        super().draw()


class GareCard(Card):
    def __init__(self, game, box, close):
        super().__init__(game, box, close)
        self.image = pygame.image.load("assets/card.png")
        self.update()

    def update(self):
        super().update()
        width, height = self.image.get_size()
        # font = pygame.font.Font(None, 32)

        # manage bottom buttons
        a = 0.15 * width
        space = (width - 2 * a) / 3
        self.sellRect = pygame.Rect(space, height - a * 1.4, a, a)
        self.sellRect.move_ip(self.closeRect.topleft)
        self.mortgageRect = self.sellRect.move(space + self.closeRect.width, 0)

    def draw(self):
        super().draw()

    def handle_event(self, event):
        if super().handle_event(event):
            if self.sellRect.collidepoint(event.pos):
                self.box.sell()
            elif self.mortgageRect.collidepoint(event.pos):
                self.box.mortgage()


class CompanyCard(Card):
    def __init__(self, game, box, close):
        super().__init__(game, box, close)
        self.image = pygame.image.load("assets/card.png")
        self.update()

    def update(self):
        super().update()
        width, height = self.image.get_size()
        # font = pygame.font.Font(None, 32)

        # manage bottom buttons
        a = 0.15 * width
        space = (width - 2 * a) / 3
        self.sellRect = pygame.Rect(space, height - a * 1.4, a, a)
        self.sellRect.move_ip(self.closeRect.topleft)
        self.mortgageRect = self.sellRect.move(space + self.closeRect.width, 0)

    def draw(self):
        super().draw()

    def handle_event(self, event):
        if super().handle_event(event):
            if self.sellRect.collidepoint(event.pos):
                self.box.sell()
            elif self.mortgageRect.collidepoint(event.pos):
                self.box.mortgage()


class SpecialCard(Card):
    def __init__(self, game, box, close):
        super().__init__(game, box, close)

    def draw(self):
        print("Nothing to Draw")
        self.game.popups.pop(0)


# ['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'sansserifcollection', 'segoefluenticons', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'segoeuivariable', 'simsun', 'nsimsun', 'simsunextb', 'sitkatext', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'agencyfb', 'algerian', 'arialrounded', 'baskervilleoldface', 'bauhaus93', 'bell', 'berlinsansfb', 'berlinsansfbdemi', 'bernardcondensed', 'blackadderitc', 'bodoni', 'bodoniblack', 'bodonicondensed', 'bodonipostercompressed', 'bookantiqua', 'bookmanoldstyle', 'bookshelfsymbol7', 'bradleyhanditc', 'britannic', 'broadway', 'brushscript', 'californianfb', 'calisto', 'castellar', 'centaur', 'century', 'centurygothic', 'centuryschoolbook', 'chiller', 'colonna', 'cooperblack', 'copperplategothic', 'curlz', 'dubai', 'dubaimedium', 'dubairegular', 'edwardianscriptitc', 'elephant', 'engravers', 'erasitc', 'erasdemiitc', 'erasmediumitc', 'felixtitling', 'footlight', 'forte', 'franklingothicbook', 'franklingothicdemi', 'franklingothicdemicond', 'franklingothicheavy', 'franklingothicmediumcond', 'freestylescript', 'frenchscript', 'palacescript', 'papyrus', 'parchment', 'perpetua', 'perpetuatitling', 'playbill', 'poorrichard', 'pristina', 'rage', 'ravie', 'rockwell', 'rockwellcondensed', 'rockwellextra', 'script', 'showcardgothic', 'snapitc', 'stencil', 'tempussansitc', 'twcen', 'twcencondensed', 'twcencondensedextra', 'vinerhanditc', 'vivaldi', 'vladimirscript', 'widelatin', 'wingdings2', 'wingdings3', 'leelawadeegras', 'microsoftuighurgras']
