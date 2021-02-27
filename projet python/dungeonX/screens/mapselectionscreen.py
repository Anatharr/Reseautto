import pygame, os
from . import Window
from ..graphics import Button, TextInput, TextDisplayer
from ..map import Dungeon
from ..constants import TILE_WIDTH

SCALE = 3
MOUSE_SENSIBILITY = 4

class MapSelectorScreen(Window):
    def __init__(self, game):
        super().__init__(game)
        
        self.background = pygame.image.load("dungeonX/assets/menu/background.png").convert()
        self.background = pygame.transform.scale(self.background, self.get_size())
        self.game.textDisplayer.print("Load or create a new game",(0,20), rectSize=(self.get_width(),200), center=True, scale=0.4, screen=self.background)

        self.backbutton = Button(game,(20,+20), "",size=(50,50),imgPath="dungeonX/assets/menu/back_arrow.png", textScale=0.3, action=lambda: self.game.setScreen('main_menu'))

        self.window = pygame.image.load("dungeonX/assets/ui/mapselector/window.png").convert()
        self.window = pygame.transform.scale(self.window, (self.window.get_width()*SCALE, self.window.get_height()*SCALE))
        self.window.set_colorkey((0,0,0))
        self.rect = self.window.get_rect().move((self.get_width()-self.window.get_width())//2, (self.get_height()-self.window.get_height())//2)

        self.viewport = pygame.Surface((self.window.get_width()-18*SCALE, self.window.get_height()-12*SCALE))
        self.viewport.set_colorkey((0,0,0))

        self.cursor = pygame.image.load("dungeonX/assets/ui/mapselector/cursor.png").convert()
        self.cursor = pygame.transform.scale(self.cursor, (self.cursor.get_width()*SCALE, self.cursor.get_height()*SCALE))

        self.loadButton = Button(game, (self.rect.right-200, self.rect.bottom+5), "Load Game", size=(200,100), textScale=0.3, action=self.loadGame)
        self.loadButtonDisabled = Button(game, (self.rect.right-200, self.rect.bottom+5), "Load Game", size=(200,100), textScale=0.3, imgPath="dungeonX/assets/ui/button_gray.png")
        self.createButton = Button(game, (self.rect.left, self.rect.bottom+5), "Create a new game", size=(200,100), textScale=0.3, action=self.createGame)

        self.hoverImg = pygame.Surface((self.viewport.get_width(), 50), flags=pygame.SRCALPHA)
        self.hoverImg.fill((255,255,255, 128))
        self.offsetY = 0
        self.selectedIndex = None
        self.files = []

    def createGame(self):
        self.game.screens["game"].dungeon = Dungeon(self.game.screens["game"])

        self.game.screens["game"].enemies = self.game.screens["game"].dungeon.currentFloor.enemies
        self.game.screens["game"].objects = self.game.screens["game"].dungeon.currentFloor.objects
        self.game.screens["game"].players = self.game.screens["game"].dungeon.players
        self.game.screens["game"].inventorywindow.bag = self.game.screens["game"].dungeon.bag

        self.game.setScreen("character_choice")

    def loadGame(self):
        self.game.screens["game"].dungeon = Dungeon.load('dungeonX/saves/'+self.files[self.selectedIndex]+'.dngX')

        self.game.screens["game"].dungeon.game = self.game.screens["game"]
        for floor in self.game.screens["game"].dungeon.floors:
            floor.game = self.game.screens["game"]
        lst = self.game.screens["game"].dungeon.currentFloor.enemies + self.game.screens["game"].dungeon.currentFloor.objects
        lst += self.game.screens["game"].dungeon.players if self.game.screens["game"].dungeon.players!=None else []
        for ent in lst:
            ent.game = self.game.screens["game"]

        self.game.screens["game"].enemies = self.game.screens["game"].dungeon.currentFloor.enemies
        self.game.screens["game"].objects = self.game.screens["game"].dungeon.currentFloor.objects
        self.game.screens["game"].players = self.game.screens["game"].dungeon.players
        self.game.screens["game"].inventorywindow.bag = self.game.screens["game"].dungeon.bag

        # self.game.screens['game'].state = self.game.screens['game'].savedState
        # self.game.screens['game'].APRefill = self.game.screens['game'].savedAPRefill
        # self.game.screens['game'].turnNumber = self.game.screens['game'].savedTurnNumber


        if self.game.screens["game"].players == None:
            self.game.setScreen("character_choice")
        else:
            self.game.screens["game"].selectPlayer(0)
            self.game.screens["game"].setState('walk')
            self.game.setScreen("game")


    def update(self,events):
        self.files = list(map(lambda x:x[:-5], filter(lambda x:x[-5:]=='.dngX', os.listdir("dungeonX/saves/"))))
        mousePos = pygame.mouse.get_pos()

        if len(self.files)<6: self.offsetY=0 

        self.viewport.fill((0,0,0))

        absoluteSurf = pygame.Surface((self.viewport.get_width(), 50*len(self.files)))
        rects=[]
        for i, file in enumerate(self.files):
            rect = pygame.Rect(self.hoverImg.get_rect().move(0, 50*i)) # self.rect.left+6*SCALE, self.rect.top+20*SCALE+50*i
            rects.append(rect)
            self.game.textDisplayer.print(file, rect.topleft, rectSize=rect.size, scale=0.3, center_y=True, screen=absoluteSurf)
            if rect.move(self.rect.left+6*SCALE, self.rect.top+6*SCALE+self.offsetY).collidepoint(mousePos):
                pygame.draw.rect(absoluteSurf, (255,255,255), rect, width=1)

        for e in events:
            if e.type==pygame.MOUSEWHEEL:
                if self.viewport.get_height()-absoluteSurf.get_height()<self.offsetY+e.y*MOUSE_SENSIBILITY<0:
                    self.offsetY += e.y*MOUSE_SENSIBILITY
            if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                for i, rect in enumerate(rects):
                    if rect.move(self.rect.left+6*SCALE, self.rect.top+6*SCALE+self.offsetY).collidepoint(e.pos):
                        self.selectedIndex = i

        if self.selectedIndex!=None:
            absoluteSurf.blit(self.hoverImg, (0, self.selectedIndex*50))

        self.viewport.blit(absoluteSurf, (0,self.offsetY))


        self.blit(self.background, (0,0))
        self.blit(self.window, self.rect)
        self.blit(self.viewport, (self.rect.left+6*SCALE, self.rect.top+6*SCALE))

        if self.selectedIndex==None:
            self.blit(self.loadButtonDisabled.image, self.loadButtonDisabled.rect)
        else:
            self.loadButton.update(events)
            self.blit(self.loadButton.image, self.loadButton.rect)

        self.createButton.update(events)
        self.blit(self.createButton.image, self.createButton.rect)

        self.backbutton.update(events)
        self.blit(self.backbutton.image, self.backbutton.rect)