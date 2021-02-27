import math, pygame
from dungeonX import Game
from dungeonX.graphics import TextDisplayer, ParticleSystem

game = Game()

def testGameCreation():
	assert math.isclose(game.RATIO, game.DISPLAY_SIZE[0]/game.DISPLAY_SIZE[1])
	assert game.dt == 0
	assert not game.running

	assert type(game.display) is pygame.Surface
	assert game.display.get_size() == game.DISPLAY_SIZE
	
	assert type(game.textDisplayer) is TextDisplayer
	assert type(game.particleSystem) is ParticleSystem

	assert game.currentScreen in game.screens
	assert game.keymap is not None

def testSetScreen():
	oldScreen = game.currentScreen
	game.setScreen("invalid screen")
	assert game.currentScreen == oldScreen

	game.setScreen("main_menu")
	assert game.currentScreen == "main_menu"

