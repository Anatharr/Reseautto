from enum import Enum
from math import sqrt
from random import randint
from dungeonX.characters import Character

class SpellEnum(Enum) :
    Fireball = 'Fireball'
    AcidStream = 'Acid Stream'
    MeteorSwarm = 'Meteor Swarm'

class Spell() :
    """
    This class represents the mage's spells.

    Attributes
    ----------
    quantity : int
        the spell quantity
    radius : int
        how far (in tiles) the spell can be cast
    spellType : SpellEnym
        type - Fireball, Acid Stream, Meteor Swarm
    actionPointCost : int
        cost in action points to cast spell
    damageDice1 : int
        dice multiplier
    damageDice2 : int
        dice sides

    for example 2d6 => damageDice1=2 and damageDice2=6
    """
    def __init__(self, quantity, radius, spellType : SpellEnum, actionPointCost, damageDice1, damageDice2) :
        self.quantity = quantity
        self.radius = radius
        self.spellType = spellType
        self.damageDice=[damageDice1,damageDice2]

    def getQuantity(self) :
        return self.quantity

    def getRadius(self) :
        return self.radius

    def changeQuantity(self, n=1) :
        self.quantity += n

    def setRadius(self, new) :
        self.radius = new

    def getDice(self) :
        return self.damageDice

    def setDice(self, newDice) :
        self.damageDice = newDice

    def getSpellType(self) :
        return self.spellType

    def distanceBetween(self, xA, yA, xB, yB):
    	""" Returns the distance between A and B """
    	return sqrt((xB-xA)*(xB-xA) + (yB-yA)*(yB-yA))

    def closeEnough(self, pos1, pos2, max) :
        """
            return : distance(pos1, pos2) <= max
        """
        return self.distanceBetween(pos1[0], pos1[1], pos2[0], pos2[1]) <= max

    def calculateDamage(self) :
        return self.damageDice[0]*randint(1, self.damageDice[1])

    def FireballArea(self,pos) :
        '''
        returns a list of the tiles around the position (x,y)
        '''
        (x,y)=pos
        area = []
        for i in range(-3,4) :
            for j in range(-3,4) :
                area.append((x+i,y+j))
        return area

    def castSpell(self, caster, opponentPos) :
        """
            desc : casts one of three mage spells (Fireball, Acid Stream, Animal Friendship)
            opponentPos : the tile at which the mage casts the spell on (an Enemy could be on the tile or not)

            1) check spell quantity, then decrease
            2) check if close enough to cast spell
            3) decrement HP
            4) update combat log
        """
        if self.quantity < 1 :
            return
        self.changeQuantity(-1)

        if not self.closeEnough(caster.getPosition(), opponentPos, self.radius) :
            caster.game.game.addToLog("Not close enough!")
            return

        damage = self.calculateDamage()

        if self.spellType == "Fireball" :
            area = self.FireballArea(opponentPos)
            killed = False
            killCounter = 0
            for op in caster.game.enemies+caster.game.players:
                if op.getPosition() in area :
                    op.decrementHp(damage)
                    if op.getHP()<=0 :
                        killed=True
                        killCounter+=1
                        caster.incrementHP(50)
        else :
            for op in caster.game.enemies :
                if op.getPosition()==opponentPos :
                    op.decrementHp(damage)
                    killed = False
                    if op.getHP()<=0 :
                        killed = True
                        killCounter = 1
                        caster.incrementHP(50)
        
        message = str(caster.getPlayerType()).removeprefix("PlayerEnum.") + " cast " + str(self.spellType)
        if killed :
            message += ", killed " + str(killCounter)
        caster.game.game.addToLog(message)
