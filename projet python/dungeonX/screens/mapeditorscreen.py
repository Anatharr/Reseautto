import pygame, io, math, pickle, numpy, random
from . import Window
from ..objects import Chest, Door, Stairs
from ..items import ItemFactory
from ..graphics import Button, TextInput
from ..map import Map, Dungeon
from ..constants import TILE_WIDTH, CHESTS_CONTENT

class MapEditorScreen(Window):
	def __init__(self, game):
		super().__init__(game)
		self.pannel = Pannel(game.DISPLAY_SIZE[1], self)

		self.mapSaved = False

		self.__viewport = pygame.Surface((40*TILE_WIDTH, 40*TILE_WIDTH/game.RATIO))
		self.dungeon = None
		self.camera = pygame.Rect((0,0), game.DISPLAY_SIZE)
		self.dragAction = None
		self.choiceBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/choice.png").convert(), (372, 236))
		self.choiceBackground.set_colorkey((0,0,0))
		self.infoBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/info.png").convert(), (600, 164))
		self.infoBackground.set_colorkey((0,0,0))
		self.confirmBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/confirm.png").convert(), (372, 164))
		self.confirmBackground.set_colorkey((0,0,0))

		self.dialogState = None
		self.yesButton = Button(game, (self.get_width()//2-140-5, (self.get_height()+self.infoBackground.get_height())//2-64-15), "Yes", size=(140, 64), textScale=0.3, action=self.saveDialog)
		self.noButton = Button(game, (self.get_width()//2+5, (self.get_height()+self.infoBackground.get_height())//2-64-15), "No", size=(140, 64), imgPath="dungeonX/assets/ui/button_red.png", textScale=0.3, action=self.exit)
		self.dismissButton = Button(game, (self.get_width()//2-70, (self.get_height()+self.confirmBackground.get_height())//2-64-15), "OK", size=(140, 64), textScale=0.3, action=self.cancelDialog)
		self.saveButton = Button(game, (self.get_width()//2-140-5, (self.get_height()+self.choiceBackground.get_height())//2-64-15), "Save", size=(140, 64), textScale=0.3, action=self.saveMap)
		self.cancelButton = Button(game, (self.get_width()//2+5, (self.get_height()+self.choiceBackground.get_height())//2-64-15), "Cancel", size=(140, 64), imgPath="dungeonX/assets/ui/button_red.png", textScale=0.3, action=self.cancelDialog)
		self.filenameInput = TextInput(game, (self.get_width()//2-140, (self.get_height()+self.choiceBackground.get_height())//2-64-94))

		self.floorSelectBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/minimap/floorSelector.png").convert(), (93*3, 25*3))
		self.floorSelectBackground.set_colorkey((0,0,0))
		self.floorSelectPos = (self.get_width()-self.floorSelectBackground.get_width()-10, 10)
		BUTTON_SIZE = 20
		self.plusButton = Button(self.game, (self.floorSelectPos[0]+self.floorSelectBackground.get_width()-40-BUTTON_SIZE*2, self.floorSelectPos[1]+(self.floorSelectBackground.get_height()-BUTTON_SIZE)/2), "", size=(BUTTON_SIZE, BUTTON_SIZE), imgPath="dungeonX/assets/ui/plus_button.png", hoverMode='overlay', action=self.ascend)
		self.minusButton = Button(self.game, (self.floorSelectPos[0]+self.floorSelectBackground.get_width()-30-BUTTON_SIZE, self.floorSelectPos[1]+(self.floorSelectBackground.get_height()-BUTTON_SIZE)/2), "", size=(BUTTON_SIZE, BUTTON_SIZE), imgPath="dungeonX/assets/ui/minus_button.png", hoverMode='overlay', action=self.descend)


	def ascend(self):
		self.dungeon.ascend()

	def descend(self):
		self.dungeon.descend()


	def newMap(self):
		self.dungeon = Dungeon(None, editMode=True)
		self.camera.topleft = (0,0)
		self.dragAction = None
		self.dialogState = None

	def saveDialog(self):
		self.dialogState = "save"
		self.filenameInput.text = ""
		self.filenameInput.focus()

	def saveMap(self):
		if self.filenameInput.text!='':
			self.dungeon.editMode = False
			self.dungeon.currentFloorIndex = 0
			self.dungeon.currentFloor = self.dungeon.floors[0]
			for floor in self.dungeon.floors:
				if floor.startPos==None:
					floor.startPos = floor.getRandomValidLocation()
				if floor.endPos==None:
					floor.endPos = floor.getRandomValidLocation()
			self.dungeon.save('dungeonX/saves/'+self.filenameInput.text.replace(' ', '_')+'.dngX')
			self.dungeon.editMode = True
			self.dialogState = "save_confirmed"
			self.filenameInput.unfocus()
			self.mapSaved = True

	def cancelDialog(self):
		self.dialogState = None

	def exit(self):
		self.dialogState = None
		self.game.setScreen('main_menu')


	def setMapPixel(self, pos, pixel):
		x,y=pos
		if 1<x<self.dungeon.currentFloor.width-2 and 1<y<self.dungeon.currentFloor.height-2 and self.dungeon.currentFloor.get(x,y)!=pixel:
			self.dungeon.currentFloor.set(x,y, pixel)
			self.dungeon.currentFloor.updateWalls([(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)])
			self.mapSaved = False

	def update(self, events):
		for event in events:
			if self.dialogState:
				if event.type==pygame.KEYUP and event.key==pygame.K_ESCAPE:
					self.dialogState = None
			else:
				if event.type==pygame.KEYUP and event.key==pygame.K_ESCAPE:
					self.dialogState = "exit_confirm"
				if event.type==pygame.MOUSEBUTTONUP:
					self.dragAction = None
				if event.type==pygame.MOUSEBUTTONDOWN and not self.pannel.opened:
					pos = Map.vectToPos((event.pos[0]*self.__viewport.get_width()/self.get_width()+self.camera.left, event.pos[1]*self.__viewport.get_height()/self.get_height()+self.camera.top))
					if event.button==3:
						self.dragAction = "grab"
					if event.button==1 and not self.dragAction:
						self.dragAction = self.pannel.selectedTool
						if self.dragAction=="pencil" and not self.floorSelectBackground.get_rect().move(self.floorSelectPos).collidepoint(event.pos):
							if self.pannel.selectedPencil=='floor':
								self.setMapPixel(pos, '.')
							elif self.dungeon.currentFloor.get(*pos)=='.' and not any(obj.pos==pos for obj in self.dungeon.currentFloor.objects):
								self.mapSaved = False
								if self.pannel.selectedPencil=='chest':
									content = list(numpy.random.choice([item[0] for item in CHESTS_CONTENT], random.randrange(3,5), p=[item[1] for item in CHESTS_CONTENT]))
									for i in range(len(content)):
										content[i] = ItemFactory(content[i])
									self.dungeon.currentFloor.objects.append(Chest(pos, content))
								if self.pannel.selectedPencil=='door':
									self.dungeon.currentFloor.objects.append(Door(pos))
								if self.pannel.selectedPencil=='stairs_down':
									self.dungeon.currentFloor.endPos = pos
									self.dungeon.currentFloor.objects.append(Stairs(pos))
								if self.pannel.selectedPencil=='stairs_up':
									self.dungeon.currentFloor.startPos = pos
									self.dungeon.currentFloor.objects.append(Stairs(pos, down=False))
						if self.dragAction=="eraser":
							o = None
							for obj in self.dungeon.currentFloor.objects:
								if obj.pos==pos:
									o = obj
							if o!=None:
								self.dungeon.currentFloor.objects.remove(o)
							else:
								self.setMapPixel(pos, ' ')
				if event.type==pygame.MOUSEMOTION:
					pos = Map.vectToPos((event.pos[0]*self.__viewport.get_width()/self.get_width()+self.camera.left, event.pos[1]*self.__viewport.get_height()/self.get_height()+self.camera.top))
					if self.dragAction == "grab":
						self.camera.left -= event.rel[0]*self.__viewport.get_width()/self.get_width()
						self.camera.top -= event.rel[1]*self.__viewport.get_width()/self.get_width()
					if self.dragAction == "pencil":
						if self.pannel.selectedPencil=='floor':
							self.setMapPixel(pos, '.')
					if self.dragAction=="eraser":
						self.setMapPixel(pos, ' ')
		if not self.dialogState:
			self.pannel.update(events)

		# --- Render --- #
		self.__viewport.fill((0,0,0))
		self.__viewport.blit(self.dungeon.currentFloor.layers["floor"], (-self.camera.left, -self.camera.top))
		for obj in self.dungeon.currentFloor.objects:	
			self.__viewport.blit(obj.image, pygame.Vector2(obj.rect.topleft)-self.camera.topleft)
		self.__viewport.blit(self.dungeon.currentFloor.layers["walls"], (-self.camera.left, -self.camera.top))

		self.fill((30, 30, 30))
		self.blit(pygame.transform.scale(self.__viewport, self.game.DISPLAY_SIZE), (0,0))
		self.blit(self.pannel, self.pannel.pos)
		if self.dialogState:
			self.fill((128,128,128), special_flags=pygame.BLEND_SUB)
			if self.dialogState=="exit_confirm":
				self.blit(self.confirmBackground, (pygame.Vector2(self.game.DISPLAY_SIZE)-self.confirmBackground.get_size())//2)
				self.game.textDisplayer.print("Do you want to save the map ?", (pygame.Vector2(self.game.DISPLAY_SIZE)-self.confirmBackground.get_size())//2, rectSize=(372,80), center=True, scale=0.3)
				self.yesButton.update(events)
				self.blit(self.yesButton.image, self.yesButton.rect)
				self.noButton.update(events)
				self.blit(self.noButton.image, self.noButton.rect)
			elif self.dialogState=="save":
				self.blit(self.choiceBackground, (pygame.Vector2(self.game.DISPLAY_SIZE)-self.choiceBackground.get_size())//2)
				self.game.textDisplayer.print("File name", (pygame.Vector2(self.game.DISPLAY_SIZE)-self.choiceBackground.get_size())//2, rectSize=(372,72), center=True, scale=0.3)
				self.filenameInput.update(events)
				self.blit(self.filenameInput, self.filenameInput.rect)
				self.saveButton.update(events)
				self.blit(self.saveButton.image, self.saveButton.rect)
				self.cancelButton.update(events)
				self.blit(self.cancelButton.image, self.cancelButton.rect)
			elif self.dialogState=="save_confirmed":
				self.blit(self.infoBackground, (pygame.Vector2(self.game.DISPLAY_SIZE)-self.infoBackground.get_size())//2)
				self.game.textDisplayer.print("File saved to dungeonX/saves/"+self.filenameInput.text.replace(' ', '_')+".dngx", (pygame.Vector2(self.game.DISPLAY_SIZE)-self.infoBackground.get_size())//2, rectSize=(600,80), center=True, scale=0.3)
				self.dismissButton.update(events)
				self.blit(self.dismissButton.image, self.dismissButton.rect)

		self.blit(self.floorSelectBackground, self.floorSelectPos)
		self.game.textDisplayer.print("Floor : "+str(-self.dungeon.currentFloorIndex), (self.floorSelectPos[0]+30, self.floorSelectPos[1]), scale=0.2, rectSize=(self.floorSelectBackground.get_size()), screen=self, center_y=True)
		self.plusButton.update(events)
		self.minusButton.update(events)
		self.blit(self.plusButton.image, self.plusButton.rect)
		self.blit(self.minusButton.image, self.minusButton.rect)




class Pannel(pygame.Surface):
	def __init__(self, height, parent):
		self.PANNEL_SPEED = 500
		self.PANNEL_WIDTH = 252
		self.PANNEL_CLOSED_WIDTH = 40
		super().__init__((self.PANNEL_WIDTH, height))
		self.pos = (self.PANNEL_CLOSED_WIDTH-self.PANNEL_WIDTH, 0)
		self.opened = False
		self.posIter = None
		self.parent = parent
		self.selectedTool = "pencil"
		self.selectedPencil = "floor"

		self.background = pygame.Surface(self.get_size())
		self.background.fill((50,50,50))
		self.parent.game.textDisplayer.print("Tools", (5,25), screen=self.background, scale=0.4)

		self.saveButton = Button(self.parent.game, ((self.PANNEL_WIDTH-140)//2, height-150), "Save", size=(140, 64), textScale=0.3, action=self.parent.saveDialog)
		self.exitButton = Button(self.parent.game, ((self.PANNEL_WIDTH-140)//2, height-75), "Exit", size=(140, 64), imgPath="dungeonX/assets/ui/button_red.png", textScale=0.3, action=self.exit)

		TOOL_WIDTH = 64
		self.tools = {}
		for i, tool in enumerate(("pencil", "eraser", "grab")):
			self.tools[tool] = (
				pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/"+tool+".png").convert(), (TOOL_WIDTH, TOOL_WIDTH)),
				pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/"+tool+"_hovered.png").convert(), (TOOL_WIDTH, TOOL_WIDTH)),
				pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/"+tool+"_selected.png").convert(), (TOOL_WIDTH, TOOL_WIDTH)),
				pygame.Rect(20+(10+TOOL_WIDTH)*i, 50, TOOL_WIDTH, TOOL_WIDTH)
			)
			self.tools[tool][0].set_colorkey((0,0,0))
			self.tools[tool][1].set_colorkey((0,0,0))
			self.tools[tool][2].set_colorkey((0,0,0))

		PENCIL_WIDTH = 48
		PENCIL_HEIGHT = 72
		self.pencils = {}
		self.hoveredImg = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/icons/hovered.png"), (PENCIL_WIDTH, PENCIL_WIDTH))
		self.selectedImg = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/pencils/selected.png"), (PENCIL_WIDTH, PENCIL_WIDTH))

		for i, pencil in enumerate(('floor', 'chest', 'door', 'stairs_up', 'stairs_down')):
			self.pencils[pencil] = (
				pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/pencils/"+pencil+".png").convert(), (PENCIL_WIDTH, PENCIL_HEIGHT)),
				pygame.Rect(15+(10+PENCIL_WIDTH)*(i%4), 230+(5+PENCIL_HEIGHT)*(i//4), PENCIL_WIDTH, PENCIL_WIDTH)
			)
			self.pencils[pencil][0].set_colorkey((0,0,0))

	def exit(self):
		if not self.parent.mapSaved:
			self.parent.dialogState = "exit_confirm"
		else:
			self.parent.exit()


	def __pannelPosIter(self):
		elapsedTime = 0
		while (elapsedTime < self.PANNEL_SPEED):
			target = (self.PANNEL_CLOSED_WIDTH-self.PANNEL_WIDTH, 0) if not self.opened else (0,0)
			yield pygame.Vector2(self.pos).lerp(target, elapsedTime / self.PANNEL_SPEED)
			elapsedTime += self.parent.game.dt
		yield target

	def update(self, events):
		for event in events:
			if event.type==pygame.MOUSEBUTTONDOWN:
				for tool in self.tools:
					if self.tools[tool][3].move(self.pos).collidepoint(event.pos):
						self.selectedTool=tool
				for pencil in self.pencils:
					if self.pencils[pencil][1].move(self.pos).collidepoint(event.pos):
						self.selectedPencil=pencil

		mousePos = pygame.mouse.get_pos()
		if mousePos[0] < self.PANNEL_CLOSED_WIDTH and not self.opened and not self.parent.dragAction:
			self.opened = True
			self.posIter = self.__pannelPosIter()
		elif mousePos[0] > self.PANNEL_WIDTH and self.opened:
			self.opened = False
			self.posIter = self.__pannelPosIter()

		if self.posIter:
			try:
				self.pos = next(self.posIter)
			except StopIteration:
				self.posIter = None

		self.blit(self.background, (0,0))

		for key in self.tools:
			rect = self.tools[key][3].move(self.pos)
			if rect.collidepoint(mousePos) and not self.selectedTool==key:
				self.blit(self.tools[key][1], rect)
			elif self.selectedTool==key:
				self.blit(self.tools[key][2], rect)
			else:
				self.blit(self.tools[key][0], rect)

		if self.selectedTool=='pencil':
			self.parent.game.textDisplayer.print("Pencils", (5,200), screen=self, scale=0.4)
			for p in self.pencils:
				rect = self.pencils[p][1].move(self.pos)
				self.blit(self.pencils[p][0], (rect.left, rect.top-24))
				if self.selectedPencil==p:
					self.blit(self.selectedImg, rect)
				elif rect.collidepoint(mousePos):
					self.blit(self.hoveredImg, rect)

		if self.opened:
			self.saveButton.update(events)
			self.exitButton.update(events)
		self.blit(self.saveButton.image, self.saveButton.rect.move(self.pos))
		self.blit(self.exitButton.image, self.exitButton.rect.move(self.pos))

		if not self.opened and self.selectedTool:
			self.blit(pygame.transform.scale(self.tools[self.selectedTool][0], (32,32)), (self.PANNEL_WIDTH-self.PANNEL_CLOSED_WIDTH+4, 10))
			if self.selectedTool=='pencil':
				self.blit(pygame.transform.scale(self.pencils[self.selectedPencil][0], (32,48)), (self.PANNEL_WIDTH-self.PANNEL_CLOSED_WIDTH+4, 52))



		