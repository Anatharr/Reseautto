from ..constants import serializeSurf, unserializeSurf

class GameObject:
    def __init__(self, pos:tuple) :
        self.pos= pos
        
    def getPosition(self) :
        """returns position of the object """
        return (self.pos)

    def interactWithPlayer(player):
        pass

    def animsIterator(self):
        pass

    def updateAnims(self):
        pass

    def __getstate__(self):
        d = dict(serializeSurf(self.__dict__))
        d["animsIter"] = None
        return d

    def __setstate__(self, state):
        state["animsIter"] = self.animsIterator()
        self.__dict__ = unserializeSurf(state)



def testInitObject():
    """
    docstring
    """
    object = Object((1,2))
    assert object.getPosition() == (1,2)
