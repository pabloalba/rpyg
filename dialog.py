#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modules
from utils import *
from inventory import *
import sys, pygame
from pygame.locals import *

TEXT_BACKGROUND=(250,240,210)
 
# Classes
# ---------------------------------------------------------------------

class Phrase:
    def __init__(self,dialog,text,by_npc):
        self.dialog=dialog
        self.by_npc=by_npc
        self.text=text
        

        
class Result:
    #~ RESULT_ADD_TOKEN
    #~ RESULT_REMOVE_TOKEN
    #~ RESULT_ADD_ITEM
    #~ RESULT_REMOVE_ITEM
    #~ RESULT_MOVE_NPC
    #~ RESULT_REMOVE_NPC
    def __init__(self,name,result_type):
        self.name=name
        self.result_type=result_type
        self.item=''
        self.token=''
        self.pos=[]
        
    def set_item(self,item):
        self.item=item
    def set_token(self,token):
        self.token=token
    def set_pos(self,pos):
        self.pos=pos
        
        

class Dialog:
    
    def __init__(self,npc,name):
        self.name=name
        self.npc=npc
        self.phrases=[]
        self.conditions=[]
        self.results=[]
        self.phrase_num=0
        
    def add_phrase(self,text,by_npc):
        phrase=Phrase(self,text,by_npc)
        self.phrases.append(phrase)
        
    def remove_phrase(self,text):
        for p in self.phrases:
            if p.text==text:
                self.phrases.remove(p)
                
    def add_condition(self,token):
        self.conditions.append(token)
        
    def remove_condition(self,token):
        self.conditions.remove(token)
        
    def add_result(self,result):
        self.results.append(result)
    
    def remove_result(self,name):
        for r in self.results:
            if r.name==name:
                self.results.remove(r)

    def draw(self,screen, protagonist):
        if self.phrase_num<len(self.phrases):
            phrase=self.phrases[self.phrase_num]
            text=phrase.text
            if phrase.by_npc:
                y=10
                photo_x=WIDTH-210
                photo_y=y+10
                text_x=90
                image_dialog=self.npc.image_dialog
            else:
                y=HEIGHT-100
                photo_x=80
                photo_y=y-130
                text_x=310
                image_dialog=protagonist.image_dialog
                      
            pygame.draw.rect(screen, TEXT_BACKGROUND, (100, y, WIDTH-200, 80))
            pygame.draw.circle(screen, TEXT_BACKGROUND, (100, y+40),40)
            pygame.draw.circle(screen, TEXT_BACKGROUND, (WIDTH-100, y+40),40)
            if image_dialog:
                screen.blit(image_dialog,(photo_x,photo_y))
            draw_text(screen,text.decode('utf-8'), text_x, y+30, (0, 0, 0))
