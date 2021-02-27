import pygame, math
from . import Window
from ..constants import TILE_WIDTH
from ..graphics import Button

class MapWindow(Window):
	""" This is the map screen, where the map is rendered
	
	It also handles "grab and release", and scrolling to zoom in or out.

	Attributes
	----------
	parentScreen : GameScreen
		Instance of the parent GameScreen, stored because we need to
		access the players list and the dungeon.
	rect : pygame.Rect
		This rectangle is used to represents the window's position.
	__offsetX : int
		Offset along X, used to "travel" in the map.
	__offsetY : int
		Offset along Y, used to "travel" in the map.
	__zoom : int
		Zoom factor.
	__grab : bool
		True if the mouse is pressed, used to handle "grab and release"
	playerPosImg : pygame.Surface
		Stores the little cursor to show a player position.
	background : pygame.Surface
		Stores the background of the map
	viewport : pygame.Surface
		Represent the surface on which the map will be blitted, used
		to give "bounds" to the view
	vewportPos : tuple
		Stores the position of the viewport

	Methods
	-------
	update(events)
		Updates the surface. Called at every loop turn.
	"""
	def __init__(self, game, parentScreen):
		super().__init__(game)
		self.set_colorkey((255,0,255))
		self.fill((255,0,255))
		self.parentScreen = parentScreen
		self.rect = pygame.Rect((game.DISPLAY_SIZE[0]*0.15/2, parentScreen.bottombarwindow.rect.top*0.15/2), (game.DISPLAY_SIZE[0]*0.85, parentScreen.bottombarwindow.rect.top*0.85))
		self.__offsetX = 0
		self.__offsetY = 0
		self.__zoom = 3.0
		self.__grab = False
		self.playerPosImg = pygame.image.load("dungeonX/assets/minimap/playerPos.png").convert()
		self.background = pygame.image.load("dungeonX/assets/minimap/background.png").convert()
		self.__viewport = pygame.Surface((
			math.ceil(self.rect.width - 14*self.rect.width/(self.background.get_width()-14)),
			math.ceil(self.rect.height - 14*self.rect.height/(self.background.get_height()-14))
		))
		self.__viewportPos = (7*self.rect.width/(self.background.get_width()-14)+self.rect.left, 7*self.rect.height/(self.background.get_height()-14)+self.rect.top)
		self.background = pygame.transform.scale(self.background, (self.rect.width, self.rect.height))

		self.floorSelectBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/minimap/floorSelector.png").convert(), (93*3, 25*3))
		self.floorSelectBackground.set_colorkey((0,0,0))
		self.floorSelectPos = (self.get_width()*0.925 - self.floorSelectBackground.get_width(), self.rect.bottom+10)
		self.mapIndex = 0
		BUTTON_SIZE = 20
		self.plusButton = Button(self.game, (self.floorSelectPos[0]+self.floorSelectBackground.get_width()-40-BUTTON_SIZE*2, self.floorSelectPos[1]+(self.floorSelectBackground.get_height()-BUTTON_SIZE)/2), "", size=(BUTTON_SIZE, BUTTON_SIZE), imgPath="dungeonX/assets/ui/plus_button.png", hoverMode='overlay', action=self.decMapIndex)
		self.minusButton = Button(self.game, (self.floorSelectPos[0]+self.floorSelectBackground.get_width()-30-BUTTON_SIZE, self.floorSelectPos[1]+(self.floorSelectBackground.get_height()-BUTTON_SIZE)/2), "", size=(BUTTON_SIZE, BUTTON_SIZE), imgPath="dungeonX/assets/ui/minus_button.png", hoverMode='overlay', action=self.incMapIndex)

		minimap_size = [64*3, 64*3]
		self.background_minimap = pygame.transform.scale(pygame.image.load("dungeonX/assets/minimap/background_minimap.png").convert(), minimap_size)
		self.__viewport_minimap = pygame.Surface([minimap_size[0]-14*3, minimap_size[1]-14*3])
		self.minimap = pygame.Surface(minimap_size, flags=pygame.SRCALPHA)
		self.minimaprect = pygame.Rect([16, 16], minimap_size)

		self.background.set_colorkey((255,0,255))
		self.background_minimap.set_colorkey((255,0,255))
		self.playerPosImg.set_colorkey((0,0,0))

	def incMapIndex(self):
		if self.mapIndex < len(self.parentScreen.dungeon.floors)-1:
			self.mapIndex+=1
			self.resetOffset(self.parentScreen.dungeon.floors[self.mapIndex].startPos)

	def decMapIndex(self):
		if self.mapIndex > 0:
			self.mapIndex-=1
			self.resetOffset(self.parentScreen.dungeon.floors[self.mapIndex].startPos)

	def resetOffset(self, pos=None):
		""" Resets offsetX and offsetY to center the map around the selected player """
		if pos==None:
			pos = self.parentScreen.selectedPlayer.pos

		self.__offsetX = -pos[0]*3*self.__zoom + self.__viewport.get_width()/2 + 1.5*self.__zoom
		self.__offsetY = -pos[1]*3*self.__zoom + self.__viewport.get_height()/2 + 1.5*self.__zoom

	def update(self, events):
		""" Main update method

		Updates the surface. Called at every loop turn. This method
		does the following :
		- Handle events
		- Update Camera
		- Handle turn logic
		- Render the game : 
			1. Render the viewport surface
				- Erase it
				- Copy the minimap image
				- Blit each player position
				- Scale the minimap and blit it on the viewport
					surface, at the right position
			2. Blit the background (to erase the window)
			3. Blit the viewort on the window
		"""

		# --- Handle Events --- #
		for event in events:
			if event.type==pygame.MOUSEWHEEL:
				if 1.5<self.__zoom+0.1*event.y<6:
					mousePos = pygame.mouse.get_pos()
					self.__zoom += 0.1 * event.y
					self.__offsetX -= (mousePos[0] - self.__offsetX - self.rect.left)*0.1*event.y/self.__zoom
					self.__offsetY -= (mousePos[1] - self.__offsetY - self.rect.top)*0.1*event.y/self.__zoom
			if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
				self.__grab = True
			if event.type==pygame.MOUSEBUTTONUP and event.button==1:
				self.__grab = False
			if self.__grab and event.type==pygame.MOUSEMOTION:
				self.__offsetX += event.rel[0]
				self.__offsetY += event.rel[1]

		# --- Render --- #
		self.__viewport.fill((0,0,0))
		img = self.parentScreen.dungeon.floors[self.mapIndex].minimap.copy()
		if self.mapIndex==self.parentScreen.dungeon.currentFloorIndex:
			for player in self.parentScreen.players:
				img.blit(self.playerPosImg, (player.pos[0]*3, player.pos[1]*3))
		self.__viewport.blit(pygame.transform.scale(img, (math.floor(img.get_width()*self.__zoom), math.floor(img.get_height()*self.__zoom))), (self.__offsetX, self.__offsetY))
		

		# ---- Fog rendering ---- #
		fogImg = pygame.transform.scale(self.parentScreen.dungeon.floors[self.mapIndex].layers['fog'], (math.floor(img.get_width()*self.__zoom), math.floor(img.get_height()*self.__zoom))).copy()
		for p in self.parentScreen.players:
			pLoSImage = pygame.transform.scale(p.lineOfSight, (math.floor(p.lineOfSight.get_width()*3/TILE_WIDTH*self.__zoom), math.floor(p.lineOfSight.get_height()*3/TILE_WIDTH*self.__zoom)))
			fogImg.blit(pLoSImage, ((p.pos[0]+0.5)*3*self.__zoom-pLoSImage.get_width()/2, (p.pos[1]+0.5)*3*self.__zoom-pLoSImage.get_height()/2), special_flags=pygame.BLEND_SUB)
		self.__viewport.blit(fogImg, (self.__offsetX, self.__offsetY), special_flags=pygame.BLEND_SUB)

		self.blit(self.background, self.rect)
		self.blit(self.__viewport, self.__viewportPos)

		self.blit(self.floorSelectBackground, self.floorSelectPos)
		self.game.textDisplayer.print("Floor : "+str(-self.mapIndex), (self.floorSelectPos[0]+30, self.floorSelectPos[1]), scale=0.2, rectSize=(self.floorSelectBackground.get_size()), screen=self, center_y=True)
		self.plusButton.update(events)
		self.minusButton.update(events)
		self.blit(self.plusButton.image, self.plusButton.rect)
		self.blit(self.minusButton.image, self.minusButton.rect)

	def updateMinimap(self, events):
		self.__viewport_minimap.fill((0,0,0))
		img = self.parentScreen.dungeon.floors[self.mapIndex].minimap.copy()
		if self.mapIndex==self.parentScreen.dungeon.currentFloorIndex:
			for player in self.parentScreen.players:
				img.blit(self.playerPosImg, (player.pos[0]*3, player.pos[1]*3))
		offsetX = -self.parentScreen.selectedPlayer.pos[0]*3*self.__zoom + self.__viewport_minimap.get_width()/2 - 1.5*self.__zoom
		offsetY = -self.parentScreen.selectedPlayer.pos[1]*3*self.__zoom + self.__viewport_minimap.get_height()/2 - 1.5*self.__zoom
		self.__viewport_minimap.blit(pygame.transform.scale(img, (math.floor(img.get_width()*self.__zoom), math.floor(img.get_height()*self.__zoom))), (offsetX, offsetY))


		# ---- Fog rendering ---- #
		fogImg = pygame.transform.scale(self.parentScreen.dungeon.floors[self.mapIndex].layers['fog'], (math.floor(img.get_width()*self.__zoom), math.floor(img.get_height()*self.__zoom))).copy()
		for p in self.parentScreen.players:
			pLoSImage = pygame.transform.scale(p.lineOfSight, (math.floor(p.lineOfSight.get_width()*3/TILE_WIDTH*self.__zoom), math.floor(p.lineOfSight.get_height()*3/TILE_WIDTH*self.__zoom)))
			fogImg.blit(pLoSImage, ((p.pos[0]+0.5)*3*self.__zoom-pLoSImage.get_width()/2, (p.pos[1]+0.5)*3*self.__zoom-pLoSImage.get_height()/2), special_flags=pygame.BLEND_SUB)
		self.__viewport_minimap.blit(fogImg, (offsetX, offsetY), special_flags=pygame.BLEND_SUB)

		
		self.minimap.blit(self.background_minimap, (0,0))
		self.minimap.blit(self.__viewport_minimap, (7*3, 7*3))
