import socket
import json
import threading
from player import Player
from box import Box, Street, Gare, Company, Special
from popup import OkPopup

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
        self.game.popups.append(OkPopup(self.game, msg["text"]))

    def update_dice(self, data):
        self.game.dice1 = data["dice1"]
        self.game.dice2 = data["dice2"]

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
        while connected_player < self.game.settings["n_client"]:
            (clientsocket, address) = self.socket.accept()
            remote_player_image = clientsocket.recv(2048).decode()
            clientsocket.send(bytes(self.game.settings["image"], "utf-8"))
            self.game.add_player(remote_player_image)
            self.clients.append(clientsocket)
            threading.Thread(target=self.socket_thread, args=(clientsocket,)).start()
            connected_player += 1
        self.socket.close()
        self.share_players()
        self.game.our_turn = True

    def share_players(self):
        pass

    def socket_thread(self, client):
        while self.game.running:
            header = client.recv(HEADER)
            if not header:
                continue
            try:
                raw_msg = client.recv(int(header.decode()))
                msg = json.loads(raw_msg.decode())
            except Exception as e:
                # empty buffer and continue
                print(f"Failed to parse header {header}, {client.recv(4096).decode()}, {e}")
                continue

            if msg["type"] == "end_turn":  # the client ends his turn
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
                pass

            elif msg["type"] == "dice":  # the client tossed the dices
                self.update_dice(msg)
                self.broadcast(raw_msg, client)

    def next_turn(self):
        if self.turn == self.game.settings["n_client"] - 1:
            self.turn = -1
            self.game.our_turn = True
        else:
            self.turn += 1
            msg = self.prepare_message({"type": "your_turn"})
            self.clients[self.turn].send(msg)

    def broadcast(self, raw_msg, source):
        header = str(len(raw_msg)).encode("utf-8").rjust(HEADER, b"0")
        msg = header + raw_msg
        for client in self.clients:
            if client != source:
                client.send(msg)

    def send_player(self, player):
        msg = player.to_dict()
        msg["type"] = "player"
        msg = self.prepare_message(msg)
        for client in self.clients:
            client.send(msg)

    def send_box(self, box):
        msg = box.to_dict()
        msg["type"] = "box"
        msg = self.prepare_message(msg)
        for client in self.clients:
            client.send(msg)

    def send_dice(self):
        msg = {"type": "dice", "dice1": self.game.dice1, "dice2": self.game.dice2}
        msg = self.prepare_message(msg)
        for client in self.clients:
            client.send(msg)
    
    def send_info(self, text):
        msg = {"type": "info", "text": text}
        msg = self.prepare_message(msg)
        for client in self.clients:
            client.send(msg)

    def close(self):
        for client in self.clients:
            client.close()


class Client(SocketManager):
    def __init__(self, game):
        super().__init__(game)

        self.socket.connect(
            (self.game.settings["remote_ip"], self.game.settings["remote_port"])
        )
        self.socket.send(bytes(self.game.settings["image"], "utf-8"))
        remote_player_image = self.socket.recv(2048).decode()
        self.game.add_player(remote_player_image)
        self.game.our_turn = False
        threading.Thread(target=self.socket_thread, args=(self.socket,)).start()

    def socket_thread(self, server):
        while self.game.running:
            header = server.recv(HEADER)
            if not header:
                continue
            try:
                raw_msg = server.recv(int(header.decode()))
                msg = json.loads(raw_msg.decode())
            except Exception as e:
                # empty buffer and continue
                print(f"Failed to parse header {header}, {server.recv(4096).decode()}, {e}")
                continue

            if msg["type"] == "your_turn":  # it's my turn
                self.game.our_turn = True

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
    
    def send_info(self, text):
        msg = {"type": "info", "text": text}
        msg = self.prepare_message(msg)
        self.socket.send(msg)

    def close(self):
        self.socket.close()
