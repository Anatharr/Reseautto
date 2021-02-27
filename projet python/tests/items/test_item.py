from time import sleep
from dungeonX.items.Item import ItemList, ItemFactory, Item
import pytest

def testItemCreation():
    items = []
    for _ in range(100):
        swordItem = ItemFactory(ItemList.Sword)
        items.append(swordItem)
        with pytest.raises(Exception):
            swordItem.getTimeLimit() 
        assert swordItem.getName() == 'Sword'

def testItemNotUsed():
    swordItem = ItemFactory(ItemList.Sword)
    with pytest.raises(Exception):
            swordItem.getTimeLimit() 
    assert swordItem.isUsed() == False

def testItemUsed():
    potionItem = ItemFactory(ItemList.Potion)
    numberOfUsesInCreationTime = potionItem.getRemainingUses()
    potionItem.useItem()
    assert potionItem.isUsed() == True
    assert potionItem.getRemainingUses() == numberOfUsesInCreationTime - 1
    sleep(2)
    assert potionItem.getTimeRemaining() < 148
    

def testItemConsumed():
    swordItem = ItemFactory(ItemList.Sword)
    numberOfUsesInCreationTime = swordItem.getRemainingUses()
    for _ in range(numberOfUsesInCreationTime):
        assert swordItem.isconsumed() == False
        swordItem.useItem()
    assert swordItem.isconsumed() == True

def testCoin():
    smallCoin = ItemFactory(ItemList.Coin)
    assert smallCoin.getRemainingUses() == 1
    smallCoin.useItem()
    assert smallCoin.isconsumed() == True


def testItemNotFound():
    with pytest.raises(Exception):
        item = ItemFactory(ItemList.fakeItem) 
        
    


    

   