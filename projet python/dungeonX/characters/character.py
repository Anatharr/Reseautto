import math
import numpy as np
from ..constants import MAP_WIDTH, MAP_HEIGHT, Attributes, serializeSurf, unserializeSurf
from enum import Enum

class CharacterEnum(Enum):
    Enemy = 'Enemy'
    NPC = 'NPC'
    Player ='Player'


class Character :
    ID = 0

    def __init__(self, game, pos: tuple, actionPointMax, HP, armor, strength, dex, con, intell, wis, cha):
        self.game = game
        self.actionPoint = actionPointMax
        self.actionPointMax = actionPointMax
        self.pos = pos
        self.listStat = {
            Attributes.HP: HP, 
            Attributes.Armor: armor, 
            Attributes.Strength: strength, 
            Attributes.Dexterity: dex, 
            Attributes.Con: con, 
            Attributes.Intelligence: intell,
            Attributes.Wisdom: wis, 
            Attributes.Cha: cha
        }
        self.ID = Character.ID
        Character.ID += 1
        self.maxHP = HP



    def getPosition(self) :
        return self.pos

    def getHP(self) :
        """
        points de vie
        """
        return self.listStat[Attributes.HP] 
    
    def getActionPoint(self) :
        """
        points d'action (mouvements et attaques)
        """
        return self.actionPoint

    def getActionPointMax(self) :
        """
        returns character's action points maximum (value at the beginning of the turn)
        """
        return self.actionPointMax

    def getAttribute(self,att) :
        """
        Attributes : [HP, armor, strength, dex, con, intell, wis, cha]
        """
        return self.listStat[att] 

    def getID(self) :
        return self.ID 

    def getGame(self) :
        return self.game

    def setActionPointMax(self, newMax) :
        self.actionPointMax = newMax
    

    def setPosition(self,pos) :
        """
        position in coordinates
        """
        self.pos = pos


    def increaseHP(self, n):
        """
            desc : increase HP of n
            @n   : int
        """
        if  self.listStat[Attributes.HP] + n >=100:
            self.listStat[Attributes.HP]=100
        else:
            self.listStat[Attributes.HP] +=n


    def decrementHp(self, n):
        self.listStat[Attributes.HP] -= n
        if self.listStat[Attributes.HP] <= 0 : self.die()

    def setActionPoint(self,n) :   
        self.actionPoint = n


    def setAttribute(self,attribute: Attributes,n) :
        """
        strength, dex, con, intell, wis, cha
        """
        self.listStat[attribute] = n
    
    def increaseAttribute(self, attribute, n):
        """
        desc       : increase an attribute of n
        @attribute : str, attribute can be : strength, dex, con, intell, wis, cha
        @n         : int, 
        """
        if attribute == Attributes.Strength :
            self.listStat[Attributes.Strength] += n
        elif attribute == Attributes.Dexterity:
            self.listStat[Attributes.Dexterity] += n
        elif attribute == Attributes.Con :
            self.listStat[Attributes.Con] += n
        elif attribute == Attributes.Intelligence :
            self.listStat[Attributes.Intelligence] += n
        elif attribute == Attributes.Wisdom :
            self.listStat[Attributes.Wisdom] += n
        elif attribute == Attributes.Cha:
            self.listStat[Attributes.Cha] += n

    def decreaseAttribute(self, attribute, n):
        """
        desc       : decrease an attribute of n
        @attribute : str, attribute can be : strength, dex, con, intell, wis, cha
        @n         : int, 
        """
        if attribute == Attributes.Strength :
            self.listStat[Attributes.Strength] -= n
        elif attribute == Attributes.Dexterity:
            self.listStat[Attributes.Dexterity] -= n
        elif attribute == Attributes.Con :
            self.listStat[Attributes.Con] -= n
        elif attribute == Attributes.Intelligence :
            self.listStat[Attributes.Intelligence] -= n
        elif attribute == Attributes.Wisdom :
            self.listStat[Attributes.Wisdom] -= n
        elif attribute == Attributes.Cha:
            self.listStat[Attributes.Cha] -= n


    #ajouter dans le diagramme
    def increaseStats(self, stats):
        """
        desc   : increase all stats according to another listStats
        @stats : dict, list of attributes to add to self.listStats
        """
        for a in Attributes:
            try:
                self.listStat[a] += stats[a]
            except KeyError:
                pass

    #ajouter dans le diagramme
    def decreaseStats(self, stats):
        """
        desc   : decrease all stats according to another listStats
        @stats : dict, list of attributes to substract to self.listStats
        """
        for a in Attributes:
            try:
                self.listStat[a] -= stats[a]
            except KeyError:
                pass


    #ajouter dans le diagramme
    def _getAdjacentNodes(self,nodeX,nodeY):
        ''' 
            desc   : retourne les coordonnées des nodes adjacents à (nodeX,nodeY)
            @nodeX : int represente la coordonnée x 
            @nodeY : int representa la coordonnée y
            return : liste de Position    
        '''
        return [                   (nodeX  ,nodeY-1),
                (nodeX-1,nodeY)  ,                     (nodeX+1,nodeY), 
                                   (nodeX  ,nodeY+1), 
                ]
    
    def _createMapValue(self, dstX,dstY):
            ''' 
                desc   : methode utilisé par le pathfinding qui creer une representation 
                        de la map sous forme de valeur jusqu'a trouver la dst

                @dstX  : int reprensente la coordonné x de la destinnation que le character doit atteindre           
                @dstY  : int reprensente la coordonné y de la destinnation que le character doit atteindre           
                return : matrice represente la map sous forme de valeur
            '''

            sizeMapValue =  (MAP_HEIGHT, MAP_WIDTH)
            mapValue     = np.full( sizeMapValue , np.inf  )
            mapValue[self.pos] = 0 


            studyingNodes= [self.pos]    # contient les coordonnees des node à etudier
            adjacentNodes= []            # tableau permettant de memoriser les nodes adjacent etudié à une iteration 
                                         # afin de les etudier à l'iteration suivante 

            #fabrication de la map des valeurs 
            #tant qu'il y a des nodes a etudier ou qu'on n'a pas changer la valeur de dst
            while mapValue[dstX,dstY] == np.inf and studyingNodes != [] :
                #pour chaque node à etudier (studyNode) on regarde les nodes adjacents
                #pour chacun de ces nodes adjacents, si le node est valide 
                #et que ca valeur est plus grande que la valeur du studyNode

                for studyNode in studyingNodes:
                    
                    nodeValue = mapValue[studyNode]                   #valeur du node etudie 
                    alentour = self._getAdjacentNodes(*studyNode)      #repertorie les coodonnees des nodes adjacents

                    #pour chaque node adjacent, on actualise la valeur du node si sa valeur est > que celle du node actulle + 1 
                    for nodeAlentour in alentour:
                        nodeInMap = 0<=nodeAlentour[0] < mapValue.shape[0] and 0<=nodeAlentour[1] < mapValue.shape[1]
                        if nodeInMap and self.game.dungeon.currentFloor.canWalkOn(*nodeAlentour):

                            alentourValue = mapValue[nodeAlentour]  #valeur du node adjacent
                            if nodeValue+1 < alentourValue:
                                mapValue[nodeAlentour]= nodeValue+1 #la valeur du node adjacent = valeur du node etudié + 1
                                if nodeAlentour not in adjacentNodes: 
                                    adjacentNodes.append(nodeAlentour)

                studyingNodes = adjacentNodes
                adjacentNodes= []

            return mapValue

    #ajouter la gestion des point d'action consommé 
    #ajouter dans le diagramme
    def pathfind(self, dst):
            ''' 
                desc   : determine un chemin entre notre position et dst
                @dst   : Position represente la position que le character doit atteindre
                return : list de Position representant le chemin
            '''
           
            if not self.game.dungeon.currentFloor.canWalkOn(*dst):
                return None

            mapValue = self._createMapValue(*dst)

            if mapValue[dst] > self.actionPoint:
                return None

            ## findRoad ## 
    
            # cas ou il n'existe pas de chemin pour aller a dst
            if mapValue[dst]== np.inf:
                return None

            road = [dst]
            # tant qu'on est pas arrivé au node avant notre position
            while not mapValue[road[0]] == 1:
                if max(road.count(n) for n in road)!=1: # Vérification pour que la boucle ne soit pas infinie, il ne faut aucun doublons dans road
                    return None
                node = road[0]
                alentour = self._getAdjacentNodes(*node)
                # insert au rang 0 dans road le node adjacent qui a la plus petite valeur 
                road.insert(0, min( alentour, key= lambda node : mapValue[node] if 0<=node[0] < mapValue.shape[0] and 0<=node[1] < mapValue.shape[1] else float('inf')))
            
            self._decrementActionPoint(len(road))
            
            return road 


    #add to diagram
    def _move_zone(self):
        ''' 
            desc : creer une zone autour du character qui represente les cases où il peut se rendre 
        '''
        move_zone = []      
        studyingNodes = [self.pos]
        adjacentNodes = []  #stock les nodes adjacent au node present dans studyingNodes
        value = 0
        while value < self.actionPoint:
            value+=1
            for studyNode in studyingNodes:
                
                #repertorie les coodonnees des nodes adjacents
                alentour = self._getAdjacentNodes(*studyNode)
                for nodeAlentour in alentour:
                    nodeInMap = 0<=nodeAlentour[0] <  MAP_WIDTH  and 0<=nodeAlentour[1] < MAP_HEIGHT
                    if nodeInMap and self.game.dungeon.currentFloor.canWalkOn(*nodeAlentour):
                        if nodeAlentour not in adjacentNodes + move_zone:
                            adjacentNodes.append(nodeAlentour)
                            move_zone.append(nodeAlentour)


            studyingNodes = adjacentNodes
            adjacentNodes = []
        return move_zone

    def _decrementActionPoint(self, n):
        if (self.actionPoint > 0): self.actionPoint -= n

    def die(self) :
        dead = self
        if dead in dead.game.dungeon.players  :
            dead.game.dungeon.players.remove(dead)
        else :
            dead.game.dungeon.currentFloor.enemies.remove(dead)        
        




    
    