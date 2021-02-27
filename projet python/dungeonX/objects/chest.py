import pygame
from ..items import Item
from ..constants import State, TILE_WIDTH, serializeSurf, unserializeSurf
from ..objects.object import GameObject
import random

class Chest(GameObject):
	"""
	This is a subclass of object to represent the chest Object 
	Example 
	-------
	Chest creation 
		{name}Chest = Chest(content=[{name}Item],state=State.locked,key='1234')
		bronzeChest = Chest(content=[swordItem], state=State.locked, key='1234')

	
	Subclasses
	----------
	None
	
	Attributes
	----------
	
	_content : list 
		list of items  that can also be nothing (no items =>empty chest )
	_key : [str=''] 
		the key that unlocks a chest
	_state : [State=State.unlocked]
		represents the unlocked or locked state of a chest 
	
	Static Methods
	--------------
	None

	Methods
	-------
	unlock(self, key='')
		unlocks the chest if a key is needed or not 
	getState(self): state
		returns if a chest is locked or not
	addItem(self,content: Item)
		adds One item to a Chest only if it's unlocked 
	getItemsFromChest(self)
		retreive items from a chest

	"""
	def __init__(self, pos: tuple, content: [Item]=None, key: str = '', state: State = State.locked):
		super().__init__(pos)
		if content==None:
			content = generateContent()
		self._content = content
		self._state = state
		self._key = key

		self.__images = [
			pygame.image.load("dungeonX/assets/objects/chest_full_open_anim_f0.png"),
			pygame.image.load("dungeonX/assets/objects/chest_full_open_anim_f1.png"),
			pygame.image.load("dungeonX/assets/objects/chest_full_open_anim_f2.png"),
			pygame.image.load("dungeonX/assets/objects/chest_empty_open_anim_f2.png")
		]
		self.animationSpeed = 100 # in milliseconds
		self.__dt = 0
		self.__animState = 'closed'
		self.animsIter = self.animsIterator()
		self.image = self.__images[0]
		self.rect = pygame.Rect(pygame.Vector2(pos)*TILE_WIDTH,(TILE_WIDTH,TILE_WIDTH))

	def unlock(self, key='', alwaysSuccess=False): 
		"""
		unlocks the chest if a key is needed or not 
		"""
		if (self._state == State.locked): 
			if (key == self._key):
				self._state = State.unlocked
				self.__animState = 'opened'
				print('successful :Key')
			elif self.SuccessRateToUnlock(alwaysSuccess=alwaysSuccess):
				self._state = State.unlocked
				self.__animState = 'opened'
				print('successful : Luck')
			else: print('Wrong Key'); return False
		else: print('Chest already unlocked'); return False
		
	def SuccessRateToUnlock(self, alwaysSuccess=False):
		"""
		docstring
		"""
		return random.randint(1,20) < 3 or alwaysSuccess
		
	



	def getState(self):
		"""
		returns if a chest is locked or not
		"""
		return self._state
	  
	def addItem(self,content: Item):
		"""
		adds One item to a Chest only if it's unlocked 
		"""
		if(self._state == State.unlocked):
			self._content.append(content)
		else: print('Please unlock chest before adding items'); return False
		

	def getItemsFromChest(self):
		"""
		retreive items from a chest 
		"""
		if(self._state == State.unlocked):
			self.__animState = 'empty'
			if self._content is not None:
				tmp = self._content
				self._content = None
				return tmp 
			else: print('The chest is empty !'); return []
		else: print('Please unlock chest before retrieving items'); return False
		

	def animsIterator(self):
		i = 0
		elapsedTime = 0
		while True:
			if self.__animState == 'closed':
				elapsedTime = 0
				i = 0
			if self.__animState == 'opened' and i<2:
				elapsedTime += self.__dt
				if elapsedTime > self.animationSpeed:
					i += 1
					elapsedTime = 0
			if self.__animState == 'empty':
				i = 3
			yield self.__images[i]


	def updateAnim(self, dt):
		self.__dt = dt
		self.image = next(self.animsIter)

	def interactWithPlayer(self, player):
		if self.getState()==State.locked:
			self.unlock()
			if self.getState()==State.unlocked:
				player.game.game.addToLog(" Chest Unlocked ")
				player.game.game.addToLog(" Click to retreive one/many item(s)!")

		else:
			if not self._content:
				player.game.game.addToLog(" The chest is empty !")
			else:
				for item in self.getItemsFromChest():
					player.getBag().addItem(item)
				player.game.game.addToLog(" Item(s) retreived ")


