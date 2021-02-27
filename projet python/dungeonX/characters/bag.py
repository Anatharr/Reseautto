from ..items import Item, ItemFactory
from ..constants import ItemAttributes, ItemList
# from dungeonX.objects.object import Object

class Bag():
    def __init__(self, maxWeight: int = 30, content : [Item] = []):
        contentWeight = sum([item.getWeight() for item in content])

        self._maxWeight = maxWeight
        if (contentWeight > self._maxWeight):
            print("Please add less items in the bag since limit is reached")
            self._content = []
            self._currentWeight = 0
        else:
            self._content = content
            self._currentWeight = contentWeight
        

    def addItem(self, item: Item):
        if (item.getWeight() + self._currentWeight > self._maxWeight):
            print("You can't add this item to the bag: max weight reached")
            return False
        self._content.append(item)
        self._currentWeight += item.getWeight()

    def removeItem(self, item: Item):
        if (item not in self._content):
            print('This item is not in your bag')
            return False
        self._content.remove(item)
        self._currentWeight -= item.getWeight()
        return item

    def getCurrentWeight(self):
        return self._currentWeight

    def getMaxWeight(self):
        return self._maxWeight

    def getBalance(self):
        return sum([item.getValue() for item in self._content if item.getItemType() == ItemList.Coin])

    def getItemsFromType(self, itemType: ItemList):
        return [item for item in self._content if item.getItemType() == itemType]

    def getAllItems(self):
        return self._content

    def flush(self):
        self._content = []
        self._currentWeight = 0

