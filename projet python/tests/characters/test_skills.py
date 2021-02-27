from dungeonX.characters.skills import Skill, SkillFactory, SkillEnum

def testSkillCreation():
    stealth = SkillFactory(SkillEnum.Stealth)
    stealth.addPoints(50)
    assert stealth.getCurrentRank() == 1
    assert stealth.getCurrentSkillPoints() == 7
    assert stealth.getRankUpPoints() == 34
    assert stealth.getCurrentRankUpPoints() == 20
    
def testdumbSkillTest():
    stealth = SkillFactory(SkillEnum.Stealth)
    stealth.addPoints(25)
    assert stealth.getCurrentRank() == 0
    assert stealth.getCurrentSkillPoints() == 5
    assert stealth.getCurrentRankUpPoints() == 25







