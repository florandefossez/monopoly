import pygame
import json
import random


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
            if i in range(1, 10) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(
                    Box.boxes[i].player.small_red_image
                    if Box.boxes[i].in_mortgage
                    else Box.boxes[i].player.small_image,
                    Box.boxes[i].rect.move(l * 0.35, -0.3 * l),
                )
            if i in range(11, 20) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(
                    pygame.transform.rotate(
                        Box.boxes[i].player.small_red_image
                        if Box.boxes[i].in_mortgage
                        else Box.boxes[i].player.small_image,
                        270,
                    ),
                    Box.boxes[i].rect.move(Box.game.r * l, 0.35 * l),
                )
            if i in range(21, 30) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(
                    Box.boxes[i].player.small_red_image
                    if Box.boxes[i].in_mortgage
                    else Box.boxes[i].player.small_image,
                    Box.boxes[i].rect.move(l * 0.35, Box.game.r * l),
                )
            if i in range(31, 40) and getattr(Box.boxes[i], "player", None) is not None:
                Box.game.screen.blit(
                    pygame.transform.rotate(
                        Box.boxes[i].player.small_red_image
                        if Box.boxes[i].in_mortgage
                        else Box.boxes[i].player.small_image,
                        90,
                    ),
                    Box.boxes[i].rect.move(-l * 0.3, 0.35 * l),
                )


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
            game.yesnopopup(
                f"Voulez vous acheter {self.name} pour {self.base_price} $ ?",
                resolve_yes=lambda: self.purchase(player),
                resolve_no=lambda: None,
            )
            return
        elif self.player != player and not self.in_mortgage:
            self.player.earn(self.rent[self.houses], f"Loyer {self.name}")
            player.pay(self.rent[self.houses], f"Loyer {self.name}")
            game.okpopup(
                f"Vous payer {self.rent[self.houses]} $ au joueur {self.player.name}"
            )
        elif self.player != player and self.in_mortgage:
            game.okpopup(
                "Cette propriété est en hypothèque, vous n'avez rien a payer !"
            )

            return
        self.game.socket_manager.send_player(self.player)

    def purchase(self, player):
        if player.money < self.base_price:
            player.game.okpopup("Vous n'avez pas assez d'argent")
        else:
            player.game.okpopup("Achat effectué")
            player.pay(self.base_price, f"Achat {self.name}")
            self.player = player
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def add_house(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        elif self.houses == 5:
            self.game.okpopup(
                "Vous ne pouvez pas construite davantage sur cette propriété",
                foreground=True,
            )
            return
        elif not all(
            [
                box.player == self.game.myself
                for box in Box.boxes
                if isinstance(box, Street) and box.color == self.color
            ]
        ):
            self.game.okpopup(
                f"Vous ne possédez pas l'ensemble de propriétés du groupe {self.color}",
                foreground=True,
            )
            return
        elif self.in_mortgage:
            self.game.okpopup(
                "Cette propriété est en hypothèque, vous devez lever l'hypothèque avant de pouvoir construire",
                foreground=True,
            )
            return
        elif self.game.myself.money < self.house_price:
            self.game.okpopup(
                "Vous n'avez pas suffisement d'argent pour construire", foreground=True
            )
            return
        else:
            self.game.myself.pay(self.house_price, f"Construction maison {self.name}")
            self.houses += 1
            self.game.okpopup(
                f"Nouvelle maison construite sur {self.name}", foreground=True
            )
        self.game.socket_manager.send_player(self.player)
        self.game.socket_manager.send_box(self)

    def remove_house(self):
        if self.player is None:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        elif self.houses == 0:
            self.game.okpopup(
                "Aucune maison n'est construite sur cette propriété", foreground=True
            )
            return
        else:
            self.houses -= 1
            self.player.earn(self.house_price * 9 // 10, f"Vente maison {self.name}")
            self.game.okpopup(
                f"Vous avez vendu une maison sur {self.name} pour {self.house_price*9//10} $",
                foreground=True,
            )
        self.game.socket_manager.send_player(self.player)
        self.game.socket_manager.send_box(self)

    def mortgage(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        elif self.in_mortgage and self.game.myself.money < self.base_price * 6 // 10:
            self.game.okpopup(
                "Vous n'avez pas suffisement d'argent pour lever l'hypothèque",
                foreground=True,
            )
            return
        elif self.in_mortgage and self.game.myself.money >= self.base_price * 6 // 10:
            self.game.myself.pay(self.base_price * 6 // 10, f"Hypothèque {self.name}")
            self.in_mortgage = False
            self.game.okpopup(
                f"L'hypothèque sur {self.name} a été levé pour {self.base_price * 6 // 10} $",
                foreground=True,
            )
        elif self.houses != 0:
            self.game.okpopup(
                "Vous devez vendre toutes les constructions de la propriété avant de l'hypotéquer",
                foreground=True,
            )
            return
        else:
            self.game.myself.earn(self.base_price // 2, f"Hypothèque {self.name}")
            self.in_mortgage = True
            self.game.okpopup(
                f"Vous avez hypothéqué {self.name}, vous recevez {self.base_price//2}",
                foreground=True,
            )
        self.game.socket_manager.send_player(self.player)
        self.game.socket_manager.send_box(self)

    def sell(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        elif any(
            [
                box.houses != 0
                for box in Box.boxes
                if isinstance(box, Street) and box.color == self.color
            ]
        ):
            self.game.okpopup(
                "Vous devez vendre toutes les constructions du groupe de proporiété avant de pouvoir ventre cette propriété",
                foreground=True,
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
            game.yesnopopup(
                f"Voulez vous acheter {self.name} pour 200 $ ?",
                resolve_yes=lambda: self.purchase(player),
                resolve_no=lambda: None,
            )
            return
        elif self.player != player and not self.in_mortgage:
            price = 25 * 2 ** (
                sum([Box.boxes[i].player == self.player for i in [5, 15, 25, 35]]) - 1
            )
            self.player.earn(price, self.name)
            player.pay(price, self.name)
            game.okpopup(f"Vous payer {price} $ au joueur {self.player.name}")
        elif self.player != player and self.in_mortgage:
            game.okpopup(
                "Cette propriété est en hypothèque, vous n'avez rien a payer !"
            )
            return
        self.game.socket_manager.send_player(self.player)

    def purchase(self, player):
        if player.money < 200:
            player.game.okpopup("Vous n'avez pas assez d'argent")
            return
        else:
            player.game.okpopup("Achat effectué")
            player.pay(200, f"Achat {self.name}")
            self.player = player
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def sell(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        may_sell(self)

    def mortgage(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        elif self.in_mortgage and self.game.myself.money < 120:
            self.game.okpopup(
                "Vous n'avez pas suffisement d'argent pour lever l'hypothèque",
                foreground=True,
            )
            return
        elif self.in_mortgage and self.game.myself.money >= 120:
            self.game.myself.pay(120, f"Hypothèque {self.name}")
            self.in_mortgage = False
            self.game.okpopup(
                f"L'hypothèque sur {self.name} a été levé pour 120 $", foreground=True
            )
        else:
            self.game.myself.earn(100, f"Hypothèque {self.name}")
            self.in_mortgage = True
            self.game.okpopup(
                f"Vous avez hypothéqué {self.name} vous recevez 100 $", foreground=True
            )
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def to_dict(self):
        return {
            "n": self.n,
            "player": self.player.name if self.player is not None else None,
            "in_mortgage": self.in_mortgage,
        }

    def update_from_dict(self, data):
        if data["n"] != self.n:
            raise (Exception("Error in box update"))
        if "player" in data:
            if data["player"] is None:
                self.player = None
            elif data["player"] == self.game.myself.name:
                self.player = self.game.myself
            else:
                self.player = [
                    player
                    for player in self.game.players
                    if player.name == data["player"]
                ][0]
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
            game.yesnopopup(
                f"Voulez vous acheter {self.name} pour 150 $ ?",
                resolve_yes=lambda: self.purchase(player),
                resolve_no=lambda: None,
            )
            return
        elif self.player != player and not self.in_mortgage:
            if (
                self.player == Box.boxes[12].player
                and self.player == Box.boxes[28].player
            ):
                price = (game.dice1 + game.dice2) * 10
            else:
                price = (game.dice1 + game.dice2) * 4
            self.player.earn(price, self.name)
            player.pay(price, self.name)
            game.okpopup(f"Vous payer {price} $ au joueur {self.player.name}")
        elif self.player != player and self.in_mortgage:
            game.okpopup(
                "Cette propriété est en hypothèque, vous n'avez rien a payer !"
            )
            return
        self.game.socket_manager.send_player(self.player)

    def purchase(self, player):
        if player.money < 150:
            player.game.okpopup("Vous n'avez pas assez d'argent")
            return
        else:
            player.game.okpopup("Achat effectué")
            player.pay(150, f"Achat {self.name}")
            self.player = player
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def mortgage(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas")
            return
        elif self.in_mortgage and self.game.myself.money < 90:
            self.game.okpopup(
                "Vous n'avez pas suffisement d'argent pour lever l'hypothèque",
                foreground=True,
            )
            return
        elif self.in_mortgage and self.game.myself.money >= 90:
            self.game.myself.pay(90, f"Hypothèque {self.name}")
            self.in_mortgage = False
            self.game.okpopup(
                f"L'hypothèque sur {self.name} a été levé pour 90 $", foreground=True
            )
        else:
            self.game.myself.earn(75, f"Hypothèque {self.name}")
            self.in_mortgage = True
            self.game.okpopup(
                f"Vous avez hypothéqué {self.name} vous recevez 75 $", foreground=True
            )
        self.game.socket_manager.send_box(self)
        self.game.socket_manager.send_player(self.game.myself)

    def sell(self):
        if self.player != self.game.myself:
            self.game.okpopup("Cette propriété ne vous appartient pas", foreground=True)
            return
        may_sell(self)

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
        chance = json.load(f)
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
                player.pay(200, "Impôts")
                game.parc += 200
            case "chance":
                self.playcard(player, game, True)
            case "prison":
                self.prison(player, game)
            case "parc":
                player.earn(game.parc, "Parc gratuit")
                game.okpopup(f"Vous touchez {game.parc} $ du parc gratuit !")
                game.parc = 0
            case "go_to_prison":
                game.socket_manager.send_player(player)
                player.prison_time = 2
                player.position = 10
                game.okpopup("Vous allez en prison !")
                player.update_position()
            case "taxe":
                player.pay(100, "Taxes")
                game.okpopup("Payez 100 $ de taxes")
                game.parc += 100
        self.game.socket_manager.send_parc()

    def prison(self, player, game):
        if player.prison_time == 0:
            return
        player.prison_time -= 1
        if player.get_out_of_prison_card:
            game.yesnopopup(
                "Voulez-vous sortir de prison avec votre carte ?",
                resolve_yes=lambda: self.leave_prison(player, game, False),
                resolve_no=lambda: None,
            )
        else:
            game.yesnopopup(
                "Voulez-vous sortir de prison pour 50 $ ?",
                resolve_yes=lambda: self.leave_prison(player, game, True),
                resolve_no=lambda: None,
            )

    def leave_prison(self, player, game, pay):
        if pay:
            player.pay(50, "Prison")
            game.parc += 50
            game.socket_manager.send_parc()
        else:
            player.get_out_of_prison_card -= 1
        player.prison_time = 0
        player.position += game.dice1 + game.dice2
        game.socket_manager.send_player(player)
        player.update_position()
        player.play()

    def playcard(self, player, game, isChance):
        if isChance:
            card = Special.chance[random.randint(0, 14)]
        else:
            card = Special.community_chest[random.randint(0, 15)]
        match card["type"]:
            case "earn":
                game.okpopup(
                    card["text"],
                    resolve_ok=lambda: player.earn(
                        card["amount"], "Chance" if isChance else "Caisse de Communauté"
                    ),
                )
            case "pay":
                game.parc += card["amount"]
                game.okpopup(
                    card["text"],
                    resolve_ok=lambda: player.pay(
                        card["amount"], "Chance" if isChance else "Caisse de Communauté"
                    ),
                )
            case "goto":

                def goto(player, game, card):
                    if player.position > card["position"]:
                        player.earn(200, "Départ")
                    player.position = card["position"]
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()

                game.okpopup(card["text"], resolve_ok=lambda: goto(player, game, card))
            case "goto_prison":
                game.socket_manager.send_player(player)
                game.okpopup(card["text"])
                player.prison_time = 2
                player.position = 10
                player.update_position()
            case "next_train_station":

                def goto(player, game, card):
                    player.position = (player.position + 5) // 10 * 10 + 5
                    if player.position >= 40:
                        player.earn(200, "Départ")
                        player.position %= 40
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()

                game.okpopup(card["text"], resolve_ok=lambda: goto(player, game, card))

            case "next_company":

                def goto(player, game, card):
                    if player.position >= 28:
                        player.earn(200, "Départ")
                    player.position = 28 if player.position in range(12, 28) else 12
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()

                game.okpopup(card["text"], resolve_ok=lambda: goto(player, game, card))
            case "move_back":

                def goto(player, game, card):
                    player.position -= 3
                    player.update_position()
                    game.socket_manager.send_player(player)
                    player.play()

                game.okpopup(card["text"], resolve_ok=lambda: goto(player, game, card))
            case "renovations":
                price = 0
                for box in Box.boxes:
                    if isinstance(box, Street) and box.player == player:
                        if box.houses < 5:
                            price += box.houses * card["house"]
                        else:
                            price += card["hotel"]
                game.okpopup(
                    card["text"], resolve_ok=lambda: player.pay(price, "Rénovations")
                )
            case "get_out_of_prison":
                player.get_out_of_prison_card += 1
                game.okpopup(card["text"])
            case "pay_everyone":
                game.okpopup(card["text"])
                game.socket_manager.send_info(
                    f"Vous recevez {card['amount']} $ de {player.name}."
                )
                price = 0
                for p in game.players:
                    if p.position is None:
                        continue
                    p.earn(
                        card["amount"],
                        ("Chance " if isChance else "Caisse de Communauté ")
                        + player.name,
                    )
                    game.socket_manager.send_player(p)
                    price += card["amount"]
                player.pay(price, "Chance" if isChance else "Caisse de Communauté")
            case "earn_from_everyone":
                game.okpopup(card["text"])
                game.socket_manager.send_info(
                    f"Vous versez {card['amount']} $ à {player.name}."
                )
                price = 0
                for p in game.players:
                    if p.position is None:
                        continue
                    p.pay(
                        card["amount"],
                        ("Chance " if isChance else "Caisse de Communauté ")
                        + player.name,
                    )
                    game.socket_manager.send_player(p)
                    price += card["amount"]
                player.earn(price, "Chance" if isChance else "Caisse de Communauté")

    def to_dict(self):
        return {"n": self.n}

    def update_from_dict(self, _):
        pass


def may_sell(box):
    box.game.yesnopopup(
        f"Voulez vous vendre {box.name} à la banque ?",
        resolve_no=lambda: None,
        resolve_yes=lambda: sell_to_bank(box),
        foreground=True,
    )


def sell_to_bank(box):
    if box.in_mortgage:
        box.game.myself.earn(box.base_price // 2, f"Vente {box.name}")
        box.player = None
        box.game.okpopup(
            f"Vous avez vendu {box.name} à la banque pour {box.base_price//2} $",
            foreground=True,
        )
    else:
        box.game.myself.earn(box.base_price, f"Vente {box.name}")
        box.player = None
        box.game.okpopup(
            f"Vous avez vendu {box.name} à la banque pour {box.base_price} $",
            foreground=True,
        )
    box.game.socket_manager.send_box(box)
    box.game.socket_manager.send_player(box.game.myself)
    box.game.socket_manager.send_info(
        f"{box.game.myself.name} à vendu {box.name} à la banque"
    )
