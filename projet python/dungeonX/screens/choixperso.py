import pygame
from . import Window

class ChoixPerso(Window):
	def __init__(self):
		super().__init__(game)
		self.backgroundColor=(0,0,0)
	def update():
		self.fill(self.backgroundColor)
		c=1
		while c:
			for event in pygame.event.type.get() :
				if pygame.event.type==Quit() :
					exit()
			Listimages=[]
			perso=pygame.image.load("dungeonX/assets/characters/big_demon_idle_f0.png").convert()
			self.blit(perso,(50,50))
			Listimages.append(perso)
			images=os.listdir("dungeonX/assets/characters")
			front=pygame.font.Font(None,25)
			for i in range(len(images)) :
				self.fill(self.backgroundColor)
				if pygame.event.key==pygame.K_LEFT :
					perso=pygame.image.load("dungeonX/assets/characters/"+images[i]).convert()
					Listimages.append(perso)
					self.blit(perso,(50,50))
					text=font.render("                                  "+images[i][:-4],1,(255,255,255))
					self.blit(text,(0,0))
				if pygame.event.key==pygame.K_RIGHT:
					perso=pygame.image.load("dungeonX/assets/characters/"+images[i-1]).convert()
					Listimages.append(perso)
					self.blit(perso,(50,50))
					text=font.render("                                  "+images[i-1][:-4],1,(255,255,255))
					self.blit(text,(0,0))
		pygame.display.flip()
		pygame.clock.tick(60)
		L=set(Listimages)
		Listimages=list(L)