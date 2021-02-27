import pygame, math
from . import Window
from dungeonX.constants import Attributes
from ..characters.skills import SkillEnum
from ..graphics import Button
from enum import Enum
CHARACTER_SCALE=2.5

class CharacterWindow(Window):
	"""
	This is the character window, it displays informations
	regarding the currently selected character

	"""
	def __init__(self, game, parentScreen):
		self.background = pygame.image.load("dungeonX/assets/ui/characterwindow/background.png")
		self.background = pygame.transform.scale(self.background, (math.floor(self.background.get_width()*CHARACTER_SCALE), math.floor(self.background.get_height()*CHARACTER_SCALE)))
		self.background.set_colorkey((255,0,255))
		super().__init__(game, self.background.get_size())
		self.set_colorkey((0,0,0))
		self.rect = self.get_rect()
		self.rect.move_ip(parentScreen.get_width()-self.get_width(), parentScreen.get_height()-self.get_height())
		self.parentScreen=parentScreen
		self.game=game

		game.textDisplayer.print("Charisma", (10*CHARACTER_SCALE,58*CHARACTER_SCALE), scale=0.2, rectSize=(78*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("Strength", (10*CHARACTER_SCALE,78*CHARACTER_SCALE), scale=0.2, rectSize=(78*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("Dexterity", (10*CHARACTER_SCALE,98*CHARACTER_SCALE), scale=0.2, rectSize=(78*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("Constitution", (10*CHARACTER_SCALE,118*CHARACTER_SCALE), scale=0.2, rectSize=(78*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("Intelligence", (10*CHARACTER_SCALE,138*CHARACTER_SCALE), scale=0.2, rectSize=(78*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("Wisdom", (10*CHARACTER_SCALE,158*CHARACTER_SCALE), scale=0.2, rectSize=(78*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("HP", (10*CHARACTER_SCALE,186*CHARACTER_SCALE), scale=0.2, rectSize=(18*CHARACTER_SCALE, 8*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		game.textDisplayer.print("AC", (71*CHARACTER_SCALE,186*CHARACTER_SCALE), scale=0.2, rectSize=(18*CHARACTER_SCALE, 8*CHARACTER_SCALE), center=True, center_y=True, screen=self.background)
		
		self.bar_background = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/inventory/bar_background.png").convert(), ((math.floor(29*CHARACTER_SCALE)), (math.floor(3*CHARACTER_SCALE))))
		
		self.bar_foreground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/inventory/bar_foreground.png").convert(), ((math.floor(32*CHARACTER_SCALE)), (math.floor(3*CHARACTER_SCALE))))
		
		self.bar_foreground.set_colorkey((0,0,0))
		
	def update(self,event):
		
		player = self.parentScreen.selectedPlayer
		
		self.fill((0,0,0))

		self.blit(self.bar_background, (73*CHARACTER_SCALE, 42*CHARACTER_SCALE))
		self.blit(self.bar_foreground, ((73-(1-player.getExp()/player.expToLevelUp)*29)*CHARACTER_SCALE, 42*CHARACTER_SCALE))
		self.blit(self.background, (0,0))
		self.blit(pygame.transform.scale(player.image,(math.floor((24*CHARACTER_SCALE)), math.floor(36*CHARACTER_SCALE))), (math.floor(8*CHARACTER_SCALE)+2, math.floor(10*CHARACTER_SCALE)+5))

		self.game.textDisplayer.print(player.name, (48*CHARACTER_SCALE,15*CHARACTER_SCALE), scale=0.3, rectSize=(56*CHARACTER_SCALE, 11*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print("lvl\n"+str(player.level), (40*CHARACTER_SCALE,34*CHARACTER_SCALE), scale=0.2, rectSize=(24*CHARACTER_SCALE, 16*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Cha)), (91*CHARACTER_SCALE,58*CHARACTER_SCALE), scale=0.2, rectSize=(17*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Strength)), (91*CHARACTER_SCALE,78*CHARACTER_SCALE), scale=0.2, rectSize=(15*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Dexterity)), (91*CHARACTER_SCALE,98*CHARACTER_SCALE), scale=0.2, rectSize=(15*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Con)), (91*CHARACTER_SCALE,118*CHARACTER_SCALE), scale=0.2, rectSize=(15*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Intelligence)), (91*CHARACTER_SCALE,138*CHARACTER_SCALE), scale=0.2, rectSize=(15*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Wisdom)), (91*CHARACTER_SCALE,158*CHARACTER_SCALE), scale=0.2, rectSize=(15*CHARACTER_SCALE, 10*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.HP)), (30*CHARACTER_SCALE,186*CHARACTER_SCALE), scale=0.2, rectSize=(16*CHARACTER_SCALE, 8*CHARACTER_SCALE), center=True, screen=self)
		
		self.game.textDisplayer.print(str(player.getAttribute(Attributes.Armor)), (91*CHARACTER_SCALE,186*CHARACTER_SCALE), scale=0.2, rectSize=(16*CHARACTER_SCALE, 8*CHARACTER_SCALE), center=True, screen=self)
		
		