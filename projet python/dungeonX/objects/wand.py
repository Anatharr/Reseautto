import pygame
from ..map import Map
from ..items import Item
from ..constants import State, TILE_WIDTH
from ..objects.object import GameObject
import random
from dungeonX.characters.players.classes import Spell, SpellEnum


class Wand(GameObject):
    def __init__(self, pos: tuple, content: [Spell], state:State = State.locked):
        super().__init__(pos)
        self._content = content
        self._state = state
        self.__animState = 'opened'            
        self.__images = [
			pygame.image.load("dungeonX/assets/items/weapon_green_magic_staff.png"),
			pygame.image.load("dungeonX/assets/objects/weapon_red_magic_staff.png"),
        ]
        self.__dt = 0
        self.__animState = 'unused'
        self.__animsIter = self.__animsIterator()
        self.image = self.__images[0]



    def unlock(self, alwaysSuccess=False): 
        if (self._state == State.locked): 
            self._state = State.unlocked
            self.getSpellsFromWand()
        else : print ('already opened '); return False
		
        
    def getSpellsFromWand(self):
        """
        retreive items from a wand 
        """
        if(self._state == State.unlocked):
            if self._content is not None:
                tmp = self._content
                self._content = None
                self.__animState = 'used'
                return tmp 
            else: print('wand contains no spell !')
	
    def getState(self):
        """
        returns if a chest is locked or not
        """
        return self._state


    def __animsIterator(self):
       i = 0
       while True:
            if self.__animState == 'unused':
              i = 0
            if self.__animState == 'used':
              i = 1
            yield self.__images[i]


    def updateAnim(self, dt):
      self.__dt = dt
      self.image = next(self.__animsIter)