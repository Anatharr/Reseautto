import numpy as np
from dungeonX import Game
from dungeonX.characters import Character
from dungeonX.constants import Attributes, RANKS_MANAGEMENT,State
from dungeonX.characters.skills import Skill, SkillFactory, SkillEnum
from dungeonX.characters.players import Player, Fighter, Mage, Rogue, PlayerEnum
from dungeonX.characters.npc import NPC
from dungeonX.characters.enemies import Zombie, Goblin, Dragon, Enemy
from dungeonX.characters.bag import Bag
from dungeonX.objects.chest import Chest
from dungeonX.objects.door import Door
from dungeonX.items.Item import Item, ItemFactory, ItemList
from time import sleep 
from math import floor


game = Game().screens["game"] # This is not really the game but the instance of GameScreen, where the dungeon, players, etc are stored

defaultPosition = (1,2)

defaultSkills = [SkillFactory(SkillEnum.Stealth)]


hp          = 100
armor       = 7
strength    = 2
dex         = 3
con         = 4
intell      = 5
wis         = 6
cha         = 7
skillsPoint = 0

actionPoint = 10
defaultStats = (hp, armor, strength, dex, con, intell, wis, cha) #( HP, armor, strength, dex, con, intell, wis, cha )
lineOfSight = 9

defaultPotions = ItemFactory(ItemList.Potion)

def testCharacterCreation():
    Character.ID = 50
    character = Character(game, defaultPosition, actionPoint, *defaultStats)
    assert character.getID() == 50
    assert character.getHP() == 100 # Cette méthode est redondante avec character.getAttribute(Attributes.HP), il faudrait l'enlever ou alors enlever HP des attributs
    assert character.getPosition() == defaultPosition
    assert character.getActionPoint() == 10
    for i, attribute in enumerate(Attributes):
        assert character.getAttribute(attribute) == defaultStats[i]
    print(defaultStats)
    fighter = Fighter(game, defaultPosition, defaultSkills=defaultSkills, defaultStats=defaultStats)
    assert fighter.getHP() == 100
    assert fighter.getPosition() == defaultPosition
    assert fighter.getActionPoint() == 5
    assert fighter.getID() == 51
    for i, attribute in enumerate(Attributes):
        assert fighter.getAttribute(attribute) == defaultStats[i]

    # mage = Mage(game, defaultPosition, defaultSkills, defaultStats)
    rogue = Rogue(game, defaultPosition, defaultSkills=defaultSkills,defaultStats=defaultStats)
    assert rogue.getHP() == 100
    assert rogue.getPosition() == defaultPosition
    assert rogue.getActionPoint() == 5
    assert rogue.getID() == 52
    for i, attribute in enumerate(Attributes):
        assert rogue.getAttribute(attribute) == defaultStats[i]

# test w errors 

def testAttackBetweenTwoCharacters():
    player  = Player(game, (0,0), PlayerEnum.Rogue, actionPoint ,lineOfSight, defaultStats)
    player.incrementExp(20)
    opponent = Enemy(game, (1,10), 5, defaultStats, "Zombie")
    player.attack(opponent)

    ##dice ==1
    #assert player.getActionPoint() == 8
    #assert player.getExp() == 20
    #assert opponent.getHP == 100

    # changer les asserts ici : le player gagne de l'exp que quand il tue, donc lui mettre des stats très hautes pour forcer ça

    ##dice <20 =18
    #assert player.getActionPoint() == 8

    #si opponent pas mort
    #assert player.getExp()==20

    #si opponent mort
    #assert player.getExp(exp=player.exp)==70

    ##dice ==20 
    # assert player.getActionPoint() == 8
    # assert opponent.getHP()==85
    # assert player.getExp(exp=player.exp)==30


def testEnemyAttacksPlayer() :
    enemy1 = Zombie(game,(0,1),defaultStats, "Zombie")
    fighter1 = Fighter(game,(0,0),defaultSkills, actionPoint, lineOfSight, defaultStats)
    game.players=[fighter1]

    enemy1.attack(fighter1)

    assert enemy1.getActionPoint()<10
    #assert fighter1.getHP()<100   # works

    enemy1.setAttribute(Attributes.Strength,10000)
    #enemy1.attack(fighter1)
    #assert fighter1 not in game.players  # works


def testSetPositionOfCharacter():
    player = Rogue(game, defaultPosition, defaultSkills=defaultSkills, defaultStats=defaultStats)
    newPosition=(3,4)
    player.setPosition(newPosition)
    assert player.getPosition() == newPosition

def testSetAttribute():
    #set attribute : HP
    character = Character(game, defaultPosition,actionPoint ,*defaultStats)
    character.setAttribute(Attributes.HP,100) 
    assert character.getHP()==100

def testSetAttributesOfCharacter():
    character = Character(game, defaultPosition,actionPoint, *defaultStats)
    character.setAttribute(Attributes.Cha,10)
    assert character.getAttribute(Attributes.Cha) == 10 




def testcharacterDies():
    rogue=Rogue(game, (game.dungeon.currentFloor.startPos[0]+1, game.dungeon.currentFloor.startPos[1]))
    game.players=[rogue]
    #rogue.die()
    #assert game.players ==[]
    #assert  rogue not in game.players
    

def testGetPlayerBag():
    potion = ItemFactory(ItemList.Potion)
    bag=game.inventorywindow.bag
    player  = Player(game, (0,0), PlayerEnum.Rogue,  actionPoint ,lineOfSight, defaultStats)
    player1 = Player(game, (1,5),PlayerEnum.Fighter, actionPoint ,lineOfSight, defaultStats)
    assert player.getBag()  == bag 
    assert player1.getBag() == bag

def testPlayerUsesSkill():
    defaultSkillTry=[SkillFactory(SkillEnum.Stealth),SkillFactory(SkillEnum.DisableDevice)]
    player = Rogue(game, defaultPosition, defaultSkills=defaultSkillTry, defaultStats= defaultStats)
    assert player.getSkillScore()==0
    #using stealth 
    player.AtemptToApplySkill(SkillEnum.Stealth, alwaysSuccess=True)
    assert player.getVisibility() == False
    assert player.getSkillScore()== RANKS_MANAGEMENT[0]['skillPoints']
    player.attributeSkillsPoint(SkillEnum.Stealth, 5)
    assert player.getSkillScore()==0
    game.turnNumber+=1
    player.AtemptToApplySkill(SkillEnum.Stealth)
    assert player.getVisibility() == True


    
    player.AtemptToApplySkill(SkillEnum.Stealth, alwaysSuccess=True)
    assert player.getSkillScore() == RANKS_MANAGEMENT[0]['skillPoints']
    player.attributeSkillsPoint(SkillEnum.Stealth, 1)
    assert player.getSkillScore()==4  
    skillScore = player.getSkillScore()
    #using disable device tp unlock Chest 
    testChest = Chest((1,1),state=State.locked, content=[],key='1234')
    player.AtemptToApplySkill(SkillEnum.DisableDevice, alwaysSuccess=True,options=testChest)
    assert player.getSkillScore()== skillScore + RANKS_MANAGEMENT[1]['skillPoints']
    assert testChest.getState()== State.unlocked
    #using disable device for door 
    testDoor= Door((2,2),state=State.locked,key='2345')
    player.AtemptToApplySkill(SkillEnum.DisableDevice, alwaysSuccess=True,options=testDoor)
    assert player.getSkillScore()== skillScore + (2* RANKS_MANAGEMENT[1]['skillPoints'])
    assert player.getSkillScore()==18
    assert testDoor.getState()==State.unlocked

def test_NPC_sellItem():
    player = Player(game, (0,0), PlayerEnum.Rogue,actionPoint, skills = defaultSkills, stats=defaultStats, lineOfSightRadius=5)
    potion = ItemFactory(ItemList.Potion)
    npc = NPC(game, (1,2), [potion])

    playerBag = player.getBag()
    playerBag.flush()
    npcBag = npc.getBag()
    
    collectionOfCoins =[ItemFactory(ItemList.Coin) for _ in range(20)]
    for coin in collectionOfCoins:
        playerBag.addItem(coin)
    
    npc.sellItem(ItemList.Potion, player)
    assert len(playerBag.getAllItems()) == len(collectionOfCoins) + 1
    #assert len(npcBag.getAllItems()) == 0
#works when set the bag to the npc not npctrading window
def test_Player_sellItem():
    potion = ItemFactory(ItemList.Potion)
    player = Player(game, (0,0), PlayerEnum.Rogue,actionPoint, skills = defaultSkills, stats=defaultStats,lineOfSightRadius=5)
    npc = NPC(game, (1,2))
    playerBag = player.getBag()
    playerBag.flush()
    playerBag.addItem(potion)
    npcBag = npc.getBag()
    
    collectionOfCoins =[ItemFactory(ItemList.Coin) for _ in range(20)]
    for coin in collectionOfCoins:
        npcBag.addItem(coin)
    
    player.sellItem(ItemList.Potion,npc)
    #assert len(npcBag.getAllItems()) == len(collectionOfCoins) + 1
    #assert len(playerBag.getAllItems()) == 0



def testPlayerEquip():
    sword = ItemFactory(ItemList.Sword)
    armor = ItemFactory(ItemList.Armor)
    ringL = ItemFactory(ItemList.Ring)
    ringR2 = ItemFactory(ItemList.Ring)
    ringR = ItemFactory(ItemList.Ring)
    necklace = ItemFactory(ItemList.Necklace)
    potion = ItemFactory(ItemList.Potion)
    player = Player(game, (0,0), PlayerEnum.Rogue,actionPoint, skills = defaultSkills, stats=defaultStats,lineOfSightRadius=5)
    currentStats = dict(player.listStat)


    player.equip(potion)
    assert player.listStat==currentStats
    assert player.equipment==[None,None,None,None,None]

    player.getBag().flush()
    player.getBag().addItem(sword)
    player.getBag().addItem(necklace)
    player.getBag().addItem(ringR)
    player.getBag().addItem(ringL)
    player.getBag().addItem(ringR2)
    player.getBag().addItem(armor)
    player.equip(sword)
    player.equip(ringL)
    player.equip(necklace)
    player.equip(armor)
    player.equip(ringR)
    assert player.listStat!=currentStats
    assert all(player.equipment[i]==item for i,item in enumerate([sword,armor,necklace,ringL,ringR]))
    items = player.getBag().getAllItems()
    assert all(i not in items for i in [sword,armor,necklace,ringL,ringR])

    player.equip(ringR2)
    assert all(player.equipment[i]==item for i,item in enumerate([sword,armor,necklace,ringL,ringR2]))
    assert ringR in player.getBag().getAllItems()

def testSpellUsage() :
    mage1 = Mage(game, defaultPosition, defaultSkills, defaultStats, defaultPotions)
    q1 = mage1.acidStream.getQuantity()
    mage1.acidStream.changeQuantity(1)
    q2 = mage1.acidStream.getQuantity()
    assert q1+1 == q2

    mage1.castSpell(mage1.acidStream, (5, 10))
    assert mage1.acidStream.getQuantity() == q1

def testFighter() :
    """
    to test:
    - init done
    - protect done
    - level up random item done
    """

    fighter1 = Fighter(game,(0,0),defaultSkills, actionPoint, lineOfSight, defaultStats)
    enemy1 = Zombie(game,(0,1),defaultStats, "Zombie")
    mage1 = Mage(game,(1,1), defaultSkills,defaultStats, defaultPotions)
    enemy2 = Zombie(game,(0,1),defaultStats, "Zombie")

    game.players.append(fighter1)
    game.players.append(mage1)
    game.enemies.append(enemy1)

    assert fighter1.getPlayerType()==PlayerEnum.Fighter

    fighter1.setAttribute(Attributes.Strength, 1000)

    # when mage is attacked fighter protects
    enemy1.attack(mage1)
    #assert(enemy1.getHP()<100) works but commented because assert doesn't pass if dice=1

    # when fighter is attacked, he doesn't protect himself
    enemy2.attack(fighter1)
    assert enemy2.getHP()==100

    bagWeightInitial = fighter1.getBag().getCurrentWeight()
    fighter1.levelUp()
    assert fighter1.getBag().getCurrentWeight() > bagWeightInitial
    
def testEnemyConversion() :
    mage1 = Mage(game, (0,0), defaultSkills, defaultStats, defaultPotions)
    enemy1 = Zombie(game, (0,1), defaultStats, "Zombie")

    mage1.convertEnemy(enemy1)

    #assert enemy1.isConverted  works

def testExpNeededToLevelUp() :
    mage1 = Mage(game, (0,0), defaultSkills, defaultStats, defaultPotions)
    #self.expToLevelUp = floor(self.expToLevelUp*1.5)

    # level 1
    assert mage1.getLevel()==1
    assert mage1.getExpToLevelUp()==100

    # level 2
    mage1.levelUp()
    assert mage1.getExpToLevelUp()==floor(100*1.5)
    assert mage1.getExpToLevelUp()==150

    # level 3
    mage1.levelUp()
    assert mage1.getExpToLevelUp()==floor(floor(100*1.5)*1.5)
    assert mage1.getExpToLevelUp()==225

def testRest() :
    mage1 = Mage(game, (0,0), defaultSkills, defaultStats, defaultPotions)
    enemy1 = Zombie(game, (0,1), defaultStats, "Zombie")

    acidStreamQ1 = mage1.acidStream.getQuantity()
    fireballQ1 = mage1.fireball.getQuantity()
    meteorswarmQ1 = mage1.meteorSwarm.getQuantity()

    enemy1.attack(mage1)
    if mage1.getHP()<100 :
        HP1=mage1.getHP()
        mage1.rest()
        assert mage1.getHP() == HP1 + 20 or mage1.getHP()==100
        assert mage1.acidStream.getQuantity() == acidStreamQ1+1
        assert mage1.fireball.getQuantity() == fireballQ1+1
        assert mage1.meteorSwarm.getQuantity() == meteorswarmQ1+1
    else :
        print("Attack against mage didn't work")

    rogue1 = Rogue(game,defaultPosition,defaultSkills, defaultStats)

    skillScore1 = rogue1.getSkillScore()

    enemy1.attack(rogue1)
    if rogue1.getHP()<100 :
        HP1=rogue1.getHP()
        rogue1.rest()
        assert rogue1.getHP() == HP1 + 20 or rogue1.getHP()==100
        #assert rogue1.getSkillScore() == skillScore1+1
    else :
        print("Attack against rogue didn't work")

    fighter1 = Fighter(game, defaultPosition)

    bagWeigth1 = fighter1._bag.getCurrentWeight()

    enemy1.attack(fighter1)
    if fighter1.getHP()<100 :
        HP1=fighter1.getHP()
        assert fighter1.getHP() == HP1 + 20 or fighter1.getHP()==100
        assert fighter1._bag.getCurrentWeight() > bagWeigth1
    else :
        print("Attack against fighter didn't work")
        







    



    
    
