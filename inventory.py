#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Modules
import sys, pygame
from pygame.locals import *
from rpyg_utils import *
 
 
# Classes
# ---------------------------------------------------------------------


class Combination():
	def __init__(self, result, token_add=None, token_remove=None):
		self.result=result
		self.token_add=token_add
		self.token_remove=token_remove

class Item(pygame.sprite.Sprite):
    def __init__(self, name, game):
        self.name=name
        self.game=game
        self.image_url = ''
        self.text = ''        
        self.combinations={}
        
    def init_display(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(self.image_url, True)
        
    def combine(self, item):
        if item.name in self.combinations.keys():
            return self.combinations[item.name]
        else:
            if self.name in item.combinations.keys():
                return item.combinations[self.name]
            else:
                return None
        
    def add_combination(self,item,result,token_add=None, token_remove=None):
        c=Combination(result,token_add,token_remove)
        self.combinations[item]=c
    
    def remove_combination(self,item):
        del self.combinations[item]
        

class Inventory():
    def __init__(self, protagonist):
        self.items=[]
        self.item_sel=-1
        self.item_mark=-1
        self.image = None
        self.posx = 0
        self.posy = 0
        self.protagonist=protagonist
        
    def init_display(self):
        self.image = pygame.Surface((600, 480))
        self.image.fill((0, 0, 0))
        e_rect=Rect(3,3,594,474)
        pygame.draw.rect(self.image, (180, 74, 17), e_rect)
        
        self.posx=212
        self.posy=150
        
        
    def getItem(self, num):
        if num<0 or num>=len(items):
            return None
        else:
            return items[num]
    def add_item(self,item):
        self.items.append(item)
    def remove_item(self,item):
        self.items.remove(item)
    def combine(self,game):
        item1=self.items[self.item_mark]
        item2=self.items[self.item_sel]
        combination=item1.combine(item2)
        self.item_mark=-1
        if combination!=None:
            self.items.remove(item1)
            self.items.remove(item2)
            for r in combination.result:
                item=game.get_item(r)
                self.items.append(item)
            self.item_sel=len(self.items)-1
            if combination.token_remove:
                self.protagonist.remove_token(combination.token_remove)
            if combination.token_add:
                self.protagonist.add_token(combination.token_add)
            
            return True
        else:
            return False
        
    def draw(self,screen):
        screen.blit(self.image,(self.posx,self.posy))
        x=self.posx+25
        y=self.posy+30
        item_num=0
        for item in self.items:
            screen.blit(item.image,(x,y))
            
            if self.item_sel==item_num:
                pygame.draw.rect(screen, (0, 0, 255), (x, y, 75, 75),1)
                draw_text(screen,item.name, x, y-20, (0, 0, 255))
            if self.item_mark==item_num:
                pygame.draw.rect(screen, (0, 255, 0), (x, y, 75, 75),1)
                draw_text(screen,item.name, x, y-20, (0, 0, 0))
            
            x+=100
            if x>=(self.posx+550):
                x=self.posx+50
                y+=100            

            item_num+=1  
            
    def get_item(self,id):
        for item in self.items:
            if (item.id==id):
                return item
        return None
            
            
class Token():
    def __init__(self, name, game):
        self.name=name
        self.game=game
            
# ---------------------------------------------------------------------
 
# Functions
# ---------------------------------------------------------------------
 

 
 

 
# ---------------------------------------------------------------------

