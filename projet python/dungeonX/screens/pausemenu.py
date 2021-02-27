import pygame
from . import Window
from ..graphics import Button, TextInput

class PauseMenu(Window):
	def __init__(self, game, parentScreen):
		super().__init__(game, flags=pygame.SRCALPHA)
		self.backToGameButton = Button(game,(self.get_width()//2-100,self.get_height()/4), "Back To Game",size=(200,100), textScale=0.3, action=parentScreen.resumeState)
		self.saveButton = Button(game,(self.get_width()//2-100,2*self.get_height()/4), "Save",size=(200,100), textScale=0.3, action=self.saveDialog)
		self.mainMenuButton = Button(game,(self.get_width()//2-100,3*self.get_height()/4), "Main Menu",size=(200,100), textScale=0.3, imgPath="dungeonX/assets/ui/button_red.png", action=self.exitConfirm)
		self.parentScreen=parentScreen

		self.choiceBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/choice.png").convert(), (372, 236))
		self.choiceBackground.set_colorkey((0,0,0))
		self.infoBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/info.png").convert(), (600, 164))
		self.infoBackground.set_colorkey((0,0,0))
		self.confirmBackground = pygame.transform.scale(pygame.image.load("dungeonX/assets/ui/map_editor/confirm.png").convert(), (372, 164))
		self.confirmBackground.set_colorkey((0,0,0))
		self.dialogState = None
		self.yesButton = Button(game, (self.get_width()//2-140-5, (self.get_height()+self.infoBackground.get_height())//2-64-15), "Yes", size=(140, 64), textScale=0.3, action=self.saveDialog)
		self.noButton = Button(game, (self.get_width()//2+5, (self.get_height()+self.infoBackground.get_height())//2-64-15), "No", size=(140, 64), imgPath="dungeonX/assets/ui/button_red.png", textScale=0.3, action=self.exit)
		self.dismissButton = Button(game, (self.get_width()//2-70, (self.get_height()+self.confirmBackground.get_height())//2-64-15), "OK", size=(140, 64), textScale=0.3, action=self.cancelDialog)
		self.saveDialogButton = Button(game, (self.get_width()//2-140-5, (self.get_height()+self.choiceBackground.get_height())//2-64-15), "Save", size=(140, 64), textScale=0.3, action=self.saveMap)
		self.cancelButton = Button(game, (self.get_width()//2+5, (self.get_height()+self.choiceBackground.get_height())//2-64-15), "Cancel", size=(140, 64), imgPath="dungeonX/assets/ui/button_red.png", textScale=0.3, action=self.cancelDialog)
		self.filenameInput = TextInput(game, (self.get_width()//2-140, (self.get_height()+self.choiceBackground.get_height())//2-64-94))
		self.mapSaved = False

	def exitConfirm(self):
		if not self.mapSaved:
			self.dialogState = "exit_confirm"
		else:
			self.game.setScreen('main_menu')

	def exit(self):
		self.dialogState = None
		self.game.setScreen('main_menu')

	def saveDialog(self):
		if self.parentScreen.saveName==None:
			self.dialogState = "save"
			self.filenameInput.text = ""
			self.filenameInput.focus()
		else:
			self.parentScreen.dungeon.save('dungeonX/saves/'+self.parentScreen.saveName+'.dngX')
			self.dialogState = "save_confirmed"
			self.mapSaved = True


	def saveMap(self):
		if self.filenameInput.text!='':
			self.parentScreen.saveName = self.filenameInput.text.replace(' ', '_')
			self.parentScreen.dungeon.save('dungeonX/saves/'+self.parentScreen.saveName+'.dngX')
			self.dialogState = "save_confirmed"
			self.filenameInput.unfocus()
			self.mapSaved = True

	def cancelDialog(self):
		self.dialogState = None


	def update(self, events):
		self.fill((0,0,0, 100))
		self.blit(self.mainMenuButton.image, self.mainMenuButton.rect)
		self.blit(self.backToGameButton.image, self.backToGameButton.rect)
		self.blit(self.saveButton.image, self.saveButton.rect)

		if self.dialogState:
			self.fill((128,128,128), special_flags=pygame.BLEND_SUB)
			if self.dialogState=="exit_confirm":
				self.blit(self.confirmBackground, (pygame.Vector2(self.game.DISPLAY_SIZE)-self.confirmBackground.get_size())//2)
				self.game.textDisplayer.print("Do you want to save the game ?", (pygame.Vector2(self.game.DISPLAY_SIZE)-self.confirmBackground.get_size())//2, rectSize=(372,80), center=True, scale=0.3, screen=self)
				self.yesButton.update(events)
				self.blit(self.yesButton.image, self.yesButton.rect)
				self.noButton.update(events)
				self.blit(self.noButton.image, self.noButton.rect)
			elif self.dialogState=="save":
				self.blit(self.choiceBackground, (pygame.Vector2(self.game.DISPLAY_SIZE)-self.choiceBackground.get_size())//2)
				self.game.textDisplayer.print("Save name", (pygame.Vector2(self.game.DISPLAY_SIZE)-self.choiceBackground.get_size())//2, rectSize=(372,72), center=True, scale=0.3, screen=self)
				self.filenameInput.update(events)
				self.blit(self.filenameInput, self.filenameInput.rect)
				self.saveDialogButton.update(events)
				self.blit(self.saveDialogButton.image, self.saveDialogButton.rect)
				self.cancelButton.update(events)
				self.blit(self.cancelButton.image, self.cancelButton.rect)
			elif self.dialogState=="save_confirmed":
				self.blit(self.infoBackground, (pygame.Vector2(self.game.DISPLAY_SIZE)-self.infoBackground.get_size())//2)
				self.game.textDisplayer.print("File saved to dungeonX/saves/"+self.parentScreen.saveName+'.dngX', (pygame.Vector2(self.game.DISPLAY_SIZE)-self.infoBackground.get_size())//2, rectSize=(600,80), center=True, scale=0.3, screen=self)
				self.dismissButton.update(events)
				self.blit(self.dismissButton.image, self.dismissButton.rect)
		else:
			self.mainMenuButton.update(events)
			self.backToGameButton.update(events)
			self.saveButton.update(events)

