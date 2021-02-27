import pygame, math
from . import Window
from ..characters.skills import SkillEnum
from ..graphics import Button
from enum import Enum
ICON_SIZE=(60,60)

class SkillWindow(Window):
	""" This is the SkillWindow, where the player chooses how to
	spend his skillranks.

	It should only be called once in gamescreen at it handles having
	several players to display at the same time
	
	
	Attributes
	----------
	players : obj player
		Contains the current player for wich the screen is displayed
	display : contains the instance of the TextDisplayer of game
	icon_size: 
		contains the value of the constant ICON_SIZE,wich
		defines the value of the size that will be used to diplay the
		icons of the skills
	skillist:	dictionnary 
		that contains the skill as a key and the image
		assotiated to said skill
	skillrect:	dictionnary
		that contains the skill as a key and the rect
		assotiated to said skill, the rect is later used to blit the image
		of the previous dictionnary on it
	self.skillplusbutton: dictionnary 
		that contains the skill as a key
		and a button assotiatied to said skill, the button is used to 
		add a skillrank into the specified skill by calling the method
		attributepoints
	self.skillminusbutton:	dictionnary
		that contains the skill as a key
		and a button assotiatied to said skill, the button is used to 
		substract a skillrank into the specified skill by calling the method
		detributepoints
	self.skillpointplaceholder:	dictionnary
		that contains the skill as a key
		and an image assotiatied to said skill, the image will be used as 
		a background/placeholder to display the current skill points on 
		it
	self.skillpointplaceholder_pos:	dictionnary 
		that contains the skill as a key
		and an tuple associated to said skill, the tuple will be used to blit
		the placeholder according to te skill image,plusbutton and minus button
		positions
	self.skillrankplaceholder:	dictionnary
		that contains the skill as a key
		and an image assotiatied to said skill, the image will be used as 
		a background/placeholder to display the current skill rank on 
		it
	self.skillrankplaceholder_pos:	dictionnary 
		that contains the skill as a key
		and an tuple associated to said skill, the tuple will be used to blit
		the placeholder according to te skill image
	self.todisplay:	boolean 
		wich states wether or not this window should be displayed
		it is modified by the method callskillwindow(self,player)
	self.listofplayertodisplay: list
		this is a list that contains the list of players
		for wich this screen should be displayed, it serves as a queue (fifo)
		in case two or three players levelup at the same time
	self.hoveredImg :	pygame.image object
		wich contains a grey filter that 
		will be blit onto another image later
	self.hoveredAction:
		contains the name of the skill that is being hovered by
		the mouse, this is used to blit the hoveredImg onto the right skill
		image
	self.textbackground : 
		this is the image that is used as a background for the text
		that is displayed when whe hover a skill

	Methods
	-------
	update(events)
		Main update method.
	attributepoints(self,skill)
		attributes a rank into the specified skill, used when plusbutton is
		pressed
	detributepoints(self,skill):
		does the opposite of attributepoints,this method takes into acount 
		the number of skillranks the player had when initially calling this
		method so tjat we don't decrement this initial value
	displaytexthovered(self,skill):
		Displays an explanatory text for each skill when the mouse hovers a 
		skill
	Launch(self):
		Verifies wether or not this window should be displayed
	callskillwindow(self,player):
		this is the method that is used outside of this class in order to 
		add a player to the	list listplayertodisplay
	end(self):
		used when the ok button is pressed, it means that the players confirms
		its choices and that this window should close, it discards the current
		self.player so that if there is a player in the queue lists it gets 
		moved into self.player
	"""

	def __init__(self, game,parentscreen):
		super().__init__(game, (game.DISPLAY_SIZE[0]*0.6, game.DISPLAY_SIZE[1]*0.6), flags=pygame.SRCALPHA)
		self.rect_size = [self.get_width(),self.get_height()]
		self.parentscreen=parentscreen
		
		self.background = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/confirm.png").convert(), self.rect_size)
		self.background.set_colorkey((0,0,0))
		self.rect=pygame.Rect(((game.DISPLAY_SIZE[0]-self.rect_size[0])/2,(game.DISPLAY_SIZE[1]-self.rect_size[1])/2),self.rect_size)
		self.viewport=pygame.Surface(self.rect_size)
		self.player=None
		self.display=self.game.textDisplayer
		
		self.icon_size=ICON_SIZE
		

		self.skillist={'Stealth':None,'Perception':None,'DisableDevice':None}
		self.skillrect={'Stealth':pygame.Rect((-1*self.rect_size[0]/4+self.rect_size[0]/2-self.icon_size[0]/2,2*self.rect_size[1]/4), ICON_SIZE),
						'Perception':pygame.Rect((0*self.rect_size[0]/4+self.rect_size[0]/2-self.icon_size[0]/2,2*self.rect_size[1]/4), ICON_SIZE),
						'DisableDevice':pygame.Rect((1*self.rect_size[0]/4+self.rect_size[0]/2-self.icon_size[0]/2,2*self.rect_size[1]/4), ICON_SIZE),}
		self.skillplusbutton={'Stealth':None,
							'Perception':None,
								'DisableDevice':None}
		self.skillminusbutton={'Stealth':None,
									'Perception':None,
									'DisableDevice':None}

		self.skillpointplaceholder={'Stealth':None,
									'Perception':None,
									'DisableDevice':None}
		self.skillpointplaceholder_pos={'Stealth':None,
									'Perception':None,
									'DisableDevice':None}
		self.skillrankplaceholder={'Stealth':None,
									'Perception':None,
									'DisableDevice':None}
		self.skillrankplaceholder_pos={'Stealth':None,
									'Perception':None,
									'DisableDevice':None}

		
		self.todisplay=False
		self.listofplayertodisplay=[]
		self.game=game
		self.rectsize_buttons=int(ICON_SIZE[1]/3)
		self.hoveredImg = pygame.transform.scale(pygame.image.load('dungeonX/assets/ui/icons/hovered.png'), ICON_SIZE)
		self.hoveredAction = None
		self.textbackground=pygame.transform.scale(pygame.image.load('dungeonX/assets/minimap/background.png').convert(), (320,160))
		self.textbackground.set_colorkey((255,0,255))
		self.rect.topleft=(((game.DISPLAY_SIZE[0]-self.rect_size[0])/2),((game.DISPLAY_SIZE[1]-self.rect_size[1])/2))

#lists of al skills
		for skill in self.skillist:
			#buttons
			
			self.skillist[skill]= pygame.transform.scale(pygame.image.load('dungeonX/assets/ui/icons/'+str(skill)+'.png').convert(), ICON_SIZE)
			self.skillist[skill].set_colorkey((0,0,0))
			
			self.skillpointplaceholder_pos[skill]=[self.skillrect[skill][0]+ICON_SIZE[0],self.skillrect[skill][1]+self.rectsize_buttons]
			self.skillrankplaceholder_pos[skill]=[self.skillrect[skill][0],self.skillrect[skill][1]+ICON_SIZE[1]]

		self.skillplusbutton["Stealth"] = Button(self.game,(self.rect.topleft[0]+self.skillrect["Stealth"][0]+ICON_SIZE[0],self.rect.topleft[1]+self.skillrect["Stealth"][1]), "",size=(self.rectsize_buttons,self.rectsize_buttons),imgPath="dungeonX/assets/ui/plus_button.png", textScale=0.3, hoverMode='overlay', action=lambda:self.attributepoints("Stealth"))
		self.skillminusbutton["Stealth"] = Button(self.game,(self.rect.topleft[0]+self.skillrect["Stealth"][0]+ICON_SIZE[0],self.rect.topleft[1]+self.skillrect["Stealth"][1]+4*ICON_SIZE[0]/6), "",size=(self.rectsize_buttons,self.rectsize_buttons),imgPath="dungeonX/assets/ui/minus_button.png", textScale=0., hoverMode='overlay', action=lambda:self.detributepoints("Stealth"))
		
		self.skillplusbutton["DisableDevice"] = Button(self.game,(self.rect.topleft[0]+self.skillrect["DisableDevice"][0]+ICON_SIZE[0],self.rect.topleft[1]+self.skillrect["DisableDevice"][1]), "",size=(self.rectsize_buttons,self.rectsize_buttons),imgPath="dungeonX/assets/ui/plus_button.png", textScale=0.3, hoverMode='overlay', action=lambda:self.attributepoints("DisableDevice"))
		self.skillminusbutton["DisableDevice"] = Button(self.game,(self.rect.topleft[0]+self.skillrect["DisableDevice"][0]+ICON_SIZE[0],self.rect.topleft[1]+self.skillrect["DisableDevice"][1]+4*ICON_SIZE[0]/6), "",size=(self.rectsize_buttons,self.rectsize_buttons),imgPath="dungeonX/assets/ui/minus_button.png", textScale=0., hoverMode='overlay', action=lambda:self.detributepoints("DisableDevice"))	
		
		self.skillplusbutton["Perception"] = Button(self.game,(self.rect.topleft[0]+self.skillrect["Perception"][0]+ICON_SIZE[0],self.rect.topleft[1]+self.skillrect["Perception"][1]), "",size=(self.rectsize_buttons,self.rectsize_buttons),imgPath="dungeonX/assets/ui/plus_button.png", textScale=0.3, hoverMode='overlay', action=lambda:self.attributepoints("Perception"))
		self.skillminusbutton["Perception"] = Button(self.game,(self.rect.topleft[0]+self.skillrect["Perception"][0]+ICON_SIZE[0],self.rect.topleft[1]+self.skillrect["Perception"][1]+4*ICON_SIZE[0]/6), "",size=(self.rectsize_buttons,self.rectsize_buttons),imgPath="dungeonX/assets/ui/minus_button.png", textScale=0., hoverMode='overlay', action=lambda:self.detributepoints("Perception"))		
	#+1 point for the
	#specified skill

		self.okbutton=Button(game,(self.get_width()//2-75,3*self.get_height()/4-5), "Ok",size=(150,75), textScale=0.3)
	
	def attributepoints(self,skill):
		if skill=="Stealth":
			self.skill=SkillEnum.Stealth
		elif skill=="DisableDevice":
			self.skill=SkillEnum.DisableDevice
		elif skill=="Perception":
			self.skill=SkillEnum.Perception
			
		if(self.player.getSkillScore()>0):
			self.player.attributeSkillsPoint(self.skill,1)
			
			

	def detributepoints(self,skill):
		if skill=="Stealth":
			self.skill=SkillEnum.Stealth
		elif skill=="DisableDevice":
			self.skill=SkillEnum.DisableDevice
		elif skill=="Perception":
			self.skill=SkillEnum.Perception

		if((self.player.getCurrentPointsFromSkill(self.skill)) > self.skillpointinit[skill]):
			self.player.attributeSkillsPoint(self.skill,-1)
		


		
		
	def displaytexthovered(self,skill):
		
		
		if(self.hoveredAction=="Stealth"):
			self.text="You are skilled at avoiding detection,allowing you to slip past foes or strike from an unseen position.This skill covers hiding and moving silently\n In Dungeon(X), it will allow you to become invisible and deal more damage to the ennemy if you attack unseen"

		elif(self.hoveredAction=="Perception"):
			self.text="Your senses allow you to notice fine details and alert you to danger.\nPerception covers all five senses, including sight, hearing, touch, taste, and smell.\nIn Dungeon(X), it will allow you yo detect invisible ennemies"

		elif(self.hoveredAction=="DisableDevice"):
			self.text="You are skilled at disarming traps and opening locks.\nIn addition, this skill lets you sabotage simple mechanical devices,such as catapults, wagon wheels, and doors.\nIn Dungeon(X), it will allow you to open door and chest locks more easily" 

		textbackground=pygame.transform.scale(self.textbackground, (320,160)).copy()
		self.display.print(self.text,(10,0),screen=textbackground,scale=0.15,rectSize=(320,160),center=True)
		self.blit(textbackground,(self.skillrect[skill][0]-160,self.skillrect[skill][1]-160))

	

	def update(self,events):
		self.Launch()

		if(self.todisplay):

			if(self.player.getSkillScore()==0):
				self.okbutton=Button(self.game,(self.rect.topleft[0]+self.get_width()//2-75,self.rect.topleft[1]+3*self.get_height()/4-5), "Ok",size=(150,75), textScale=0.3,action=lambda:self.end())
				self.okbutton.update(events)
			else:
				self.okbutton=Button(self.game,(self.get_width()//2-75,3*self.get_height()/4-5), "Ok",size=(150,75),imgPath="dungeonX/assets/ui/button_gray.png", textScale=0.3)
			
			self.viewport.fill((0,0,0))
			
			self.blit(self.background,(0,0))	
			
			self.display.print(("You have \n"+str(self.player.getSkillScore())+"\nskill points to distribute\nfor your player\n"+self.player.name),(0,-self.get_height()/2+100),screen=self.viewport,scale=0.3,rectSize=self.rect_size,center=True)
			

			self.viewport.set_colorkey((0,0,0))
			
			self.blit(self.viewport,(0,0))
			
			
			for skill in self.skillist:

				if skill=="Stealth":
					self.skilltocall=SkillEnum.Stealth
				elif skill=="DisableDevice":
					self.skilltocall=SkillEnum.DisableDevice
				elif skill=="Perception":
					self.skilltocall=SkillEnum.Perception




				self.skillpointplaceholder[skill]=pygame.transform.scale(self.textbackground, (2*self.rectsize_buttons,self.rectsize_buttons))
				
				self.skillrankplaceholder[skill]=pygame.transform.scale(self.textbackground, (self.icon_size[0],int(self.icon_size[1]/2)))
				
				self.blit(self.skillist[skill],(self.skillrect[skill]))
				
				self.display.print(str(self.player.getCurrentPointsFromSkill(self.skilltocall)),(0,0),screen=self.skillpointplaceholder[skill],scale=0.2,rectSize=(2*self.rectsize_buttons,self.rectsize_buttons),center=True)
				self.display.print(str(self.player.getCurrentRankFromSkill(self.skilltocall)),(0,0),screen=self.skillrankplaceholder[skill],scale=0.2,rectSize=(self.icon_size[0],int(self.icon_size[1]/2)),center=True)
				
				self.skillpointplaceholder[skill].set_colorkey((255,0,255))
				self.skillrankplaceholder[skill].set_colorkey((255,0,255))
				
				self.blit(self.skillpointplaceholder[skill],self.skillpointplaceholder_pos[skill])
				
				self.blit(self.skillrankplaceholder[skill],self.skillrankplaceholder_pos[skill])
				
				self.blit(self.skillplusbutton[skill].image, self.skillplusbutton[skill].rect.move((-self.rect.left, -self.rect.top)))
				
				self.blit(self.skillminusbutton[skill].image, self.skillminusbutton[skill].rect.move((-self.rect.left, -self.rect.top)))
				
				self.skillplusbutton[skill].update(events)
				
				self.skillminusbutton[skill].update(events)
			self.blit(self.okbutton.image,(self.get_width()//2-75,3*self.get_height()/4-5))

			for e in events:
				self.hoveredAction = None
				if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
					for key in self.skillrect:
						if self.skillrect[key].move(self.rect.topleft).collidepoint(e.pos):
							self.hoveredAction = key
							
							break
			
			for key in self.skillrect:
				
				if self.hoveredAction == key:
					self.blit(self.hoveredImg, self.skillrect[key])
					self.displaytexthovered(key)



#this is the method you should use when you want the window to display, 
#mainly when a character levels up or at the beggining of the game
		
		
	def Launch(self):
		if (len(self.listofplayertodisplay)!=0 and self.todisplay==False):
			self.parentscreen.setState('skillwindow_opened')
			self.player=self.listofplayertodisplay.pop()
			self.todisplay=True
			self.skillpointinit={'Stealth':self.player.getCurrentPointsFromSkill(SkillEnum.Stealth),
						'Perception':self.player.getCurrentPointsFromSkill(SkillEnum.Perception),
						'DisableDevice':self.player.getCurrentPointsFromSkill(SkillEnum.DisableDevice)}
	def end(self):
		self.todisplay=False
		self.parentscreen.resumeState()

	def callskillwindow(self,player):
		self.listofplayertodisplay.append(player)