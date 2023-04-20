import pygame
import json
import sys
import time
import argparse
from random import randint

from player import Player
from box import Box, Street, Gare, Company, Special
from card import Card
from popup import OkPopup, YesNoPopup
from socket_manager import SocketManager, Server, Client
from sidebar import Sidebar


class Game:
    r = 1.6

    def __init__(self):
        self.running = True
        with open(args.path, "r") as f:
            self.settings = json.load(f)

        self.width = 1000
        self.height = 700
        Box.load(self)
        self.parc = 0
        self.myself = Player(self, f"assets/{self.settings['image']}.png")
        self.players = []
        self.popups = []
        self.dice1 = 1
        self.dice2 = 1
        self.double_in_row = 0
        self.our_turn = False
        self.end_turn = True

        if self.settings["server"]:
            self.socket_manager = Server(self)
        else:
            self.socket_manager = Client(self)

        pygame.display.set_caption("Server" if self.settings["server"] else "Client")
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        self.sidebar = Sidebar(self)
        self.dice_image = {}
        self.load_assets()

    def add_player(self, address):
        self.players.append(Player(self, f"assets/{address}.png"))

    def load_assets(self):
        self.background = pygame.transform.smoothscale(
            pygame.image.load("assets/plateau.jpg"), (self.height, self.height)
        )
        dice_size = 0.4 * self.height * self.r / (9 + 2 * self.r)
        for dice in range(1, 7):
            self.dice_image[dice] = pygame.transform.smoothscale(
                pygame.image.load(f"assets/dice/{dice}.png"), (dice_size, dice_size)
            )
        self.rect_dice1 = pygame.Rect(
            (
                (self.width - self.height) + dice_size * (2 + 15 / self.r),
                dice_size * (2 + 20 / self.r),
                0,
                0,
            )
        )
        self.rect_dice2 = self.rect_dice1.move(5 * dice_size / self.r, 0)

    def new_turn(self):
        self.end_turn = False

        # throw dice
        self.dice1 = randint(1, 6)
        self.dice2 = randint(1, 6)
        # self.dice1 = 4
        # self.dice2 = 6
        self.socket_manager.send_dice()

        # leave prison if double
        if self.dice1 == self.dice2:
            self.myself.prison_time = 0

        # go to prison if 3 double in a row
        if self.double_in_row == 2 and self.dice1 == self.dice2:
            self.myself.position = 10
            self.myself.prison_time = 2

            self.double_in_row = 0
            self.myself.update_position()
            self.popups.append(
                OkPopup(self, "3 doubles d'affilée : Vous allez en prison !")
            )
            self.our_turn = False
            self.socket_manager.send_player(self.myself)
            return

        # move player if not in prison
        if self.myself.prison_time == 0:
            self.myself.position += self.dice1 + self.dice2
            if self.myself.position >= 40:
                self.myself.money += 200
                self.myself.position %= 40
            self.myself.update_position()

        # play the landing box
        self.myself.play()

        # continue to play if double
        if self.dice1 == self.dice2:
            self.double_in_row += 1
        else:
            self.double_in_row = 0
            self.our_turn = False

        # send_updates
        self.socket_manager.send_player(self.myself)

        # game over ?
        if self.myself.money < 0:
            self.popups.append(
                OkPopup(
                    self,
                    "Vous n'avez plus d'argent ! Trouvez un moyen de payer pour continuer.",
                )
            )

    def run(self):
        while self.running:
            # end the turn ?
            if not self.end_turn and self.popups == [] and self.myself.money >= 0:
                self.socket_manager.next_turn()
                self.end_turn = True

            # rescale objects if needed
            if (self.width, self.height) != self.screen.get_size():
                self.width, self.height = self.screen.get_size()
                self.load_assets()
                Box.update_rect(self)
                self.myself.update_image()
                self.sidebar.update()
                for player in self.players:
                    player.update_image()
                for popup in self.popups:
                    popup.update()

            # set sidebar
            self.sidebar.draw()

            # set plateau
            self.screen.blit(self.background, (self.width - self.height, 0))

            # set players
            self.myself.draw()
            for player in self.players:
                player.draw()

            # set dices
            self.screen.blit(self.dice_image[self.dice1], self.rect_dice1)
            self.screen.blit(self.dice_image[self.dice2], self.rect_dice2)

            # set houses
            for box in Box.boxes:
                if isinstance(box, Street):
                    box.draw_houses()
            
            # set boxes owners
            Box.draw()

            # set popups
            if self.popups:
                self.popups[0].draw()

            # update screen
            pygame.display.flip()

            # tacle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.socket_manager.close()

                if self.popups:
                    self.popups[0].handle_event(event)
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for box in Box.boxes:
                        if box.rect.collidepoint(event.pos):
                            self.popups.append(Card(self, box))
                            break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.our_turn:
                        self.new_turn()

        pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="path", default="settings.json")
    args = parser.parse_args()

    pygame.init()
    game = Game()
    game.run()
