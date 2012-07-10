#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modules
import sys, pygame
from pygame.locals import *
from inventory import *
from rpyg_utils import *
from dialog import *
from game import *
from actor import *
import pickle
import os

class RPYG:
    def __init__(self, game_file):
        self.mode=MODE_GAME
        self.background_game=None
        self.protagonist=None


        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        self.display_copy=None
        pygame.display.set_caption('RPyG')
        pygame.font.init()
        self.load_game(game_file)


        for item in self.game.items:
            item.init_display()
        self.clock = pygame.time.Clock()
        self.dialog=None
        self.load_screen(self.game)

    def load_screen(self,game,name=''):
        inventory=None
        spawn_pos=None
        tokens=[]
        if self.protagonist and self.protagonist.exit_activate:
            if self.protagonist.exit_activate.keep_items_tokens:
                inventory=self.protagonist.inventory
                tokens=self.protagonist.tokens
            spawn_pos=self.protagonist.exit_activate.spawn_pos


        self.screen=None
        if (name):
            for s in game.screens:
                if s.name==name:
                    self.screen=s
        else:
            self.screen=game.screens[0]

        self.background_game=load_image(self.screen.map_file, False)
        self.protagonist=self.screen.protagonist
        if inventory==None:
            inventory=Inventory(self.protagonist)

        if spawn_pos:
            self.protagonist.pos=[int(spawn_pos[0]),int(spawn_pos[1])]

        self.protagonist.inventory=inventory
        self.protagonist.tokens=tokens
        self.protagonist.exit_activate=None
        self.protagonist.init_display()
        for npc in self.screen.npcs:
            npc.init_display()

        self.protagonist.inventory.init_display()

        #walls
        walls=[]
        num=0
        num_row=0
        num_column=0
        for wall_row in self.screen.valid_path:
            for wall_item in wall_row:
                if wall_item==0:
                    wall=NPC(self.screen,'Wall_'+str(num))
                    wall.rect=Rect(num_column*16,num_row*16,10,10)
                    walls.append(wall)
                    num+=1
                num_column+=1
            num_column=0
            num_row+=1
        self.screen.walls=walls

        self.pending_moves=[]

        #play_background_music("/home/palba/tmp/1.mp3")



    def load_game(self,filename):
        fileObj = open(filename,"r")
        self.game=pickle.load(fileObj)
        fileObj.close()


    def end_dialog(self):
        self.mode=MODE_GAME
        for result in self.dialog.results:
            print result.name+":"+result.result_type
            if result.result_type=='RESULT_REMOVE_TOKEN':
                self.protagonist.remove_token(result.token)
            elif result.result_type=='RESULT_ADD_TOKEN':
                self.protagonist.add_token(result.token)
            elif result.result_type=='RESULT_ADD_ITEM':
                self.protagonist.add_inventory_item_by_name(result.item)
            elif result.result_type=='RESULT_REMOVE_ITEM':
                self.protagonist.remove_inventory_item_by_name(result.item)
            elif result.result_type=='RESULT_REMOVE_NPC':
                if self.mode==MODE_CUT_SCENE:
                    self.mode=MODE_CUT_SCENE_REMOVE
                else:
                    self.screen.npcs.remove(self.protagonist.npc_interact)
                    self.protagonist.npc_interact=None
            elif result.result_type=='RESULT_MOVE_NPC':
                self.pending_moves.append(result.pos)
                self.mode=MODE_CUT_SCENE
            elif result.result_type=='RESULT_END_GAME':
                self.mode=MODE_END_GAME



    def process(self,events):
        for event in events:
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key==K_i:
                    self.mode=MODE_INVENTORY
                if event.key==K_ESCAPE:
                    sys.exit(0)
                if event.key==K_SPACE:
                    if self.protagonist.npc_interact:
                        self.dialog=self.protagonist.npc_interact.select_dialog(self.protagonist.tokens)
                        if self.dialog!=None:
                            self.mode=MODE_TALK
                if event.key==K_t:
                    for token in self.protagonist.tokens:
                        print "TOKEN: "+token
                if event.key==K_f:
                    pygame.display.toggle_fullscreen()



    def process_cut_scene(self,time):
        if self.protagonist.npc_interact:
            if len(self.pending_moves)>0:
                if not self.protagonist.npc_interact.move(self.pending_moves[0],time):
                    self.pending_moves.remove(self.pending_moves[0])
            else:
                if self.mode==MODE_CUT_SCENE_REMOVE:
                    self.screen.npcs.remove(self.protagonist.npc_interact)
                else:
                    self.protagonist.npc_interact.look_down()

                self.protagonist.npc_interact=None
                self.mode=MODE_GAME

    def process_dialog(self, events):
        for event in events:
            if event.type == KEYDOWN:
                if event.key==K_SPACE:
                    self.dialog.phrase_num+=1
                    if self.dialog.phrase_num>=len(self.dialog.phrases):
                        self.dialog.phrase_num=0
                        return False
        return True


    def process_inventory(self, events):
        inv=self.protagonist.inventory
        for event in events:
            if event.type == KEYDOWN:
                if event.key==K_i:
                    self.mode=MODE_GAME
                if event.key==K_RIGHT:
                    inv.item_sel+=1
                    if inv.item_sel>=len(inv.items):
                        inv.item_sel=0
                if event.key==K_LEFT:
                    inv.item_sel-=1
                    if inv.item_sel<0:
                        inv.item_sel=len(inv.items)-1
                if event.key==K_SPACE:
                    if inv.item_mark==inv.item_sel:
                        inv.item_mark=-1
                    elif inv.item_mark==-1:
                        inv.item_mark=inv.item_sel
                    else:
                        if inv.combine(self.game):
                            #~ playmusic2(SOUND_COMBINE_ERROR)
                            pass
                        else:
                            #~ playmusic2(SOUND_COMBINE)
                            pass


    def main_loop(self):
        #~ print "loop"
        events=pygame.event.get()
        time = self.clock.tick(25)

        if self.mode==MODE_GAME or self.mode==MODE_FIRST_DIALOG:
            self.process(events)
            if self.protagonist.exit_activate != None:
                self.load_screen(self.game,self.protagonist.exit_activate.screen)
            else:
                keys = pygame.key.get_pressed()
                self.protagonist.move(time, keys, self.screen.npcs)
                self.display.blit(self.background_game, (0, 0))

                for npc in self.screen.npcs:
                    npc.draw(self.display)

                for e in self.screen.exits:
                    e_rect=Rect(int(e.pos[0])*32,int(e.pos[1])*32,32,32)
                    pygame.draw.rect(self.display, (255, 0, 0), e_rect)
                self.protagonist.draw(self.display)
                self.display_copy=self.display.copy()
        elif self.mode==MODE_TALK:
            self.display.blit(self.display_copy, (0, 0))
            if self.process_dialog(events):
                self.dialog.draw(self.display,self.protagonist)
            else:
                self.end_dialog()
        elif self.mode==MODE_CUT_SCENE or self.mode==MODE_CUT_SCENE_REMOVE:
            self.process_cut_scene(time)
            self.display.blit(self.background_game, (0, 0))
            self.protagonist.draw(self.display)
            for npc in self.screen.npcs:
                npc.draw(self.display)
        elif self.mode==MODE_INVENTORY:
            self.process_inventory(events)
            self.protagonist.inventory.draw(self.display)

        if self.mode==MODE_FIRST_DIALOG:
                self.mode=MODE_TALK

        pygame.display.flip()




    def main(self):

        while self.mode!=MODE_END_GAME:
            self.main_loop()

        pygame.mixer.quit()
        #~ pygame.display.toggle_fullscreen()
        pygame.display.quit()


if len(sys.argv)>1:
    game_file=sys.argv[1]
    rpyg=RPYG(game_file)
    rpyg.main()
