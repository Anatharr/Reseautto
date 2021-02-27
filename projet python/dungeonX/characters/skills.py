from enum import Enum, auto
# from dungeonX.characters.players import Player
from dungeonX.constants import RANKS_MANAGEMENT

class SkillEnum(Enum):
	Fly = "Fly"
	Stealth = "Stealth"
	Perception= "Perception"
	DisableDevice = "DisableDevice"

class Skill():
	"""
	This is a class representing all logic behind a skill

	SkillsPoints: Point de skills qui sont donnés au joueur à chaque utilisation du skill

	SkillScore in (Player): nb of skillPoints that adds up when using a skill 

	Example 
	-------
	Skill creation 
		{name}Skill = Skillfactory(SkillEnum.{choose skill type here})
		 stealth = SkillFactory(SkillEnum.Stealth)
	
	Subclasses
	----------
	Skillfactory
	This is a class that holds the allowed types of skills along with their specs

	So if wanted to ass a new skill , you'd have to add it to the factory in order to use it
	
	Attributes
	----------

	_type : SkillEnum
		type of skill
	_ranksManagment : dict of two parameters 
		the dic that holds : skillPoints (points added to players Scord for each call of the skill )
	    rankUpPoints : points needed to be able to mpve to next Rank
	_startingRank  : int 
		represents the starting rank of a skill (trained/untrained purposes)
	__nbOfRanks :
		number of Ranks 
	_currentRank: 
		current rank of a skill 
	_currentRankUpPoints :
		Current Points "pour passer au niveau sup pour un skill"

	
	Static Methods
	--------------
	None

	Methods
	-------
	getCurrentRank(self)
		returns _curentRank 
	getType(self)
		returns type of Skill
	getCurrentSkillPoints(self)
		Returns current skillPoints of the skill in its' current Rank
	getCurrentRankUpPoints(self)
		returns current rankUpPoints available
	getRankUpPoints(self):
		returns current rankUpPoints total needed to Rankup
	addPoints(self, numberOfPoints=1)
		adds skills points to the skill 
		if the total number exceeds RankUpPoints of the rank it ranks up and keeps the change 
		if that change(PointsTodistribute) is still above the rankUpPoints of the new rank it ranks up 
		All until the change is below the rankUpPoints of the current rank 


	"""
	def __init__(self, skillType: SkillEnum, ranksManagement: dict, startingRank=0,currentTurn=0):
		self._nbOfRanks = len(ranksManagement)
		self._currentRank = startingRank
		self._ranksManagement = ranksManagement
		self._currentRankUpPoints = 0
		self._type = skillType
		self.turn = currentTurn
		self.activity=1

	def getCurrentRank(self):
		return self._currentRank
	
	def getType(self):
		return self._type

	def getCurrentSkillPoints(self):
		return self._ranksManagement[self._currentRank]['skillPoints']

	def getCurrentRankUpPoints(self):
		return self._currentRankUpPoints

	def getRankUpPoints(self):
		return self._ranksManagement[self._currentRank]['rankUpPoints']

	def addPoints(self, numberOfPoints=1):
		if self._currentRankUpPoints + numberOfPoints >= self.getRankUpPoints():
			pointsToDistribute = numberOfPoints
			while self._currentRankUpPoints + pointsToDistribute >= self.getRankUpPoints(): #loop while ther's 
				pointsToDistribute = numberOfPoints - (self.getRankUpPoints() - self._currentRankUpPoints)
				self._currentRank += 1

			self._currentRankUpPoints = pointsToDistribute
		else:
			pointsToDistribute = numberOfPoints
			self._currentRankUpPoints += pointsToDistribute

	def rankup(self,number):
		self._currentRank += number

		print("ranking up"+str(self._currentRank))


class SkillFactory(Skill): 
	def __init__(self, skill: SkillEnum):
		
		if skill == SkillEnum.Stealth:
			super().__init__(SkillEnum.Stealth, RANKS_MANAGEMENT)
		elif skill == SkillEnum.Fly:
			super().__init__(SkillEnum.Fly, RANKS_MANAGEMENT)
		elif skill == SkillEnum.Perception:
			super().__init__(SkillEnum.Perception, RANKS_MANAGEMENT)
		elif skill == SkillEnum.DisableDevice:
			super().__init__(SkillEnum.DisableDevice, RANKS_MANAGEMENT, startingRank=1)
		else: raise Exception('Not allowed skill creation')
			
		