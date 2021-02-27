import pygame
from . import Window
from ..constants import INVENTORY_SCALE, INVENTORY_SLOT_SIZE, ITEMS_IMAGES, ItemList

class InventoryWindow(Window):
	def __init__(self, game, parentScreen):
		super().__init__(game)
		self.background = pygame.image.load("dungeonX/assets/ui/inventory/background.png").convert()
		self.background.set_colorkey((255,0,255))
		self.background = pygame.transform.scale(self.background, (self.background.get_width()*INVENTORY_SCALE, self.background.get_height()*INVENTORY_SCALE))
		game.textDisplayer.print("Equipment", (8*INVENTORY_SCALE,7*INVENTORY_SCALE), scale=0.4, rectSize=(99*INVENTORY_SCALE, 12*INVENTORY_SCALE), center=True, screen=self.background)
		game.textDisplayer.print("Inventory", (116*INVENTORY_SCALE,7*INVENTORY_SCALE), scale=0.4, rectSize=(94*INVENTORY_SCALE, 12*INVENTORY_SCALE), center=True, screen=self.background)
		game.textDisplayer.print("Bag Weight", (140*INVENTORY_SCALE,106*INVENTORY_SCALE), scale=0.2, screen=self.background)
		game.textDisplayer.print("Money : ", (218*INVENTORY_SCALE,17*INVENTORY_SCALE), scale=0.2, rectSize=(22*INVENTORY_SCALE, 10*INVENTORY_SCALE), screen=self.background)
		self.set_colorkey((0,0,0))
		self.bar_background = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/inventory/bar_background.png").convert(), (29*INVENTORY_SCALE, 3*INVENTORY_SCALE))
		self.bar_foreground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/inventory/bar_foreground.png").convert(), (32*INVENTORY_SCALE, 3*INVENTORY_SCALE))
		self.bar_foreground.set_colorkey((0,0,0))

		self.hoveredRect = pygame.Rect((-INVENTORY_SCALE, -INVENTORY_SCALE), ((INVENTORY_SLOT_SIZE+2)*INVENTORY_SCALE, (INVENTORY_SLOT_SIZE+2)*INVENTORY_SCALE))
		self.hovered = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/icons/hovered.png"), self.hoveredRect.size)
		self.hovered.set_colorkey((0,0,0))

		self.bag = parentScreen.dungeon.bag
		self.rect = self.get_rect().move((pygame.Vector2((parentScreen.get_width(), parentScreen.bottombarwindow.rect.top))-self.background.get_size()+(21,0))/2)
		self.parentScreen = parentScreen
		self.itemRects = [pygame.Rect(((30+16*i)*INVENTORY_SCALE, (29+31*j)*INVENTORY_SCALE), (INVENTORY_SLOT_SIZE*INVENTORY_SCALE,INVENTORY_SLOT_SIZE*INVENTORY_SCALE)).move(self.rect.topleft) for j in range(3) for i in range(5)] \
                       + [pygame.Rect(((117+16*(i%6))*INVENTORY_SCALE, (23+16*(i//6))*INVENTORY_SCALE), (INVENTORY_SLOT_SIZE*INVENTORY_SCALE,INVENTORY_SLOT_SIZE*INVENTORY_SCALE)).move(self.rect.topleft) for i in range(30)]
		self.selectedItemIndex = None
		self.grabPos = None


	

	def update(self, events):
		mousePos = pygame.mouse.get_pos()
		allItems = list(filter(lambda x:x.getItemType()!=ItemList.Coin, self.bag.getAllItems()))

		for event in events:
			if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
				for i,rect in enumerate(self.itemRects):
					if rect.collidepoint(event.pos) and ((i<15 and i//5<len(self.parentScreen.players) and self.parentScreen.players[i//5].equipment[i%5]!=None) or (i>=15 and i-15<len(allItems) and allItems[i-15]!=None)):
						self.selectedItemIndex = i
						self.grabPos = event.pos
						break
			if event.type==pygame.MOUSEBUTTONUP and event.button==1:
				if self.selectedItemIndex!=None:
					for i, rect in enumerate(self.itemRects):
						if rect.collidepoint(event.pos):
							if self.selectedItemIndex<15:
								item = self.parentScreen.players[self.selectedItemIndex//5].equipment[self.selectedItemIndex%5]
							else:
								item = allItems[self.selectedItemIndex-15]

							if i<15 and self.selectedItemIndex>=15 and i//5<len(self.parentScreen.players):
								self.parentScreen.players[i//5].equip(item, index=i%5)
							elif i>=15 and self.selectedItemIndex<15:
									self.parentScreen.players[self.selectedItemIndex//5].unequip(item)
							break
				self.selectedItemIndex = None
				self.grabPos = None


		self.fill((0,0,0))
		self.blit(self.bar_background, (176*INVENTORY_SCALE+self.rect.left, 105*INVENTORY_SCALE+self.rect.top))
		self.blit(self.bar_foreground, ((176-(1-self.bag.getCurrentWeight()/self.bag.getMaxWeight())*29)*INVENTORY_SCALE+self.rect.left, 105*INVENTORY_SCALE+self.rect.top))

		self.blit(self.background, self.rect)
		self.game.textDisplayer.print(str(self.bag.getBalance())+' $', (239*INVENTORY_SCALE+self.rect.left,17*INVENTORY_SCALE+self.rect.top), scale=0.2, rectSize=(12*INVENTORY_SCALE, 11*INVENTORY_SCALE), screen=self)

		for i,player in enumerate(self.parentScreen.players):
			self.blit(pygame.transform.scale(player.image, (16*INVENTORY_SCALE, 24*INVENTORY_SCALE)), (9*INVENTORY_SCALE+self.rect.left, (23+31*i)*INVENTORY_SCALE+self.rect.top))
			for j,item in enumerate(player.equipment):
				if item!=None:
					if self.selectedItemIndex != i*5+j:
						rect = self.itemRects[i*5+j]
						self.fill((211,191,169), rect=rect)
						self.blit(ITEMS_IMAGES[item.getItemType()], rect)
						if rect.collidepoint(mousePos):
							self.blit(self.hovered, self.hoveredRect.move(rect.topleft))

		for i,item in enumerate(allItems):
			if self.selectedItemIndex != i+15:
				rect = self.itemRects[i+15]
				self.blit(ITEMS_IMAGES[item.getItemType()], rect)
				if rect.collidepoint(mousePos):
					self.blit(self.hovered, self.hoveredRect.move(rect.topleft))

		if self.selectedItemIndex!=None:
			rect = self.itemRects[self.selectedItemIndex].move(pygame.Vector2(mousePos)-self.itemRects[self.selectedItemIndex].center)
			if self.selectedItemIndex<15:
				item = self.parentScreen.players[self.selectedItemIndex//5].equipment[self.selectedItemIndex%5]
			else:
				item = allItems[self.selectedItemIndex-15]
			self.blit(ITEMS_IMAGES[item.getItemType()], rect)
