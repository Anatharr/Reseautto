import random
from ..constants import State, TILE_WIDTH, serializeSurf, unserializeSurf, ItemList
from .players import Player
from dungeonX.characters import Character
from dungeonX.items import Item
from dungeonX.characters.bag import Bag
import pygame
from dungeonX.map import Map



class NPC(Character) :
    def __init__(self, game, pos: tuple, itemsToSell: [Item]=[]):
        super().__init__(game,pos,5,0,0,0,0,0,0,0,0)
        #self.bag = Bag(maxWeight=300,content=itemsToSell)
        #switch bag if you want backendteststowork

        self.bag = self.game.npcwindow.bag
        
        self.__images = [
            pygame.image.load("dungeonX/assets/characters/elf_m_idle_f0.png").convert(),
            pygame.image.load("dungeonX/assets/characters/elf_m_idle_f1.png").convert(),
            pygame.image.load("dungeonX/assets/characters/elf_m_idle_f2.png").convert(),
            pygame.image.load("dungeonX/assets/characters/elf_m_idle_f3.png").convert(),
		]
        
        for i in self.__images:
             i.set_colorkey((0,0,0))

        self.animationSpeed = 100
        self.__dt = 0
        self.__animState = 'normal'
        self.animsIter = self.animsIterator()
        self.image = next(self.animsIter)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = Map.posToVect(pos) + (0,TILE_WIDTH)
        self.state = 'idle'

 
    def __getstate__(self):
        d = dict(serializeSurf(self.__dict__))
        del d["animsIter"]
        return d

    def __setstate__(self, state):
        state["animsIter"] = self.animsIterator()
        self.__dict__ = unserializeSurf(state)      


    def getBag(self):
        return self.bag


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


    # def talk(self) :
    #     print("hello! .... how are you doing ",Character.name)
    #     print(random.choice(self.L))
        
    def attack(self):
        """
        docstring
        """
        pass


    def animsIterator(self):
        i = random.randint(0,len(self.__images))
        elapsedTime = 0
        while True:
            elapsedTime += self.__dt     
            if elapsedTime > self.animationSpeed :
                elapsedTime = 0
                i += 1
            if i >= 4 :
                i=0
            yield self.__images[i]

    def updateAnim(self, dt):
      self.__dt = dt
      self.image = next(self.animsIter)


    def interactWithPlayer(self, player):
        player.game.game.addToLog("  NPC :Would you like to trade!")
        self.game.npcwindow = self 