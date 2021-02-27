import pygame
from . import Window
#from ..characters.players.classes import Fighter, Mage, Rogue
from dungeonX.characters.players.classes import Fighter, Mage, Rogue
from dungeonX.characters.skills import *
from dungeonX.objects import *

SCALE = 3
ACTION_SIZE = (14*SCALE, 14*SCALE)
BAR_SIZE = (156*SCALE, 28*SCALE)

class defaultActionsDict(dict):
	def __missing__(self, key):
		if isinstance(key, Fighter):
			value = {
				'a': 'Rest',
				'z': None,
				'e': None,
				'r': None,
				't': None,
				'y': None,
				'c': 'Character',
				'i': 'Inventory',
				'm': 'Map',
			}
		elif isinstance(key, Mage):
			value = {
				'a': 'Fireball',
				'z': 'AcidStream',
				'e': 'MeteorSwarm',
				'r': 'Convert_enemy',
				't': 'Rest',
				'y': None,
				'c': 'Character',
				'i': 'Inventory',
				'm': 'Map',
			}
		elif isinstance(key, Rogue):
			value = {
				'a': 'Stealth',
				'z': 'DisableDevice',
				'e': 'Perception',
				'r': 'Rest',
				't': None,
				'y': None,
				'c': 'Character',
				'i': 'Inventory',
				'm': 'Map',
			}
		else:
			value = {
				'a': None,
				'z': None,
				'e': None,
				'r': None,
				't': None,
				'y': None,
				'c': 'Character',
				'i': 'Inventory',
				'm': 'Map',
			}
		self[key] = value
		return value


class BottomBarWindow(Window):
	def __init__(self, game):
		super().__init__(game, game.get_size())
		self.set_colorkey((0,0,0))
		self.background = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/bottombar.png").convert(), BAR_SIZE)
		self.background.set_colorkey((0,0,0))
		self.rect = self.background.get_rect().move(((game.get_width()-BAR_SIZE[0])//2, game.get_height()-BAR_SIZE[1]-5))
		self.hoveredAction = None
		self.hoveredImg = pygame.transform.scale(pygame.image.load('dungeonX/assets/ui/icons/hovered.png'), ACTION_SIZE)
		self.actionsKeysImg = pygame.Surface(self.background.get_size())
		self.actionsKeysImg.set_colorkey((0,0,0))
		self.actionsIcons = {
			'Taunt': None,
			'Fireball': None,
			'AcidStream': None,
			'MeteorSwarm': None,
			'Inventory': None,
			'Map': None,
			'Stealth':None,
			'DisableDevice':None,
			'Perception':None,
			'Character':None,
			'Convert_enemy':None,
			'Rest':None,
			'AcidStream':None,
			'MeteorSwarm':None
		}
		for name in self.actionsIcons:
			self.actionsIcons[name] = pygame.transform.scale(pygame.image.load('dungeonX/assets/ui/icons/'+name+'.png').convert(), ACTION_SIZE)
			self.actionsIcons[name].set_colorkey((0,0,0))
		self.actionsRects = {
			'a': pygame.Rect((7*SCALE+16*SCALE*0,7*SCALE), ACTION_SIZE),
			'z': pygame.Rect((7*SCALE+16*SCALE*1,7*SCALE), ACTION_SIZE),
			'e': pygame.Rect((7*SCALE+16*SCALE*2,7*SCALE), ACTION_SIZE),
			'r': pygame.Rect((7*SCALE+16*SCALE*3,7*SCALE), ACTION_SIZE),
			't': pygame.Rect((7*SCALE+16*SCALE*4,7*SCALE), ACTION_SIZE),
			'y': pygame.Rect((7*SCALE+16*SCALE*5,7*SCALE), ACTION_SIZE),
			'c': pygame.Rect((7*SCALE+16*SCALE*6,7*SCALE), ACTION_SIZE),
			'i': pygame.Rect((7*SCALE+16*SCALE*7,7*SCALE), ACTION_SIZE),
			'm': pygame.Rect((7*SCALE+16*SCALE*8,7*SCALE), ACTION_SIZE),
		}
		self.actions = defaultActionsDict()
		self.blinkKey = None

		self.popupBackground = pygame.image.load("dungeonX/assets/ui/popup.png").convert()
		self.popupBackground.set_colorkey((0,0,0))

		self.keysOverlayImage = pygame.Surface(self.background.get_size())
		self.keysOverlayImage.set_colorkey((0,0,0))
		for k in 'azertycim':
			game.game.textDisplayer.print(k, (self.actionsRects[k].right-ACTION_SIZE[1]/4, self.actionsRects[k].bottom-ACTION_SIZE[0]/4), scale=0.2, center=True, center_y=True, screen=self.keysOverlayImage)
		
	def assignAction(self, key, actionName):
		if key not in 'azerty':
			print("WARNING: Invalid key to assign action : "+key)
			return
		self.actions[self.game.selectedPlayer][key] = actionName

	def executeAction(self, key):
		self.game.selectedActionName = None
		if key=='i':
			if self.game.state == 'inventory_opened':
				self.game.resumeState()
			else:
				self.game.setState('inventory_opened')
		elif key=='m':
			if self.game.state == 'map_opened':
				self.game.resumeState()
			else:
				self.game.mapwindow.resetOffset()
				self.game.setState('map_opened')
		elif key =='c':
			self.game.displaycharacterwindow = not self.game.displaycharacterwindow

		else:
			actionName = self.actions[self.game.selectedPlayer][key]
			if actionName == "Stealth":
				self.game.selectedPlayer.AtemptToApplySkill(SkillEnum.Stealth, alwaysSuccess=True)
			elif actionName == "Perception":
				self.game.selectedPlayer.AtemptToApplySkill(SkillEnum.Perception, alwaysSuccess=True)
			elif actionName == "Rest":
				self.game.selectedPlayer.rest()
			else: self.game.selectedActionName = actionName


	def getDetails(self, actionName):
		if actionName == 'Taunt':
			return ("Range: 5\nCost: 1 Action Point\n---\nTaunts nearby enemies to attack you.", (10,0), 0.15, (230,90))
		if actionName == 'Fireball':
			return ("Range: 5\nZone size: 3\nCost: 6 Action Points\n---\nLaunch a huge fireball to burn your enemies.", (10,0), 0.15, (230,110))
		if actionName == 'Stealth':
			return ("Cost: 1 Action Point\nDuration: 1 turns\n---\nBecome invisible to escape enemies.", (10,0), 0.15, (230,110))
		if actionName == 'DisableDevice':
			return ("Range: 6\nCost: 1 Action Point\n---\nDisable the nearest trap, or unlock a door, a chest without key.", (10,0), 0.15, (230,110))
		if actionName == 'Perception':
			return ("Cost: 1 Action Point\nDuration: 2 turns\n---\nExtends your line of sight during a limited time.", (10,0), 0.15, (230,110))
		if actionName == 'Convert_enemy':
			return ("Range: 2\nCost: 1 Action Point\n---\nConverts an enemy into a friendly creature.", (10,0), 0.15, (230,110))
		if actionName == 'Inventory':
			return ("Inventory", (0,0), 0.2, (140,30))
		if actionName == 'Map':
			return ("Minimap", (0,0), 0.2, (140,30))
		if actionName == 'Character':
			return ("Character sheet", (0,0), 0.2, (140,50))
		if actionName == 'Rest' :
			return ("Pass your turn and gain 20 HP.",(10,0), 0.15, (230,90))
		if actionName == 'AcidStream' :
			return ("Range:1\nCost: 3 Action Points\n---\nReleases a stream of acid onto a chosen enemy.",(10,0), 0.15, (230,110))
		if actionName == 'MeteorSwarm' :
			return ("Range:1\nCost: 9 Action Points\n---\nLaunches a meteor swarm onto a chosen enemy.",(10,0), 0.15, (230,110))

		return ("", None, 0, None)


	def update(self, events):
		for e in events:
			if e.type == pygame.KEYDOWN:
				if pygame.key.name(e.key) in 'azertycim':
					self.executeAction(pygame.key.name(e.key))
					self.blinkKey = pygame.key.name(e.key)
			if e.type == pygame.KEYUP:
				self.blinkKey = None			
			if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
				self.hoveredAction = None
				for key in 'azertycim':
					if self.actionsRects[key].move(self.rect.topleft).collidepoint(e.pos):
						self.hoveredAction = key
						break
			if e.type == pygame.MOUSEBUTTONDOWN:
				self.hoveredAction = None
				for key in 'azertycim':
					if self.actionsRects[key].move(self.rect.topleft).collidepoint(e.pos):
						self.executeAction(key)
						break

		self.fill((0,0,0))
		self.blit(self.background, self.rect)
		for key in 'azertycim':
			actionName = self.actions[self.game.selectedPlayer][key]
			if actionName:
				self.blit(self.actionsIcons[actionName], self.actionsRects[key].move(self.rect.topleft))
			if self.hoveredAction == key:
				self.blit(self.hoveredImg, self.actionsRects[key].move(self.rect.topleft))

				text, pos, scale, size = self.getDetails(actionName)
				if size:
					popup=pygame.transform.scale(self.popupBackground, size)
					self.game.game.textDisplayer.print(text, pos, screen=popup, scale=scale, rectSize=size, center=True, center_y=True)
					self.blit(popup, (self.actionsRects[key].left+self.rect.left, self.actionsRects[key].top+self.rect.top-size[1]-10))


		if self.blinkKey!=None:
			self.blit(self.hoveredImg, self.actionsRects[self.blinkKey].move(self.rect.topleft))

		self.blit(self.keysOverlayImage, self.rect)
