import pygame, io
from . import Window, MainMenu, PauseMenu, GameScreen, MapEditorScreen, CharacterChoice, LogWindow, MapSelectorScreen
from ..graphics import Button, TextInput
from ..map import Map
from ..constants import TILE_WIDTH

class SettingsMenu(Window):
    def __init__(self,game):
        super().__init__(game)
        self.rect = self.get_rect()
        self.background = pygame.image.load("dungeonX/assets/menu/background.png")
        self.backbutton = Button(game,(20,+20), "",size=(50,50),imgPath="dungeonX/assets/menu/back_arrow.png", textScale=0.3,action=lambda:self.game.setScreen('main_menu'))
        self.background = pygame.transform.scale(self.background, (self.rect.width, self.rect.height))

        self.game.textDisplayer.print("Screen Resolution", (0,self.get_height()/4-150), rectSize=(self.get_width(),200), center=True, center_y=True, scale=0.3, screen=self.background)

        self.normalresButton = Button(game,(self.get_width()//2-210,self.get_height()/4), "1280 x 720", size=(200,100), textScale=0.3)
        self.highresButton = Button(game,(self.get_width()//2+10,self.get_height()/4), "1920 x 1080", size=(200,100), textScale=0.3)
        self.normalresButtonDisabled = Button(game,(self.get_width()//2-210,self.get_height()/4), "1280 x 720", size=(200,100), textScale=0.3, imgPath="dungeonX/assets/ui/button_gray.png", action=lambda: self.resizeWindow(res=(1280,720)))
        self.highresButtonDisabled = Button(game,(self.get_width()//2+10,self.get_height()/4), "1920 x 1080", size=(200,100), textScale=0.3, imgPath="dungeonX/assets/ui/button_gray.png", action=lambda: self.resizeWindow(res=(1920,1080)))

        self.fullscreenButton = Button(game,(self.get_width()//2-100, 2*self.get_height()/4), "Fullscreen",size=(200,100), textScale=0.3, action=self.game.toggleFullscreen)
        self.fullscreenButtonDisabled = Button(game,(self.get_width()//2-100, 2*self.get_height()/4), "Fullscreen",size=(200,100), textScale=0.3, imgPath="dungeonX/assets/ui/button_gray.png", action=self.game.toggleFullscreen)
        self.keyBindingButton = Button(game,(self.get_width()//2-100,3*self.get_height()/4), "Key Bindings",size=(200,100), textScale=0.3)

        self.currentscreen = 'settings_menu'

    def resizeWindow(self, res):
        self.game.DISPLAY_SIZE = res
        self.game.display = pygame.display.set_mode(self.game.DISPLAY_SIZE)
        dungeon = self.game.screens["game"].dungeon
        self.game.screens = {
            "main_menu" : MainMenu(self.game),
            "settings_menu": SettingsMenu(self.game),
            "character_choice": CharacterChoice(self.game),
            "map_selector": MapSelectorScreen(self.game),
            "game" : GameScreen(self.game, dungeon=dungeon),
            "map_editor" : MapEditorScreen(self.game),
        }
        self.game.log=LogWindow(self.game)


    def update(self, events):
        # --- Render --- #
        self.blit(self.background, (0,0))

        self.keyBindingButton.update(events)
        self.blit(self.keyBindingButton.image, self.keyBindingButton.rect)
        self.backbutton.update(events)
        self.blit(self.backbutton.image,self.backbutton.rect)

        if self.game.fullscreen:
            self.fullscreenButton.update(events)
            self.blit(self.fullscreenButton.image, self.fullscreenButton.rect)
        else:
            self.fullscreenButtonDisabled.update(events)
            self.blit(self.fullscreenButtonDisabled.image, self.fullscreenButtonDisabled.rect)


        if self.game.DISPLAY_SIZE == (1280,720):
            self.normalresButton.update(events)
            self.blit(self.normalresButton.image, self.normalresButton.rect)
        else:
            self.normalresButtonDisabled.update(events)
            self.blit(self.normalresButtonDisabled.image, self.normalresButtonDisabled.rect)

        if self.game.DISPLAY_SIZE == (1920,1080):
            self.highresButton.update(events)
            self.blit(self.highresButton.image, self.highresButton.rect)
        else:
            self.highresButtonDisabled.update(events)
            self.blit(self.highresButtonDisabled.image, self.highresButtonDisabled.rect)

      
        if self.keyBindingButton.isPressed():	
            pass
