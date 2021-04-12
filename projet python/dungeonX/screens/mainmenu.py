import pygame, io
from . import Window
from ..graphics import Button, TextInput
from ..map import Map

class MainMenu(Window):

	def __init__(self,game):
		super().__init__(game)
		
		self.rect = self.get_rect()
		self.background = pygame.image.load("dungeonX/assets/menu/background.png")
		self.background = pygame.transform.scale(self.background, (self.rect.width, self.rect.height))

		self.game.textDisplayer.print("Dungeon(X)", (0,0), rectSize=(self.get_width(),200), center=True, center_y=True, scale=1.2, screen=self.background)


		self.newGameButton  = Button(game,(self.get_width()//2-100,(self.get_height()-150)/5+100)   , "New Game"   ,size=(200,85), textScale=0.3)
		self.loadGameButton = Button(game,(self.get_width()//2-100,2*(self.get_height()-150)/5+100) , "Map Editor" ,size=(200,85), textScale=0.3)
		self.multiplayer     = Button(game,(self.get_width()//2-100,3*(self.get_height()-150)/5+100), "multiplayer",size=(200,85), textScale=0.3)
		self.settingsButton = Button(game,(self.get_width()//2-100,4*(self.get_height()-150)/5+100) , "Settings"   ,size=(200,85), textScale=0.3)
		self.exitButton     = Button(game,(self.get_width()//2-100,5*(self.get_height()-150)/5+100) , "Exit Game"  ,size=(200,85), textScale=0.3, imgPath="dungeonX/assets/ui/button_red.png")
		self.currentscreen='main_menu'
		
	def update(self, events):
		# --- Render --- #
		self.blit(self.background, (0,0))
		self.blit(self.loadGameButton.image, self.loadGameButton.rect)
		self.blit(self.multiplayer.image, self.multiplayer.rect)
		self.blit(self.settingsButton.image, self.settingsButton.rect)
		self.blit(self.exitButton.image, self.exitButton.rect)
		self.blit(self.newGameButton.image, self.newGameButton.rect)

		self.newGameButton.update(events)
		if self.newGameButton.isPressed():
			self.game.setScreen('map_selector')

		self.loadGameButton.update(events)
		if self.loadGameButton.isPressed():
			self.game.setScreen('map_editor')
			self.game.screens['map_editor'].newMap()

		self.multiplayer.update(events)
		if self.multiplayer.isPressed():
			self.game.multiplayer = True
			self.game.setScreen('multiplayer')

		self.settingsButton.update(events)
		if self.settingsButton.isPressed():	
			self.game.setScreen('settings_menu')
		
		self.exitButton.update(events)
		if self.exitButton.isPressed():	
			self.game.running = False