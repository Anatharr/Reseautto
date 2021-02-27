import pygame
from . import Window
from ..characters import Bag
from dungeonX.items import *
from dungeonX.constants import ITEMS_IMAGES ,ItemList 
from enum import Enum
NPC_SCALE =4
# class ItemImages(Enum):
#     sword = "dungeonX/assets/items/weapon_duel_sword.png"
#     potion = "dungeonX/assets/items/flask_big_blue.png"
#     coin =  "dungeonX/assets/items/coin_anim_f0.png"

class NpcTradingWindow(Window):
    def __init__(self, game, parentScreen):
        super().__init__(game)
        self.background = pygame.image.load("dungeonX/assets/ui/npcinventory.png")
        self.background.set_colorkey((0,0,0))
        self.rect = self.get_rect().move((pygame.Vector2((parentScreen.get_width(), parentScreen.get_height()))-self.background.get_size()+(21,0))/2)
        self.parentscreen = parentScreen
        self.bag: Bag = Bag(1000000,content=[ItemFactory(ItemList.Potion),ItemFactory(ItemList.Sword)])
        game.textDisplayer.print("Items To Trade",  (116*NPC_SCALE,7*NPC_SCALE), scale=0.4, rectSize=(94*NPC_SCALE, 12*NPC_SCALE), center=True, screen=self.background)
        self.background = pygame.transform.scale(self.background, (self.background.get_width()*NPC_SCALE,self.background.get_height()*NPC_SCALE))
        self.rect = (100,100)
        self.set_colorkey((0,0,0))
        self.itemRects = [pygame.Rect(((3+16*i)*NPC_SCALE, (18+16*j)*NPC_SCALE), (12*NPC_SCALE,12*NPC_SCALE)) for j in range(3) for i in range(5)] \
                       + [pygame.Rect(((117+16*(i%6))*NPC_SCALE, (23+16*(i//6))*NPC_SCALE), (12*NPC_SCALE,12*NPC_SCALE)) for i in range(30)]
        self.hovered = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/icons/hovered.png"),(16*NPC_SCALE,16*NPC_SCALE))
        self.hovered.set_colorkey((0,0,0))

    def sellItem(self, typeOfItem: ItemList, buyer):
        '''
        selling an item to a player
        '''
        playerBag = buyer.getBag()
        playerMoney = playerBag.getBalance()

        itemsOfSameType = self.bag.getItemsFromType(typeOfItem)
        itemToSell: Item = next((item for item in itemsOfSameType), None)

        if itemToSell == None:
            print("I don't have that item in my inventory"); return 

        if playerMoney < itemToSell.getValue():
            print("You don't have enough coins in your bag!"); return 

        self.bag.removeItem(itemToSell)
        playerBag.addItem(itemToSell)


    def update(self, events):
        mousePos = pygame.mouse.get_pos()
        self.blit(self.background, (0,0))
        allItems = list(filter(lambda x:x.getItemType()!=ItemList.Coin, self.bag.getAllItems()))
        i = 0
        for i,item in enumerate(allItems):
            self.blit(ITEMS_IMAGES[item.getItemType()],self.itemRects[i])
            if self.itemRects[i].collidepoint(mousePos):
                self.blit(self.hovered,self.itemRects[i])
                item = allItems[i]


        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1 :
                for i,rect in enumerate(self.itemRects):
                    if rect.collidepoint(event.pos) :
                        #self.blit(self.hovered,self.itemRects[i])
                        #self.sellItem(item.getItemType(),self.parentscreen.selectedPlayer)

                        break


        





