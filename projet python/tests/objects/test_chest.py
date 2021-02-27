from dungeonX.objects.chest import Chest
from dungeonX.items.Item import ItemFactory, Item, ItemList
from dungeonX.constants import State
import pytest

defaultPos = (5,5)

def testChestSwitchState():
    swordItem = ItemFactory(ItemList.Sword)
    bronzeChest = Chest(defaultPos, content=[swordItem], state=State.locked, key='1234')
    bronzeChest.unlock(key='1234')
    assert bronzeChest.getState() == State.unlocked

def testRetrieveItems():
    swordItem = ItemFactory(ItemList.Sword)
    bronzeChest = Chest(defaultPos, content=[swordItem], state=State.locked, key='1234')
    assert bronzeChest.getItemsFromChest() == False
    bronzeChest.unlock(key='1234')
    assert bronzeChest.getItemsFromChest() == [swordItem]
    

def testAddItemBeforeAndAfterUnlock():
    swordItem = ItemFactory(ItemList.Sword)
    bronzeChest = Chest(defaultPos, state=State.locked, key='1234', content=[])
    assert bronzeChest.addItem(swordItem) == False
    bronzeChest.unlock(key='1234')
    bronzeChest.addItem(swordItem)
    assert bronzeChest.getItemsFromChest() == [swordItem]

def testUnlockChest():
    easyChest = Chest(defaultPos, state=State.locked, content=[])
    assert easyChest.getItemsFromChest() == False
    easyChest.unlock()
    content = easyChest.getItemsFromChest()
    for item in content:
        print(item.getName())
        print(easyChest)
    assert content == []

def testAlreadyUnlocked():
    easyChest = Chest(defaultPos, state=State.locked, content=[])
    easyChest.unlock()
    assert easyChest.unlock() == False


def testUnlockChestWithLuckRate():
    easyChest = Chest(defaultPos, state=State.locked, content=[],key='1234')
    assert easyChest.getState() == State.locked
    easyChest.unlock(alwaysSuccess=True)
    assert easyChest.getState() == State.unlocked





    
