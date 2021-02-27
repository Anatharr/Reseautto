from math import sqrt
from random import randint
from math import sqrt
from ...constants import Attributes, MAP_WIDTH, MAP_HEIGHT, MEMORY_DURATION, MAX_HP
#from ...map import Map
from .. import Character
from ..players import Player, PlayerEnum
from enum import Enum
#from dungeonX.screens.gamescreen import GameScreen

class EnemyEnum(Enum) :
    Zombie = 'Zombie'
    Dragon = 'Dragon'
    Goblin = 'Goblin'

class Enemy(Character) :
    def __init__(self, game, pos: tuple, actionPointMax, stats:tuple, enemyType : EnemyEnum):
        super().__init__(game, pos, actionPointMax, *stats)
        self.lastKnownFriends = dict(friends = [], turn=[])
        self.lastKnownTargets = dict(targets = [], turn=[])
        self.converted        = False
        self.enemyTarget      = None
        self._enemyType       = enemyType

    def getLastKnownFriends(self) :
        return self.lastKnownFriends["friends"] 

    def getlastKnownTargets(self) :
        return self.lastKnownTargets["targets"] 

    def getFriendsMemoryTurn(self):
        """
            desc   : give us the list representing the number of turn a friend is in the memory
            return : list
        """
        return self.lastKnownFriends["turn"]
        
    def getTargetMemoryTurn(self):
        """
            desc   : give us the list representing the number of turn a player is in the memory
            return : list
        """
        return self.lastKnownTargets["turn"]

    def getNbOfTurnInMemory(self, characterIndex, characterType):
        """
            desc           : tell us since how many turn the character is in memory
            characterIndex : int, index of the character in the appropriate list ( player or friend)
            characterType  : str, can be neither "target" or "friend" in order to know in which list we have to check
            return         : int, representing the number of turn the character is in memory
        """
        assert(characterType == "target" or characterType=="friend")
        characterTurnList = self.lastKnownFriends["turn"] if characterType == "friend" else self.lastKnownTargets["turn"]
        return characterTurnList[characterIndex]

    def getIndexInMemory(self, character, characterType):
        """
            desc          : give us the index of the character in the appropriate memory list 
            character     : character we want to know the index
            characterType : str, can be neiter "target" or " friend" in order to know in which list we have to check
            return        : int, reresenting the index of the character in the memory
        """
        assert(characterType == "target" or characterType=="friend")
        characterMemoryList = self.lastKnownFriends["friends"] if characterType == "friend" else self.lastKnownTargets["targets"]
        return characterMemoryList.index(character)
    """
    def setLastKnownFriendPosition(self,newpos) :
        self.lastKnownFriendPosition = newpos

    """
    def getEnemyType(self) :
        return self._enemyType

    def setEnemyType(self, newType : EnemyEnum) :
        self._enemyType = newType

    def findAreaFromRadius(self,radius=None) :
        """
            desc   : form a square zone around an enemy that represent the vision of the enemy
            radius : fix the maximum distance field of view
            return : list of tuple, representing all cell that we can see
        """
        radius = radius or self.actionPoint
        posX,posY  = self.getPosition()
        area = []
        for i in range (-radius, radius+1):
            for j in range(-radius, radius+1):
                if i==0 and j==0:
                    continue   
                if 0<= posX+i < MAP_WIDTH  and 0<=posY+j <MAP_HEIGHT:
                    area.append((posX+i, posY+j))  
        return area



    def lookAround(self) :
        """ 
            desc : look in a zone around us (define by findAreaFromRadius()) add character we saw in the appropriate list 
                    (lastKnownFriends["friend"] or lastKnownTargets["targets"] )

        """
        area = self.findAreaFromRadius()
        #check if there is a player in the cells that we see
        for _player in self.game.players:
            #handle the stealth skill of the rogue

            if _player.getPlayerType() == PlayerEnum.Rogue and not _player.getVisibility() and not self.converted:
                continue
            elif _player.getPosition() in area:            
               
                if not self.converted:
                    self.memoriseCharacter(_player, "target")    # append to memory as a target
                else:
                    self.memoriseCharacter(_player, "friend")    # append to memory as a friend
                        
        #check if there is a enemy in the cells we see
        for _enemies in self.game.enemies:
            if _enemies.getPosition() in area:
                if not self.converted:
                    self.memoriseCharacter(_enemies, "friend")  # append to memory as a friend
                else:
                    self.memoriseCharacter(_enemies, "target")  # append to memory as a target

        """
        someone=0
        enemyHP=101
        for instances in Player.instances:
            if instances in area :
                if instances.getHP < enemyHP :
                    self.lastKnownPlayerPosition= instances.getPosition()
                    someone=1
                    enemyHP=instances.getHP
        if someone==0 :
            self.lastKnownPlayerPosition= (None, None)
        else :
            self.sharePosition(self.pos)
        """



    def memoriseCharacter(self,newCharacter, characterType) :
        """
            desc          : append newCharacter that we see in the field of view into the appropriate memory list
            newPlayer     : the player we want to memorise
            characterType : str, can be neiter "target" or " friend" in order to know in which list we have to check
        """
        assert(characterType == "target" or characterType == "friend")

    
        characterList = self.lastKnownTargets["targets"] if characterType == "target" else self.lastKnownFriends["friends"]
        turnList      = self.lastKnownTargets["turn"]    if characterType == "target" else self.lastKnownFriends["turn"]
 
        #check if i already see this player
        if newCharacter not in characterList:
            characterList.append(newCharacter)
            turnList.append(0)
        else:
            #the player is already in lastKnonwPlayers["players"] so we just update the turn
            characterIndex =  self.getIndexInMemory(newCharacter,characterType)                 
            turnList[characterIndex] = 0  # reset to 0 to keep the player more longer in the memory



    def updateMemory(self):
        """
            desc : increase the element of lastKnownTargets["turn"] and lastKnownFriends["turn"] lists
                   and check if we have to forget the characters ( by default we memorise a character for 5 turn ) 
        """
        TargetTurnList  = self.getTargetMemoryTurn()
        friendsTurnList = self.getFriendsMemoryTurn()

        # update the Target in memory
        for i in range (len(TargetTurnList)):
            TargetTurnList[i]+=1
            # if we have a player in memory for too long, we have to forget him
            if TargetTurnList[i] >= MEMORY_DURATION:
                #delete the PLAYER from memory
                print(" ")
                print( "--------- deleting----------------")
                print( f" memory : {self.lastKnownTargets} i : {i}")
                self.lastKnownTargets["targets"].pop(i)

        #update the friends in memory
        for j in range (len(friendsTurnList)):
            friendsTurnList[j]+=1
            if friendsTurnList[j] >= MEMORY_DURATION:
                self.lastKnownFriends["friends"].pop(j)

        # update turn lists 
        self.lastKnownFriends["turn"] = [ turn for turn in self.lastKnownFriends["turn"] if turn < MEMORY_DURATION ]
        self.lastKnownTargets["turn"] = [ turn for turn in self.lastKnownTargets["turn"] if turn < MEMORY_DURATION ]

        print( f" memory after updating {self.lastKnownTargets} ")
        print(" ")
        



    """
    def sharePosition(self,pos) :
        for instances in Enemy.instances :
            if instances.getType == self.enemyType :
                instances.setLastKnownFriendPosition(pos) 


    def randomWalking(self, actionPoint) :
        while super().getActionPoint()>0 :
            (x,y)=super().getPosition() 
            around=[(x-1,y+1),(x,y+1),(x+1,y+1),(x-1,y),(x+1,y),(x-1,y-1),(x,y-1),(x+1,y-1)]

            super().pathfind(around[randint(1,8)],super().getActionPoint())
    """
    def around(self,pos) :
        '''
        returns a list of the tiles around the position (x,y)
        '''
        (x,y)=pos
        return [(x-1,y+1),(x,y+1),(x+1,y+1),(x+1,y),(x+1,y-1),(x,y-1),(x-1,y-1),(x-1,y)]
    

    def attack(self, opponent):
        """
        enemy attack function
        @param opponent the player the enemy is attacking

        1) check if self next to opponent
        2) check if enough action points then decrement
        3) roll dice
        4) if dice=1 then attack didn't work + update combat log
        5) add own strength to damage
        6) if dice=20 no check needed, else we compare damage to opponent armor to see if attack worked
            - if attack doesn't work update combat log
        7) if own HP < 100 we do less damage
        8) remove damage according to opponent armor
        9) decrement opponent HP
        10) if fighter next to self, fighter attacks
        11) update combat log
        """
        print(f"[{self.ID}] has atked")
        assert opponent.getPosition() in self.around(self.pos)

        if not isinstance(opponent, Enemy) and not opponent.isVisible :
            return

        if self.getActionPoint() < 2 : return
        self._decrementActionPoint(2)
    
        dice = randint(1,20)

        if dice == 1 :
            message = str(self._enemyType) + " tried to attack " + opponent.nameWithoutPrefix() + ". Dice roll = 1, attack didn't work!"
            self.game.game.addToLog(message)
            return

        damage = dice + self.listStat[Attributes.Strength]

        if dice < 20 :
            if damage < opponent.getAttribute(Attributes.Armor) :
                message = str(self._enemyType) + " tried to attack " + opponent.nameWithoutPrefix() + ". Dice = " + str(dice) + ". Check failed, not strong enough!"
                self.game.game.addToLog(message) 
                return

        if self.listStat[Attributes.HP]<100 :
            damage-=10

        damage -= opponent.getAttribute(Attributes.Armor)

        opponent.decrementHp(damage)
        killed=False
        if opponent.getHP()<=0:
            killed = True
        
        message = str(self._enemyType) + " attacked " + opponent.nameWithoutPrefix() + ": total damage=" + str(damage) + ", damage from dice=" + str(dice) + ", damage from strength=" + str(self.listStat[Attributes.Strength]) + ", damage penalty from opponent armor=" + str(opponent.getAttribute(Attributes.Armor))
        if self.listStat[Attributes.HP]<100 :
            message += ", damage penalty from low HP=10"
        if killed :
            message += ", opponent killed"
   
        self.game.game.addToLog(message)

        print("before for loop")
        for opponent2 in self.game.players :
            print("in for loop")
            print("player: " + str(opponent2.getPlayerType()))
            if opponent2.getPosition() in self.around(self.pos) and opponent2.getPlayerType()==PlayerEnum.Fighter and opponent2!=opponent:
                print("calling protect")
                opponent2.protect(self)
        

        

    """
    
    def newTurn(self) :
        if not self.converted :
            if self.pos == self.lastKnownFriendPosition :
                self.lastKnownFriendPosition = (0,0)
                
            self.lookAround()
            if self.lastKnownPlayerPosition == (None, None) :
                if self.lastKnownFriendPosition == (None, None) :
                    self.randomWalking(self.actionPoint)
                else :
                    super().pathfind((self.lastKnownFriendPositionX, self.lastKnownFriendPositionY))
            else :
                self.sharePosition(self.pos)
                if (self.lastKnownPlayerPosition) in self.findAreaFromRadius(1) :
                    for opponent in Player.instances :
                        if opponent.getPosition() == self.lastKnownPlayerPosition :
                            self.attack(opponent)
                            if opponent.getHP()<=0 :
                                self.lastKnownPlayerPosition = (None, None)
                else:
                    super().pathfind((self.lastKnownPlayerPositionX, self.lastKnownPlayerPositionY))
        
        else :
            self.lookAround()
            if self.lastKnownFriendPosition == (None, None) :
                if self.lastKnownPlayerPosition == (None, None) :
                    self.randomWalking(self.actionPoint)
                else :
                    super().pathfind((self.lastKnownPlayerPositionX, self.lastKnownPlayerPositionY))
            else :
                if self.lastKnownFriendPosition in self.findAreaFromRadius(1) :
                    for opponent in Enemy.instances :
                        if opponent.getPosition() == self.lastKnownFriendPosition :
                            self.attack(opponent)
                            if opponent.getHP()<=0 :
                                self.lastKnownFriendPosition = (None, None)
                else :
                    super().pathfind((self.lastKnownFriendPositionX, self.lastKnownFriendPositionY))
     """       
    def convert(self) :
        self.converted=True

    def isConverted(self) :
        return self.converted

    def nameWithoutPrefix(self):
        name = ""
        if self.converted:
            name+="Converted "

        if self._enemyType==EnemyEnum.Goblin:
            name+="Goblin"
        elif self._enemyType==EnemyEnum.Dragon:
            name+="Dragon"
        elif self._enemyType==EnemyEnum.Zombie:
            name+="Zombie"

        return name

