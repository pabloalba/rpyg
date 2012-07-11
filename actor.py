#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modules
from rpyg_utils import *
from inventory import *
from dialog import *

import os



# Classes
# ---------------------------------------------------------------------
class Actor:
    def __init__(self,screen,name,pos=[0,0],img_file=None,img_dialog=None,max_rows=4,max_cols=4):
        self.name=name
        self.pos=pos
        if (not img_file):
            img_file = os.path.join('images','default_chara.png')
        self.img_file=img_file
        if (not img_dialog):
            img_dialog = os.path.join('images','default_dialog_img.png')
        self.img_dialog=img_dialog
        self.max_rows=max_rows
        self.max_cols=max_cols
        self.speed=0.25
        self.row=0
        self.column=0
        self.screen=screen
        self.rect = None

    def init_display(self):

        self.chara = cut_chara(self.img_file, self.max_rows, self.max_cols)
        self.image = self.chara[0][0]
        self.rect = self.image.get_rect()
        self.rect.topleft=[self.pos[0]*32,self.pos[1]*32]
        if self.img_dialog:
            self.image_dialog=load_image(self.img_dialog,True)
        else:
            self.img_dialog=None

    def disapear(self):
        self.rect.centerx=3000

    def animate(self):
        if self.column>0:
            self.column-=1
        else:
            self.column=self.max_cols-1

    def move_up(self, time):
        self.rect.centery -= self.speed * time
        if self.max_rows>3:
            self.row=3
        self.animate()
        self.image=self.chara[self.row][self.column]
        return True

    def move_down(self,time):
        self.rect.centery += self.speed * time
        self.row=0
        self.animate()
        self.image=self.chara[self.row][self.column]
        return True

    def move_left(self,time):
        self.rect.centerx -= self.speed * time
        if self.max_rows>1:
            self.row=1
        self.animate()
        self.image=self.chara[self.row][self.column]
        return True

    def move_right(self,time):
        self.rect.centerx += self.speed * time
        if self.max_rows>2:
            self.row=2
        self.animate()
        self.image=self.chara[self.row][self.column]
        return True

    def look_down(self):
        self.image=self.chara[0][0]



    def draw(self, screen):
        screen.blit(self.image, self.rect)

class NPC(Actor):
    def __init__(self,screen,name):
        Actor.__init__(self, screen, name)
        self.dialogs=[]
        self.speed=0.10

    def add_dialog(self,name):
        dialog=Dialog(self,name)
        self.dialogs.append(dialog)

    def remove_dialog(self, dialog):
        self.dialogs.remove(dialog)

    def get_dialog(self,name):
       for d in self.dialogs:
            if d.name==name:
                return d

    def select_dialog(self, tokens):
        default=None
        for dialog in self.dialogs:
            if len(dialog.conditions)>0:
                if set(dialog.conditions).issubset(set(tokens)):
                    return dialog
            else:
                default=dialog
        return default

    def move(self,movement, time):
        x=(int(movement[0])+0.5)*32-self.rect.centerx
        y=(int(movement[1])+0.5)*32-self.rect.centery-12
        if x<-8:
            self.move_left(time)
            return True
        elif x>8:
            self.move_right(time)
            return True
        elif y>8:
            self.move_down(time)
            return True
        elif y<-8:
            self.move_up(time)
            return True
        else:
            return False





class Protagonist(Actor):
    def __init__(self,screen,name=''):
        Actor.__init__(self, screen, name)
        self.inventory=Inventory(self)
        self.tokens=[]
        self.npc_interact=None
        self.exit_activate=None

    def move(self, time, keys, objects):
        lastposy=self.rect.centery
        lastposx=self.rect.centerx
        moved=False
        if keys[K_UP]:
            if (self.move_up(time)):
                moved=True
        if keys[K_DOWN]:
           if (self.move_down(time)):
                moved=True
        if keys[K_LEFT]:
            if (self.move_left(time)):
                moved=True
        if keys[K_RIGHT]:
            if (self.move_right(time)):
                moved=True

        #Only if moved
        if (moved):
                self.npc_interact=None
                for npc in self.screen.npcs:
                    rect = Rect(npc.rect.left,npc.rect.top,npc.rect.width,npc.rect.height-10)
                    if self.rect.colliderect(rect):
                        self.rect.centerx=lastposx
                        self.rect.centery=lastposy
                        self.npc_interact=npc


                baserect=Rect(self.rect.left,self.rect.top+35,20,10)
                for wall in self.screen.walls:
                    if baserect.colliderect(wall.rect):
                        self.rect.centerx=lastposx
                        self.rect.centery=lastposy

                for e in self.screen.exits:
                    e_rect=Rect(int(e.pos[0])*32+10,int(e.pos[1])*32,10,50)
                    if baserect.colliderect(e_rect):
                        self.exit_activate=e




    def add_inventory_item(self,item):
        self.inventory.add_item(item)

    def add_inventory_item_by_name(self,name):
        item=self.screen.game.get_item(name)
        self.inventory.add_item(item)

    def remove_inventory_item_by_name(self,name):
        item=self.screen.game.get_item(name)
        self.inventory.remove_item(item)

    def add_token(self,token):
        if not token in self.tokens:
            self.tokens.append(token)

    def remove_token(self,token):
        if token in self.tokens:
            self.tokens.remove(token)

    def move_up(self, time):
        if self.rect.top >= 0:
            self.rect.centery -= self.speed * time
            if self.max_rows>3:
                self.row=3
            self.animate()
            self.image=self.chara[self.row][self.column]
            return True
        return False

    def move_down(self,time):
        if self.rect.bottom <= HEIGHT:
            self.rect.centery += self.speed * time
            self.row=0
            self.animate()
            self.image=self.chara[self.row][self.column]
            return True
        return False

    def move_left(self,time):
        if self.rect.left >= 0:
            self.rect.centerx -= self.speed * time
            if self.max_rows>1:
                self.row=1
            self.animate()
            self.image=self.chara[self.row][self.column]
            return True
        return False

    def move_right(self,time):
        if self.rect.right <= WIDTH:
            self.rect.centerx += self.speed * time
            if self.max_rows>2:
                self.row=2
            self.animate()
            self.image=self.chara[self.row][self.column]
            return True
        return False



# ---------------------------------------------------------------------

# Functions
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------

def main():
    return 0

if __name__ == '__main__':
    main()
