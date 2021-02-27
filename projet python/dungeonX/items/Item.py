import pygame
from enum import Enum, auto
from datetime import datetime
from ..constants import Attributes, ItemAttributes, TimeFrame, ItemList
# from dungeonX.objects.object import Object


class Item(TimeFrame):
    """
    This class is used to represent the items of the game
    By default , you can only create an item by using a pre-existing one from the ItemList
    using the itemFactory for stats. 

    Example 
    -------
    Item creation
    {name}Item = ItemFactory(ItemList.{Name})
    swordItem = ItemFactory(ItemList.Sword)


    Subclasses
    ----------
    ItemFactory
    this class is used to specify the attributes for all possible items 
    that are in ItemList 

    Attributes
    ---------- 
    _name : str
    in order to spot the name of an Item 
    _stats : list
    this list represents all the attributes of an item
    _timeLimit: [timeLimitInSeconds = 'infinity']
    contains the time limit of an Item
    _used : boolean
    varibale to see if an item is used


    Static Methods
    --------------
    None

    Methods
    -------
    getTimeRemaining(self) : int unless raises exception 
    returns the remaining living time /effect time 
    of an item from its' time limit
    getTimeLimit(self): int unless raises exception 
    returns the time limit of an item in general in case 
    of not 'infinity'
    useItem(self)
    decrements nb of usages of an item while making sure if
    it's still usable or consumed  
    getName(self): name (str)
    returns name of the item
    isUsed(self)
    verifies if name item is used 
    (if useItem method was called ).
    getRemainingUses(self): stats[ItemAttributes.NbOfUses]
    returns NbOfUses of an item 
    isconsumed(self)
    verifies if an item is not usable anymore (consumed).
    """
    def __init__(self, name: str, itemType, stats: list, timeLimitInSeconds = 'infinity'):
        super().__init__(timeLimitInSeconds=timeLimitInSeconds)
        self._name = name
        self._stats = stats
        self._used = False 
        self._type = itemType

    def useItem(self):
        """
        decrements nb of usages of an item while making sure if it it's still usable 
        """
        if (self.getRemainingUses() == 0):
            raise Exception("You can't use your item anymore")
        self._used = True
        self._timeAtFirstUsed = datetime.now() 
        self._stats[ItemAttributes.NbOfUses] -= 1

    def getName(self): 
        """
        returns name of the item
        """
        return self._name

    def isUsed(self): 
        """
        verifies if name item is used (if useItem method was called )
        """
        return self._used 

    def getRemainingUses(self):
        """
        returns NbOfUses of an item 
        """
        return self._stats[ItemAttributes.NbOfUses]

    def isconsumed(self):
        """
        verifies if an item is not usable anymore (consumed)
        """
        try:
            return self.getRemainingUses() == 0 or self.getTimeRemaining() == 0
        except:
            return self.getRemainingUses() == 0

    def getWeight(self):
        """
        Returns weight of an Item
        """
        return self._stats[ItemAttributes.Weight]	

    def getValue(self):
        """
        Returns value of an Item
        """
        return self._stats[ItemAttributes.Value]

    def getItemType(self):
        return self._type

    def getEffectiveStats(self):
        return {key: self._stats[key] for key in Attributes}

class ItemFactory(Item):
    def __init__(self, item: ItemList):
        if item == item.Sword:
            stats = {
                Attributes.HP : 10,
                Attributes.Armor : 0,
                Attributes.Strength : 2,
                Attributes.Dexterity : 5, 
                Attributes.Con : 1,
                Attributes.Intelligence : 1,
                Attributes.Wisdom : 0,
                Attributes.Cha : 1,
                ItemAttributes.Consumable :0,
                ItemAttributes.NbOfUses : 10000,
                ItemAttributes.Weight : 50,
                ItemAttributes.Value : 30
            } 
            super().__init__("Sword", ItemList.Sword,stats)
        elif item ==item.Armor :
            stats = {
                Attributes.HP : 10,
                Attributes.Armor : 100,
                Attributes.Strength : 10,
                Attributes.Dexterity : 5, 
                Attributes.Con : 1,
                Attributes.Intelligence : 1,
                Attributes.Wisdom : 0,
                Attributes.Cha : 1,
                ItemAttributes.Consumable :0,
                ItemAttributes.NbOfUses : 100,
                ItemAttributes.Weight : 300,
                ItemAttributes.Value : 25
            } 
            super().__init__("Armor", ItemList.Armor, stats)
        elif item ==item.Ring :
            stats = {
                Attributes.HP : 50,
                Attributes.Armor : 0,
                Attributes.Strength : 0,
                Attributes.Dexterity : 10, 
                Attributes.Con : 1,
                Attributes.Intelligence : 1,
                Attributes.Wisdom : 0,
                Attributes.Cha : 1,
                ItemAttributes.Consumable :0,
                ItemAttributes.NbOfUses : 100,
                ItemAttributes.Weight : 10,
                ItemAttributes.Value : 25
            } 
            super().__init__("Ring", ItemList.Ring, stats)
        elif item ==item.Necklace :
            stats = {
                Attributes.HP : 50,
                Attributes.Armor : 0,
                Attributes.Strength : 0,
                Attributes.Dexterity : 10, 
                Attributes.Con : 1,
                Attributes.Intelligence : 1,
                Attributes.Wisdom : 0,
                Attributes.Cha : 1,
                ItemAttributes.Consumable :0,
                ItemAttributes.NbOfUses : 100,
                ItemAttributes.Weight : 10,
                ItemAttributes.Value : 25
            } 
            super().__init__("Necklace", ItemList.Necklace, stats)

        elif item ==item.Potion :
            stats = {
                Attributes.HP : 1,
                Attributes.Armor : 0,
                Attributes.Strength : 10,
                Attributes.Dexterity : 5, 
                Attributes.Con : 1,
                Attributes.Intelligence : 1,
                Attributes.Wisdom : 5,
                Attributes.Cha : 1,
                ItemAttributes.Consumable :1,
                ItemAttributes.NbOfUses : 1,
                ItemAttributes.Weight : 15,
                ItemAttributes.Value : 5
            } 
            super().__init__("Potion", ItemList.Potion, stats, timeLimitInSeconds=150)
        elif item==item.PotionIngredient1:
                stats ={
                Attributes.Wisdom : 5,
                ItemAttributes.NbOfUses : 1,
                ItemAttributes.Value : 3
                }
                super().__init__("PotionIngredient1", ItemList.PotionIngredient1,stats)
        elif item ==item.Coin :
            stats = {
                ItemAttributes.Consumable :1,
                ItemAttributes.NbOfUses : 1,
                ItemAttributes.Value : 1,
                ItemAttributes.Weight : 1
            } 
            super().__init__("Coin", ItemList.Coin, stats)
        else:
            raise Exception('Item not found')

