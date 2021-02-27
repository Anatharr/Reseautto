import pygame, math
from . import Window

SCALE = 3

class StatusWindow(Window):
	def __init__(self, game, parentScreen):
		self.parentScreen = parentScreen
		self.background = pygame.image.load("dungeonX/assets/ui/statuswindow/background.png").convert()
		self.background = pygame.transform.scale(self.background, (math.floor(self.background.get_width()*SCALE), math.floor(self.background.get_height()*SCALE)))
		self.background.set_colorkey((255,0,255))
		super().__init__(game, self.background.get_size())
		self.set_colorkey((0,0,0))
		self.rect = self.get_rect().move((game.DISPLAY_SIZE[0]-self.get_width(), game.DISPLAY_SIZE[1]-self.get_height()))

		self.bar_bg = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/statuswindow/bar_background.png").convert(), (29*SCALE,3*SCALE))
		self.bar_fg = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/statuswindow/bar_foreground.png").convert(), (32*SCALE,3*SCALE))
		self.bar_fg.set_colorkey((0,0,0))

		self.pRects = [
			pygame.Rect((9*SCALE, 8*SCALE), (16*SCALE, 24*SCALE)),
			pygame.Rect((9*SCALE, 36*SCALE), (16*SCALE, 24*SCALE)),
			pygame.Rect((9*SCALE, 64*SCALE), (16*SCALE, 24*SCALE)),
		]

		self.blinkKey = None			
		self.hoveredKey = None

		self.hoveredImg = pygame.transform.scale(pygame.image.load('dungeonX/assets/ui/icons/hovered.png'), ((16+2)*SCALE, (24+2)*SCALE))
		self.keysOverlayImage = pygame.Surface(self.get_size())
		self.keysOverlayImage.set_colorkey((0,0,0))
		for k in range(3):
			game.textDisplayer.print(str(k+1), (self.pRects[k].right-2*SCALE, self.pRects[k].top+2*SCALE), scale=0.2, center=True, center_y=True, screen=self.keysOverlayImage)


	def handleInput(self, events):
		for e in events:
			if e.type == pygame.KEYDOWN:
				for key in range(3):
					if pygame.key.name(e.key)==str(key+1):
						self.parentScreen.selectPlayer(key)
						self.blinkKey = key
			if e.type == pygame.KEYUP:
				self.blinkKey = None			
			if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
				self.hoveredKey = None
				for key in range(3):
					if self.pRects[key].move(self.rect.topleft).collidepoint(e.pos):
						self.hoveredKey = key
						break
			if e.type == pygame.MOUSEBUTTONDOWN:
				self.hoveredKey = None
				for key in range(3):
					if self.pRects[key].move(self.rect.topleft).collidepoint(e.pos):
						self.parentScreen.selectPlayer(key)
						break


	def update(self, events):
		for i in range(3):
			self.blit(self.bar_bg, (34*SCALE, (10+28*i)*SCALE))
			if i<len(self.parentScreen.players):
				player = self.parentScreen.players[i]
				self.blit(self.bar_fg, ((34-(1-player.getHP()/player.maxHP)*29)*SCALE, (10+28*i)*SCALE))

		self.blit(self.background, (0,0))

		for i in range(3):
			if i<len(self.parentScreen.players):
				player = self.parentScreen.players[i]
				self.blit(pygame.transform.scale(player.image, self.pRects[i].size), self.pRects[i])
				txt = "HP:"+str(player.getHP()) + '/' + str(player.maxHP) + "\nAP:" + str(player.getActionPoint()) + '/' + str(player.getActionPointMax())
			else:
				txt = "Dead"
			self.game.textDisplayer.print(txt, (31*SCALE, (16+28*i)*SCALE), scale=0.15, rectSize=(36*SCALE,17*SCALE) ,center=True, center_y=True, screen=self)

		if self.hoveredKey != None:
			self.blit(self.hoveredImg, self.pRects[self.hoveredKey].move((-1*SCALE,-1*SCALE)))
		if self.blinkKey != None:
			self.blit(self.hoveredImg, self.pRects[self.blinkKey].move((-1*SCALE,-1*SCALE)))

		self.blit(self.keysOverlayImage, (0,0))

