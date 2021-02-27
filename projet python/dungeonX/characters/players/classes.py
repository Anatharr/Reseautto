from random import randrange, randint
from ...map import Map
from ..enemies import Enemy
from . import PlayerController
from ..skills import *
from dungeonX.characters.players.player import PlayerEnum
from enum import Enum
from ...constants import DEFAULT_ACTION_POINT, DEFAULT_LINEOFSIGHT, ItemList, DEFAULT_FIGHTER_STAT, DEFAULT_ROGUE_STAT, DEFAULT_MAGE_STAT
from dungeonX.items.Item import ItemFactory
from math import sqrt
from dungeonX.constants import Attributes
from dungeonX.characters.spells import Spell

class Fighter(PlayerController) :

    def __init__(self, game, pos : tuple, defaultSkills=[], actionPointMax= DEFAULT_ACTION_POINT, lineOfSightRadius=DEFAULT_LINEOFSIGHT , defaultStats=DEFAULT_FIGHTER_STAT):
        super().__init__(game, pos, PlayerEnum.Fighter, defaultSkills, actionPointMax,lineOfSightRadius, defaultStats, mod="knight_f")

    # def taunt(self) :
    #     for enemy in (x , x=enemy()):
    #         enemy.target=self



    def protect(self, opponent) :
        """
        protecting a friend nearby who is getting attacked
        """
        print("Fighter protecting")
        print("AP: " + str(self.getActionPoint()))
        self.setActionPoint(self.actionPoint + 2)
        print("Decremented")
        super().attack(opponent)
        
    def randomItem(self) :
        """
        @return random sword or armor for fighter level up
        """
        randType = randrange(2) # 0:Sword  1:Armor
        if randType==0 :
            newItem = ItemFactory(ItemList.Sword)
        else :
            newItem = ItemFactory(ItemList.Armor)
        return newItem

    def levelUp(self) :
        """
        Level up for fighter. Calls Player class levelup + fighter gets random sword or armor
        """
        super().levelUp()
        self.getBag().addItem(self.randomItem())

class Rogue(PlayerController) :
    def __init__(self, game, pos : tuple, defaultSkills=[], defaultStats=DEFAULT_ROGUE_STAT, actionPointMax= DEFAULT_ACTION_POINT,  lineOfSightRadius=DEFAULT_LINEOFSIGHT):
        super().__init__(game, pos, PlayerEnum.Rogue, defaultSkills,actionPointMax,lineOfSightRadius, defaultStats, mod="lizard_m")

    # def disarmTrap(self) :
    #     trap.activated=False
    # def openLock(self) :
    #     Chest.locked=True

    # def sneakAttack(self) :
    #     Character.listStat[0]-=1
    #     return "Oops...Sneak Attack!"

    def levelUp(self) :
        super().levelUp()
        self._skillScore+=1

class Mage(PlayerController) :
    def __init__(self, game, pos, skills=[], stats=DEFAULT_MAGE_STAT, actionPointMax= DEFAULT_ACTION_POINT,  lineOfSightRadius=DEFAULT_LINEOFSIGHT):
        super().__init__(game, pos, PlayerEnum.Mage, skills, actionPointMax,lineOfSightRadius, stats, mod="wizzard_f")
        self.acidStream = Spell(1, 5, 'Acid Stream', 3, 1, 4)
        self.fireball = Spell(1, 5, 'Fireball', 6, 2, 6)
        self.meteorSwarm = Spell(1, 5, 'Meteor Swarm', 9, 6, 6)

    def around(self,pos) :
        '''
        returns a list of the tiles around the position (x,y)
        '''
        (x,y)=pos
        return [(x-1,y+1),(x,y+1),(x+1,y+1),(x+1,y),(x+1,y-1),(x,y-1),(x-1,y-1),(x-1,y)]

    """
    def createPotion(self, typePotion) :
        '''
        types of potions: healing, oil of sharpness (increase damage done during attacks), hero potion (reduces damage when attacked)
        '''
        for pot in self.potions :
            if pot[0]==typePotion :
                for ingr in pot[3] :
                    if all(ingr in super().bag) :
                        canBeMade=1
                    else :
                        canBeMade=0

        if canBeMade :
            for pot in self.potions :
                if pot[0]==typePotion :
                    pot[1]+=1
        # TODO finish potion creation


    def takePotion(self, potionsIndex) :
        pass

    def givePotion(self) :
        pass

    """

    def rest(self) :
        super().increaseHP(20)
        self.fireball.changeQuantity()
        self.acidStream.changeQuantity()
        self.meteorSwarm.changeQuantity()

    def levelUp(self) :
        super().levelUp()
        self.acidStream.changeQuantity(1)
        self.fireball.changeQuantity(1)
        self.meteorSwarm.changeQuantity(1)

    def castSpell(self, spellCast : Spell, tile) :
        spellCast.castSpell(self, tile)

    def distanceBetween(self, xA, yA, xB, yB):
    	""" Returns the distance between A and B """
    	return sqrt((xB-xA)*(xB-xA) + (yB-yA)*(yB-yA))

    def closeEnough(self, pos1 : tuple, pos2 : tuple, max) :
        """
            return : distance(pos1, pos2) <= max
        """
        return self.distanceBetween(pos1[0],pos1[1],pos2[0],pos2[1])<=max

    def convertEnemy(self, opponent : Enemy) :
        """
        Mage special ability - convert an enemy in radius of 5
        Conversion works if 1d20+CHA(mage)>1d20+CHA(enemy)+10
        """
        print('converting ', opponent)
        if not self.closeEnough(opponent.getPosition(),self.pos,5) :
            self.game.game.addToLog("Not close enough!")
            return

        diceMage = randint(1,20)
        diceEnemy = randint(1,20)

        if diceMage + self.getAttribute(Attributes.Cha) > diceEnemy + opponent.getAttribute(Attributes.Cha) + 10 :
            opponent.convert()
            message = "Mage converted enemy " + str(opponent.getEnemyType())
            self.game.game.addToLog(message)
        else :
            message = "Mage tried to convert enemy " + str(opponent.getEnemyType()) + ", conversion failed!"
            self.game.game.addToLog(message)


""" 
    def castFireball(self) :
        ''' 
        fireball spell; affects all enemies in a certain area/radius
        '''
        # TODO not let mage cast spell if they are too far
        if self.spells[0][0]==0 : return
        self.setActionPoint(self.actionPoint-2)
        area=self.around(self.getPosition())
        for i in range(self.spells[0][2]+1) :
            for j in range(8) :
                area.append(self.around(area[j]))

        area=list(dict.fromkeys(area))
        Map.reddenTiles(area)

        for instances in Enemy.instances :
            if instances.super().getPosition() in area :
                instances.listStat[0]-=self.spells[0][1]
                if instances.listStat[0]<=0 :
                    instances.super().die(instances)
        
        self.spells[0][0]-=1
        

    def castAcidStream(self,opponent) :
        if self.spells[1][0]==0 : return
        opponent.listStat[0]-=self.spells[1][1]
        self.setActionPoint(self.actionPoint-2)
        if opponent.listStat[0]<=0 :
            opponent.super().die(opponent)

    def castAnimalFriendship(self,opponent) :
        if self.spells[2][0]==0 : return
        works=randint(0,100)
        self.setActionPoint(self.actionPoint-2)
        if works>self.spells[2][1] : return # TODO message "didn't work"
        opponent.setType("converted")
        opponent.convert()
 """
