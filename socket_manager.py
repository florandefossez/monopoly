import socket
import json
import threading
from player import Player
from box import Box, Street, Gare, Company, Special
from receiveDeal import ReceiveDeal
import pygame
import sys

HEADER = 4


class SocketManager:
    def __init__(self, game):
        self.game = game
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def update_player(self, data):
        Player.update_from_dict(data)

    def update_box(self, data):
        Box.update_from_dict(data)

    def info(self, msg):
        self.game.okpopup(msg["text"])

    def update_dice(self, data):
        self.game.dice1 = data["dice1"]
        self.game.dice2 = data["dice2"]

    def deal(self, data):
        self.game.popups.append(ReceiveDeal(self.game, data))

    def send_player(self, player):
        raise (Exception("should be handled by Client or Server subclass"))

    def send_box(self, box):
        raise (Exception("should be handled by Client or Server subclass"))

    def send_dice(self):
        raise (Exception("should be handled by Client or Server subclass"))

    def send_info(self, text):
        raise (Exception("should be handled by Client or Server subclass"))

    @staticmethod
    def prepare_message(msg):
        body = bytes(json.dumps(msg), "utf-8")
        header = str(len(body)).encode("utf-8").rjust(HEADER, b"0")
        return header + body


class Server(SocketManager):
    def __init__(self, game):
        super().__init__(game)
        self.clients = []
        self.turn = -1

        self.socket.bind(
            (self.game.settings["local_ip"], self.game.settings["local_port"])
        )
        connected_player = 0
        self.socket.listen(5)
        print("En attente de connexion...")
        while connected_player < self.game.settings["n_client"]:
            (clientsocket, address) = self.socket.accept()
            self.clients.append([clientsocket, None])
            threading.Thread(target=self.socket_thread, args=(clientsocket,)).start()
            connected_player += 1
        self.socket.close()
        self.share_players()
        self.next_turn()

    def share_players(self):
        msg = {
            "type": "presentation",
            "address": self.game.settings["image"],
            "name": self.game.settings["name"],
        }
        self.broadcast(json.dumps(msg).encode("utf-8"), None)
        timeout = 0
        for client in self.clients:
            while client[1] is None:
                pygame.time.wait(100)
                timeout += 1
                if timeout >= 100:
                    raise TimeoutError("failed to retrive client information")
            msg["address"] = client[1].address
            msg["name"] = client[1].name
            self.broadcast(json.dumps(msg).encode("utf-8"), client[0])

    def socket_thread(self, client):
        while self.game.running:
            try:
                header = client.recv(HEADER)
            except:
                if not self.game.running:
                    return
                c = [c for c in self.clients if c[0] == client][0]
                self.clients.remove(c)
                if c[1] is not None:
                    self.end(c[1])
                    print(f"Erreur de connexion {c[1].name} a quitté la partie")
                return
            if not header:
                continue
            try:
                raw_msg = client.recv(int(header.decode()))
                msg = json.loads(raw_msg.decode())
            except Exception as e:
                # empty buffer and continue
                print(
                    f"Failed to parse header {header}, {client.recv(4096).decode()}, {e}"
                )
                continue

            if msg["type"] == "presentation":  # first message from client
                p = self.game.add_player(msg["address"], msg["name"])
                print(f"{msg['name']} a rejoint la partie !")
                for c in self.clients:
                    if c[0] == client:
                        c[1] = p

            elif msg["type"] == "end_turn":  # the client ends his turn
                self.next_turn()

            elif msg["type"] == "player":  # the client gives updates of a player
                self.update_player(msg)
                self.broadcast(raw_msg, client)

            elif msg["type"] == "box":  # the client gives updates of a box
                self.update_box(msg)
                self.broadcast(raw_msg, client)

            elif msg["type"] == "info":  # the client give an info to broadcast
                self.info(msg)
                self.broadcast(raw_msg, client)

            elif msg["type"] == "msg":  # the client send a message to someone
                self.private_msg(msg)

            elif msg["type"] == "dice":  # the client tossed the dices
                self.update_dice(msg)
                self.broadcast(raw_msg, client)

            elif msg["type"] == "parc":
                self.game.parc = msg["amount"]
                self.broadcast(raw_msg, client)

            elif msg["type"] == "deal":  # someone send me a deal
                self.deal(msg)

            elif msg["type"] == "bill":
                if msg["player"] == self.game.myself.name:
                    self.game.bill.add(msg["amount"], msg["text"])
                else:
                    self.send_bill(msg["player"], msg["amount"], msg["text"])

            elif msg["type"] == "abandon":
                self.game.okpopup(f"{msg['player']} a abandonné la partie")
                self.broadcast(raw_msg, client)
                self.end([p for p in self.game.players if p.name == msg["name"]][0])

    def next_turn(self):
        players = [self.game.myself] + self.game.players

        if all([p.position is None for p in players]):
            self.game.okpopup("Fin de Partie !")
            return

        for p in players:
            p.his_turn = False

        self.turn = (1 + self.turn) % len(players)
        while players[self.turn].position is None:
            self.turn = (1 + self.turn) % len(players)

        players[self.turn].his_turn = True
        msg = self.prepare_message(
            {"type": "new_turn", "player": players[self.turn].name}
        )

        for client in self.clients:
            client[0].send(msg)

    def end(self, player):
        player.position = None
        self.send_player(player)
        for box in Box.boxes:
            if hasattr(box, "player") and box.player == player:
                box.player = None
                box.in_mortgage = False
                if hasattr(box, "houses"):
                    box.houses = 0
                self.send_box(box)
        if player.his_turn:
            player.his_turn = False
            self.send_end_turn = False
            self.next_turn()

    def broadcast(self, raw_msg, source):
        header = str(len(raw_msg)).encode("utf-8").rjust(HEADER, b"0")
        msg = header + raw_msg
        for client in self.clients:
            if client[0] != source:
                client[0].send(msg)

    def send_player(self, player):
        msg = player.to_dict()
        msg["type"] = "player"
        msg = self.prepare_message(msg)
        for client in self.clients:
            client[0].send(msg)

    def send_box(self, box):
        msg = box.to_dict()
        msg["type"] = "box"
        msg = self.prepare_message(msg)
        for client in self.clients:
            client[0].send(msg)

    def send_dice(self):
        msg = {"type": "dice", "dice1": self.game.dice1, "dice2": self.game.dice2}
        msg = self.prepare_message(msg)
        for client in self.clients:
            client[0].send(msg)

    def send_parc(self):
        msg = {"type": "parc", "amount": self.game.parc}
        msg = self.prepare_message(msg)
        for client in self.clients:
            client[0].send(msg)

    def send_info(self, text):
        msg = {"type": "info", "text": text}
        msg = self.prepare_message(msg)
        for client in self.clients:
            client[0].send(msg)

    def send_deal(self, deal):
        msg = self.prepare_message(deal)
        for client in self.clients:
            if client[1].name == deal["recipient"]:
                client[0].send(msg)

    def send_private_msg(self, text, recipient_name):
        msg = {"text": text, "type": "msg", "recipient": recipient_name}
        msg = self.prepare_message(msg)
        for client in self.clients:
            if client[1].name == recipient_name:
                client[0].send(msg)

    def deal(self, data):
        if data["recipient"] == self.game.myself.name:
            super().deal(data)
        else:
            self.send_deal(data)

    def private_msg(self, msg):
        if msg["recipient"] == self.game.myself.name:
            self.info(msg)
        else:
            self.send_private_msg(msg["text"], msg["recipient"])

    def send_bill(self, player_name, amount, text):
        msg = {"text": text, "type": "bill", "player": player_name, "amount": amount}
        msg = self.prepare_message(msg)
        for client in self.clients:
            if client[1].name == player_name:
                client[0].send(msg)

    def send_abandon(self):
        msg = self.prepare_message({"type": "abandon", "player": self.game.myself.name})
        self.end(self.game.myself)

        for client in self.clients:
            client[0].send(msg)
        if self.game.myself.his_turn:
            self.next_turn()

    def close(self):
        for client in self.clients:
            client[0].close()


class Client(SocketManager):
    def __init__(self, game):
        super().__init__(game)

        self.start = False
        try:
            self.socket.connect(
                (self.game.settings["remote_ip"], self.game.settings["remote_port"])
            )
        except:
            print("La connexion a échoué")
            self.game.running = False
            sys.exit(1)

        msg = {
            "type": "presentation",
            "address": self.game.settings["image"],
            "name": self.game.settings["name"],
        }
        self.socket.send(self.prepare_message(msg))
        print("Partie trouvé !")
        print("En attente des autres joueurs...")
        threading.Thread(target=self.socket_thread, args=(self.socket,)).start()
        while not self.start:
            pygame.time.wait(500)

    def socket_thread(self, server):
        while self.game.running:
            try:
                header = server.recv(HEADER)
            except:
                print("Erreur de connexion")
                self.game.running = False
                sys.exit(1)
            if not header:
                continue
            try:
                raw_msg = server.recv(int(header.decode()))
                msg = json.loads(raw_msg.decode())
            except Exception as e:
                # empty buffer and continue
                print(
                    f"Failed to parse header {header}, {server.recv(4096).decode()}, {e}"
                )
                continue

            if msg["type"] == "presentation":  # server send new player
                self.game.add_player(msg["address"], msg["name"])
                self.start = True

            elif msg["type"] == "new_turn":  # new turn
                for p in self.game.players:
                    p.his_turn = False
                if msg["player"] == self.game.myself.name:
                    self.game.myself.his_turn = True
                else:
                    [p for p in self.game.players if p.name == msg["player"]][
                        0
                    ].his_turn = True

            elif msg["type"] == "player":  # the server gives updates on a player
                self.update_player(msg)

            elif msg["type"] == "box":  # the server gives updates on a box
                self.update_box(msg)

            elif msg["type"] == "info":  # the server gives an info to broadcast
                self.info(msg)

            elif msg["type"] == "msg":  # someone send me a message
                self.info(msg)

            elif msg["type"] == "dice":  # someone tossed the dices
                self.update_dice(msg)

            elif msg["type"] == "parc":
                self.game.parc = msg["amount"]

            elif msg["type"] == "deal":  # someone send me a deal
                self.deal(msg)

            elif msg["type"] == "bill":
                self.game.bill.add(msg["amount"], msg["text"])

            elif msg["type"] == "abandon":
                self.game.okpopup(f"{msg['player']} a abandonné la partie")

    def next_turn(self):
        msg = self.prepare_message({"type": "end_turn"})
        self.socket.send(msg)

    def send_player(self, player):
        msg = player.to_dict()
        msg["type"] = "player"
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_box(self, box):
        msg = box.to_dict()
        msg["type"] = "box"
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_dice(self):
        msg = {"type": "dice", "dice1": self.game.dice1, "dice2": self.game.dice2}
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_parc(self):
        msg = {"type": "parc", "amount": self.game.parc}
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_info(self, text):
        msg = {"type": "info", "text": text}
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_deal(self, deal):
        msg = self.prepare_message(deal)
        self.socket.send(msg)

    def send_private_msg(self, text, recipient_name):
        msg = {"text": text, "type": "msg", "recipient": recipient_name}
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_bill(self, player_name, amount, text):
        msg = {"text": text, "type": "bill", "player": player_name, "amount": amount}
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def send_abandon(self):
        msg = self.prepare_message({"type": "abandon", "player": self.game.myself.name})
        self.socket.send(msg)

    def close(self):
        self.socket.close()
