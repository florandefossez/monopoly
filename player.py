import pygame
from box import Box


class Player:
    def __init__(self, game, address):
        self.address = address
        Player.game = game
        self.position = 0
        self.box = Box.boxes[0]
        self.money = 20000
        self.prison_time = 0
        self.frame = []
        self.update_image()
        self.get_out_of_prison_card = 0

    def update_image(self):
        image_size = (
            0.4 * self.game.height * self.game.r / (9 + 2 * self.game.r)
        )  # 0.4*L
        small_image_size = 0.3*self.game.height / (9 + 2 * self.game.r) # 0.3*l
        self.image = pygame.transform.smoothscale(
            pygame.image.load(self.address), (image_size, image_size)
        )
        self.small_image = pygame.transform.smoothscale(
            pygame.image.load(self.address), (small_image_size, small_image_size)
        )
        self.rect = self.image.get_rect()
        offset = (
            self.game.height * (1 - 0.4 * self.game.r) / (18 + 4 * self.game.r)
        )  # (l-0.4*L)/2
        self.offset = pygame.Rect(offset, offset, 0, 0)
        self.update_position(1)

    def update_position(self, n_frame=100):
        self.box = Box.boxes[self.position]
        destination = self.box.rect.move(self.offset.topleft)
        if self.position in range(11):
            destination.move_ip(
                0, self.game.height * (self.game.r - 1) / (9 + 2 * self.game.r)
            )  # 0, L-l
        elif self.position in range(30, 40):
            destination.move_ip(
                self.game.height * (self.game.r - 1) / (9 + 2 * self.game.r), 0
            )  # L-l, 0
        for i in range(n_frame, 0, -1):
            self.frame.append(
                destination.move(
                    i / n_frame * (self.rect.left - destination.left),
                    i / n_frame * (self.rect.top - destination.top),
                )
            )
        self.rect.topleft = destination.topleft

    def pay(self, amount):
        self.money -= amount
    
    def earn(self, amount):
        self.money += amount

    def play(self):
        Box.boxes[self.position].play(self, self.game)

    def draw(self):
        if self.frame:
            self.game.screen.blit(self.image, self.frame.pop(0))
        else:
            self.game.screen.blit(self.image, self.rect)

    def to_dict(self):
        return {"pos": self.position, "money": self.money, "name": self.address}

    def _update_from_dict(self, data):
        if data.get("name") != self.address:
            return
        if "money" in data:
            self.money = data["money"]
        if "pos" in data:
            self.position = data["pos"]
            self.update_position()

    @staticmethod
    def update_from_dict(data):
        if "name" not in data:
            raise (Exception(f"Error in player update {data}"))
        if data["name"] == Player.game.myself.address:
            player = Player.game.myself
        else:
            player = [p for p in Player.game.players if p.address == data["name"]][0]
        player._update_from_dict(data)
