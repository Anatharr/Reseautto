import pygame, math, itertools, os, random
from ...constants import TILE_WIDTH, State, serializeSurf, unserializeSurf
from ...graphics import createRoundImage
from ...objects import Chest, Door
from ...characters.bag import Bag
from dungeonX.characters.npc import NPC
from ..skills import Skill
from ...screens import LogWindow
from dungeonX.characters.players.player import Player, PlayerEnum
from ..enemies import Enemy

### Map functions ###
# they are here to avoid a circular import with the map file,
# this is a hotfix and should change in future updates.
def posToVect(pos):
    return pygame.Vector2(pos)*TILE_WIDTH



class PlayerController(Player):
    """ This class is used to handle a player with pygame

    The goal of this class is to handle all the graphical part and
    create a link between the "back-end" and the "front-end".

    Attributes
    ----------
    finalTarget : tuple
        This tuple stores the final targeted cell's position, if there
        is one.
    stepsToTarget : list
        This list stores every cells that the player needs to go
        through in order to go from his current position to
        finalTarget.
    currentTarget : tuple
        This tuple stores the current targeted cell's position, if
        there is one. It will take every value of stepsToCell
    timeToMove : int
        This integer represents the time that the player will take to 
        travel one cell, in milliseconds.
    animationSpeed : dict
        This dict stores the speed of each animation, according to the
        state of the player, in milliseconds.
    state : str
        This string represents the current state of the player, used
        to show the appropriate animation.
    direction : int
        This int represents the direction of the player. It can be
        either 0 for left, or 1 for right.
    images : 3D list
        This 3D list contains every frame image, for every state and
        every facing. The syntax to get a particular frame is :
        images[state][direction][frameNumber]
    image : pygame.Surface
        This surface contains the current frame which has to be
        rendered.
    rect : pygame.Rect
        This rectangle represents the position and size of the player.
        It is used for easy collision detection, and rendering.
    positions : iter
        This iterator go througn every absolute positions that may be
        taken by the player. See _positionIter() for more details.
    frames : iter
        This iterator go througn every frames that may be rendered,
        based on current state and animationSpeed. See framesIter()
        for more details.
    _dt : int
        This int is just a copy of the game's dt, see Game for more
        information
    lineOfSight : pygame.Surface
        This surface contains an image used to represent the field of
        view of the player.
    lineOfSightFoW : pygame.Surface
        This surface contains an image representing the field of view
        of the player, used to render the fog of war.


    Methods
    -------
    nextTarget()
        This method handles iteration through _targets
    setTarget()
        Setter for finalTarget.
    updateAnim(dt)
        Updates the frame that may be rendered.
    updateState(dt) : str
        Updates the state and current position, and returns the
        current state.
    updateLineOfSight()
        Updates lineOfSight and lineOfSightFoW, this method must be
        called everytime we change lineOfSightRadius
    """

    def __init__(self, game, pos:tuple, types: PlayerEnum, skills:[Skill], actionPointMax, lineOfSightRadius, stats:tuple, mod="knight_m"):
        super().__init__(game, pos, types, actionPointMax,lineOfSightRadius, stats, skills= skills)
        self.currentTarget = None
        self.targetObject = None
        self.finalTarget = None
        self.stepsToTarget = None
        self.timeToMove = 300 # in milliseconds
        self.animationSpeed = {'idle': 120, 'run': 100} # in milliseconds
        self.game=game
        self.rect = pygame.Rect((0,0), (TILE_WIDTH, math.floor(TILE_WIDTH*24/16)))
        self.rect.midbottom = posToVect(pos) + (TILE_WIDTH/2, TILE_WIDTH)
        self.state = 'idle'
        self.direction = 0
        self._type = type

        # Load all frames
        self.images = dict()
        for state in ('idle', 'run'):
            self.images[state] = [[], []]
            for i in range(4):
                if os.path.isfile("dungeonX/assets/characters/" + '_'.join([mod, state, 'f'+str(i)]) + ".png"):
                    img = pygame.image.load("dungeonX/assets/characters/" + '_'.join([mod, state, 'f'+str(i)]) + ".png").convert()
                else:
                    print("Warning: Missing texture \"dungeonX/assets/characters/" + '_'.join([mod, state, 'f'+str(i)]) + ".png\"")
                    img = pygame.image.load("dungeonX/assets/missing.png").convert()
                img.set_colorkey((0,0,0))
                self.images[state][0].append(img)
                self.images[state][1].append(pygame.transform.flip(img, True, False))

        self.positions = None
        self.frames = self.frameIter()
        self._dt = 0
        self.image = next(self.frames)

        self.updateLineOfSight()


    def __getstate__(self):
        d = dict(serializeSurf(self.__dict__))
        del d["positions"]
        del d["frames"]
        return d

    def __setstate__(self, state):
        state["positions"] = None
        state["frames"] = self.frameIter()
        self.__dict__ = unserializeSurf(state)



    def updateLineOfSight(self):
        """ Updates lineOfSight and lineOfSightFoW

        This method must be called everytime we change lineOfSightRadius
        """
        roundImg = createRoundImage(self.lineOfSightRadius, foreground=(255,255,255), background=(0,0,0))
        offsetX, offsetY = roundImg.get_width()//2, roundImg.get_height()//2
        self.__lineOfSightRelativeCells = [(x-offsetX,y-offsetY) for x in range(roundImg.get_width()) for y in range(roundImg.get_height()) if roundImg.get_at((x,y))==(255,255,255) and (x,y)!=(-offsetX,-offsetY)]

        self.lineOfSight = createRoundImage(self.lineOfSightRadius, foreground=(255,255,255), background=(0,0,0), borderPaths=[
            "dungeonX/assets/fog/corner.png",
            "dungeonX/assets/fog/line.png",
            "dungeonX/assets/fog/little_corner.png",
        ])

        self.lineOfSightFoW = createRoundImage(self.lineOfSightRadius, foreground=(30,30,30), background=(0,0,0, 0), borderPaths=[
            "dungeonX/assets/fog/fow_corner.png",
            "dungeonX/assets/fog/fow_line.png",
            "dungeonX/assets/fog/fow_little_corner.png",
        ])



    def nextTarget(self):
        """ This method handles iteration through stepsToTarget

        It also computes the direction based on the next movement
        along X.
        """
        if self.stepsToTarget:
            t = self.stepsToTarget.pop(0)
            self.currentTarget = pygame.Vector2(t[0]+0.5, t[1]+1)*TILE_WIDTH
            movementX = self.currentTarget.x - posToVect(self.pos).x
            self.direction = 0 if movementX > 0 else 1 if movementX < 0 else self.direction
            self.pos = t
        else:
            self.stepsToTarget = None
            self.currentTarget = None
            self.finalTarget   = None



    def positionsIter(self):
        """ This iterator go through every absolute positions that may be
        taken by the player.
        """
        elapsedTime = 0
        while (elapsedTime < self.timeToMove):
            yield pygame.Vector2(self.rect.midbottom).lerp(self.currentTarget, elapsedTime / self.timeToMove)
            elapsedTime += self._dt
        yield self.currentTarget


    def frameIter(self):
        """ This iterator go througn every frames that may be rendered,
        based on current state and animationSpeed.
        """
        elapsedTime = 0
        frame = random.randint(0, len(self.images[self.state][self.direction])-1)
        while True:
            elapsedTime += self._dt

            if elapsedTime > self.animationSpeed[self.state]:
                elapsedTime = 0
                frame += 1

            if frame>len(self.images[self.state]):
                frame=0
            yield self.images[self.state][self.direction][frame]


    def setTarget(self, target:tuple, targetObject=None):
        """ Setter for finalTarget """
        path = None
        if targetObject:
            targetObject = targetObject[-1]
            x, y = targetObject.pos
            for cell in ((x-1,y), (x,y-1), (x+1,y), (x,y+1)):
                if self.pos==cell:
                    self.targetObject = targetObject
                    return
                p = self.pathfind(cell)
                if p!=None and (path==None or len(p)<len(path)):
                    path=p
        else:
            path = self.pathfind(target)
        self.stepsToTarget = path

        if self.stepsToTarget:
            self.finalTarget = target
            self.targetObject = targetObject
            
            if not self.currentTarget:
                self.nextTarget()


    def updateAnim(self, dt:int):
        """ Updates the frame that may be rendered.

        This method must be
        called at every loop turn if the player is within the camera
        scope.
        """
        self._dt = dt # Stored for future use (in _positionsIter and frameIter)
        self.image = next(self.frames)


    def updateState(self, dt:int) -> str:
        """ Updates the state and current position, and returns the
        current state.
        """

        if self.lineOfSightNormalTurn==self.game.turnNumber:
            self.lineOfSightRadius = self.normalLoSRadius
            self.updateLineOfSight()
            self.lineOfSightNormalTurn = None

        if self.currentTarget:
            self.state = 'run'
            if not self.positions:
                self.positions = self.positionsIter()

            try:
                self.rect.midbottom = next(self.positions)
            except StopIteration:
                self.positions = None
                self.nextTarget()
        else:
            self.state = 'idle'
            if self.targetObject:
                if isinstance(self.targetObject, Enemy):
                    self.attack(self.targetObject)
                else:
                    self.targetObject.interactWithPlayer(self)
                self.targetObject = None

        return self.state


    def getLineOfSightCells(self):
        return [(self.pos[0]+x, self.pos[1]+y) for x,y in self.__lineOfSightRelativeCells]


    def teleport(self, pos):
        # Stop everything
        self.finalTarget = None
        self.currentTarget = None
        self.stepsToTarget = None
        self.targetObject = None
        self.positions = None
        self.state = 'idle'

        # Set position
        self.pos = pos
        self.rect.midbottom = posToVect(pos) + (TILE_WIDTH/2, TILE_WIDTH)
