import pygame
import json
import random
from popup import OkPopup, YesNoPopup, SelectPlayer


class Box:
    boxes = []

    def __init__(self, n, name):
        self.n = n
        self.name = name
        self.rect = pygame.Rect(0, 0, 0, 0)

    @staticmethod
    def update_rect(game):
        l = game.height / (9 + 2 * game.r)
        L = l * game.r
        for box in Box.boxes:
            box.rect.update(game.width - game.height, 0, 0, 0)
            if box.n in range(1, 10):
                box.rect.move_ip(L + l * (9 - box.n), game.height - L)
                box.rect.size = l, L
            elif box.n in range(11, 20):
                box.rect.move_ip(0, L + l * (19 - box.n))
                box.rect.size = L, l
            elif box.n in range(21, 30):
                box.rect.move_ip(L + l * (box.n - 21), 0)
                box.rect.size = l, L
            elif box.n in range(31, 40):
                box.rect.move_ip(game.height - L, L + l * (box.n - 31))
                box.rect.size = L, l
            elif box.n == 0:
                box.rect.move_ip(game.height - L, game.height - L)
                box.rect.size = L, L
            elif box.n == 10:
                box.rect.move_ip(0, game.height - L)
                box.rect.size = L, L
            elif box.n == 20:
                box.rect.move_ip(0, 0)
                box.rect.size = L, L
            elif box.n == 30:
                box.rect.move_ip(game.height - L, 0)
                box.rect.size = L, L
        Box.house_image = pygame.transform.smoothscale(
            pygame.image.load("assets/house.png"), (l / 4, l / 4)
        )
        Box.hotel_image = pygame.transform.smoothscale(
            pygame.image.load("assets/hotel.png"), (l / 4, l / 4)
        )

    @staticmethod
    def load(game):
        Box.game = game
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for i, box in enumerate(data):
            match box["type"]:
                case "special":
                    c = Special(i, box["name"], box["method"])
                case "street":
                    c = Street(
                        i,
                        box["name"],
                        box["base_price"],
                        box["color"],
                        box["house_price"],
                        box["rent"],
                    )
                case "gare":
                    c = Gare(i, box["name"])
                case "company":
                    c = Company(i, box["name"])
                case _:
                    raise (Exception(f"{box['type']} is not a box type"))
            Box.boxes.append(c)
        Box.update_rect(game)

    @staticmethod
    def update_from_dict(data):
        if "n" not in data:
            raise (Exception(f"Error in box update {data}"))
        Box.boxes[data["n"]].update_from_dict(data)
    
    @staticmethod
    def update():
        pass

    @staticmethod
    def draw():
        l = Box.game.height / (9 + 2 * Box.game.r)
        for i in range(40):
            if i in range(1,10) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(Box.boxes[i].player.small_red_image if Box.boxes[i].in_mortgage else Box.boxes[i].player.small_image, Box.boxes[i].rect.move(l*0.35,-0.3*l))
            if i in range(11,20) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(pygame.transform.rotate(Box.boxes[i].player.small_red_image if Box.boxes[i].in_mortgage else Box.boxes[i].player.small_image ,270), Box.boxes[i].rect.move(Box.game.r*l,0.35*l))
            if i in range(21,30) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(Box.boxes[i].player.small_red_image if Box.boxes[i].in_mortgage else Box.boxes[i].player.small_image , Box.boxes[i].rect.move(l*0.35,Box.game.r*l))
            if i in range(31,40) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(pygame.transform.rotate(Box.boxes[i].player.small_red_image if Box.boxes[i].in_mortgage else Box.boxes[i].player.small_image ,90), Box.boxes[i].rect.move(-l*0.3,0.35*l))


class Street(Box):
    def __init__(self, n, name, base_price, color, house_price, rent):
        super().__init__(n, name)
        self.houses = 0
        self.base_price = base_price
        self.color = color
        self.house_price = house_price
        self.rent = rent
        self.player = None
        self.in_mortgage = False

    def play(self, player, game):
        if self.player is None:
            game.popups.append(
                YesNoPopup(
                    game,
                    f"Voulez vous acheter {self.name} pour {self.base_price} $ ?",
                    resolve_yes=lambda: self.purchase(player),
                    resolve_no=lambda: None,
                )
            )
            return
        elif self.player != player and not self.in_mortgage:
            self.player.money += self.rent[self.houses]
            player.money -= self.rent[self.houses]
            game.popups.append(
                OkPopup(
                    game,
                    f"Vous payer {self.rent[self.houses]} $ au joueur {self.player.name}",
                )
            )
        elif self.player != player and self.in_mortgage:
            game.popups.append(
                OkPopup(
                    game,
                    "Cette propriété est en hypothèque, vous n'avez rien a payer !",
                )
            )
            return
        self.game.socket_manager.send_player(self.player)

    def purchase(self, player):
        if player.money < self.base_price:
            player.game.popups.append(
                OkPopup(player.game, f"Vous n'avez pas assez d'argent")
            )
        else:
            player.game.popups.append(OkPopup(player.game, f"Achat effectué"))
            player.money -= self.base_price
            self.player = player
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def add_house(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return
        elif self.houses == 5:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Vous ne pouvez pas construite davantage sur cette propriété",
                ),
            )
            return
        elif not all(
            [
                box.player == self.game.myself
                for box in Box.boxes
                if isinstance(box, Street) and box.color == self.color
            ]
        ):
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    f"Vous ne possédez pas l'ensemble de propriétés du groupe {self.color}",
                ),
            )
            return
        elif self.in_mortgage:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Cette propriété est en hypothèque, vous devez lever l'hypothèque avant de pouvoir construire",
                ),
            )
            return
        elif self.game.myself.money < self.house_price:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game, "Vous n'avez pas suffisement d'argent pour construire"
                ),
            )
            return
        else:
            self.game.myself.money -= self.house_price
            self.houses += 1
            self.game.popups.insert(
                0, OkPopup(self.game, f"Nouvelle maison construite sur {self.name}")
            )
        self.game.socket_manager.send_player(self.player)
        self.game.socket_manager.send_box(self)

    def remove_house(self):
        if self.player is None:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return
        elif self.houses == 0:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game, "Aucune maison n'est construite sur cette propriété"
                ),
            )
            return
        else:
            self.houses -= 1
            self.player.money += self.house_price * 9 // 10
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    f"Vous avez vendu une maison sur {self.name} pour {self.house_price*9//10} $",
                ),
            )
        self.game.socket_manager.send_player(self.player)
        self.game.socket_manager.send_box(self)

    def mortgage(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return
        elif self.in_mortgage and self.game.myself.money < self.base_price // 2:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Vous n'avez pas suffisement d'argent pour lever l'hypothèque",
                ),
            )
            return
        elif self.in_mortgage and self.game.myself.money >= self.base_price // 2:
            self.game.myself.money -= self.base_price // 2
            self.in_mortgage = False
            self.game.popups.insert(
                0, OkPopup(self.game, f"L'hypothèque sur {self.name} a été levé")
            )
        elif self.houses != 0:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Vous devez vendre toutes les constructions de la propriété avant de l'hypotéquer",
                ),
            )
            return
        else:
            self.game.myself.money += self.base_price // 2
            self.in_mortgage = True
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    f"Vous avez hypothéqué {self.name} pour {self.base_price//2}",
                ),
            )
        self.game.socket_manager.send_player(self.player)
        self.game.socket_manager.send_box(self)

    def sell(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return
        elif any(
            [
                box.houses != 0
                for box in Box.boxes
                if isinstance(box, Street) and box.color == self.color
            ]
        ):
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Vous devez vendre toutes les constructions du groupe de proporiété avant de pouvoir ventre cette propriété",
                ),
            )
            return
        may_sell(self)
        return


    def draw_houses(self):
        if not self.houses:
            return
        if self.n in range(1, 10):
            if self.houses == 5:
                Box.game.screen.blit(
                    Box.hotel_image, self.rect.move(3 * self.rect.width / 8, 0)
                )
            else:
                for i in range(self.houses):
                    Box.game.screen.blit(
                        Box.house_image, self.rect.move(i * self.rect.width / 4, 0)
                    )
        if self.n in range(11, 20):
            if self.houses == 5:
                Box.game.screen.blit(
                    pygame.transform.rotate(Box.hotel_image, -90),
                    self.rect.move(
                        self.rect.width - self.rect.height / 4, 3 * self.rect.height / 8
                    ),
                )
            else:
                for i in range(self.houses):
                    Box.game.screen.blit(
                        pygame.transform.rotate(Box.house_image, -90),
                        self.rect.move(
                            self.rect.width - self.rect.height / 4,
                            i * self.rect.height / 4,
                        ),
                    )
        if self.n in range(21, 30):
            if self.houses == 5:
                Box.game.screen.blit(
                    pygame.transform.rotate(Box.hotel_image, 180),
                    self.rect.move(
                        3 * self.rect.width / 8, self.rect.height - self.rect.width / 4
                    ),
                )
            else:
                for i in range(self.houses):
                    Box.game.screen.blit(
                        pygame.transform.rotate(Box.house_image, 180),
                        self.rect.move(
                            i * self.rect.width / 4,
                            self.rect.height - self.rect.width / 4,
                        ),
                    )
        if self.n in range(31, 40):
            if self.houses == 5:
                Box.game.screen.blit(
                    pygame.transform.rotate(Box.hotel_image, 90),
                    self.rect.move(0, 3 * self.rect.height / 8),
                )
            else:
                for i in range(self.houses):
                    Box.game.screen.blit(
                        pygame.transform.rotate(Box.house_image, 90),
                        self.rect.move(0, i * self.rect.height / 4),
                    )

    def to_dict(self):
        return {
            "n": self.n,
            "houses": self.houses,
            "player": self.player.name if self.player is not None else "No_one",
            "in_mortgage": self.in_mortgage,
        }

    def update_from_dict(self, data):
        if data["n"] != self.n:
            raise (Exception("Error in box update"))
        if "houses" in data:
            self.houses = data["houses"]
        if "player" in data:
            if data["player"] == "No_one":
                self.player = None
            elif data["player"] == self.game.myself.name:
                self.player = self.game.myself
            else:
                player = [
                    player
                    for player in self.game.players
                    if player.name == data["player"]
                ][0]
                self.player = player
        if "in_mortgage" in data:
            self.in_mortgage = data["in_mortgage"]


class Gare(Box):
    def __init__(self, n, name):
        super().__init__(n, name)
        self.player = None
        self.in_mortgage = False
        self.base_price = 200

    def play(self, player, game):
        if self.player is None:
            game.popups.append(
                YesNoPopup(
                    game,
                    f"Voulez vous acheter {self.name} pour 200 $ ?",
                    resolve_yes=lambda: self.purchase(player),
                    resolve_no=lambda: None,
                )
            )
            return
        elif self.player != player and not self.in_mortgage:
            price = 25 * 2 ** (
                sum([Box.boxes[i].player == self.player for i in [5, 15, 25, 35]]) - 1
            )
            self.player.money += price
            player.money -= price
            game.popups.append(
                OkPopup(game, f"Vous payer {price} $ au joueur {self.player.name}")
            )
        elif self.player != player and self.in_mortgage:
            game.popups.append(
                OkPopup(
                    game,
                    "Cette propriété est en hypothèque, vous n'avez rien a payer !",
                )
            )
            return
        self.game.socket_manager.send_player(self.player)

    def purchase(self, player):
        if player.money < 200:
            player.game.popups.append(
                OkPopup(player.game, f"Vous n'avez pas assez d'argent")
            )
            return
        else:
            player.game.popups.append(OkPopup(player.game, f"Achat effectué"))
            player.money -= 200
            self.player = player
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def sell(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return


        elif self.in_mortgage:
            self.game.myself.money += 100
            self.player = None
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game, f"Vous avez vendu {self.name} à la banque pour 100 $"
                ),
            )
        else:
            self.game.myself.money += 200
            self.player = None
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game, f"Vous avez vendu {self.name} à la banque pour 200 $"
                ),
            )
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def mortgage(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return
        elif self.in_mortgage and self.game.myself.money < 100:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Vous n'avez pas suffisement d'argent pour lever l'hypothèque",
                ),
            )
            return
        elif self.in_mortgage and self.game.myself.money >= 100:
            self.game.myself.money -= 100
            self.in_mortgage = False
            self.game.popups.insert(
                0, OkPopup(self.game, f"L'hypothèque sur {self.name} a été levé")
            )
        else:
            self.game.myself.money += 100
            self.in_mortgage = True
            self.game.popups.insert(
                0, OkPopup(self.game, f"Vous avez hypothéqué {self.name} pour {100}")
            )
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def to_dict(self):
        return {
            "n": self.n,
            "player": self.player.name if self.player is not None else "No_one",
            "in_mortgage": self.in_mortgage,
        }

    def update_from_dict(self, data):
        if data["n"] != self.n:
            raise (Exception("Error in box update"))
        if "player" in data:
            if data["player"] == "No_one":
                self.player = None
            elif data["player"] == self.game.myself.name:
                self.player = self.game.myself
            else:
                player = [
                    player
                    for player in self.game.players
                    if player.name == data["player"]
                ][0]
                self.player = player
        if "in_mortgage" in data:
            self.in_mortgage = data["in_mortgage"]


class Company(Box):
    def __init__(self, n, name):
        super().__init__(n, name)
        self.player = None
        self.in_mortgage = False
        self.base_price = 150

    def play(self, player, game):
        if self.player is None:
            game.popups.append(
                YesNoPopup(
                    game,
                    f"Voulez vous acheter {self.name} pour 150 $ ?",
                    resolve_yes=lambda: self.purchase(player),
                    resolve_no=lambda: None,
                )
            )
            return
        elif self.player != player and not self.in_mortgage:
            if (
                self.player == Box.boxes[12].player
                and self.player == Box.boxes[28].player
            ):
                price = game.dice * 10
            else:
                price = game.dice * 4
            self.player.money += price
            player.money -= price
            game.popups.append(
                OkPopup(game, f"Vous payer {price} $ au joueur {self.player.name}")
            )
        elif self.player != player and self.in_mortgage:
            game.popups.append(
                OkPopup(
                    game,
                    "Cette propriété est en hypothèque, vous n'avez rien a payer !",
                )
            )
            return
        self.game.socket_manager.send_player(self.player)

    def purchase(self, player):
        if player.money < 150:
            player.game.popups.append(
                OkPopup(player.game, f"Vous n'avez pas assez d'argent")
            )
            return
        else:
            player.game.popups.append(OkPopup(player.game, f"Achat effectué"))
            player.money -= 150
            self.player = player
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def mortgage(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return
        elif self.in_mortgage and self.game.myself.money < 75:
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game,
                    "Vous n'avez pas suffisement d'argent pour lever l'hypothèque",
                ),
            )
            return
        elif self.in_mortgage and self.game.myself.money >= 75:
            self.game.myself.money -= 75
            self.in_mortgage = False
            self.game.popups.insert(
                0, OkPopup(self.game, f"L'hypothèque sur {self.name} a été levé")
            )
        else:
            self.game.myself.money += 75
            self.in_mortgage = True
            self.game.popups.insert(
                0, OkPopup(self.game, f"Vous avez hypothéqué {self.name} pour 75 $")
            )
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def sell(self):
        if self.player != self.game.myself:
            self.game.popups.insert(
                0, OkPopup(self.game, "Cette propriété ne vous appartient pas")
            )
            return


        elif self.in_mortgage:
            self.game.myself.money += 75
            self.player = None
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game, f"Vous avez vendu {self.name} à la banque pour 75 $"
                ),
            )
        else:
            self.game.myself.money += 150
            self.player = None
            self.game.popups.insert(
                0,
                OkPopup(
                    self.game, f"Vous avez vendu {self.name} à la banque pour 150 $"
                ),
            )
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def to_dict(self):
        return {
            "n": self.n,
            "player": self.player.name if self.player is not None else "No_one",
            "in_mortgage": self.in_mortgage,
        }

    def update_from_dict(self, data):
        if data["n"] != self.n:
            raise (Exception("Error in box update"))
        if "player" in data:
            if data["player"] == "No_one":
                self.player = None
            elif data["player"] == self.game.myself.name:
                self.player = self.game.myself
            else:
                player = [
                    player
                    for player in self.game.players
                    if player.name == data["player"]
                ][0]
                self.player = player
        if "in_mortgage" in data:
            self.in_mortgage = data["in_mortgage"]


class Special(Box):

    with open("chance.json", "r", encoding="utf-8") as f:
        chance= json.load(f)
    with open("community_chest.json", "r", encoding="utf-8") as f:
        community_chest = json.load(f)

    def __init__(self, n, name, method):
        super().__init__(n, name)
        self.method = method

    def play(self, player, game):
        match self.method:
            case "depart":
                pass
            case "caisse":
                self.playcard(player, game, False)
            case "impots":
                player.money -= 200
                game.parc += 200
                # Manage parc socket update
            case "chance":
                self.playcard(player, game, True)
            case "prison":
                self.prison(player, game)
            case "parc":
                player.money += game.parc
                game.popups.append(
                    OkPopup(
                        game,
                        f"Vous touchez {game.parc} $ du parc gratuit !",
                    )
                )
                game.parc = 0
                # Manage parc socket update
            case "go_to_prison":
                game.socket_manager.send_player(player)
                player.prison_time = 2
                player.position = 10
                game.popups.append(OkPopup(game, "Vous allez en prison !"))
                player.update_position()
            case "taxe":
                player.pay(100)
                game.popups.append(OkPopup(game, "Payez 100 $ de taxes"))
                game.parc += 100

    def prison(self, player, game):
        if player.prison_time == 0:
            return
        player.prison_time -= 1
        if player.money < 50:
            return
        game.popups.append(
            YesNoPopup(
                game,
                "Voulez-vous sortir de prison pour 50 $ ?",
                resolve_yes=lambda: self.leave_prison(player, game),
                resolve_no=lambda: None,
            )
        )

    def leave_prison(self, player, game):
        player.money -= 50
        game.parc += 50
        player.prison_time = 0
        player.position += game.dice1 + game.dice2
        game.socket_manager.send_player(player)
        player.update_position()
        player.play()
    
    def playcard(self, player, game, isChance):
        if isChance: 
            card = Special.chance[random.randint(0,14)]
        else:
            card = Special.community_chest[random.randint(0,15)]
        match card["type"]:
            case "earn":
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : player.earn(card["amount"])
                ))
            case "pay":
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : player.pay(card["amount"])
                ))
            case "goto":
                def goto(player, game, card):
                    if player.position > card["position"]:
                        player.money += 200
                    player.position = card["position"]
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : goto(player, game, card)
                ))
            case "goto_prison":
                game.socket_manager.send_player(player)
                game.popups.append(OkPopup(game, card['text']))
                player.prison_time = 2
                player.position = 10
                player.update_position()
            case "next_train_station":
                def goto(player, game, card):
                    player.position = (player.position+5)//10*10 + 5
                    if player.position >= 40:
                        player.money += 200
                        player.position %= 40
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : goto(player, game, card)
                ))
            case "next_company":
                def goto(player, game, card):
                    player.position = 28 if player.position in range(12,28) else 12
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : goto(player, game, card)
                ))
            case "move_back":
                def goto(player, game, card):
                    player.position -= 3
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : goto(player, game, card)
                ))
            case "renovations":
                price = 0
                for box in Box.boxes:
                    if isinstance(box, Street) and box.player == player:
                        if box.houses < 5:
                            price += box.houses*card["house"]
                        else:
                            price += card["hotel"]
                game.popups.append(OkPopup(
                    game,
                    card["text"],
                    resolve_ok=lambda : player.pay(price)
                ))
            case "get_out_of_prison":
                player.get_out_of_prison_card += 1
                game.popups.append(OkPopup(game, card["text"]))
            case "pay_everyone":
                game.popups.append(OkPopup(game, card["text"]))
                game.socket_manager.send_info(f"Vous recevez {card['amount']} $ de {player.name}.")
                price = 0
                for p in game.players:
                    p.earn(card["amount"])
                    game.socket_manager.send_player(p)
                    price += card['amount']
                player.pay(price)
            case "earn_from_everyone":
                game.popups.append(OkPopup(game, card["text"]))
                game.socket_manager.send_info(f"Vous versez {card['amount']} $ à {player.name}.")
                price = 0
                for p in game.players:
                    p.pay(card["amount"])
                    game.socket_manager.send_player(p)
                    price += card['amount']
                player.earn(price)

    def to_dict(self):
        return {"n": self.n}

    def update_from_dict(self, _):
        pass




def may_sell(box):
    box.game.popups.insert(
        0,
        YesNoPopup(
        box.game,
        f"Voulez vous vendre {box.name} à la banque ?",
        resolve_no=lambda : may_sell_to_player(box),
        resolve_yes=lambda : sell_to_bank(box)
        ))

def sell_to_bank(box):
    if box.in_mortgage:
            box.game.myself.money += box.base_price/2
            box.player = None
            box.game.popups.insert(
                0,
                OkPopup(
                    box.game, f"Vous avez vendu {box.name} à la banque pour {box.base_price/2} $"
                ),
            )
    else:
        box.game.myself.money += box.base_price
        box.player = None
        box.game.popups.insert(
            0,
            OkPopup(
                box.game, f"Vous avez vendu {box.name} à la banque pour {box.base_price} $"
            ),
        )
    box.game.socket_manager.send_box(box)
    box.game.socket_manager.send_player(box.game.myself)
    box.game.socket_manager.send_info(f"{box.game.myself.name} à vendu {box.name} à la banque")

def may_sell_to_player(box):
    box.game.popups.insert(
        0,
        YesNoPopup(
            box.game,
            f"Voulez vous vendre {box.name} à un joueur ?",
            resolve_no=lambda : None,
            resolve_yes=lambda : sell_to_player(box)
    ))

def sell_to_player(box):
    def sell_to(player):
        box.game.myself.money += box.base_price
        player.money -= box.base_price
        box.player = player
        box.game.popups.insert(
            0,
            OkPopup(
                box.game, f"Vous avez vendu {box.name} à {player.name} $"
            ),
        )
        box.game.socket_manager.send_box(box)
        box.game.socket_manager.send_player(player)
        box.game.socket_manager.send_info(f"{box.game.myself.name} à vendu {box.name} à {player.name}")

    box.game.popups.insert(
        0,
        SelectPlayer(
            box.game,
            f"Choisissez un joueur",
            resolve=sell_to
        )
    )
    
   
    
    