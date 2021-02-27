from . import Enemy
from . import EnemyController
from ...constants import DEFAULT_ACTION_POINT, Attributes


class Dragon(EnemyController) :
	def __init__(self, game, pos, stats:tuple, eType, actionPointMax=3*DEFAULT_ACTION_POINT):
		"""
		
		"""
		super().__init__(game, pos, actionPointMax, stats, eType, mod="dragon",) 

class Goblin(EnemyController) :
	def __init__(self, game, pos, stats:tuple, eType, actionPointMax=DEFAULT_ACTION_POINT):
		"""
		
		"""
		super().__init__(game, pos, actionPointMax, stats, eType, mod="orc_shaman",)  
		self.bonusStrenght = 0

	def strengthBonusArea(self) :
		(x,y)=self.getPosition()
		area = []
		for i in range(-3,4) :
			for j in range(-3,4) :
				area.append((x+i,y+j))
		return area

	def playAction(self, dt:int) -> str:
		"""
		Override parent function to handle strength bonuses
		"""
		area = self.strengthBonusArea()
		friends = list(filter(lambda x:x in area, self.game.enemies))
		self.decreaseAttribute(Attributes.Strength, self.bonusStrenght) # Remove old bonus
		self.bonusStrenght = 5*len(friends)                             # Compute new bonus
		self.increaseAttribute(Attributes.Strength, self.bonusStrenght)      # Apply
		super().playAction(dt)


class Zombie(EnemyController) :
	def __init__(self, game, pos, stats:tuple, eType, actionPointMax=DEFAULT_ACTION_POINT):
		"""
		@reborn : boolean, indicate if the zombie has been reborned
		"""
		super().__init__(game, pos, actionPointMax, stats, eType, mod="zombie",)  
		self.reborn = False


	def die(self):
		if self.reborn :
			pass
			#super().die()
		else :
			self.reborn = True
			self.decrementHp(-100)

	def is_reborn(self):
		"""
		desc    : tell if the zombie is a reborn one
		@return : boolean
		"""
		return self.reborn



"""
	def makeDecision(self):

		super().makeDecision()
"""


"""
	def reborn(self):
		self.setHP(50)
"""




