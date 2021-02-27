import pygame
from ..constants import TILE_WIDTH
from . import GameObject


class Stairs(GameObject):
    def __init__(self, pos:tuple, down:bool=True):
        super().__init__(pos)
        self.down = down

        if down:
            self.image = pygame.image.load("dungeonX/assets/objects/stairs_down.png").convert()
        else:
            self.image = pygame.image.load("dungeonX/assets/objects/stairs_up.png").convert()
        self.image.set_colorkey((0,0,0))

        self.rect = self.image.get_rect()
        self.rect.bottomleft = pygame.Vector2(pos)*TILE_WIDTH + (0,TILE_WIDTH)

    def updateAnim(self, dt):
        pass

    def interactWithPlayer(self, player):
        if self.down:
            player.game.dungeon.descend()
        else:
            player.game.dungeon.ascend()