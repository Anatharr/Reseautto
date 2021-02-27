import pygame, random, math, os, pickle, numpy
from collections import defaultdict
from .constants import TILE_WIDTH, MAP_WIDTH, MAP_HEIGHT, MAP_NB_ROOMS, TILESET, TILESET_H, TILESET_MINI, WALLS, serializeSurf, unserializeSurf, DEFAULT_DRAGON_STAT, DEFAULT_GOBLIN_STAT, DEFAULT_ZOMBIE_STAT, CHESTS_CONTENT
from .objects import Stairs, Chest
from .characters import Bag
from .items import ItemFactory
from dungeonX.characters.enemies.enemies import Zombie, Goblin, Dragon

class Map:
	"""
	This class is used to represent the map of the game

	By default the map is automatically generated, but you can specify
	a filename in the constructor to load it from a file. See
	loadFromFile(self, path) documentation for more info on the file
	format.

	Subclasses
	----------
	Tile(pygame.sprite.Sprite)
		this class is used to render all the tiles of the map

	Attributes
	----------
	_data : list
		this 2D list represents the dungeon. It should not be modified
		from outside of this class.
	width : int
		contains the width of the loaded grid
	height : int
		contains the height of the loaded grid
	layers : list
		this list contains all the layers of the map
	minimap : pygame.Surface
		this Surface is a miniaturized version of the map, used to
		render the minimap.
	startPos : tuple
		this tuple represents a valid position where we can spawn the
		player.

	Static Methods
	--------------
	vectToPos(vect) : tuple
		convert the given pygame.Vector2 into the position in the map
		grid.
	posToVect(pos) : pygame.Vector2
		converts the given position into an absolute position vector.

	Methods
	-------
	get(x, y) : str
		returns the char at the given coords of the map.
	set(x, y, char)
		sets the given char in the map
	loadFromFile(path)
		loads the map from a given file.
	generate()
		generates a completely random map.
	getRandomValidLocation() : tuple
		returns a tuple of valid coords where we can spawn an object.
	canWalkOn(x, y) : boolean
		return True if the given tile is walkable.
	_drawLine(xA,yA, xB,yB, char='o')
		draws the AB line with a given char.
	"""

	def __init__(self, dungeon, path=None, generate=True):
		self.dungeon = dungeon
		self.width = MAP_WIDTH
		self.height = MAP_HEIGHT
		self._data = [[' ' for x in range(self.width)] for y in range(self.height)]
		self.objects = []
		self.enemies = []
		self.startPos = None
		self.endPos = None

		# Load or generate the map
		if path:
			self.loadFromFile(path)
		elif generate:
			self.generate()

		# Load all tiles and create map images
		self.layers = {
			"floor": pygame.Surface((self.width*TILE_WIDTH, self.height*TILE_WIDTH)),
			"walls": pygame.Surface((self.width*TILE_WIDTH, self.height*TILE_WIDTH)),
			"fog": pygame.Surface((self.width*TILE_WIDTH, self.height*TILE_WIDTH))
		}
		self.minimap = pygame.Surface((self.width*3, self.height*3))
		self.minimap_fog = pygame.Surface((self.width*3, self.height*3))

		self.layers['fog'].fill((255,255,255))
		self.minimap_fog.fill((255,255,255))
		self.layers['floor'].fill((30,30,30))
		self.layers['walls'].fill((0,0,0))

		self.minimap.set_colorkey((0,0,0))
		self.layers['floor'].set_colorkey((0,0,0))
		self.layers['walls'].set_colorkey((0,0,0))

		self.updateImages()

		# Populate the map
		if self.startPos:
			self.objects.append(Stairs(self.startPos, down=False))
		if self.endPos:
			self.objects.append(Stairs(self.endPos))
		
		tot = 0
		for x in range(self.width):
			for y in range(self.height):
				if self.get(x,y)=='.':
					tot+=1
		for i in range(math.floor(tot*0.0075)) :
			self.enemies.append(Goblin(self.dungeon.game, self.getRandomValidLocation(), DEFAULT_GOBLIN_STAT, "Goblin")) 
		for i in range(math.floor(tot*0.005)) :
			self.enemies.append(Zombie(self.dungeon.game, self.getRandomValidLocation(), DEFAULT_ZOMBIE_STAT, "Zombie"))
		for i in range(math.floor(tot*0.0001)) :
			self.enemies.append(Dragon(self.dungeon.game, self.getRandomValidLocation(), DEFAULT_DRAGON_STAT, "Dragon"))

	def __getstate__(self):
		d = serializeSurf(self.__dict__)
		return d

	def __setstate__(self, state):
		self.__dict__ = unserializeSurf(state)


	def updateImages(self, cells=None):
		""" This method updates floor and walls images
		This operation is very time-consuming and must be called only
		once, and the modified cells must be specified.
		"""
		if not cells:
			cells = ((x, y) for x in range(self.width) for y in range(self.height))

		for x,y in cells:
			if self.get(x, y)!='?':
				tile = TILESET[self.get(x, y)]
				tile_h = TILESET_H[self.get(x, y)]
				tile_mini = TILESET_MINI[self.get(x,y)]
				if type(tile) == list:
					tile = random.choice(tile)

				self.minimap.blit(tile_mini, (x*3, y*3))
				self.layers["floor"].blit(tile, (x*TILE_WIDTH, y*TILE_WIDTH))					
				if tile_h:
					self.layers["walls"].blit(tile_h, (x*TILE_WIDTH, (y-1)*TILE_WIDTH))


	def updateWalls(self, cells=None):
		""" This method updates the walls according to the floor.
		This operation is very time-consuming and must be called only
		once, and the modified cells must be specified.
		"""
		if not cells:
			cells = ((x, y) for x in range(self.width) for y in range(self.height))

		walls = []
		for x,y in cells:
			if self.get(x,y)!='.':
				neighbours = ''.join('.' if self.get(X, Y)=='.' else ' ' for Y in range(y-1, y+2) for X in range(x-1, x+2))
				if neighbours in WALLS:
					walls.append((x, y, WALLS[neighbours]))
		for x, y, w in walls:
			self.set(x, y, w)

		self.updateImages(cells)




	def loadFromFile(self, path):
		""" Load a map from a given file """
		self._data = []
		with open(path, 'rb') as file:
			for line in file.read().decode("utf-8").split('\r\n' if os.name=='nt' else '\n'):
				if line=='':
					continue
				if '^' in line:
					self.startPos = (line.index('^'), len(self._data))
				if '$' in line:
					self.endPos = (line.index('$'), len(self._data))
				self._data.append(list(line.replace('^', '.').replace('$', '.')))
		self.width = len(self._data[0])
		self.height = len(self._data)
		if self.startPos==None:
			self.startPos = self.getRandomValidLocation()
		if self.endPos==None:
			self.endPos = self.getRandomValidLocation()

	@staticmethod
	def vectToPos(vect):
		if type(vect) in (tuple, list):
			if len(vect)!=2:
				raise ValueError("invalid vector : "+str(vect))
			return (math.floor(vect[0]/TILE_WIDTH), math.floor(vect[1]/TILE_WIDTH))
		return (math.floor(vect.x/TILE_WIDTH), math.floor(vect.y/TILE_WIDTH))

	@staticmethod
	def posToVect(pos):
		return pygame.Vector2(pos)*TILE_WIDTH

	@staticmethod
	def distanceBetween(xA, yA, xB, yB):
		""" Returns the distance between A and B """
		return math.sqrt((xB-xA)*(xB-xA) + (yB-yA)*(yB-yA))



	def generate(self):
		""" Generate a fully randomized dungeon

		This method uses a minimum spanning tree in order to link all
		the room's centers between them and give a sense of progression
		in the dungeon floor. For more information on the algorithm, see
		the following link :
		https://www.geeksforgeeks.org/kruskals-minimum-spanning-tree-algorithm-greedy-algo-2/

		STEPS:
		1. Fill the map with void.
		2. Add all the rooms, keeping track of their centers.
		3. Compute the minimum spanning tree.
		4. Draw the graph.
		5. Find all the dead ends.
		6. Add walls around all the map
		7. Spawn some objects on the dead ends.
		"""

		# Fill the map with void (' ')
		self._data = [[' ' for _ in range(self.width)] for _ in range(self.height)]
		centers = []

		for _ in range(MAP_NB_ROOMS):
			# Pick a rect width random size and coords
			w, h = random.randint(3, 10), random.randint(3, 10)
			startX = random.randint(3, self.width-3-w)
			startY = random.randint(3, self.height-3-h)

			# Check if this rect overlaps another rect
			if any(self.get(x,y)=='.' for x in range(startX, startX+w) for y in range(startY, startY+h)):
				continue

			# Fill the rect
			for x in range(startX, startX+w):
				for y in range(startY, startY+h):
					self.set(x, y, '.')

			# Register the rect's center
			centers.append((math.floor(startX+w/2), math.floor(startY+h/2)))

		# For each center compute all edge's weigths within a certain range (for performance reasons)
		_edges = [(math.floor(Map.distanceBetween(*A, *B)), A, B)
						for A in centers for B in centers if A!=B and Map.distanceBetween(*A, *B)<=self.width/3]
		edges = []

		# Delete all duplicated edges
		for i in range(len(_edges)):
			d, A, B = _edges[i]
			if not (d, B, A) in edges:
				edges.append((d, A, B))

		minimumSpanningTree = []

		# The edges are sorted by distance in order to favor small edges in the final graph
		for _,A,B in sorted(edges):
			if not _isGraphCyclic( minimumSpanningTree + [(A,B)] ):
				minimumSpanningTree.append((A,B))

		__deadEnds = []

		# Draw all lines
		for A,B in minimumSpanningTree:
			self._drawLine(*A, *B)
			__deadEnds.append(A)
			__deadEnds.append(B)
			
		# Get all dead ends, they will be useful as they are coords where we can spawn interesting objects such as chests, stairs, etc
		deadEnds = [A for A in __deadEnds if __deadEnds.count(A) == 1]
		self.startPos = deadEnds.pop(random.randrange(len(deadEnds)))
		self.endPos = deadEnds.pop(random.randrange(len(deadEnds)))
		for pos in deadEnds:
			content = list(numpy.random.choice([item[0] for item in CHESTS_CONTENT], random.randrange(3,5), p=[item[1] for item in CHESTS_CONTENT]))
			for i in range(len(content)):
				content[i] = ItemFactory(content[i])
			self.objects.append(Chest(pos, content))

		# add walls around averything
		walls = []
		for y,line in enumerate(self._data):
			for x,c in enumerate(line):
				if 1<x<self.width-2 and 1<y<self.height-2:
					if c==' ':
						neighbours = ''.join(self.get(X, Y) for Y in range(y-1, y+2) for X in range(x-1, x+2))
						if neighbours in WALLS:
							walls.append((x, y, WALLS[neighbours]))
						else:
							walls.append((x, y, '?'))
		for x, y, w in walls:
			self.set(x, y, w)


	def getRandomValidLocation(self):
		""" Returns a tuple which a valid random point where we can spawn an entity """
		ok = False
		while not ok:
			x = random.randrange(len(self._data[0]))
			y = random.randrange(len(self._data))

			if self.canWalkOn(x, y) and (self.startPos==None or self.distanceBetween(x,y, *self.startPos)>3):
				ok = True

		return (x, y)


	def canWalkOn(self, x, y):
		""" Return True if the tile is walkable """
		return 0<=x<self.width and 0<y<=self.height and self.get(x, y)=='.' and not any(entity.pos==(x,y) for entity in self.enemies+self.objects+(self.dungeon.players if self.dungeon.players!=None else []))


	def set(self, x, y, char):
		""" Sets the given char in the map """
		self._data[y][x]=char

	def get(self, x, y):
		""" Returns the char at the given coords """
		try:
			return self._data[y][x]
		except IndexError:
			return ' '

	def _drawLine(self, xA,yA, xB,yB, char='.'):
		""" Draws the AB line with a given char.

		The line isn't really straigth but the main goal was to ensure
		that it was continuous in order to be able to place walls
		around it and keep it walkable. For example :

			   ┌──────┐
			   │A.....└┐
			   └────┐..└┐       <--- GOOD
				    └┐.B│
				     └──┘

			   ┌───┐
			   │A..└─┐
			   └──┐..└──┐       <--- BAD
				  └─┐..B│
				    └───┘
		"""

		x = xA
		y = yA
		while x!=xB or y!=yB:
			self.set(x, y, char)
			nesw = {
				Map.distanceBetween(x,y-1, xB,yB): (x, y-1),
				Map.distanceBetween(x+1,y, xB,yB): (x+1, y),
				Map.distanceBetween(x,y+1, xB,yB): (x, y+1),
				Map.distanceBetween(x-1,y, xB,yB): (x-1, y)
			}
			x, y = nesw[min(nesw)]

	def renderInConsole(self):
		""" Render the map as text in the console

		This functions serves to debug and test the
		map loading / generation.
		"""
		print('\n')
		for index, line in enumerate(self._data):
			print(''.join(line))



def _isGraphCyclic(graph):
	""" Checks if the given graph contains a cycle
	
	This function is used to find the minimum spanning tree in the
	Map.generate() method. It uses a union-find algorithm, watch the
	following video for	more details on how it works:
		https://youtu.be/mHz-mx-8lJ8
	"""

	parent = defaultdict(tuple)

	def find_parent(i):
		if parent[i] == ():
			return i
		if parent[i]!= ():
			return find_parent(parent[i])

	def union(x,y):
		parent[find_parent(x)] = find_parent(y)

	for i,j in graph:
		x = find_parent(i)
		y = find_parent(j)
		if x == y:
			return True
		union(x,y)



class Dungeon:
	def __init__(self, game, editMode=False):
		self.game = game
		self.editMode = editMode
		self.players = None
		if not self.editMode:
			self.game.blitLoadingScreen()
		self.currentFloor = Map(self, generate=not editMode)
		self.floors = [self.currentFloor]
		self.currentFloorIndex = 0
		self.bag = Bag(500)

	def save(self, path):
		with open(path, 'wb') as file:
			file.write(pickle.dumps(self))

	@staticmethod
	def load(path):
		with open(path, 'rb') as file:
			return pickle.loads(file.read())

	def descend(self):
		if not self.editMode:
			self.game.blitLoadingScreen()

		self.currentFloorIndex += 1
		if self.currentFloorIndex == len(self.floors):
			self.floors.append(Map(self, generate=not self.editMode))
		self.currentFloor = self.floors[self.currentFloorIndex]
		if not self.editMode:
			self.loadFloor()

	def ascend(self):
		if self.currentFloorIndex == 0:
			if not self.editMode:
				self.game.game.addToLog("You can't run away from the dungeon.")
			return
		self.currentFloorIndex -= 1
		self.currentFloor = self.floors[self.currentFloorIndex]
		if not self.editMode:
			self.loadFloor(self.currentFloor.endPos)

	def loadFloor(self, startPos=None):
		self.game.mapwindow.mapIndex = self.currentFloorIndex
		self.game.enemies = self.currentFloor.enemies
		self.game.objects = self.currentFloor.objects

		startingPositions = [ (-1,0), (0,-1), (1,0), (0,1) ]
		startingPositions.pop(random.randrange(4))
		if startPos==None:
			startPos = self.currentFloor.startPos
		x,y = startPos
		for i, player in enumerate(self.game.players):
			a,b = startingPositions[i]
			player.teleport((x+a, y+b))
			player.setActionPoint(player.actionPointMax)
