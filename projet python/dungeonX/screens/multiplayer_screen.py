import pygame, io
from . import Window
from ..graphics import Button
class Multiplayer_screen(Window):
    def __init__(self, game):
        super().__init__(game)
        self.rect = self.get_rect()
        self.background = pygame.image.load("dungeonX/assets/menu/background.png")
       
        self.backbutton = Button(game,(20,+20), "", size=(50,50), imgPath="dungeonX/assets/menu/back_arrow.png", textScale=0.3)
        self.background = pygame.transform.scale(self.background, (self.rect.width, self.rect.height))

        self.game.textDisplayer.print("multiplayer mode", (0,self.get_height()/4-150), rectSize=(self.get_width(),200), center=True, center_y=True, scale=0.3, screen=self.background)

        self.newPartieButton    = Button(game,(self.get_width()//2-210,self.get_height()/4), "new partie"   , size=(200,100), textScale=0.3)
        self.joinPartieButton   = Button(game,(self.get_width()//2+10 ,self.get_height()/4), "join a partie", size=(200,100), textScale=0.3)

    

    def update(self, events):
        self.blit(self.background, (0,0))

        self.backbutton.update(events)
        self.blit(self.backbutton.image,self.backbutton.rect)

        self.newPartieButton.update(events)
        self.blit(self.newPartieButton.image,self.newPartieButton.rect)

        self.joinPartieButton.update(events)
        self.blit(self.joinPartieButton.image,self.joinPartieButton.rect)

        if self.backbutton.isPressed():
            self.game.multiplayer=False
            self.game.setScreen('main_menu')

        if self.newPartieButton.isPressed():
            self.game.setScreen('character_choice')

        elif self.joinPartieButton.isPressed():
            self.game.joining = True
            self.game.setScreen('character_choice')


