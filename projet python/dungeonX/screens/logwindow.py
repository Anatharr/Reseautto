import pygame, math
from . import Window
from ..graphics import Button

class LogWindow(Window):
	""" This is the LogWindow where the logs are displayed in a 
	separate rectangle
	
	It should only be called once in game and works with the game
	method addToLog
	
	
	Attributes
	----------
	mylist: list 
		list of the logs messages that are added by the various 
		classes and objects
	messagecount: integer
		number of messages that there are in 
		my list and that should be displayed.
	maxmessage: integer 
		max number of messages that should be
		displayed at any time 
	logs_size: tuple 
		stores the values of the width and the height
		of the window
	display: 
		instance of the Textdisplayer for game
	background: pygame.surface
		image background that will be used to display the
		logs on
	frame:	pygame.surface
		image of the frame of the window
	scroll_y: int 
		this is the value that allows us to create a 
		scrolling effect in the window.
	__viewport_logs: pygame.surface
		this is a surface that will
		be used by the object display to print text on, its y
		value is purposefully high in order to scroll through
		this surface
	newmessage:	boolean 
		that states wether or not there is a new
	 	or several new messages to display, this is used to update
	 	the log display
	 logsrect: pygame.rect 
	 	that represents the rectangle that we 
	 	blit the logs window on to
	 self.offsety: int
	 	this is the value that we get from the object display,
	 	it tells us how much size it took to display a messsage
	 	vertically so that we can display the next message at 
	 	the right y value
	

	Methods
	-------
	update(events)
		Main update method.
	scrollup()
		increments the scroll_y value
	scrolldown()
		decrements the scroll_y value
	

"""
	
	def __init__(self, game):
		super().__init__(game, (game.DISPLAY_SIZE[0]*0.25, game.DISPLAY_SIZE[1]*0.25), flags=pygame.SRCALPHA)
		self.mylist=[]
		self.i=0
		self.messagecount=0
		self.maxmessage=50
		self.logs_size = [self.get_width(),self.get_height()]
		self.display=self.game.textDisplayer
		
		self.background = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/logwindow/background.png").convert_alpha(), self.logs_size)
		self.background.set_alpha(150)
		self.frame = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/logwindow/frame.png").convert_alpha(), self.logs_size)
		self.scroll_y=0
		self.__viewport_logs = pygame.Surface([self.get_width(),5000])
		self.rectsize_buttons=(25,25)
			
		self.uparrowButton = Button(game,(self.get_width()-43,game.DISPLAY_SIZE[1]*0.75+18), "",size=self.rectsize_buttons,imgPath="dungeonX/assets/ui/logwindow/uparrow_button.png", textScale=0.3, hoverMode='overlay', action=lambda:self.scrolldown())
		self.downarrowButton = Button(game,(self.get_width()-43,game.DISPLAY_SIZE[1]*0.75+43), "",size=self.rectsize_buttons,imgPath="dungeonX/assets/ui/logwindow/downarrow_button.png",  textScale=0.3, hoverMode='overlay', action=lambda:self.scrollup())
		self.newmessage=False
		self.logsrect = pygame.Rect([0,game.DISPLAY_SIZE[1]-self.get_height()], self.logs_size)
		
		
		self.maxscroll_y =80000
	def scrollup(self):

		self.scroll_y = max(self.scroll_y - 15, self.maxscroll_y)

	def scrolldown(self):

	
		self.scroll_y = min(self.scroll_y+15,35)

	def update(self,events):
		if self.logsrect.collidepoint(pygame.mouse.get_pos()): 	

			for event in events:
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 4:
				
						self.scrolldown()
						
					if event.button == 5:
				
						self.scrollup()
					
		self.__viewport_logs.fill((0,0,0))
		self.offsety=0
		for i in range (self.messagecount):
			self.display.print((("Turn  "+str(self.game.screens["game"].turnNumber))+' :  '+self.game.mylist[-self.messagecount+i]),(5,(self.offsety)),screen=self.__viewport_logs,scale=0.15,rectSize=(self.get_width()-20,5000),center_y=False)
			self.offsety+=self.display.get_offsety()
			
		if self.newmessage:

			self.scroll_y=-self.offsety+180
			self.maxscroll_y=self.scroll_y
			self.newmessage=False


		if self.offsety!=0:
			pass
			
		self.fill((0,0,0,0))

		self.__viewport_logs.set_colorkey((0,0,0))
		self.blit(self.background,(0,0))
		self.blit(self.__viewport_logs,(0,self.scroll_y))
		self.blit(self.frame, (0,0))
		self.blit(self.downarrowButton.image,(self.get_width()-43,43))
		self.blit(self.uparrowButton.image,(self.get_width()-43,18))
		self.uparrowButton.update(events)
		self.downarrowButton.update(events)

	
	
		

	