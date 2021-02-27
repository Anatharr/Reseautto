import sys, pygame, math
from .constants import DEFAULT_KEYMAP, INVENTORY_SCALE, INVENTORY_SLOT_SIZE, ITEMS_IMAGES
from .screens import MainMenu, PauseMenu, GameScreen, MapEditorScreen,SettingsMenu,CharacterChoice,LogWindow, MapSelectorScreen, Multiplayer_screen
from .graphics import TextDisplayer, ParticleSystem

class Game:
	""" This class is used to handle the main window with pygame

	The instance of game can be passed as a parameter to any class,
	in order to refer to it afterwards.

	Attributes
	----------
	DISPLAY_SIZE : tuple
		This tuple represent the size of the main window with the
		format (width, height).
	RATIO : float
		This is the ratio width/height, which can be used to compute
		either the width or the height if we need to keep the aspect
		ratio.
	display : pygame.Surface
		This is the main surface of pygame. Each screen is rendered
		on this surface in the main loop.
	running : bool
		This attribute defines whether the game (the main loop) is 
		running or not.
	dt : int
		This number represents the time elapsed since the last loop
		turn. It is used to compute accurate movements regardless of
		potential lag.
	clock : pygame.Clock
		This attribute stores the main pygame clock. It is needed to
		compute dt (see above).
	textDisplayer : GUI.TextDisplayer
		This attribute stores the instance of the TextDisplayer, used
		to print text on the screen. See TextDisplayer's documentation
		for more information.
	particleSystem : GUI.ParticleSystem
		This attribute stores the instance of the ParticleSystem, used
		to handle particles in the game. See ParticleSystem's
		documentation for more information.
	currentScreen : str
		This string stores the current screen which needs to be
		rendered on the display.
	screens : dict
		This dict stores every screen instance in the game.
	keymap : dict
		This dict contains the currently loaded keymap, i.e. each key
		assiciated with an action. See dungeonX/constants.py for the
		defaults.
	log:
		This is the instance of Logswindow that will be used
		throughout the game
	Methods
	-------
	setScreen(name)
		Setter for currentScreen.
	start()
		Starts the game. This method contains pygame's main loop.
	
	addtolog(msg)
		adds the msg as a string to the list of logs that will 
		be displayed by the class logwindow
	"""

	def __init__(self):
		pygame.init()
		pygame.display.set_caption('Dungeon(X)')
		self.DISPLAY_SIZE   = (1280, 720)
		self.RATIO          = 16/9
		self.fullscreen     = False
		self.multiplayer    = False
		self.joining		= False # indicate if we are joining an online game
		self.display        = pygame.display.set_mode(self.DISPLAY_SIZE, flags=pygame.HWSURFACE)
		self.running        = False
		self.dt             = 0
		self.clock          = pygame.time.Clock()
		self.textDisplayer  = TextDisplayer(self)
		self.particleSystem = ParticleSystem(self)

		for item in ITEMS_IMAGES:
			if type(ITEMS_IMAGES[item]) is str:
				ITEMS_IMAGES[item] = pygame.image.load("dungeonX/assets/ui/icons/items/"+ITEMS_IMAGES[item]+".png").convert()
				ITEMS_IMAGES[item] = pygame.transform.scale(ITEMS_IMAGES[item], (INVENTORY_SLOT_SIZE*INVENTORY_SCALE, INVENTORY_SLOT_SIZE*INVENTORY_SCALE))
				ITEMS_IMAGES[item].set_colorkey((0,0,0))

		self.currentScreen = "main_menu"
		self.screens = {
			"main_menu" : MainMenu(self),
			"multiplayer" : Multiplayer_screen(self),
			"settings_menu": SettingsMenu(self),
			"character_choice": CharacterChoice(self),
			"map_selector": MapSelectorScreen(self),
			"game" : GameScreen(self),
			"map_editor" : MapEditorScreen(self),
		}
		self.keymap = dict(DEFAULT_KEYMAP)
		self.mylist=[]
		self.log=LogWindow(self)

	def toggleFullscreen(self):
		self.fullscreen = not self.fullscreen
		pygame.display.toggle_fullscreen()

	def setScreen(self, name : str):
		""" Setter for currentScreen """
		if name in self.screens:
			self.currentScreen = name
		else:
			print("Warning : invalid screen '" + name + "'", file=sys.stderr)

	def start(self):
		""" Starts the game

		This method contains the main loop, which updates the current
		screen then renders it on the display, resizing it if needed.
		"""
		self.running = True

		# fps_min=200

		try:
			while self.running:
				events = pygame.event.get()

				self.particleSystem.needsUpdate = True

				self.screens[self.currentScreen].update(events)
				if self.particleSystem.needsUpdate:
					self.particleSystem.update(self.dt)

				self.display.blit(self.screens[self.currentScreen], (0,0))
				pygame.display.update()

				for event in events:
					if event.type==pygame.QUIT:
						self.running=False

				self.dt = self.clock.tick(200)
				
				# fpsHasChanged = False
				# if not fps_min<=math.floor(self.clock.get_fps()):
				# 	fpsHasChanged = True
				# 	fps_min = min(fps_min, math.floor(self.clock.get_fps())) if self.clock.get_fps()!=0 else fps_min
				# if fpsHasChanged:
				# 	print('FPS min :', fps_min)

		finally:
			pygame.quit()


	def __getstate__(self):
		return None


	def  addToLog(self,message:str):

		"""
This is the method that is used to add a message
to the logs so that it is displayed.
The message is not formated during this method,so you could
print anything you want, it is just a string so it 
should be formated according to your need before calling
this method
"""
			
		self.mylist.append(message)
		if(self.log.messagecount<self.log.maxmessage):
			self.log.messagecount+=1
		self.log.newmessage=True