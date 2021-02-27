import pygame, math, random
from collections import defaultdict
from .constants import TILE_WIDTH

### Map functions ###
# they are here to avoid a circular import with the map file,
# this is a hotfix and should change in future updates.
def posToVect(pos):
    return pygame.Vector2(pos)*TILE_WIDTH



class Button(pygame.sprite.Sprite):
	""" Simple class to represent a button

	This class is used to represent a button in any screen. It
	inherits from pygame.sprite.Sprite in order to render it easily in
	a SpriteGroup if there are several graphical objects. It
	implements a little scaling effect when the mouse is over the
	button. In order to optimize rendering, two images are crafted
	when the button is created (__image, __hoveredImage).

	Attributes
	----------
	game : Game
		the global instance of the game, available here if needed.
	__image : pygame.Surface
		image of the button when the mouse is not over the button
	__hoveredImage : pygame.Surface
		image of the button when the mouse is over the button
	rect : pygame.Rect
		this rectangle defines the position and size of the button,
		it must be used with pygame's sprites, and is useful to
		compute collisions
	image : pygame.Surface
		the current image to render, it will be either __image or
		__hoveredImage
	__hovered : bool
		True if the mouse is currently over the button
	__isPressed : bool
		True when the button is pressed, only during one loop turn

	Methods
	-------
	update(events)
		Updates the button. It must be called at every loop turn.
	isPressed() : bool
		Getter for __isPressed
	"""
	def __init__(self, game, pos:tuple, text:str, size: tuple = None, imgPath: str = "dungeonX/assets/ui/button_green.png", textScale=0.5, textLineSpacing=1, hoverMode='scale', action=None):
		super().__init__()
		img = pygame.image.load(imgPath)
		if not size:
			size = img.get_rect().size
		self.__size = size
		self.__path = imgPath
		self.action = action
		self.game = game
		self.__hovered = False
		self.__isPressed = False
		self.hoverMode = hoverMode

		self.__image = pygame.transform.scale(img, size)
		game.textDisplayer.print(text, (6,0), scale=textScale, lineSpacing=textLineSpacing, rectSize=(size[0]-10, size[1]), center=True, screen=self.__image)
		
		if hoverMode=='overlay':
			self.__hoveredImage = self.__image.copy()
			self.__hoveredImage.blit(pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/icons/hovered_black.png"), size), (0,0))
		else:
			if hoverMode!='scale':
				print("Warning : Unknown hoverMode '"+hoverMode+"'")
			self.__hoveredImage = pygame.transform.scale(self.__image, (size[0]+10, size[1]+10))
		
		self.__image.set_colorkey((0,0,0))
		self.__hoveredImage.set_colorkey((0,0,0))
		self.image = self.__image
		self.rect = self.__image.get_rect()
		self.rect.topleft = pos

	def update(self, events):
		""" Updates the button

		This method must be called at every loop turn
		"""
		if self.rect.collidepoint(pygame.mouse.get_pos()) and not self.__hovered:
			self.__hovered = True
			if self.hoverMode=='scale':
				self.rect.inflate_ip(10, 10)
		elif not self.rect.collidepoint(pygame.mouse.get_pos()) and self.__hovered:
			if self.hoverMode=='scale':
				self.rect.inflate_ip(-10, -10)
			self.__hovered = False

		if self.__hovered:
			self.image = self.__hoveredImage
		else:
			self.image = self.__image

		for event in events:
			if event.type==pygame.MOUSEBUTTONUP and self.__hovered:
				self.__isPressed = True
				if self.action:
					self.action()
				return
		self.__isPressed = False

	def isPressed(self) -> bool:
		""" Getter for __isPressed """
		return self.__isPressed

	# @property
	# def imagePath(self):
	# 	return self.__path

	# @imagePath.setter
	# def imagePath(self, imgPath):
	# 	img = pygame.image.load(imgPath)
	# 	self.__image = pygame.transform.scale(img, self.__size)
	# 	self.image = self.__image
	# 	self.__path = imgPath
	# 	self.__hoveredImage = pygame.transform.scale(self.__image, (self.__size[0]+10, self.__size[1]+10))
	# 	self.__image.set_colorkey((0,0,0))
	# 	self.__hoveredImage.set_colorkey((0,0,0))

	


class TextInput(pygame.Surface):
	def __init__(self, game, pos, width=10, textScale=0.3):
		self.game = game
		self.textScale = textScale
		super().__init__((game.textDisplayer.getWidthOf('W', scale=textScale)*width+15, game.textDisplayer.height*textScale+10))
		self.selected = False
		self.rect = self.get_rect().move(pos)
		self.text = ""
		self.width = width

	def focus(self):
		pygame.key.start_text_input()
		self.selected = True

	def unfocus(self):
		pygame.key.stop_text_input()
		self.selected = False

	def update(self, events):
		for event in events:
			if event.type==pygame.MOUSEBUTTONDOWN:
				if self.rect.collidepoint(event.pos):
					self.focus()
				else:
					self.unfocus()
			if self.selected and event.type==pygame.KEYDOWN:
				if event.key==pygame.K_BACKSPACE:
					self.text = self.text[:-1]
			if self.selected and event.type==pygame.TEXTINPUT:
				if len(self.text)<self.width:
					self.text += event.text

		if self.selected:
			self.fill((100, 100, 100))
		elif self.rect.collidepoint(pygame.mouse.get_pos()):
			self.fill((70, 70, 70))
		else:
			self.fill((50 ,50 ,50))

		self.game.textDisplayer.print(self.text+('_' if self.selected and len(self.text)<self.width else ''), (10,0), rectSize=self.rect.size, scale=self.textScale, screen=self)


class Cell():
	""" Simple class to represent an overlay for a cell

	This class is used to draw overlays, i.e. a collection of cells
	on a certain color, with a given transparency, to indicate a zone.

	Attributes
	----------
	img : pygame.Surface
		this image represent one cell, and is crafted once in __init__
		in order to optimize rendering

	Methods
	-------
	drawCells(screen, cells, cameraPos)
		Draws the given collection of cells on the given screen, with
		an offset given by the cameraPos
	"""

	def __init__(self, color):
		self.img = pygame.Surface((TILE_WIDTH, TILE_WIDTH), pygame.SRCALPHA)
		self.img.fill(list(color)+[128] if len(color)<4 else color)
		pygame.draw.rect(self.img, color, pygame.Rect(0,0,TILE_WIDTH,TILE_WIDTH), width=1)

	def drawCells(self, screen, cells, cameraPos):
		""" Draws the given collection of cells
		
		Parameters
		----------
		screen : pygame.Surface
			screen where the cells must be drawn
		cells : list
			list of tuple representing each cell position
		cameraPos : tuple
			the current cameraPos, needed to correctly draw the cells
		"""
		for cell in cells:
			cellVect = posToVect(cell) - cameraPos
			screen.blit(self.img, cellVect)



class TextDisplayer:
	""" Class is used to print any text on the screen

	This class is instancied once in the initialization of the game.
	It can print any text within the printable ascii characters, and
	common accents are being automatically removed (not all accents
	are supported tho, all unknown characters will be replaced with
	question marks). The font is automatically loaded from a file
	where all characters must be given in ascii order and separated
	with a vertical line of the sepColor (0,255,0 by default).

	Attributes
	----------
	game : Game
		the global instance of the game, available here if needed.
	height : int
		height of the font, without considering any scale
	__chars : dict
		this dict contains all images for every possible character

	Methods
	-------
	convertText(text) : str
		Returns a new text where almost all accents are replaced
	getWidthOf(text, scale=1) : int
		Returns the width that the given text will take, according to
		the specified scale
	print(text, pos, scale=1, lineSpacing=1, rectSize=None, center=False, screen=None)
		Draws the given text on a screen

	"""
	def __init__(self, game, path="dungeonX/assets/ui/font_white.png", sepColor=pygame.Color(0,255,0)):
		self.game = game
		fontImg = pygame.image.load(path)
		self.height = fontImg.get_height()
		self.__chars = {}

		asciiIndex = ord(' ')
		x=0; tx=0
		while x <= fontImg.get_width():
			if x==fontImg.get_width() or fontImg.get_at((x, 0)) == sepColor:
				self.__chars[chr(asciiIndex)] = pygame.Surface((tx, self.height))
				self.__chars[chr(asciiIndex)].blit(fontImg, (0,0), (x-tx, 0, tx, self.height))
				self.__chars[chr(asciiIndex)].set_colorkey((0,0,0))
				asciiIndex += 1
				tx=-1
			x+=1; tx+=1

	def convertText(self, text:str) -> str:
		""" Returns a new text where almost all accents are replaced """
		old = 'áàâäéèêëíìîïóòôöúùûüÁÀÂÄÉÈÊËÍÌÎÏÓÒÔÖÚÙÛÜ'
		new = 'aaaaeeeeiiiioooouuuuAAAAEEEEIIIIOOOOUUUU'
		for i in range(len(old)):
			text = text.replace(old[i], new[i])
		return text

	def getWidthOf(self, text, scale=1):
		""" Returns the width that the given text will take, according to
		the specified scale """
		text = self.convertText(text)
		return sum([self.__chars[c].get_width()*scale for c in text])

	def print(self, text, pos, scale=1, lineSpacing=1, rectSize=(0,0), center=False, screen=None, center_y=True):
		""" Draws the given text on a screen
		
		Parameters
		----------
		text : str
			the text to draw
		pos : tuple
			the position where the text must be drawn
		scale : int
			scale of all the text
		lineSpacing : int
			scale of the line spacing
		rectSize : tuple
			size of the rectangle that may contain the text, needed
			if the center parameter is True
		center : bool
			boolean defining whether the text should be centered on
			the given rectSize or not
		screen : pygame.Surface
			custom screen to draw the text to, defaults to the game
			currentScreen.
		"""
		self.Yoffset=0
		if not screen:
			screen = self.game.screens[self.game.currentScreen]
		text = self.convertText(text)


		if rectSize[0]:
			formattedText = defaultdict(list)

			for i, word in enumerate(text.split('\n')):
				formattedText[str(i)]+=[word]

			for i in list(formattedText.keys()):
				j=1
				# if self.getWidthOf(formattedText[i][0], scale) >= rectSize[0]:
				for word in formattedText[i][0].split(' '):
					if self.getWidthOf(' '.join(formattedText[i+'.'+str(j)]+[word]), scale) >= rectSize[0]:
						j+=1
					formattedText[i+'.'+str(j)]+=[word]
				del formattedText[i]
		else:
			formattedText = {0: [text]}
		if center_y:
			offsetY = (rectSize[1]-self.height*scale*lineSpacing*(len(formattedText)))//2
		else:
			offsetY=0
		for i in formattedText:
			offsetX = (rectSize[0]-self.getWidthOf(' '.join(formattedText[i]), scale))//2 if center else 0
			for c in ' '.join(formattedText[i]):
				if not c in self.__chars:
					c = '?'
				size = self.__chars[c].get_size()
				charImg = pygame.transform.scale(self.__chars[c], (math.floor(size[0]*scale), math.floor(size[1]*scale)))
				screen.blit(charImg, (pos[0]+offsetX, pos[1]+offsetY))
				offsetX += charImg.get_width()
			offsetY+=self.height*scale*lineSpacing
			self.Yoffset+=self.height*scale*lineSpacing	
		self.Yoffset+=self.height*scale*lineSpacing	



	def get_offsety(self):
		"""this method is mainly for logs display and should eventually be renamed properly 
"""
		return self.Yoffset

class ParticleSystem:
	def __init__(self, game):
		self.game = game
		self.screen = None
		self.particles = []
		self.availableTypes = ("fire", "spark", "fire_cell")
		self.needsUpdate = True
		self.__images = {
			"fire": [
				pygame.image.load('dungeonX/assets/particles/fire_f0.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f1.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f2.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f3.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f4.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f5.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f6.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_f7.png').convert(),
			],
			"spark": [
				pygame.image.load('dungeonX/assets/particles/fire_white_f0.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f1.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f2.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f3.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f4.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f5.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f6.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_white_f7.png').convert(),
			],
			"fire_cell": [
				pygame.image.load('dungeonX/assets/particles/fire_cell_f0.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f1.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f2.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f3.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f4.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f5.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f6.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f7.png').convert(),
				pygame.image.load('dungeonX/assets/particles/fire_cell_f8.png').convert(),
			],
		}
		self.__particlesConfig = {
			"fire": {
				'posOffset': [-16, -14],
				'velocityX': [-1.5, 1.5],
				'velocityY': [-3, -2],
				'ttl': [400, 600],
				'frameTimings': [400, 350, 300, 250, 200, 150, 100, 50],
				'special_flags': pygame.BLEND_ADD,
			},
			"fire_cell": {
				'posOffset': -8,
				'velocityX': 0,
				'velocityY': 0,
				'ttl': [400, 440],
				'frameTimings': [360, 320, 280, 240, 200, 160, 120, 80, 40],
				'special_flags': 0				
			},
			"spark": {
				'posOffset': [-16, -14],
				'velocityX': [-5, 5],
				'velocityY': [-5, 5],
				'ttl': [400, 600],
				'frameTimings': [400, 350, 300, 250, 200, 150, 100, 50],
				'special_flags': pygame.BLEND_ADD			
			}
		}

		for key in self.__images:
			for img in self.__images[key]:
				img.set_colorkey((0,0,0))


	def attachScreen(self, screen):
		self.screen = screen

	def createParticle(self, particleType, pos, count=1):
		if particleType not in self.availableTypes:
			print("WARNING: Unknown particle type: "+particleType)
			return
		config = self.__particlesConfig[particleType]

		for _ in range(count):
			values = {}
			for key in config:
				if type(config[key]) is list:
					values[key] = random.uniform(config[key][0], config[key][1])
				else:
					values[key] = config[key]
		
			particlePos = [pos[0]+values['posOffset'], pos[1]+values['posOffset']]
			particleVelocity = [values['velocityX'], values['velocityY']]

		self.particles.append([particleType, particlePos, particleVelocity, values['ttl'], values['special_flags']])

	def update(self, dt):
		for i, particle in sorted(enumerate(self.particles), reverse=True):
			frame = 0
			for t in self.__particlesConfig[particle[0]]['frameTimings']:
				if particle[3] > t:
					break
				frame += 1

			frame = min(frame, len(self.__images[particle[0]])-1)

			if self.screen:
				self.screen.blit(self.__images[particle[0]][frame], particle[1], special_flags=particle[4])
			else:
				self.game.screens[self.game.currentScreen].blit(self.__images[particle[0]][frame], particle[1], special_flags=particle[4])
			a = particle[2][0]
			self.particles[i][1][0] += a
			self.particles[i][1][1] += particle[2][1]
			self.particles[i][3] -= dt
			if self.particles[i][3] <= 0:
				self.particles.pop(i)

		self.needsUpdate = False





# --- Functions --- #
def createRoundImage(radius, background:pygame.Color = (0,0,0), foreground:pygame.Color = (255,255,255), borderPaths:list = None):
	_image = pygame.Surface((radius*2+1, radius*2+1))
	pygame.draw.circle(_image, (255,255,255), [radius, radius], radius, draw_top_left=True, draw_top_right=True)
	_image.blit(pygame.transform.rotate(_image, -90), (0,0), special_flags=pygame.BLEND_ADD)
	_image.blit(pygame.transform.rotate(_image, 180), (0,0), special_flags=pygame.BLEND_ADD)

	if len(background)==4 or len(foreground)==4:
		_image = _image.convert_alpha()

	if background!=(0,0,0) or foreground!=(255,255,255):
		for x in range(_image.get_width()):
			for y in range(_image.get_height()):
				pixel = _image.get_at((x,y))
				if pixel==(0,0,0):
					_image.set_at((x,y), background)
				elif pixel==(255,255,255):
					_image.set_at((x,y), foreground)

	if not borderPaths:
		return _image

	image = pygame.transform.scale(_image, (_image.get_width()*TILE_WIDTH, _image.get_height()*TILE_WIDTH))


	corner = pygame.image.load(borderPaths[0])
	line = pygame.image.load(borderPaths[1])
	little_corner = pygame.image.load(borderPaths[2])

	for x in range(_image.get_width()):
		for y in range(_image.get_height()):
			if _image.get_at((x, y))==foreground:
				neighbours = ''
				for neighbour in [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]:
					if neighbour[0] in range(_image.get_width()) and neighbour[1] in range(_image.get_height()) and _image.get_at(neighbour)==foreground:
						neighbours += '1'
					else:
						neighbours += '0'

				if neighbours=='0011':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(corner, (x*TILE_WIDTH, y*TILE_WIDTH))
				if neighbours=='0110':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(pygame.transform.rotate(corner, 90), (x*TILE_WIDTH, y*TILE_WIDTH))
				if neighbours=='1100':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(pygame.transform.rotate(corner, 180), (x*TILE_WIDTH, y*TILE_WIDTH))
				if neighbours=='1001':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(pygame.transform.rotate(corner, -90), (x*TILE_WIDTH, y*TILE_WIDTH))

				if neighbours=='1011':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(line, (x*TILE_WIDTH, y*TILE_WIDTH))
				if neighbours=='0111':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(pygame.transform.rotate(line, 90), (x*TILE_WIDTH, y*TILE_WIDTH))
				if neighbours=='1110':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(pygame.transform.rotate(line, 180), (x*TILE_WIDTH, y*TILE_WIDTH))
				if neighbours=='1101':
					image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
					image.blit(pygame.transform.rotate(line, -90), (x*TILE_WIDTH, y*TILE_WIDTH))

				if neighbours=='1111':
					diag_neighbours = ''
					for neighbour in [(x-1, y-1), (x+1, y-1), (x+1, y+1), (x-1, y+1)]:
						if neighbour[0] in range(_image.get_width()) and neighbour[1] in range(_image.get_height()) and _image.get_at(neighbour)==foreground:
							diag_neighbours += '1'
						else:
							diag_neighbours += '0'

					if diag_neighbours=='1011':
						image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
						image.blit(little_corner, (x*TILE_WIDTH, y*TILE_WIDTH))
					if diag_neighbours=='0111':
						image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
						image.blit(pygame.transform.rotate(little_corner, 90), (x*TILE_WIDTH, y*TILE_WIDTH))
					if diag_neighbours=='1110':
						image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
						image.blit(pygame.transform.rotate(little_corner, 180), (x*TILE_WIDTH, y*TILE_WIDTH))
					if diag_neighbours=='1101':
						image.fill(background, (x*TILE_WIDTH, y*TILE_WIDTH, TILE_WIDTH, TILE_WIDTH))
						image.blit(pygame.transform.rotate(little_corner, -90), (x*TILE_WIDTH, y*TILE_WIDTH))

	return image