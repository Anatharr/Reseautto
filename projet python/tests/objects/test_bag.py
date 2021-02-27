from dungeonX.items.Item import Item, ItemFactory, ItemList
from dungeonX.characters.bag import Bag
from dungeonX.characters.players import Player
from dungeonX.characters.skills import Skill, SkillEnum, SkillFactory
import pytest


def testMaxWeightReached():
    b = Bag(10, [ItemFactory(ItemList.Armor) for _ in range(10)])
    assert b.getAllItems()== []


def testBagCreationAndFailureInAddingItems():
    potion = ItemFactory(ItemList.Potion)
    b = Bag(16,[potion])
    assert b.getCurrentWeight() == potion.getWeight()
    newPotion = ItemFactory(ItemList.Potion)
    assert b.addItem(newPotion)== False 
    assert b.getCurrentWeight() == potion.getWeight()
    assert b.getAllItems()== [potion]


def testRemoveNonexistantItemInBag():
    potion = ItemFactory(ItemList.Potion)
    b = Bag(16,[potion])
    newPotion = ItemFactory(ItemList.Potion)
    assert b.removeItem(newPotion)==False 

def testBagCreationAndAddingItems():
    potion = ItemFactory(ItemList.Potion)
    b = Bag(100, [potion])
    assert b.getCurrentWeight() == potion.getWeight()
    newPotion = ItemFactory(ItemList.Potion)
    b.addItem(newPotion)
    assert b.getCurrentWeight() == potion.getWeight() + newPotion.getWeight()



def testBalanceInBag():
    items = []
    coins = []
    potion = ItemFactory(ItemList.Potion)
    items.append(potion)
    for _ in range(3):
        coin = ItemFactory(ItemList.Coin)
        coins.append(coin)
        items.append(coin)

    b = Bag(100, items)
    assert b.getBalance() == sum([coin.getValue() for coin in coins])
    
def testChooseItemAndRemoveIt():
    potion = ItemFactory(ItemList.Potion)
    coin = ItemFactory(ItemList.Coin)
    items = [potion, coin]
    b = Bag(100, items)
    potionItems =  b.getItemsFromType(ItemList.Potion)
    assert b.getAllItems() == items
    b.removeItem(potionItems[0])
    assert b.getAllItems() == [coin]