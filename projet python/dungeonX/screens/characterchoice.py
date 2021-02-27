import pygame
from . import Window
from ..graphics import Button, TextInput
from ..map import Map
from dungeonX.characters.players.classes import PlayerEnum
from ..constants import TILE_WIDTH
from enum import Enum, auto
from dungeonX.network.networkModule import NetworkModule

CHARACTER_HEIGHT = 128
CHARACTER_WIDTH = 16*CHARACTER_HEIGHT//24
START_BUTTON_WIDTH = 200
START_BUTTON_HEIGHT = 100
class PlayerImages(Enum):
    Fighter = "dungeonX/assets/characters/knight_f_idle_f0.png"
    Rogue = "dungeonX/assets/characters/lizard_m_idle_f0.png"
    Mage = "dungeonX/assets/characters/wizzard_f_hit_f0.png"

class CharacterChoice(Window):
    """ This is the intermediate screen, between starting a new game and actually launching it
	
    It's main functionnality is giving choice of players and launch the game 
	
	Attributes
	----------
	rect: 
		Sets up Rect of screen 
	background : 
		Background of the screen 
	playersButtons : list
		List which contains all player buttons to choose from 
	startButton : Button
		Button than lauches start with selected players
	currentscreen : screen 
		Character screen to call in other screens 
	Methods
	-------
	update(events)
	    Main update Method      
	Private Methods
	-------
	_retrievePlayerTypes():
		Returns the players selected in screen 
	_findPlayerEnum(playerImage: PlayerImages):
		Returns the type of player in terms of png chosen 
	_rotateImage(forButton: Button):
		Rotates image of buttons in loop to make easier selection of player 

	"""
    def __init__(self, game):
        super().__init__(game)
        self.rect= self.get_rect()
        
        self.background = pygame.image.load("dungeonX/assets/menu/background.png")
        self.background = pygame.transform.scale(self.background, (self.rect.width, self.rect.height))
        self.playersButtons = [[], [], []]
        for i in range(3):
            for player in PlayerImages:
                self.playersButtons[i] += Button(game,(self.get_width()*(1+i)//4-CHARACTER_WIDTH//2, (self.get_height()-CHARACTER_HEIGHT)//2), "", imgPath=player.value, size=(CHARACTER_WIDTH,CHARACTER_HEIGHT)),

        self.indexes = [0,1,2]

        self.backbutton = Button(game,(20,20), "",size=(50,50),imgPath="dungeonX/assets/menu/back_arrow.png", textScale=0.3)

        self.startButton = Button(game,(self.get_width()//2-START_BUTTON_WIDTH//2,5*self.get_height()//6-START_BUTTON_HEIGHT//2),"Start",(START_BUTTON_WIDTH, START_BUTTON_HEIGHT))
        self.currentscreen = 'character_choice'

    def update(self,events):
        self.blit(self.background, (0,0))
        self.game.textDisplayer.print("Choose your Characters",(0,50), rectSize=(self.get_width(),200), center=True, scale=0.5)

        for i in range(3):
            button = self.playersButtons[i][self.indexes[i]]
            button.update(events)
            self.blit(button.image, button.rect)
            if button.isPressed():
                self.indexes[i] = (self.indexes[i]+1)%3

        self.blit(self.startButton.image,self.startButton.rect)
        self.startButton.update(events)
        if self.startButton.isPressed():
            if self.game.multiplayer:
                if self.game.joining:
                    print("plz enter an addr to connect")
                    addr = str(input())    
                    print("plz enter a port to connect")
                    port = int( input())
                network = NetworkModule(connection_addr=tuple((addr,port))) if self.game.joining else NetworkModule()
                network.start()
                
            self.game.screens["game"].selectDefaultPlayers(self._retrievePlayerTypes())
            self.game.screens["game"].setState('walk')
            self.game.screens["game"].dungeon.loadFloor()
            self.game.setScreen('game')

        self.backbutton.update(events)
        self.blit(self.backbutton.image, self.backbutton.rect)

        if self.backbutton.isPressed():
            if self.game.multiplayer:
                self.game.setScreen('multiplayer')
            else:
                self.game.setScreen('map_selector')
                

    def _retrievePlayerTypes(self):
        playerTypes = []
        for i in range(3):
            playerTypes.append(self._findPlayerEnum(self.indexes[i]))
        return playerTypes

    def _findPlayerEnum(self, index):
        if index==0: return PlayerEnum.Fighter
        elif index==1: return PlayerEnum.Rogue
        elif index==2: return PlayerEnum.Mage
        else: return
            

    # def _rotateImage(self, forButton: Button):
    #     currentPlayer = None
    #     for player in PlayerImages:
    #         if player.value == forButton.imagePath: currentPlayer = player
    #     for player in PlayerImages:
    #         if player != currentPlayer: forButton.imagePath = player.value
