# Monopoly Game with Pygame

This repository contains the code for a Monopoly game written in Python with Pygame. The game is designed to be played by multiple players on a local network. One player plays the role of the server, the other participants join the game as clients

## Requirements

In order to play the game, you will need to have Python at least 3.9 installed on your machine with pygame.


## How to Play

Clone the repository to your local machine
```
git clone https://github.com/florandefossez/monopoly.git
```

Navigate to the repository directory and run the main.py file with Python
```
cd monopoly
python main.py
```

A CLI prompt should ask you to set up your game.

One player must create a party and serve the game on his local IP address with a port.

The other players join the game and give the IP address and port of the server.

Each player chooses a pawn and a nickname (nicknames must be distinct!)


Once every players have joined the party, they takes turns rolling the dice and moving their piece around the board (by pressing the space key).
The goal of the game is to accumulate wealth and bankrupt your opponents.
The game ends when all players except one have gone bankrupt.

## Pyinstaller

If you're using pyinstaller to share the app with non python users:
```
cd monopoly
pyinstaller --noconfirm --onedir --console --add-data assets;assets/ --add-data chance.json;. --add-data community_chest.json;. --add-data data.json;.  main.py
```
A ./dist/main folder should be created, share the hole folder and run main.exe to start the game !

## Features

- Multiplayer system based on socket connection
- Randomized board layout and chance/community chest cards
- Interactive board with animations for moving pieces and purchasing properties
- System for exchanging goods between players
- Invoices and income history


### Credits

This game was developed by Floran Defossez.

The Monopoly board images used in the game are property of Hasbro.