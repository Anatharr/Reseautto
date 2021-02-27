import numpy as np
from dungeonX.map import Dungeon
from dungeonX.characters import Character
from dungeonX.constants import Attributes
from dungeonX.characters.skills import Skill, SkillFactory, SkillEnum
from dungeonX.characters.players import Player, Fighter, Mage, Rogue
from dungeonX.characters.enemies import Enemy, Zombie, Dragon, Goblin
from dungeonX.items import Item
from dungeonX import Game
pos = (0,0)
types = "Zombie"
types2 = "Dragon"
types3 = "Goblin"
hp          = 100
armor       = 1
strength    = 2
dex         = 3
con         = 4
intell      = 5
wis         = 6
cha         = 7
defaultStats = ( hp, armor, strength, dex, con, intell, wis, cha)
game = Game().screens["game"]
def testCreationOfennemy():
    
    ennemy= Zombie (game,pos,defaultStats, types)
    assert(isinstance(ennemy, Zombie))  
    enemy2 = Dragon(game,pos,defaultStats, types2)
    assert(isinstance(enemy2, Dragon))
    enemy3 = Goblin(game,pos,defaultStats, types3)
    assert(isinstance(enemy3, Goblin))



