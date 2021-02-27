import dungeonX.graphics as graphics
from dungeonX import Game

game = Game()

def testGraphicsCreation():
    button = graphics.Button(game, (32,32), "Test Button")
    cellsoverlay = graphics.Cell((255, 0, 0))

