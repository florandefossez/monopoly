import pygame
from box import Box, Street
from card import Card

class InputProperty:

    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.selectedProperty = -1
        self.properties = []
        for box in Box.boxes:
            if getattr(box, "player", None) == player:
                self.properties.append(box)
    
    def update(self, rect):
        self.rect = rect
        self.updateProp()

    def updateProp(self):
        if self.selectedProperty == -1:
            self.input_box = pygame.image.load("assets/card.png")
        else:
            box = self.properties[self.selectedProperty]
            self.input_box = Card(self.game, box, False).card
        
        self.input_box = pygame.transform.smoothscale(self.input_box, self.rect.size)
    
    def get_value(self):
        if self.selectedProperty == -1:
            return None
        else:
            return self.properties[self.selectedProperty].n
    
    def draw(self):
        self.game.screen.blit(self.input_box, self.rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.selectedProperty = (self.selectedProperty + 2)%(len(self.properties)+1) -1
                self.updateProp()