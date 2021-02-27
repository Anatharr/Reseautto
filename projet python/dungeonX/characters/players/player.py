from ...constants import Attributes, PLAYERNAME, ItemList
from ...items import Item
from ..skills import SkillEnum, Skill, SkillFactory
from .. import Character
from dungeonX.characters.bag import Bag
from random import randint
from enum import Enum
from math import floor
from dungeonX.objects import Chest,Door
from datetime import datetime
import time
from copy import copy 
import random

BASE_MODIFIER = -5
DEFAULT_DIFFICULTY_CHECK = 20

class PlayerEnum(Enum):
    Rogue ='Rogue'
    Mage ='Mage'
    Fighter='Fighter'
        

class Player(Character) :

    def __init__(self, game, pos: tuple, playerType : PlayerEnum, actionPointMax, lineOfSightRadius, stats:tuple, skills : [Skill] =[]):
        print("stat", stats)
        print("lineOfSightRadius",lineOfSightRadius)
        super().__init__(game, pos, actionPointMax,*stats) #( HP, armor, strength, dex, con, intell, wis, cha )
        self._skills = skills
        self._skillScore = 0
        self.level = 1
        self.exp = 0
        self._bag = self.game.inventorywindow.bag
        self.name = PLAYERNAME
        self._playerType = playerType
        self.lineOfSightRadius = lineOfSightRadius
        self.normalLoSRadius = lineOfSightRadius
        self.equipment = [None, None, None, None, None] # Weapon, Armor, Necklace, Left Ring, Right Ring
        self.expToLevelUp = 100
        self.lineOfSightNormalTurn = None
        
    def getVisibility(self):
        userSkill: Skill = self._searchSkill(SkillEnum.Stealth)
        if userSkill == None:
            print("You don't have stealth in your skills"); return
        return (self.game.getCurrentTurnNumber()>= userSkill.turn+ userSkill.activity)

    def nameWithoutPrefix(self) :
        if self._playerType==PlayerEnum.Fighter :
            return "Fighter"
        if self._playerType==PlayerEnum.Mage :
            return "Mage"
        return "Rogue" 

    #ajouter dans le diagramme
    def equip(self, item, index=None):
        """
        desc  : equip an item and handle the according modification of stats
        @item : Item
        """
        if item.getItemType() == ItemList.Sword:
            index = 0
        elif item.getItemType() == ItemList.Armor:
            index = 1
        elif item.getItemType() == ItemList.Necklace:
            index = 2
        elif item.getItemType() == ItemList.Ring:
            if index not in (3,4):
                index = 3 if self.equipment[3]==None else 4
        else:
            print("Cannot equip this item")
            return

        if self.equipment[index]!=None:
            self.unequip(self.equipment[index])
        self.equipment[index] = item
        self.increaseStats(item.getEffectiveStats())
        self.maxHP += item.getEffectiveStats()[Attributes.HP]
        self._bag.removeItem(item)

    #ajouter dans le diagramme
    def unequip(self, item):
        """
        desc  : unequip an item and handle the according modification of stats
        @item : Item
        """
        if item not in self.equipment:
            print("Item not equipped")
            return
        self.decreaseStats(item.getEffectiveStats())
        self.maxHP -= item.getEffectiveStats()[Attributes.HP]
        self._bag.addItem(item)
        self.equipment[self.equipment.index(item)] = None
        
    def rest(self):
        self.setActionPoint(0)
        super().increaseHP(20)
 
    def useItem(self, item : Item) :
        '''
            desc  : consommation d'un itemactionPoint
            @item : Item
        '''
        item.useItem()

    def levelUp(self) :
        self._skillScore +=1
        self.increaseAttribute(Attributes.Strength,1)
        self.increaseAttribute(Attributes.Dexterity,1)
        self.increaseAttribute(Attributes.Con,1)
        self.increaseAttribute(Attributes.Intelligence,1)
        self.increaseAttribute(Attributes.Cha,1)
        self.increaseAttribute(Attributes.Wisdom,1)
        self.setAttribute(Attributes.HP,100)
        self.exp = 0
        super().setActionPointMax(floor(5+self.level/2))
        self.level+=1
        self.expToLevelUp = floor(self.expToLevelUp*1.5)
        self.game.skillwindow.callskillwindow(self)

    def getLevel(self) :
        return self.level

    def getExp(self) :
        return self.exp

    def setLevel(self,n) :
        self.level = n

    def incrementExp(self,n) :
        if self.exp + n >= self.expToLevelUp :
            self.levelUp()
            self.exp=0
        else :
            self.exp +=n

    def getSkillScore(self) :  
        return self._skillScore

    def incrementSkillScore(self,n) :
        self._skillScore += n

    def isVisible(self) :
        return self.visibility
    
    def getExpToLevelUp(self) :
        return self.expToLevelUp

    def _searchSkill(self, skillType: SkillEnum):
        return next((skill for skill in self._skills if skill.getType() == skillType), None)

    def AtemptToApplySkill(self, skillType: SkillEnum, alwaysSuccess=False, options=None):
        """
        function that player uses to try apply wanted skill
        """
        userSkill: Skill = self._searchSkill(skillType)

        if userSkill == None:
            print('This Skill was not found'); return
        if(self.actionPoint<=0):self.game.game.addToLog('Not enough action Points');return
        self.actionPoint -= 1
        if not self._SuccessRateSkill(skillType, alwaysSuccess=alwaysSuccess):
            self.game.game.addToLog("Unsuccessful try, maybe try again "); return
        userSkill.turn = self.game.getCurentInitialTurnNumber()
        if (skillType == SkillEnum.Stealth) :
            print(f"player type : {self.getPlayerType()} player enum : {PlayerEnum.Rogue}")
            if(self.getPlayerType() == PlayerEnum.Rogue):
                self.incrementSkillScore(userSkill.getCurrentSkillPoints())
                self.getVisibility()
                self.game.game.addToLog('Stealth used : you can be invisible for '+str(userSkill.activity)+' turn(s)')

            else: print("skill only for Rogue to use ")

        elif (skillType == SkillEnum.DisableDevice):
            #disarm a trap (unexistant) else :unlock a door/chetst without key 
            if(self.getPlayerType() == PlayerEnum.Rogue):
                self.incrementSkillScore(userSkill.getCurrentSkillPoints())
                if type(options) == Chest:
                    chest: Chest = options
                    chest.unlock(alwaysSuccess=True)
                    print(f'unlocked: {chest.getState()}')
                elif type(options)== Door:
                    door :Door = options
                    door.unlock(alwaysSuccess=True)
                    print(f'unlocked: {door.getState()}')
            else : print("skill only for Rogue to use ")
        elif (skillType == SkillEnum.Perception):
                if self.lineOfSightRadius<10:
                    self.game.game.addToLog("Perception used successfully")
                    self.lineOfSightRadius+=1
                    self.lineOfSightNormalTurn = self.game.turnNumber+2
                    self.updateLineOfSight()
                else:
                    self.game.game.addToLog("Your cannot see further.")
        else: print("This skill was not implemented")
        
    def updateLineOfSight(self):
        pass

    def attributeSkillsPoint(self,skillType: SkillEnum,numberfromScore:int):
        """
        attributes the number of skillPoints from SkillScore to wanted skill to rank up
        """
        userSkill: Skill = self._searchSkill(skillType)

        if userSkill == None:
            print(f'This Skill ({skillType}) was not found'); return
        
        if numberfromScore > self._skillScore:
            print(f'Max skill score number to attribute: {self._skillScore}'); return
        
        userSkill.addPoints(numberfromScore)
        self._skillScore -= numberfromScore
        
        


    def skillrankup(self,skillType:SkillEnum,numberfromScore):
        """
        this is a simplified version of the previous method,
        We should clarify the method to use
        """
        self.userSkill: Skill = self._searchSkill(skillType)

        if self.userSkill == None:
            print(f'This Skill ({skillType}) was not found'); return

        self.userSkill.rankup(numberfromScore)
        self._skillScore -= numberfromScore


    def _SuccessRateSkill(self, skillType: SkillEnum, alwaysSuccess=False):
        """
        Determines if a skill will be successful in call of not
        """
        userSkill: Skill = self._searchSkill(skillType)
        if userSkill == None:
            print(f'This Skill ({skillType}) was not found'); return

        if userSkill.getType() == SkillEnum.Stealth:
            att = Attributes.Dexterity
        elif userSkill.getType() == SkillEnum.Perception:
            att = Attributes.Intelligence
        elif userSkill.getType() == SkillEnum.DisableDevice:
            att = Attributes.Dexterity
        abilityScore = BASE_MODIFIER
        for _ in range(1,self.getAttribute(att),2):
            abilityScore +=1
        skillrank = userSkill.getCurrentRank()

        if alwaysSuccess: comparisonValue = DEFAULT_DIFFICULTY_CHECK + 1 
        else: comparisonValue = random.randint(1,20)+skillrank+abilityScore

        difficultyCheck = DEFAULT_DIFFICULTY_CHECK
        if comparisonValue >= difficultyCheck :
            return comparisonValue >= difficultyCheck 

    def getPlayerType(self):
        return self._playerType

    def attack(self, opponent):
        """
        Playes's version of attack.
        Mechanics :
        - dice roll = random(20 max) + strength + skills
        - if dice roll > opponent armor then attack works
        """
        print("ATTACKING")
        if self.getActionPoint()<2 : 
            return

        self._decrementActionPoint(2)

        ######## dice roll #########
        dice = randint(1,20) 
        print("Dice:" + str(dice))

        # d20=1 : attack didn't work
        if dice == 1 :
            message = self.nameWithoutPrefix() + " tried to attack " + str(opponent.getEnemyType()) + ". Dice=1, attack didn't work!"
            self.game.game.addToLog(message)
            return
        
        damage = dice + self.listStat[Attributes.Strength]

        # d20=20 : no AC check
        if dice<20 :
            # attack didn't work
            if damage < opponent.listStat[Attributes.Armor] :
                # type error playerType
                print("stats low")
                message = self.nameWithoutPrefix() + " tried to attack " + str(opponent.getEnemyType()) + ". Dice = " + str(dice) + ". Check failed, not strong enough!"
                self.game.game.addToLog(message)
                return
            
        damaged=False
        # damage decreases depending on the opponent's armor and HP
        damage -= opponent.listStat[Attributes.Armor]
        if opponent.listStat[Attributes.HP] < 100 :
            damage+=10
            damaged=True

        opponent.decrementHp(damage)
        print("decremented")

        # opponent killed
        if(opponent.getAttribute(Attributes.HP)<=0) :
            killed = True
            self.incrementExp(50) # exp goes up if opponent killed
        else :
            killed = False

        # type error playerType
        message = self.nameWithoutPrefix() + " attacked " + str(opponent.getEnemyType()) + ": total damage=" + str(damage) + ", damage from dice=" + str(dice) + ", damage from strength=" + str(self.listStat[Attributes.Strength])  + ", damage penalty from opponent armor=" + str(opponent.getAttribute(Attributes.Armor))  
        if damaged :
            message += ", damage penalty from low HP=10"
        if killed :
            message += ", opponent killed"

        self.game.game.addToLog(message)

    def getBag(self):
        return self._bag

    def sellItem(self, typeOfItem: ItemList, buyer) :
        '''
        selling an item to a player
        '''
        playerBag = buyer.getBag()
        playerMoney = playerBag.getBalance()

        

        itemsOfSameType = self._bag.getItemsFromType(typeOfItem)
        itemToSell: Item = next((item for item in itemsOfSameType), None)

        if itemToSell == None:
            print("I don't have that item"); return

        if playerMoney < itemToSell.getValue():
            print("You don't have enough coins in your bag!"); return

        self._bag.removeItem(itemToSell)
        playerBag.addItem(itemToSell)
    
    def getCurrentRankFromSkill(self, skillType: SkillEnum):
        userSkill: Skill = self._searchSkill(skillType)
        if userSkill == None:
            print(f'This Skill ({skillType}) was not found'); return
        return userSkill.getCurrentRank()


    def getCurrentPointsFromSkill(self, skillType: SkillEnum):
        userSkill: Skill = self._searchSkill(skillType)
        if userSkill == None:
            print(f'This Skill ({skillType}) was not found'); return
        return userSkill.getCurrentRankUpPoints()