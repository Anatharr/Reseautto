from ..constants import State, TILE_WIDTH
from . import GameObject
import random
import pygame


class Door(GameObject):
    def __init__(self, pos: tuple, state: State=State.locked, key: str = ''):
        super().__init__(pos)
        self._state = state
        self._key = key
        self.__images = [
            pygame.image.load(
                "dungeonX/assets/objects/door_closed.png").convert(),
            pygame.image.load(
                "dungeonX/assets/objects/door_opened.png").convert()
        ]
        for i in self.__images:
            i.set_colorkey((0,0,0))
            
        self.__dt = 0
        self.__animState = 'closed'
        self.animsIter = self.animsIterator()
        self.image = self.__images[0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pygame.Vector2(pos)*TILE_WIDTH + (0,TILE_WIDTH)

    def unlock(self, key='', alwaysSuccess=False):
        if (self._state == State.locked):
            if (key == self._key):
                self._state = State.unlocked
                self.__animState = 'opened'
                print('Successful: Key')
            elif self.SuccessRateToUnlock(alwaysSuccess=alwaysSuccess):
                self._state = State.unlocked
                self.__animState = 'opened'
                print('Successful :Luck')
            else:
                print('Wrong Key'); return False
        else:
            print('Door already unlocked'); return False

    def getState(self):
        return self._state

    def SuccessRateToUnlock(self, alwaysSuccess=False):
        """
        docstring
        """
        return random.randint(1, 10) <3 or alwaysSuccess

    def animsIterator(self):
       i = 0
       while True:
            if self.__animState == 'closed':
              i = 0
            if self.__animState == 'opened':
              i = 1
            yield self.__images[i]

    def updateAnim(self, dt):
      self.__dt = dt
      self.image = next(self.animsIter)

    def interactWithPlayer(self, player):
        if self.getState()==State.locked:
            self.unlock()
            if self.getState()==State.unlocked:
                player.game.game.addToLog(" Unlocked Door !")
        else:
            player.game.game.addToLog(" Door already unlocked !")
