import pygame, math, itertools, os, random
from ...constants import TILE_WIDTH, MAX_HP, serializeSurf, unserializeSurf
from ...graphics import createRoundImage
from . import Enemy
from random import randint


### Map functions ###
# they are here to avoid a circular import with the map file,
# this is a hotfix and should change in future updates.

def vectToPos(vect):
    if type(vect) in (tuple, list):
        if len(vect)!=2:
            raise ValueError("invalid vector : "+str(vect))
        return (math.floor(vect[0]/TILE_WIDTH), math.floor(vect[1]/TILE_WIDTH))
    return (math.floor(vect.x/TILE_WIDTH), math.floor(vect.y/TILE_WIDTH))

def posToVect(pos):
    return pygame.Vector2(pos)*TILE_WIDTH

def distanceBetween(xA, yA, xB, yB):
    """ Returns the distance between A and B """
    return math.sqrt((xB-xA)*(xB-xA) + (yB-yA)*(yB-yA))




class EnemyController(Enemy):
    def __init__(self, game, pos:tuple, actionPointMax, stats:tuple, eType, mod="orc_shaman"):
        """
            @mod : tuple, choose the asset mod can be : ("gobelin"), ("big","zombie"), ()
        """
        super().__init__(game, pos, actionPointMax, stats, eType)
        self.currentTarget  = None
        self.finalTarget    = None
        self.stepsToTarget  = None
        self.timeToMove     = 300 # in milliseconds
        self.animationSpeed = {'idle': 120, 'run': 100} # in milliseconds
        
        self.rect = pygame.Rect((0,0), (TILE_WIDTH, math.floor(TILE_WIDTH*24/16)))
        self.rect.midbottom = posToVect(pos) + (TILE_WIDTH/2, TILE_WIDTH)
        self.state = 'idle'
        self.direction = 0
        self._type = eType
        self.decisionMade = False

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

      
    def __getstate__(self):
        d = dict(serializeSurf(self.__dict__))
        del d["positions"]
        del d["frames"]
        return d

    def __setstate__(self, state):
        state["positions"] = None
        state["frames"] = self.frameIter()
        self.__dict__ = unserializeSurf(state)




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
            self.finalTarget = None



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


    def setTarget(self, target:tuple):
        """ Setter for finalTarget """
        self.stepsToTarget = self.pathfind(target)

        if self.stepsToTarget:
            self.finalTarget = target            
            if not self.currentTarget:
                self.nextTarget()


    def updateAnim(self, dt:int):
        """ Updates the frame that may be rendered.

        This method must be
        called at every loop turn if the player is within the camera
        scope.
        """
        self._dt = dt # Stored for future use (in positionsIter and frameIter)
        self.image = next(self.frames)

    def playAction(self, dt:int) -> str:
        """ Updates the state and current position, and returns the
        current state.
        """
        if self.enemyTarget:
           
            if self.playerNextTo(self.enemyTarget):
                self.attack(self.enemyTarget)
                
                if not self.currentTarget or self.getActionPoint() > 0:
                    print("move after atk")
                    if self.friendInMemory():
                        self.goTowardFriend()
                    else:
                        self.escapeFrom(self.enemyTarget)
                self.enemyTarget = None

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

        return self.state


                
       ################# PSEUDO CODE DU COMPORTEMENT DES ENNEMIS ####################

        ## oublier les friends et player en memoire depuis trop longtemps##
        # regarder si il y a des players around 

        # CAS 1 on vient de voir un player : 

            #si on vient de voir des players: 
                # si distance == 1:
                        # attaquer directement 
                        # si knowFriend() :
                            # go toward friend
                        # sinon 
                            #fuire
                # si Distance( enemy, player) > actionPointand  il existe une case adjacente au player libre and attackable():
                    # state = attacking
                    # aller a coter du player 

                    ### dans updateState #######
                    # attaquer
                    # si il reste des point d'action:
                        # aller vers la case atteignable la plus proche d'un friend sinon la plus loin du player

                    ######################################

                # sinon: 
                    # si knowFriend(): 
                        # si le friend n'est pas a cote :    
                            # se diriger vers lui 
                        #sinon:
                            #pas bouger
                    # sinon :  
                        # fuire

           
                
        # CAS 2 il n'y a pas de player around 
            # si on a vu un player au tour precedent:
                # go toward player
            
            # si friend around ( et pas a coté) OR friend en memoire :
                # go toward friend
                
            #sinon 
                # random walking

    def makeDecision(self):
        ### VERIFIER LES CAS OU ON NE PEUT PAS SE DEPLACER A L ENDROIT VOULU ###
        print(f"-------------enemy  [{self.ID}] is playing -----------")
        self.decisionMade = True
        self.setActionPoint(self.actionPointMax)

        
        #update characters list memorised 
        self.updateMemory() 
        self.lookAround()

        # print(f"enemy  [{self.ID}] memory: {self.lastKnownTargets} | {self.lastKnownFriends}")

        print( self.lastKnownTargets)
        print(self.lastKnownFriends)

        # list of player that we just saw by looking around
        targetAround = self.targetJustSaw()
        # we  saw a target this turn 
        if targetAround != []:
            self.getTarget()
            #target is next to us
            if self.playerNextTo(self.enemyTarget):
                return
            if not self.tooWeak(self.enemyTarget) or self.friendAround():
                if self.attackable(self.enemyTarget):
                    self.goTowardTarget(self.enemyTarget)
                    return 
                else:
                    self.getCloserToTarget()
                    return
            else:
                self.escapeFrom(self.enemyTarget)
                return
        else:
            #list of player we saw last turn
            targetsSawLastTurn = [ _target for _target in self.lastKnownTargets["targets"] 
                                    if self.getNbOfTurnInMemory(self.getIndexInMemory(_target,"target"), "target") == 1]

            # if we saw player last turn 
            if targetsSawLastTurn != []:
                target = self.getTheNearestCharacter(targetsSawLastTurn)
                self.huntingTarget(target)
                return
            elif self.friendInMemory() and not self.friendNextTo() :

                self.goTowardFriend()
                return
            else:
                self.randomWalking()
                return



    def friendAround(self):
        for friend in self.lastKnownFriends["friends"]:
            if int(distanceBetween(*self.getPosition(), *friend.getPosition())) <= self.actionPoint:
                return True
        return False

    def playerNextTo(self,target):
        return int(distanceBetween(*self.getPosition(), *target.getPosition())) == 1

    def friendNextTo(self):
        distance = self.getTheNearestCharacter(self.getLastKnownFriends(), withDistance=True)[1]
        return distance == 1


    def getCloserToTarget(self):
        """
            desc : set the road to go to the cell that divide the distance between our target by 2
        """
        distance = int(distanceBetween(*self.enemyTarget.getPosition(), *self.getPosition()))
        for cell in self._move_zone():
            if int(distanceBetween(*cell, *self.enemyTarget.getPosition())) == int(distance/2):
                print(f"[{self.ID}] get closer to {self.enemyTarget}  pos : {self.getPosition()} -> { cell} target pos : {self.enemyTarget.getPosition()}")
                self.setTarget(cell)
                return


    def goTowardTarget(self, target):
        """
            desc    : set the road to go to the nearest accessible adjacent cell of the target we want to go toward
            target  : character that we want to go toward
        """
        nearestCell = min ( self.getAccesibleCell(target), key= lambda cell: distanceBetween(*cell, *self.getPosition()))
        print(f"[{self.ID}] go toward target {target} pos : {self.getPosition()} -> { nearestCell} target pos : {self.enemyTarget.getPosition()}  ")

        self.setTarget(nearestCell)

    def goTowardFriend(self):
        """
            desc : set the road to go to the nearest accessible cell of the nearest friend in memory
        """
        nearestFriend, distance = self.getTheNearestCharacter(self.lastKnownFriends["friends"], withDistance=True)

        if distance != 1 :
            nearestCell = self.getTheNearestCell(nearestFriend.getPosition())
            print(f"[{self.ID}] go toward friend {nearestFriend} pos {self.getPosition()} -> { nearestCell} ")
            self.setTarget(nearestCell) 

    def escapeFrom(self, target):
        """
            desc   : set the farest cell target compare to the target 
            target : target we want to escape from
        """

        move_zone = self._move_zone()
        farestCell = max( move_zone, key= lambda cell: distanceBetween(*cell, *target.getPosition()))
        print(f"[{self.ID}] escapeFrom {target} pos {self.getPosition()} -> { target.getPosition()}")
        self.setTarget(farestCell)
    
    def huntingTarget(self,target ):
        """
            desc   : set the road in order to go to the nearest last known position of the target we saw last turn in order to find him
            target : player, representing the nearest player we saw last turntarget.getPositio
        """
        
        nearestCell = self.getTheNearestCell(target.getPosition())
        print(f"[{self.ID}] is hunting {target}  pos : {self.getPosition()} -> { nearestCell} target pos {target.getPosition()}")
        self.setTarget(nearestCell)


    def randomWalking(self):
        """
            desc : set a random road 
        """
        randomPosition = self.getRandomPosition()
        print(f"[{self.ID}] is random walking pos : {self.getPosition()} -> { randomPosition} ")
        self.setTarget(randomPosition)


    def getRandomPosition(self):
        """
            desc   : choose a random position in the move zone list 
            return : tuple, that represent an accesible position 
        """
        move_zone = self._move_zone()
        
        return move_zone[randint(0,len(move_zone)-1)]

    def tooWeak(self, target, epsilon=20):
        """
            desc   : tell you if there is a high gap between your hp and the hp of your target
            target : character, represent the target you want to atk
            return : boolean
        """
        return  target.getHP() - self.getHP() >= 20


    def attackable(self, target):
        """
            desc     : tell you have enought action point to move toward player and atk him 
                       and if there are free accessible (contain in the move zone) cell around player 
            target   : player we want to evaluate
            return   : boolean
        """
        distance = distanceBetween(*self.getPosition(), *target.getPosition())
        return  distance <= self.actionPoint-1 and self.freeCellAround(target) 

    def freeCellAround(self,character):
        """
            desc      : tell us if there are accessible adjacent cells of a character
            character : the character we want to go next to
            return    : boolean 
        """
        freeCells = [ cell for cell in self._getAdjacentNodes(*character.getPosition()) 
                    if self.game.dungeon.currentFloor.canWalkOn(*cell) and cell in self._move_zone()]

        return freeCells != []

    def getAccesibleCell(self, character):
        """
            desc      : give us the accessible cell around a player
            character : the character we want to go next to
            return    : list of tuple, representing all the free accessible position 
        """
        freeCells = [ cell for cell in self._getAdjacentNodes(*character.getPosition()) 
                    if self.game.dungeon.currentFloor.canWalkOn(*cell) and cell in self._move_zone()]

        return freeCells
    
    def targetJustSaw(self):
        """
            desc   : this method inform us about the targets that we saw this turn with the lookAround() method
            return : list, representing the player that we saw this turn
        """
        targetSaw  = []
        targetList = self.lastKnownTargets["targets"] 
        turnList   = self.lastKnownTargets ["turn"]
        for _target in targetList :
            index = targetList.index(_target)
            if turnList[index] == 0:
                targetSaw.append(_target)
        
        return targetSaw 

    def getTheNearestCharacter(self, characterList, withDistance=False):
        """
            desc          : this method give you the nearest character in the characterList
            characterList : list of character
            withDistance  : if this parameter == True this method will give you the distance between us and the nearest character
            return        : character  or a character and a distance in a tuple 
            """
        distanceMin = 0
        nearestCharacter = None
        for _character in characterList:
            calculateDistance = distanceBetween(*self.getPosition(), *_character.getPosition())
            if distanceMin == 0 or calculateDistance < distanceMin:
                distanceMin = calculateDistance
                nearestCharacter = _character
        return (nearestCharacter, int(distanceMin)) if withDistance else nearestCharacter
    
    def friendInMemory(self):
        """
            desc : tell us if we have friend in memory
            return : boolean
        """
        return self.lastKnownFriends["friends"] != []


    def getTheNearestCell(self, pos):
        """
            des    : look for the nearest accessible free cell compared to the position (pos)
            pos    : tuple, represente the cell which we want to go 
            return : tuple, represente the nearest position found 
        """
        return  min(self._move_zone(), key=lambda cell: distanceBetween(*cell, *pos) )


    def getTarget(self):
        print("getting a target")
        friendsList = [] 
        targetsList = []
        fieldOfView = self.findAreaFromRadius()
        targetToShare = None
        #looking for friends around
        for friend in self.lastKnownFriends["friends"]:
            if friend.getPosition() in fieldOfView:
                friendsList.append(friend)
        
        if friendsList != []:
            # looking for target around
            for target in self.lastKnownTargets["targets"]:
                if target.getPosition() in fieldOfView:
                    targetsList.append(target)
            
            if len(targetsList) == 1:
                targetToShare = targetsList[0]
                self.enemyTarget = targetToShare
                self.shareTarget(friendsList)
                print(f"( only one target ) my target is {self.enemyTarget}")
                return       

            #considere self for the calculation of the balancing position
            friendsList.append(self)

            # searching for targets that have low hp
            targetsLowHp = [ _target for _target in targetsList if _target.getHP() <= MAX_HP ]

            if targetsLowHp != []:
                targetsList = targetsLowHp
            
            ponderedPosition = self.ponderedPosition(friendsList)
            targetToShare    = self.findTheNearestTarget(targetsList, ponderedPosition)
            self.enemyTarget = targetToShare
            self.shareTarget(friendsList)
            print(f"(multiple target) my target is {self.enemyTarget}")
            return
        else:
            self.enemyTarget = self.getTheNearestCharacter(self.lastKnownTargets["targets"])
            print(f"(enemy alone) my target is {self.enemyTarget}")
        
    def shareTarget(self, friendsList):
        for friend in friendsList:
            friend.enemyTarget = self.enemyTarget
    
    def ponderedPosition(self, characterList):
        return ( 
                 math.ceil( sum(character.getPosition()[0] for character in characterList)/len(characterList) ),
                 math.ceil( sum(character.getPosition()[1] for character in characterList)/len(characterList) )
               )
    def findTheNearestTarget(self,targetList, refPosition):

        return  min( targetList, key=lambda target: distanceBetween(*target.getPosition(), *refPosition) )



    def hasTarget(self):
        return self.enemyTarget is not None