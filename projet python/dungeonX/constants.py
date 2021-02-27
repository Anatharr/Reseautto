import math, pygame, os
from enum import Enum, auto 
from datetime import timedelta, datetime

def serializeSurf(s):
	if type(s) == dict:
		s = dict(s)
		for k in s:
			s[k] = serializeSurf(s[k])
	elif type(s) == list:
		s = list(s)
		for i, e in enumerate(s):
			s[i] = serializeSurf(e)
	elif type(s) == tuple:
		s = tuple(s)
		for i, e in enumerate(s):
			s = s[:i] + (serializeSurf(e),) + s[i+1:]
	elif type(s) == pygame.Surface:
		return ("pygame.Surface", pygame.image.tostring(s, 'RGBA'), s.get_alpha(), s.get_size(), s.get_colorkey())
	return s

def unserializeSurf(s):
	if type(s) == dict:
		for k in s:
			s[k] = unserializeSurf(s[k])
	elif type(s)==tuple and s[0]=="pygame.Surface":
		t, surf, alpha, size, colorkey = s
		s = pygame.image.fromstring(surf, size, 'RGBA')
		s.set_alpha(alpha)
		s.set_colorkey(colorkey)
		return s
	elif type(s) == tuple:
		for i, e in enumerate(s):
			s = s[:i] + (unserializeSurf(e),) + s[i+1:]
	elif type(s) == list:
		for i, e in enumerate(s):
			s[i] = unserializeSurf(e)
	return s

class TimeFrame:
	def __init__(self, timeLimitInSeconds='infinity'):
		self._timeLimit  = timeLimitInSeconds
		self._used = False
		self._timeAtFirstUsed = 0 
	
	def getTimeRemaining(self):
		"""
		returns remaining living time /effect time of an item 
		"""
		if (self._timeLimit == 'infinity'):
			raise Exception('No time limit')
		if not self._used:
			return self._timeLimit 
		else:
			timeLimitFormatted = self._timeAtFirstUsed + timedelta(seconds=self._timeLimit) 
			timeRemaining = timeLimitFormatted - datetime.now() 
			return 0 if timeRemaining.total_seconds() <= 0 else timeRemaining.total_seconds() 

	def getTimeLimit(self): 
		"""
		gets the time limit of an Item in case of not 'infintiy'
		"""
		if (self._timeLimit != 'infinity'):
			return self._timeLimit 
		else: raise Exception('No time limit')

	def startCountdown(self):
		self._used = True
		self._timeAtFirstUsed = datetime.now() 

class Attributes(Enum):
    """ Enumeration of all possible attributes for a character """
    HP = auto()
    Armor = auto()
    Strength = auto()
    Dexterity = auto()
    Con = auto()
    Intelligence = auto()
    Wisdom = auto()
    Cha = auto()


class ItemAttributes(Enum): 
	Consumable = auto()
	NbOfUses =  auto()
	Value = auto()
	Weight = auto()

class State(Enum):
    """ Enumeration of all possible states of an object """
    locked = auto()
    unlocked = auto()

RANKS_MANAGEMENT = {
	0: {'skillPoints': 5, 'rankUpPoints': 30 },
	1: {'skillPoints': 7, 'rankUpPoints': 34 },
	2: {'skillPoints': 9, 'rankUpPoints': 39 },
	3: {'skillPoints': 10, 'rankUpPoints': 40 },
	4: {'skillPoints': 11, 'rankUpPoints': 50 }
}

# FLOOR_MAX=9
TILE_WIDTH = 16
NUMBER_ENEMY=10
PLAYERNAME="jack"


# Items settings
class ItemList(Enum): 
    Sword = auto() 
    Armor = auto()
    Ring = auto()
    Necklace = auto()
    Potion = auto()
    Coin = auto()
    PotionIngredient1 = auto()
    fakeItem = auto()

ITEMS_IMAGES = {
    ItemList.Sword: "sword",
    ItemList.Armor: "armor_steel",
    ItemList.Ring: "ring",
    ItemList.Potion: "potion_red",
    ItemList.Coin: "coin",
    ItemList.Necklace: "missing",
}



# Map generation settings #
MAP_ROOMS_DENSITY=0.25
MAP_WIDTH        = 100
MAP_HEIGHT       = 100
MAP_NB_ROOMS     = math.floor(MAP_HEIGHT*MAP_WIDTH*MAP_ROOMS_DENSITY)
CHESTS_CONTENT = [
    (ItemList.Sword,	0.09),
    (ItemList.Armor,	0.09),
    (ItemList.Ring,		0.1),
    (ItemList.Necklace,	0.11),
    (ItemList.Potion,	0.11),
    (ItemList.Coin,		0.5),
]


# ACTION POINT 
DEFAULT_ACTION_POINT = 5

DEFAULT_LINEOFSIGHT = 5
MAX_HP = 100
# players constants
DEFAULT_FIGHTER_STAT = (MAX_HP, 50, 50, 40, 10, 30, 0, 0) #( HP, armor, strength, dex, con, intell, wis, cha )
DEFAULT_ROGUE_STAT   = (MAX_HP, 20, 20, 50, 10, 40, 0, 30)
DEFAULT_MAGE_STAT    = (MAX_HP, 15, 15, 35, 35, 50, 0, 25)


# enemies constants
MEMORY_DURATION = 5  # represent the time that enemy memorise character
# represent the time that enemy memorise character
DEFAULT_ZOMBIE_STAT = (MAX_HP, 8, 13, 6, 16, 3, 6, 5)
DEFAULT_GOBLIN_STAT = (MAX_HP, 15, 8, 14, 10, 10, 8, 8)
DEFAULT_DRAGON_STAT = (MAX_HP, 30, 27, 10, 25, 16, 13, 21)

# Inventory Render constants
INVENTORY_SCALE = 4
INVENTORY_SLOT_SIZE = 12


def cellsrange(radius : int) -> list:
    """ Get a list or cells in a certain range.

    Returns a list of cells in a certain range, assuming the starting position as (0,0)
    For example cellsrange(2) should return :
        [
                          ( 0,-2),
                 (-1,-1), ( 0,-1), ( 1,-1), 
        (-2, 0), (-1, 0), ( 0, 0), ( 1, 0), ( 2, 0),
                 (-1, 1), ( 0, 1), ( 1, 1),
                          ( 0, 2)
        ]
    The list isn't sorted in any particular way.
    """
    return [(x, y) for x in range(-radius, radius+1) for y in range(-radius, radius+1) if abs(x)+abs(y)<=radius]

SKILLS_INFO={
	"Fireball": (cellsrange(5), None), # (range, target type)
	"AcidStream": (cellsrange(5), 'enemy'), # (range, target type)
	"MeteorSwarm": (cellsrange(5), 'enemy'), # (range, target type)
	"DisableDevice": (cellsrange(6), 'object'),
	"Convert_enemy": (cellsrange(2), 'enemy'),
}


"""
The DEFAULT_KEYMAP dict contains all keyboard settings to load by
default. When the game is started, this dict is copied in game.keymap
and can be altered from then with this variable.
"""
DEFAULT_KEYMAP = {
	'selectPlayer1': pygame.K_1,
	'selectPlayer2': pygame.K_2,
	'selectPlayer3': pygame.K_3,
	'startTurn': pygame.K_RETURN,
	# 'toggleMap': pygame.K_m,
	# 'toggleInventory': pygame.K_i,
	'opencharacterwindow': pygame.K_c,
	# 'applyStealth':pygame.K_e,
	# 'applyDisableDevice':pygame.K_r,
	# 'applyPerception':pygame.K_t

}


void = pygame.Surface((TILE_WIDTH, TILE_WIDTH))
void.fill((30,30,30))

void_h = pygame.Surface((TILE_WIDTH, TILE_WIDTH))
void_h.fill((0,0,0))

minivoid = pygame.Surface((3, 3))
minivoid.fill((0,0,0))


"""
The TILESET dict contains all possible characters in the ascii
representation of the map in order to match each character with its
tile.
"""
TILESET = {
	' ': void,
	'.': [
		pygame.image.load("dungeonX/assets/tiles/floor_1.png"),
		pygame.image.load("dungeonX/assets/tiles/floor_2.png"),
		pygame.image.load("dungeonX/assets/tiles/floor_3.png"),
		pygame.image.load("dungeonX/assets/tiles/floor_5.png"),
	],

	'╳': pygame.image.load("dungeonX/assets/tiles/wall_c.png"),

	'─': pygame.image.load("dungeonX/assets/tiles/wall_lr_d.png"),
	'━': pygame.image.load("dungeonX/assets/tiles/wall_lr_u.png"),
	'═': pygame.image.load("dungeonX/assets/tiles/wall_llrr.png"),

	'│': pygame.image.load("dungeonX/assets/tiles/wall_ud_l.png"),
	'┃': pygame.image.load("dungeonX/assets/tiles/wall_ud_r.png"),
	'║': pygame.image.load("dungeonX/assets/tiles/wall_uudd.png"),
	
	'┌': pygame.image.load("dungeonX/assets/tiles/wall_dr_r.png"),
	'┏': pygame.image.load("dungeonX/assets/tiles/wall_dr_l.png"),
	'╔': pygame.image.load("dungeonX/assets/tiles/wall_ddrr.png"),

	'└': pygame.image.load("dungeonX/assets/tiles/wall_ur_r.png"),
	'┗': pygame.image.load("dungeonX/assets/tiles/wall_ur_l.png"),
	'╚': pygame.image.load("dungeonX/assets/tiles/wall_uurr.png"),
	
	'┐': pygame.image.load("dungeonX/assets/tiles/wall_dl_l.png"),
	'┓': pygame.image.load("dungeonX/assets/tiles/wall_dl_r.png"),
	'╗': pygame.image.load("dungeonX/assets/tiles/wall_ddll.png"),
	
	'┘': pygame.image.load("dungeonX/assets/tiles/wall_ul_l.png"),
	'┛': pygame.image.load("dungeonX/assets/tiles/wall_ul_r.png"),
	'╝': pygame.image.load("dungeonX/assets/tiles/wall_uull.png"),
	
	'╥': pygame.image.load("dungeonX/assets/tiles/wall_ddlr.png"),
	'╦': pygame.image.load("dungeonX/assets/tiles/wall_ddllrr.png"),
	'┮': pygame.image.load("dungeonX/assets/tiles/wall_dlrr.png"),
	'┭': pygame.image.load("dungeonX/assets/tiles/wall_dllr.png"),

	'╡': pygame.image.load("dungeonX/assets/tiles/wall_udll.png"),
	'╣': pygame.image.load("dungeonX/assets/tiles/wall_uuddll.png"),
	'┧': pygame.image.load("dungeonX/assets/tiles/wall_uddl.png"),
	'┦': pygame.image.load("dungeonX/assets/tiles/wall_uudl.png"),

	'╞': pygame.image.load("dungeonX/assets/tiles/wall_udrr.png"),
	'╠': pygame.image.load("dungeonX/assets/tiles/wall_uuddrr.png"),
	'┟': pygame.image.load("dungeonX/assets/tiles/wall_uddr.png"),
	'┞': pygame.image.load("dungeonX/assets/tiles/wall_uudr.png"),

	'╨': pygame.image.load("dungeonX/assets/tiles/wall_uulr.png"),
	'╩': pygame.image.load("dungeonX/assets/tiles/wall_uullrr.png"),
	'┶': pygame.image.load("dungeonX/assets/tiles/wall_ulrr.png"),
	'┵': pygame.image.load("dungeonX/assets/tiles/wall_ullr.png"),

	'╷': pygame.image.load("dungeonX/assets/tiles/wall_d.png"),
	'╵': pygame.image.load("dungeonX/assets/tiles/wall_u.png"),
	'╴': pygame.image.load("dungeonX/assets/tiles/wall_l.png"),
	'╶': pygame.image.load("dungeonX/assets/tiles/wall_r.png"),
	
	'┼': pygame.image.load("dungeonX/assets/tiles/wall_udlr_u.png"),
	'╋': pygame.image.load("dungeonX/assets/tiles/wall_udlr_d.png"),
	'╬': pygame.image.load("dungeonX/assets/tiles/wall_uuddllrr.png"),
	'╆': pygame.image.load("dungeonX/assets/tiles/wall_uddlrr.png"),
	'╅': pygame.image.load("dungeonX/assets/tiles/wall_uddllr.png"),
	'╄': pygame.image.load("dungeonX/assets/tiles/wall_uudlrr.png"),
	'╃': pygame.image.load("dungeonX/assets/tiles/wall_uudllr.png"),
}


"""
The TILESET_H dict contains all possible characters in the ascii
representation of the map in order to match each character with its
tile_h. Those tiles are used to create the 2.5D effect.
"""
TILESET_H = {
	' ': void_h,
	'.': void_h,

	'╳': pygame.image.load("dungeonX/assets/tiles/wall_c_h.png"),

	'─': void_h,
	'━': pygame.image.load("dungeonX/assets/tiles/wall_lr_u_h.png"),
	'═': pygame.image.load("dungeonX/assets/tiles/wall_llrr_h.png"),

	'│': pygame.image.load("dungeonX/assets/tiles/wall_ud_l_h.png"),
	'┃': pygame.image.load("dungeonX/assets/tiles/wall_ud_r_h.png"),
	'║': pygame.image.load("dungeonX/assets/tiles/wall_uudd_h.png"),
	
	'┌': void_h,
	'┏': pygame.image.load("dungeonX/assets/tiles/wall_dr_l_h.png"),
	'╔': pygame.image.load("dungeonX/assets/tiles/wall_ddrr_h.png"),

	'└': pygame.image.load("dungeonX/assets/tiles/wall_ur_r_h.png"),
	'┗': pygame.image.load("dungeonX/assets/tiles/wall_ur_l_h.png"),
	'╚': pygame.image.load("dungeonX/assets/tiles/wall_uurr_h.png"),
	
	'┐': void_h,
	'┓': pygame.image.load("dungeonX/assets/tiles/wall_dl_r_h.png"),
	'╗': pygame.image.load("dungeonX/assets/tiles/wall_ddll_h.png"),
	
	'┘': pygame.image.load("dungeonX/assets/tiles/wall_ul_l_h.png"),
	'┛': pygame.image.load("dungeonX/assets/tiles/wall_ul_r_h.png"),
	'╝': pygame.image.load("dungeonX/assets/tiles/wall_uull_h.png"),
	
	'╥': void_h,
	'╦': pygame.image.load("dungeonX/assets/tiles/wall_ddllrr_h.png"),
	'┮': pygame.image.load("dungeonX/assets/tiles/wall_dlrr_h.png"),
	'┭': pygame.image.load("dungeonX/assets/tiles/wall_dllr_h.png"),

	'╡': pygame.image.load("dungeonX/assets/tiles/wall_udll_h.png"),
	'╣': pygame.image.load("dungeonX/assets/tiles/wall_uuddll_h.png"),
	'┧': pygame.image.load("dungeonX/assets/tiles/wall_uddl_h.png"),
	'┦': pygame.image.load("dungeonX/assets/tiles/wall_uudl_h.png"),

	'╞': pygame.image.load("dungeonX/assets/tiles/wall_udrr_h.png"),
	'╠': pygame.image.load("dungeonX/assets/tiles/wall_uuddrr_h.png"),
	'┟': pygame.image.load("dungeonX/assets/tiles/wall_uddr_h.png"),
	'┞': pygame.image.load("dungeonX/assets/tiles/wall_uudr_h.png"),

	'╨': pygame.image.load("dungeonX/assets/tiles/wall_uulr_h.png"),
	'╩': pygame.image.load("dungeonX/assets/tiles/wall_uullrr_h.png"),
	'┶': pygame.image.load("dungeonX/assets/tiles/wall_ulrr_h.png"),
	'┵': pygame.image.load("dungeonX/assets/tiles/wall_ullr_h.png"),

	'╷': pygame.image.load("dungeonX/assets/tiles/wall_d_h.png"),
	'╵': pygame.image.load("dungeonX/assets/tiles/wall_u_h.png"),
	'╴': pygame.image.load("dungeonX/assets/tiles/wall_l_h.png"),
	'╶': pygame.image.load("dungeonX/assets/tiles/wall_r_h.png"),
	
	'┼': pygame.image.load("dungeonX/assets/tiles/wall_udlr_u_h.png"),
	'╋': pygame.image.load("dungeonX/assets/tiles/wall_udlr_d_h.png"),
	'╬': pygame.image.load("dungeonX/assets/tiles/wall_uuddllrr_h.png"),
	'╆': pygame.image.load("dungeonX/assets/tiles/wall_uddlrr_h.png"),
	'╅': pygame.image.load("dungeonX/assets/tiles/wall_uddllr_h.png"),
	'╄': pygame.image.load("dungeonX/assets/tiles/wall_uudlrr_h.png"),
	'╃': pygame.image.load("dungeonX/assets/tiles/wall_uudllr_h.png"),
}


"""
The TILESET_MINI dict contains all possible characters in the ascii
representation of the map in order to match each character with its
tile_mini. Those tiles are used to render the minimap
"""
TILESET_MINI = {
	' ': minivoid,
	'.': pygame.image.load("dungeonX/assets/minimap/floor.png"),

	'╳': pygame.image.load("dungeonX/assets/minimap/wall_c.png"),

	'─': pygame.image.load("dungeonX/assets/minimap/wall_lr_d.png"),
	'━': pygame.image.load("dungeonX/assets/minimap/wall_lr_u.png"),
	'═': pygame.image.load("dungeonX/assets/minimap/wall_llrr.png"),

	'│': pygame.image.load("dungeonX/assets/minimap/wall_ud_l.png"),
	'┃': pygame.image.load("dungeonX/assets/minimap/wall_ud_r.png"),
	'║': pygame.image.load("dungeonX/assets/minimap/wall_uudd.png"),
	
	'┌': pygame.image.load("dungeonX/assets/minimap/wall_dr_r.png"),
	'┏': pygame.image.load("dungeonX/assets/minimap/wall_dr_l.png"),
	'╔': pygame.image.load("dungeonX/assets/minimap/wall_ddrr.png"),

	'└': pygame.image.load("dungeonX/assets/minimap/wall_ur_r.png"),
	'┗': pygame.image.load("dungeonX/assets/minimap/wall_ur_l.png"),
	'╚': pygame.image.load("dungeonX/assets/minimap/wall_uurr.png"),
	
	'┐': pygame.image.load("dungeonX/assets/minimap/wall_dl_l.png"),
	'┓': pygame.image.load("dungeonX/assets/minimap/wall_dl_r.png"),
	'╗': pygame.image.load("dungeonX/assets/minimap/wall_ddll.png"),
	
	'┘': pygame.image.load("dungeonX/assets/minimap/wall_ul_l.png"),
	'┛': pygame.image.load("dungeonX/assets/minimap/wall_ul_r.png"),
	'╝': pygame.image.load("dungeonX/assets/minimap/wall_uull.png"),
	
	'╥': pygame.image.load("dungeonX/assets/minimap/wall_ddlr.png"),
	'╦': pygame.image.load("dungeonX/assets/minimap/wall_ddllrr.png"),
	'┮': pygame.image.load("dungeonX/assets/minimap/wall_dlrr.png"),
	'┭': pygame.image.load("dungeonX/assets/minimap/wall_dllr.png"),

	'╡': pygame.image.load("dungeonX/assets/minimap/wall_udll.png"),
	'╣': pygame.image.load("dungeonX/assets/minimap/wall_uuddll.png"),
	'┧': pygame.image.load("dungeonX/assets/minimap/wall_uddl.png"),
	'┦': pygame.image.load("dungeonX/assets/minimap/wall_uudl.png"),

	'╞': pygame.image.load("dungeonX/assets/minimap/wall_udrr.png"),
	'╠': pygame.image.load("dungeonX/assets/minimap/wall_uuddrr.png"),
	'┟': pygame.image.load("dungeonX/assets/minimap/wall_uddr.png"),
	'┞': pygame.image.load("dungeonX/assets/minimap/wall_uudr.png"),

	'╨': pygame.image.load("dungeonX/assets/minimap/wall_uulr.png"),
	'╩': pygame.image.load("dungeonX/assets/minimap/wall_uullrr.png"),
	'┶': pygame.image.load("dungeonX/assets/minimap/wall_ulrr.png"),
	'┵': pygame.image.load("dungeonX/assets/minimap/wall_ullr.png"),

	'╷': pygame.image.load("dungeonX/assets/minimap/wall_d.png"),
	'╵': pygame.image.load("dungeonX/assets/minimap/wall_u.png"),
	'╴': pygame.image.load("dungeonX/assets/minimap/wall_l.png"),
	'╶': pygame.image.load("dungeonX/assets/minimap/wall_r.png"),
	
	'┼': pygame.image.load("dungeonX/assets/minimap/wall_udlr_u.png"),
	'╋': pygame.image.load("dungeonX/assets/minimap/wall_udlr_d.png"),
	'╬': pygame.image.load("dungeonX/assets/minimap/wall_uuddllrr.png"),
	'╆': pygame.image.load("dungeonX/assets/minimap/wall_uddlrr.png"),
	'╅': pygame.image.load("dungeonX/assets/minimap/wall_uddllr.png"),
	'╄': pygame.image.load("dungeonX/assets/minimap/wall_uudlrr.png"),
	'╃': pygame.image.load("dungeonX/assets/minimap/wall_uudllr.png"),
}



"""
The WALL dict contains all possible combinations of neighbours of an
empty cell in order to determine wich type of wall is required
the neighbours are formatted like this :

	'...'
	'.╳.'   -->   "...' + '.╳.' + '.. "   -->   ".... ... ": '╳'
	'.. '

"""
WALLS = {
	"         ": ' ',
	"        .": '┌',
	"       . ": '─',
	"       ..": '─',
	"      .  ": '┐',
	"      . .": '╥',
	"      .. ": '─',
	"      ...": '─',
	"     .   ": '┃',
	"     .  .": '┃',
	"     . . ": '┛',
	"     . ..": '┛',
	"     ..  ": '┧',
	"     .. .": '┧',
	"     ... ": '┛',
	"     ....": '┛',
	"   .     ": '│',
	"   .    .": '┟',
	"   .   . ": '┗',
	"   .   ..": '┗',
	"   .  .  ": '│',
	"   .  . .": '┟',
	"   .  .. ": '┗',
	"   .  ...": '┗',
	"   . .   ": '║',
	"   . .  .": '║',
	"   . . . ": '╵',
	"   . . ..": '╵',
	"   . ..  ": '║',
	"   . .. .": '║',
	"   . ... ": '╵',
	"   . ....": '╵',
	"  .      ": '└',
	"  .     .": '╞',
	"  .    . ": '┶',
	"  .    ..": '┶',
	"  .   .  ": '╋',
	"  .   . .": '╆',
	"  .   .. ": '┶',
	"  .   ...": '┶',
	"  .  .   ": '┃',
	"  .  .  .": '┃',
	"  .  . . ": '┛',
	"  .  . ..": '┛',
	"  .  ..  ": '┧',
	"  .  .. .": '┧',
	"  .  ... ": '┛',
	"  .  ....": '┛',
	"  ..     ": '┞',
	"  ..    .": '╠',
	"  ..   . ": '╚',
	"  ..   ..": '╚',
	"  ..  .  ": '┞',
	"  ..  . .": '╠',
	"  ..  .. ": '╚',
	"  ..  ...": '╚',
	"  .. .   ": '║',
	"  .. .  .": '║',
	"  .. . . ": '╵',
	"  .. . ..": '╵',
	"  .. ..  ": '║',
	"  .. .. .": '║',
	"  .. ... ": '╵',
	"  .. ....": '╵',
	" .       ": '━',
	" .      .": '┮',
	" .     . ": '═',
	" .     ..": '═',
	" .    .  ": '┭',
	" .    . .": '╦',
	" .    .. ": '═',
	" .    ...": '═',
	" .   .   ": '┓',
	" .   .  .": '┓',
	" .   . . ": '╴',
	" .   . ..": '╴',
	" .   ..  ": '╗',
	" .   .. .": '╗',
	" .   ... ": '╴',
	" .   ....": '╴',
	" . .     ": '┏',
	" . .    .": '╔',
	" . .   . ": '╶',
	" . .   ..": '╶',
	" . .  .  ": '┏',
	" . .  . .": '╔',
	" . .  .. ": '╶',
	" . .  ...": '╶',
	" . . .   ": '╷',
	" . . .  .": '╷',
	" . . . . ": '╳',
	" . . . ..": '╳',
	" . . ..  ": '╷',
	" . . .. .": '╷',
	" . . ... ": '╳',
	" . . ....": '╳',
	" ..      ": '━',
	" ..     .": '┮',
	" ..    . ": '═',
	" ..    ..": '═',
	" ..   .  ": '┭',
	" ..   . .": '╦',
	" ..   .. ": '═',
	" ..   ...": '═',
	" ..  .   ": '┓',
	" ..  .  .": '┓',
	" ..  . . ": '╴',
	" ..  . ..": '╴',
	" ..  ..  ": '╗',
	" ..  .. .": '╗',
	" ..  ... ": '╴',
	" ..  ....": '╴',
	" ...     ": '┏',
	" ...    .": '╔',
	" ...   . ": '╶',
	" ...   ..": '╶',
	" ...  .  ": '┏',
	" ...  . .": '╔',
	" ...  .. ": '╶',
	" ...  ...": '╶',
	" ... .   ": '╷',
	" ... .  .": '╷',
	" ... . . ": '╳',
	" ... . ..": '╳',
	" ... ..  ": '╷',
	" ... .. .": '╷',
	" ... ... ": '╳',
	" ... ....": '╳',
	".        ": '┘',
	".       .": '┼',
	".      . ": '┵',
	".      ..": '┵',
	".     .  ": '╡',
	".     . .": '╅',
	".     .. ": '┵',
	".     ...": '┵',
	".    .   ": '┦',
	".    .  .": '┦',
	".    . . ": '╝',
	".    . ..": '╝',
	".    ..  ": '╣',
	".    .. .": '╣',
	".    ... ": '╝',
	".    ....": '╝',
	".  .     ": '│',
	".  .    .": '┟',
	".  .   . ": '┗',
	".  .   ..": '┗',
	".  .  .  ": '│',
	".  .  . .": '┟',
	".  .  .. ": '┗',
	".  .  ...": '┗',
	".  . .   ": '║',
	".  . .  .": '║',
	".  . . . ": '╵',
	".  . . ..": '╵',
	".  . ..  ": '║',
	".  . .. .": '║',
	".  . ... ": '╵',
	".  . ....": '╵',
	". .      ": '╨',
	". .     .": '╄',
	". .    . ": '╩',
	". .    ..": '╩',
	". .   .  ": '╃',
	". .   . .": '╬',
	". .   .. ": '╩',
	". .   ...": '╩',
	". .  .   ": '┦',
	". .  .  .": '┦',
	". .  . . ": '╝',
	". .  . ..": '╝',
	". .  ..  ": '╣',
	". .  .. .": '╣',
	". .  ... ": '╝',
	". .  ....": '╝',
	". ..     ": '┞',
	". ..    .": '╠',
	". ..   . ": '╚',
	". ..   ..": '╚',
	". ..  .  ": '┞',
	". ..  . .": '╠',
	". ..  .. ": '╚',
	". ..  ...": '╚',
	". .. .   ": '║',
	". .. .  .": '║',
	". .. . . ": '╵',
	". .. . ..": '╵',
	". .. ..  ": '║',
	". .. .. .": '║',
	". .. ... ": '╵',
	". .. ....": '╵',
	"..       ": '━',
	"..      .": '┮',
	"..     . ": '═',
	"..     ..": '═',
	"..    .  ": '┭',
	"..    . .": '╦',
	"..    .. ": '═',
	"..    ...": '═',
	"..   .   ": '┓',
	"..   .  .": '┓',
	"..   . . ": '╴',
	"..   . ..": '╴',
	"..   ..  ": '╗',
	"..   .. .": '╗',
	"..   ... ": '╴',
	"..   ....": '╴',
	".. .     ": '┏',
	".. .    .": '╔',
	".. .   . ": '╶',
	".. .   ..": '╶',
	".. .  .  ": '┏',
	".. .  . .": '╔',
	".. .  .. ": '╶',
	".. .  ...": '╶',
	".. . .   ": '╷',
	".. . .  .": '╷',
	".. . . . ": '╳',
	".. . . ..": '╳',
	".. . ..  ": '╷',
	".. . .. .": '╷',
	".. . ... ": '╳',
	".. . ....": '╳',
	"...      ": '━',
	"...     .": '┮',
	"...    . ": '═',
	"...    ..": '═',
	"...   .  ": '┭',
	"...   . .": '╦',
	"...   .. ": '═',
	"...   ...": '═',
	"...  .   ": '┓',
	"...  .  .": '┓',
	"...  . . ": '╴',
	"...  . ..": '╴',
	"...  ..  ": '╗',
	"...  .. .": '╗',
	"...  ... ": '╴',
	"...  ....": '╴',
	"....     ": '┏',
	"....    .": '╔',
	"....   . ": '╶',
	"....   ..": '╶',
	"....  .  ": '┏',
	"....  . .": '╔',
	"....  .. ": '╶',
	"....  ...": '╶',
	".... .   ": '╷',
	".... .  .": '╷',
	".... . . ": '╳',
	".... . ..": '╳',
	".... ..  ": '╷',
	".... .. .": '╷',
	".... ... ": '╳',
	".... ....": '╳',
}
