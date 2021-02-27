from dungeonX.objects.door import Door
from dungeonX.constants import State

def testDoorUnlock():
    Frontdoor= Door((1,1),State.locked)
    Frontdoor.unlock(alwaysSuccess=True)
    assert Frontdoor.getState() == State.unlocked