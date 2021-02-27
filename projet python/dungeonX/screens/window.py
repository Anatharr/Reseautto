import pygame

class Window(pygame.Surface):
	""" This class is a blueprint for every screen

	It inherit pygame.Surface in order to simplify the render function.
	By doing so, we can directly blit (understand this as "paste") the
	window on the main display. Thus we only need to update the window
	at each loop turn when we want to render it, and in the update
	function we can directly call self.blit(img, position) to render a
	surface.

	Attributes
	----------
	game : Game
		the global instance of the game, available here if needed.

	Methods
	-------
	update(events)
		Updates the surface. Called at every loop turn.

	"""
	def __init__(self, game, size=None, flags=0):
		super().__init__(size or game.DISPLAY_SIZE, flags=flags)
		self.game = game

	def update(self, events):
		""" Updates the surface. Called at every loop turn. """
		pass
