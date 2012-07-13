#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import pickle
from game import *
from gtk import *
import os, math
import gobject, cairo

import zipfile
import tempfile

import shutil

import rpyg_utils

def load_image(filepath):
        img=Image()
        img.set_from_file(filepath)
        return img



# Create a GTK+ widget on which we will draw using Cairo
class MapScreen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, imagepath, screen):
        super(MapScreen, self).__init__()
        self.imagepath=imagepath
        self.cr=None
        self.screen=screen
        self.mark_x = -1
        self.mark_y = -1



    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        if (not self.cr):
            # Create the cairo context
            self.cr = self.window.cairo_create()
        cr = self.cr

        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()

        self.draw_image(cr)


    def draw_image(self, cr):
        image = cairo.ImageSurface.create_from_png (self.imagepath);
        cr.set_source_surface (image, 0, 0)
        cr.paint ()
        #Draw separation lines
        cr.set_source_rgb(0, 0, 1)
        x=0
        y=0
        while (x<=32):
            cr.rectangle(x*32, 0, 1, 768)
            x+=1
            cr.fill()

        while (y<=24):
            cr.rectangle(0,y*32, 1024, 1)
            y+=1
            cr.fill()


        #mark
        if (self.mark_x > -1) and (self.mark_y > -1):
            cr.set_source_rgba(1, 1, 0, 0.5)
            cr.rectangle(self.mark_x*32, self.mark_y*32, 32, 32)
            cr.fill()
        else:
            #Marked Path
            cr.set_source_rgba(0, 0, 1, 0.5)
            for x in range(64):
                for y in range(48):
                    if self.screen.valid_path[y][x]==1:
                        cr.rectangle(x*16, y*16, 16, 16)
                        cr.fill()




    def repaint(self):
         cr = self.window.cairo_create()
         self.draw_image(cr)



class  RPYG_Designer:
    def __init__(self, game_file):

        filename = "rpyg_designer.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)

        self.game_filename=''

        self.win_rpyg=self.builder.get_object('win_rpyg')

        self.win_rpyg.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("lightgray"))

        self.builder.get_object('box_prot_title').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('label_prot').modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#ffffff'))
        self.builder.get_object('box_prot').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))

        self.builder.get_object('box_npcs_title').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('label_npcs').modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#ffffff'))

        self.builder.get_object('box_exits_title').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('label_exits').modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#ffffff'))






        self.builder.get_object('box_npcs').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('box_exits').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('main_area').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('other_properties').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('viewport2').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))



        #Init dialogs window
        icon  = self.load_image(os.path.join('images','pos_map.png'), 16, 16)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_prot_map').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_npc_map').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_exit_map').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_destiny_map').set_image(image)

        icon  = self.load_image(os.path.join('images','dialog.png'), 90)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_npc_dialogs').set_image(image)

        icon  = self.load_image(os.path.join('images','help.png'), 25)
        self.builder.get_object('help_1').set_from_pixbuf(icon)
        self.builder.get_object('help_2').set_from_pixbuf(icon)
        
        icon  = self.load_image(os.path.join('images','arrow.png'))
        self.builder.get_object('img_arrow_1').set_from_pixbuf(icon)
        self.builder.get_object('img_arrow_2').set_from_pixbuf(icon)
        
        
        icon  = self.load_image(os.path.join('images','add_dialog_prot.png'), 90)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_add_dialog_prot').set_image(image)
        
        icon  = self.load_image(os.path.join('images','add_dialog_npc.png'), 90)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_add_dialog_npc').set_image(image)
        
        icon  = self.load_image(os.path.join('images','add_token.png'), 32)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_add_token').set_image(image)
        
        icon  = self.load_image(os.path.join('images','help.png'), 25)
        self.builder.get_object('img_hlp_conditions').set_from_pixbuf(icon)
        
        
        
        
        self.builder.get_object('box_conditions').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('box_dialog').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('box_results').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))        
        #Init for combos
        cell = gtk.CellRendererText()
        self.builder.get_object('cmb_results').pack_start(cell, True)
        self.builder.get_object('cmb_results').add_attribute(cell, "text", 0)
        
        
        


        self.liststore_screens = None
        self.liststore_npcs = None
        self.liststore_exits = None
        self.liststore_tokens = None
        self.liststore_items = None
        self.liststore_dialogs = None
        self.liststore_phrase = None
        self.liststore_results = None
        
        self.conditions_handler = None
        
        self.screen = None
        self.npc = None
        self.s_exit = None
        self.token = None
        self.item = None
        self.dialog = None
        self.phrase = None
        self.result = None
        
        self.select_window_cancel_callback = None
        self.select_window_ok_callback = None
        
        self.game = Game()
        self.init_iconview_maps()
        self.init_iconview_tokens()
        self.init_iconview_items()
        self.init_iconview_dialogs()
        
        
        self.builder.get_object('liststore_results')
        
        
        


        
        
        if (game_file):
            self.open_game_file(game_file)
        

    def init_iconview_maps(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_maps')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_screens):
            liststore = self.liststore_screens
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_map_clicked)


        #Add icon for 'add screen'
        add_icon = self.load_image("images/add_map.png", 144, 90)
        liststore.append([add_icon, "Add screen"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_screens = liststore

        

        self.win_rpyg.show_all()
        
    def init_iconview_tokens(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_tokens')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_tokens):
            liststore = self.liststore_tokens
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_token_clicked)


        #Add icon for 'add token'
        add_icon = self.load_image("images/add_token.png", 32, 32)
        liststore.append([add_icon, "Add token"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_tokens = liststore

        

        self.win_rpyg.show_all()
        
        
    def init_iconview_items(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_items')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_items):
            liststore = self.liststore_items
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_item_clicked)


        #Add icon for 'add item'
        add_icon = self.load_image("images/add_item.png", 32, 32)
        liststore.append([add_icon, "Add item"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_items = liststore

        

        self.win_rpyg.show_all()
        
        
    def init_iconview_dialogs(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_dialogs')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_dialogs):
            liststore = self.liststore_dialogs
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
             #assign event
            iconview.connect('button-release-event', self.on_icon_dialog_clicked)


        #Add icon for 'add dialog'
        add_icon = self.load_image("images/add_dialog.png", 32, 32)
        liststore.append([add_icon, "Add dialog"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_dialogs = liststore

       

    def init_iconview_phrase(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_phrase')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_phrase):
            liststore = self.liststore_phrase
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_phrase_clicked)


        #set liststore
        iconview.set_model(liststore)
        self.liststore_phrase = liststore
        
        

        self.builder.get_object('win_dialogs').show_all()

        
    def init_iconview_results(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_results')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_results):
            liststore = self.liststore_results
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_result_clicked)


        #Add icon for 'add result'
        add_icon = self.load_image("images/add_result.png", 32, 32)
        liststore.append([add_icon, "Add result"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_results = liststore

        

        self.win_rpyg.show_all()
        

    def init_iconview_npcs(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_npcs')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_npcs):
            liststore = self.liststore_npcs
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_npc_clicked)



        #Add icon for 'add npc'
        add_icon = self.load_image("images/add_npc.png", 32, 48)
        liststore.append([add_icon, "Add npc"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_npcs = liststore

        

        self.win_rpyg.show_all()

    def init_iconview_exits(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_exits')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_exits):
            liststore = self.liststore_exits
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            #assign event
            iconview.connect('button-release-event', self.on_icon_exit_clicked)



        #Add icon for 'add exit'
        add_icon = self.load_image(os.path.join("images","add_exit.png"), 32, 32)
        liststore.append([add_icon, "Add exit"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_exits = liststore

        

        self.win_rpyg.show_all()



    def on_icon_map_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, open add dialog
            if (pos == 0):
                self.open_map_dialog()
            else:
                self.load_screen(pos-1)
                
                
    def on_iconview_maps_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = self.builder.get_object('iconview_maps').get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]
                if pos>0:
                    screen = self.game.screens[pos-1]
                    if self.show_confirm('Do you want to delete the screen "'+screen.name+'"?'):
                        self.screen = None
                        self.game.screens.remove(screen)                        
                        self.init_iconview_maps()
                        self.load_screens()
                        self.builder.get_object('screen_properties').set_sensitive(False)
                        self.builder.get_object('other_properties').set_sensitive(False)
                        self.load_map_image(os.path.join('images','void.png'))                        
                        self.liststore_npcs.clear()                        
                        self.builder.get_object('prot_name').set_text('')
                        self.builder.get_object('prot_x').set_text('')
                        self.builder.get_object('prot_y').set_text('')
                        self.load_prot_chara(self.builder.get_object('btn_prot_image_chara'), None)
                        self.actor_load_image_dialog(self.builder.get_object('btn_prot_image_dialogs'), None)
                        self.builder.get_object('txt_screen_name').set_text('')
                        self.builder.get_object('txt_screen_music').set_text('')
                        

    def on_icon_npc_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, open add dialog
            if (pos == 0):
                self.open_npc_dialog(None)
            else:
                self.npc = self.screen.npcs[pos-1]
                self.load_npc_properties(self.npc)
                
    def on_iconview_npcs_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = self.builder.get_object('iconview_npcs').get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]
                if pos>0:
                    npc = self.screen.npcs[pos-1]
                    if self.show_confirm('Do you want to delete the npc "'+npc.name+'"?'):
                        self.npc = None
                        self.screen.npcs.remove(npc)
                        element = self.liststore_npcs.get_iter(pos)
                        self.liststore_npcs.remove(element)
                        self.load_npcs()
                
        

    def on_icon_exit_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, add exit
            if (pos == 0):
                name = "exit "+str(len(self.screen.exits)+1)
                self.s_exit = self.screen.add_exit(name)
                #add exit icon
                pixbuf = self.load_image(os.path.join("images","exit.png"), 32, 32)
                self.liststore_exits.append([pixbuf, self.s_exit.name])
                #Select last element
                pos = len(self.screen.exits)
                self.builder.get_object('iconview_exits').select_path((pos,))
                self.load_exit_properties(self.s_exit)

            else:
                self.s_exit = self.screen.exits[pos-1]
                self.load_exit_properties(self.s_exit)
                
    def create_token_icon(self, token):
        #add token icon
        pixbuf = self.load_image(os.path.join("images","token.png"), 32, 32)
        liststore_item = [pixbuf, token.name]
        self.liststore_tokens.append(liststore_item)
        return liststore_item
        
                
    def on_icon_token_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, add token
            if (pos == 0):
                name = "token "+str(len(self.game.tokens)+1)
                token = self.game.add_token(name)
                self.token = token
                
                self.create_token_icon(token)
                
                #Select last element
                pos = len(self.game.tokens)
                self.builder.get_object('iconview_tokens').select_path((pos,))
                self.load_token_properties(token)

            else:
                self.token = self.game.tokens[pos-1]
                self.load_token_properties(self.token)
                
                
                
    def on_iconview_tokens_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = iconview.get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]      
                if (pos>0):          
                    token = self.game.tokens[pos-1]
                    
                    can_delete = True
                    names = ''
                    conditions = ''
                    for screen in self.game.screens:
                        for npc in screen.npcs:
                            for dialog in npc.dialogs:
                                for result in dialog.results:
                                    if (result.token == token):
                                        can_delete = False
                                        names += '\n    -'+screen.name+' > '+npc.name+' > '+dialog.name+' > '+result.name
                                for condition in dialog.conditions:
                                    if (condition == token):
                                        can_delete = False
                                        conditions += '\n    -'+screen.name+' > '+npc.name+' > '+dialog.name
                                    
                    if can_delete:
                        if self.show_confirm('Do you want to delete the token "'+token.name+'"?'):
                            self.token = None
                            self.game.tokens.remove(token)
                            self.init_iconview_tokens()
                            self.load_tokens()
                    else:
                        text = "The token can't be deleted because it is used on"
                        if (conditions):
                            text+="\n\n* The conditions for:"+conditions
                        if (names):
                            text+="\n\n* The results:"+names
                        
                        
                        self.show_error(text)
                        
                        
                        
                        
                
    def on_icon_result_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, add result
            if (pos == 0):
                name = "result "+str(len(self.dialog.results)+1)
                result = self.dialog.add_result(name)
                
                #add result icon
                pixbuf = self.load_image(os.path.join("images","result.png"), 32, 32)
                self.liststore_results.append([pixbuf, name])
                #Select last element
                pos = len(self.dialog.results)
                self.builder.get_object('iconview_results').select_path((pos,))
                self.result = result
                self.load_result_properties(self.result)

            else:
                self.result = self.dialog.results[pos-1]
                self.load_result_properties(self.result)
                
                
    def on_iconview_results_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = iconview.get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0] 
                if (pos>0):               
                    result = self.dialog.results[pos-1]
                    if self.show_confirm('Do you want to delete the result "'+result.name+'"?'):
                        self.result = None
                        self.dialog.results.remove(result)
                        self.load_dialog_properties(self.dialog)             
                
                
    def on_icon_item_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, open add dialog
            if (pos == 0):
                self.open_item_dialog(None)
            else:
                self.item = self.game.items[pos-1]
                self.load_item_properties(self.item)
                
                
    def on_iconview_items_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = iconview.get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]      
                if (pos>0):          
                    item = self.game.items[pos-1]
                    
                    can_delete = True
                    names = ''
                    for screen in self.game.screens:
                        for npc in screen.npcs:
                            for dialog in npc.dialogs:
                                for result in dialog.results:
                                    if (result.item == item):
                                        can_delete = False
                                        names += '\n    -'+screen.name+' > '+npc.name+' > '+dialog.name+' > '+result.name
                                    
                    if can_delete:
                        if self.show_confirm('Do you want to delete the item "'+item.name+'"?'):
                            self.item = None
                            self.game.items.remove(item)
                            self.init_iconview_items()
                            self.load_items()
                    else:
                        self.show_error("The item can't be deleted because it is used on the results:\n"+names)
                    
                
    def on_icon_dialog_clicked(self, iconview, event):        
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, add dialog
            if (pos == 0):
                name = "dialog "+str(len(self.npc.dialogs)+1)
                dialog = self.npc.add_dialog(name)
                
                #add dialog icon
                pixbuf = self.load_image(os.path.join("images","dialog.png"), 32, 32)
                self.liststore_dialogs.append([pixbuf, name])
                #Select last element
                pos = len(self.npc.dialogs)
                self.builder.get_object('iconview_dialogs').select_path((pos,))                
                self.dialog = dialog
                self.load_dialog_properties(self.dialog)

            else:                
                self.dialog = self.npc.dialogs[pos-1]
                self.load_dialog_properties(self.dialog)
                
                
    def on_iconview_dialogs_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = iconview.get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]     
                if pos>0:           
                    dialog = self.npc.dialogs[pos-1]
                    if self.show_confirm('Do you want to delete the dialog "'+dialog.name+'"?'):
                        self.dialog = None
                        self.npc.dialogs.remove(dialog)
                        self.load_dialogs()
                    


    def on_exit_keep_toggled(self, button):
        self.s_exit.keep_items_tokens = button.get_active()



    def load_screen(self, pos):
        self.screen = self.game.screens[pos]
        self.load_map_image(self.screen.map_file)
        self.builder.get_object('screen_box').set_sensitive(True)
        self.builder.get_object('screen_properties').set_sensitive(True)
        self.builder.get_object('txt_screen_name').set_text(self.screen.name)
        self.builder.get_object('txt_screen_music').set_text(str(os.path.basename(self.screen.music_file)))
        self.load_prot()
        self.load_npcs()
        self.load_exits()


    def open_map_dialog(self):
        filename = self.open_file('*.png')
        if (filename):
            
            screen_map  = self.load_image(filename)
            
            #Get size
            width = screen_map.get_width()
            height = screen_map.get_height()
            
            if (width != 1024) or (height != 768):
                self.show_error ("Screen file not valid. Must be an image of 1024x768 pixels")
                return None
            
            
            #Create new screen
            screen_name = str(os.path.basename(filename))[0:-4]

            #Search more screens with same name
            num = 0
            for s in self.game.screens:
                if s.name.startswith(screen_name):
                    num += 1
            if (num > 0):
                screen_name += str(num)

            screen = self.game.add_screen(screen_name)
            screen.map_file = filename

            screen_icon  = self.load_image(filename, 144, 90)
            self.liststore_screens.append([screen_icon, screen_name])

            #resize iconview
            self.builder.get_object('iconview_maps').set_size_request(200*len(self.game.screens),90)

            self.win_rpyg.show_all()
            #Select last element
            pos = len(self.game.screens)
            self.builder.get_object('iconview_maps').select_path((pos,))
            self.load_screen(pos-1)


    def open_npc_dialog(self,button):
        filename = self.open_file('*.png')
        if (filename):
            #Create new npc
            npc_name = str(os.path.basename(filename))[0:-4]

            #Search more npcs with same name
            num = 0
            for n in self.screen.npcs:
                if n.name.startswith(npc_name):
                    num += 1
            if (num > 0):
                npc_name += str(num)
            
            npc = self.screen.add_npc(npc_name)
            pixbuf = self.set_actor_chara(npc, filename)
            if (pixbuf):                
                #Load and select npc
                pos = len(self.screen.npcs)
                self.npc = self.screen.npcs[pos-1]
                self.add_npc_icon(self.npc)
                self.load_npc_properties(self.npc)
                self.builder.get_object('iconview_npcs').select_path((pos,))
                self.builder.get_object('npc_area').set_sensitive(True)
            else:
                self.screen.npcs.remove(npc)
                
                
    def open_item_dialog(self,button):
        filename = self.open_file('*.png *.jpg')
        if (filename):
            #Create new item
            item_name = str(os.path.basename(filename))[0:-4]

            #Search more items with same name
            num = 0
            for n in self.game.items:
                if n.name.startswith(item_name):
                    num += 1
            if (num > 0):
                item_name += str(num)
            
            item = self.game.add_item(item_name)
            item.image_url = filename
            
            #add item icon
            pixbuf = self.load_image(filename, 32, 32)
            self.liststore_items.append([pixbuf, item_name])
            #Select last element
            pos = len(self.game.items)
            self.builder.get_object('iconview_items').select_path((pos,))
            self.load_item_properties(item)
            self.item = self.game.items[pos-1]
            
    def load_exits(self):
        self.init_iconview_exits()
        self.builder.get_object('exit_name').set_text('')
        self.builder.get_object('exit_x').set_text('')
        self.builder.get_object('exit_y').set_text('')
        self.builder.get_object('destiny_name').set_text('')
        self.builder.get_object('destiny_x').set_text('')
        self.builder.get_object('destiny_y').set_text('')
        self.builder.get_object('exit_area').set_sensitive(False)
        if (len(self.screen.exits) != 0 ):
            #Load exits
            i = 0
            for e in self.screen.exits:
                pixbuf = self.load_image(os.path.join("images","exit.png"), 32, 32)
                self.liststore_exits.append([pixbuf, e.name])


    def load_npcs(self):
        self.builder.get_object('npc_area').set_sensitive(False)
        self.builder.get_object('npc_name').set_text('')
        self.builder.get_object('npc_x').set_text('')
        self.builder.get_object('npc_y').set_text('')
        self.actor_load_image_dialog(self.builder.get_object('btn_npc_image_dialogs'), os.path.join('images','void.png'))
        self.init_iconview_npcs()
        if (len(self.screen.npcs) != 0 ):
            #Load npcs
            i = 0
            for npc in self.screen.npcs:
                self.add_npc_icon(npc)


    def load_tokens(self):
        self.init_iconview_tokens()
        self.builder.get_object('token_name').set_text('')
        self.builder.get_object('token_area').set_sensitive(False)
        if (len(self.game.tokens) != 0 ):
            #Load tokens
            i = 0
            for t in self.game.tokens:
                pixbuf = self.load_image(os.path.join("images","token.png"), 32, 32)
                self.liststore_tokens.append([pixbuf, t.name])
                
    def load_dialogs(self):
        self.init_iconview_dialogs()
        self.init_iconview_conditions()
        self.init_iconview_results()
        self.init_iconview_phrase()
        self.builder.get_object('dialog_name').set_text('')
        self.builder.get_object('dialog_area').set_sensitive(False)
        
        if (len(self.npc.dialogs) != 0 ):
            #Load dialogs
            i = 0
            for d in self.npc.dialogs:
                pixbuf = self.load_image(os.path.join("images","dialog.png"), 32, 32)
                self.liststore_dialogs.append([pixbuf, d.name])

    def load_items(self):
        self.init_iconview_items()
        self.builder.get_object('item_name').set_text('')
        self.builder.get_object('item_area').set_sensitive(False)
        if (len(self.game.items) != 0 ):
            #Load items
            i = 0
            for item in self.game.items:
                pixbuf = self.load_image(item.image_url, 32, 32)
                self.liststore_items.append([pixbuf, item.name])
                
    def load_results(self):
        self.init_iconview_results()
        self.builder.get_object('cmb_results').set_active(-1)
        self.builder.get_object('btn_result_token').set_label('')
        self.builder.get_object('btn_result_item').set_label('')
        
        icon  = self.load_image(os.path.join('images','void.png'))
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_result_token').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_result_item').set_image(image)
        
        
        self.builder.get_object('result_area').set_sensitive(False)
        if (len(self.game.results) != 0 ):
            #Load results
            i = 0
            for t in self.game.results:
                pixbuf = self.load_image(os.path.join("images","result.png"), 32, 32)
                self.liststore_results.append([pixbuf, t.name])


    def add_npc_icon(self, npc):
        #Add npc icon
        pixbuf = gtk.gdk.pixbuf_new_from_file(npc.img_file)
        subpixbuf = pixbuf.subpixbuf(0, 0, 32, 48)
        self.liststore_npcs.append([subpixbuf, npc.name])
        self.win_rpyg.show_all()

    def load_npc_properties(self, npc):
        self.builder.get_object('npc_area').set_sensitive(True)
        #Write npc properties
        self.builder.get_object('npc_name').set_text(npc.name)
        self.builder.get_object('npc_x').set_text(str(npc.pos[0]))
        self.builder.get_object('npc_y').set_text(str(npc.pos[1]))
        self.actor_load_image_dialog(self.builder.get_object('btn_npc_image_dialogs'), self.npc.img_dialog)

    def load_exit_properties(self, s_exit):
        self.builder.get_object('exit_area').set_sensitive(True)
        #Write exit properties
        self.builder.get_object('exit_name').set_text(s_exit.name)
        self.builder.get_object('exit_x').set_text(str(s_exit.pos[0]))
        self.builder.get_object('exit_y').set_text(str(s_exit.pos[1]))
        self.builder.get_object('exit_keep').set_active(s_exit.keep_items_tokens)
        if s_exit.screen:
            self.builder.get_object('destiny_name').set_text(s_exit.screen.name)
        else:
            self.builder.get_object('destiny_name').set_text('')
        self.builder.get_object('destiny_x').set_text(str(s_exit.spawn_pos[0]))
        self.builder.get_object('destiny_y').set_text(str(s_exit.spawn_pos[1]))


    def load_token_properties(self, token):
        self.builder.get_object('token_area').set_sensitive(True)
        #Write token properties
        self.builder.get_object('token_name').set_text(token.name)
        
    def load_item_properties(self, item):
        self.builder.get_object('item_area').set_sensitive(True)
        #Write token properties
        self.builder.get_object('item_name').set_text(item.name)
        
   
        
        
        

    def load_prot(self):
        name = self.screen.protagonist.name
        if not name:
            name = "Protagonist"
        self.builder.get_object('prot_name').set_text(name)
        self.builder.get_object('prot_x').set_text(str(self.screen.protagonist.pos[0]))
        self.builder.get_object('prot_y').set_text(str(self.screen.protagonist.pos[1]))
        self.actor_load_image_dialog(self.builder.get_object('btn_prot_image_dialogs'), self.screen.protagonist.img_dialog)
        self.load_prot_chara(self.builder.get_object('btn_prot_image_chara'), self.screen.protagonist.img_file)



    ###################################################
    # Actors and exits
    ###################################################



    #Protagonist
    def btn_prot_image_dialogs_clicked(self, button):
        self.btn_image_dialogs_clicked(button, self.screen.protagonist)

    def btn_prot_image_chara_clicked(self, button):
        filename = self.open_file('*.png')
        if (filename):
            pixbuf = self.set_actor_chara(self.screen.protagonist, filename)
            if (pixbuf):
                self.load_prot_chara(button, filename)

    def load_prot_chara(self, button, filename):
        if not filename:
            filename = os.path.join('images','default_chara.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        image = gtk.image_new_from_pixbuf(pixbuf.subpixbuf(0, 0, 32, 48))
        button.set_image(image)

    def btn_prot_map_clicked(self, button):
        self.btn_map_clicked(button, self.on_prot_map_clicked, self.screen.protagonist.pos[0], self.screen.protagonist.pos[1])


    def on_prot_map_clicked(self,screenmap,event):
        field_x = self.builder.get_object('prot_x')
        field_y = self.builder.get_object('prot_y')
        self.screen.protagonist.pos = self.on_map_clicked(screenmap,event, field_x, field_y)

    def update_prot_coordinates(self, field):
        try:
            x = int(self.builder.get_object('prot_x').get_text())
            y = int(self.builder.get_object('prot_y').get_text())
            self.screen.protagonist.pos[0] = x
            self.screen.protagonist.pos[1] = y
        except:
            pass


    #npc
    def btn_npc_image_dialogs_clicked(self, button):
        self.btn_image_dialogs_clicked(button, self.npc)


    def btn_npc_map_clicked(self, button):
        self.btn_map_clicked(button, self.on_npc_map_clicked, self.npc.pos[0], self.npc.pos[1])

    def on_npc_map_clicked(self,screenmap,event):
        field_x = self.builder.get_object('npc_x')
        field_y = self.builder.get_object('npc_y')
        self.npc.pos = self.on_map_clicked(screenmap, event, field_x, field_y)

    def update_npc_coordinates(self, a, b):
        try:
            x = int(self.builder.get_object('npc_x').get_text())
            y = int(self.builder.get_object('npc_y').get_text())
            self.npc.pos[0] = x
            self.npc.pos[1] = y
        except:
            pass

    #exit
    def btn_exit_map_clicked(self, button):
        self.btn_map_clicked(button, self.on_exit_map_clicked, self.s_exit.pos[0], self.s_exit.pos[1])

    def on_exit_map_clicked(self,screenmap,event):
        field_x = self.builder.get_object('exit_x')
        field_y = self.builder.get_object('exit_y')
        self.s_exit.pos = self.on_map_clicked(screenmap,event, field_x, field_y)

    def update_exit_coordinates(self, a, b):
        try:
            x = int(self.builder.get_object('exit_x').get_text())
            y = int(self.builder.get_object('exit_y').get_text())
            self.s_exit.pos[0] = x
            self.s_exit.pos[1] = y
        except:
            pass

    def update_destiny_coordinates(self, a, b):
        try:
            x = int(self.builder.get_object('destiny_x').get_text())
            y = int(self.builder.get_object('destiny_y').get_text())
            self.s_exit[0] = x
            self.s_exit[1] = y
        except:
            pass



    def btn_destiny_map_clicked(self, button):
        self.show_window_select(self.liststore_screens, self.on_btn_destiny_ok_clicked, self.on_btn_destiny_cancel_clicked)

    def on_btn_destiny_cancel_clicked(self, button):
        pass

    def on_btn_destiny_ok_clicked(self, button):
        iconview = self.builder.get_object('iconview_select')
        selected = iconview.get_selected_items()
        if len(selected)==1:
            pos = selected[0][0]
            self.s_exit.screen = self.game.screens[pos]
            self.builder.get_object('destiny_name').set_text(self.s_exit.screen.name)
            self.btn_map_clicked(button, self.on_destiny_map_clicked, self.s_exit.spawn_pos[0], self.s_exit.spawn_pos[1], self.s_exit.screen.map_file)

    def on_destiny_map_clicked(self,screenmap,event):
        field_x = self.builder.get_object('destiny_x')
        field_y = self.builder.get_object('destiny_y')
        self.s_exit.spawn_pos = self.on_map_clicked(screenmap, event, field_x, field_y)










    #actors
    def set_actor_chara(self, actor, filename):
        if (filename):
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                #Get size
                width = pixbuf.get_width()
                height = pixbuf.get_height()
                
                if (width % 32 != 0) or (height % 48 != 0):
                    self.show_error ("Chara file not valid. Must be an image of 32x48 charas")
                    return None
                
                actor.max_rows = width / 32
                actor.max_cols = height / 48
                actor.img_file = filename
                return pixbuf
            except:
                self.show_error ("Chara file not valid. Must be an image of 32x48 charas")
                return None

    def btn_image_dialogs_clicked(self, button, actor):
        filename = self.open_file('*.png *.jpg')
        if (filename):
            self.actor_load_image_dialog(button, filename)
            actor.img_dialog = filename


    def actor_load_image_dialog(self, button, filename):
        if not filename:
            filename = os.path.join('images','default_dialog_img.png')
        icon  = self.load_image(filename, 90)
        image = gtk.image_new_from_pixbuf(icon)
        button.set_image(image)


    def btn_map_clicked(self, button, callback, x, y, map_file=None):
        if not map_file:
            map_file = self.screen.map_file
        filepath=map_file
        if (filepath):
            drawing_area = gtk.DrawingArea()
            map_screen = MapScreen(filepath,self.screen)
            map_screen.show()
            map_screen.connect("button_press_event", callback)
            map_screen.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            win_map = self.builder.get_object('win_map')

            try:
                map_screen.mark_x = x
                map_screen.mark_y = y
            except:
                pass

            win_map.add(map_screen)
            win_map.set_size_request(1024, 768)
            win_map.set_visible(True)

    def on_map_clicked(self, screenmap, event, field_x, field_y):
        if event.button==1:
            x=int(math.floor(event.x/32))
            y=int(math.floor(event.y/32))
            field_x.set_text(str(x))
            field_y.set_text(str(y))
            self.builder.get_object('win_map').destroy()
            pos = [x, y]
            return pos


    ##########################
    # Dialogs
    ##########################
    
    def on_btn_npc_dialogs_clicked(self, button):
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.npc.img_file)
        subpixbuf = pixbuf.subpixbuf(0, 0, 32, 48)
        self.builder.get_object('img_dialog_npc_chara').set_from_pixbuf(subpixbuf)
            
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.screen.protagonist.img_file)
        subpixbuf = pixbuf.subpixbuf(0, 0, 32, 48)
        self.builder.get_object('img_dialog_prot_chara').set_from_pixbuf(subpixbuf)
        
        pixbuf = self.load_image(self.screen.protagonist.img_file, 90)
        self.builder.get_object('img_dialog_prot').set_from_pixbuf(pixbuf)
        
        pixbuf = self.load_image(self.npc.img_dialog, 90)
        self.builder.get_object('img_dialog_npc').set_from_pixbuf(pixbuf)
        
        self.builder.get_object('lbl_dialogs_with').set_text('Dialogs with '+self.npc.name)
        
        self.load_dialogs()
        
        self.builder.get_object('win_dialogs').set_visible(True)
    
    def on_btn_dialog_ok_clicked(self, button):
        self.builder.get_object('win_dialogs').set_visible(False)


    def on_btn_add_dialog_prot_activate(self, button):
        self.phrase = self.dialog.add_phrase('',False)
        self.dialog_add_phrase(False)
    
    def on_btn_add_dialog_npc_clicked(self, button):
        self.phrase = self.dialog.add_phrase('',True)
        self.dialog_add_phrase(True)
        
    def dialog_add_phrase(self, by_npc, text='', select_phrase=True):
        #add icon
        if (by_npc):
            pixbuf = self.load_image(os.path.join("images","dialog_npc.png"))
        else:
            pixbuf = self.load_image(os.path.join("images","dialog_prot.png"))
            
        self.liststore_phrase.append([pixbuf, text])
        
        if select_phrase:
            #Select last element
            pos = len(self.dialog.phrases)
            self.builder.get_object('iconview_phrase').select_path((pos-1,))
            self.load_phrase_properties(self.phrase)
        
    def load_phrase_properties(self, phrase):
        self.builder.get_object('phrase').set_text(phrase.text)

    def on_icon_phrase_clicked(self, iconview, event):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            self.phrase = self.dialog.phrases[pos]
            self.load_phrase_properties(self.phrase)
            
            
    def on_iconview_phrase_key_release_event(self, iconview, event):
        if event.keyval == 65535:
            selected = iconview.get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]                
                phrase = self.dialog.phrases[pos]
                if self.show_confirm('Do you want to delete the phrase "'+phrase.text+'"?'):
                    self.phrase = None
                    self.dialog.phrases.remove(phrase)
                    self.load_dialog_properties(self.dialog)
                    
                
                
                    
            
    def on_phrase_changed(self, field):
        if (field.get_text()):            
            selected = self.builder.get_object('iconview_phrase').get_selected_items()
            if (len(selected) == 1):
                self.phrase.text = field.get_text()
                pos = selected[0][0]
                self.liststore_phrase[pos][1]=self.phrase.text
                

    def load_dialog_properties(self, dialog):
        self.builder.get_object('iconview_conditions').handler_block(self.conditions_handler)
        self.builder.get_object('dialog_area').set_sensitive(True)
        #Write dialog properties
        self.builder.get_object('dialog_name').set_text(dialog.name)
        self.init_iconview_phrase()
        self.init_iconview_conditions()
        self.init_iconview_results()
                
        #Load phrases
        for p in dialog.phrases:
            self.dialog_add_phrase(p.by_npc, p.text, False)
            
        #load conditions
        pos = 0
        for token in self.game.tokens:
            if token in dialog.conditions:
                self.builder.get_object('iconview_conditions').select_path((pos,))
            pos += 1
                
        self.builder.get_object('iconview_conditions').handler_unblock(self.conditions_handler)
        
        
        #load results
        self.builder.get_object('result_area').set_sensitive(False)
        for result in self.dialog.results:
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join('images','result.png'))
            self.liststore_results.append([pixbuf, result.name])
            
            
            
                
        
    def clear_result_properties(self):
        self.builder.get_object('btn_result_token').set_label('')
        self.builder.get_object('btn_result_item').set_label('')
        
        icon  = self.load_image(os.path.join('images','void.png'))
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_result_token').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_result_item').set_image(image)
        
        self.builder.get_object('lbl_select_token').set_sensitive(False)
        self.builder.get_object('btn_result_token').set_sensitive(False)
        self.builder.get_object('lbl_select_item').set_sensitive(False)
        self.builder.get_object('btn_result_item').set_sensitive(False)
        
            
    def load_result_properties(self, result):
        self.clear_result_properties()
        self.builder.get_object('result_area').set_sensitive(True)        
        combo = self.builder.get_object('cmb_results')
        combo.set_active(result.result_type)
        self.on_cmb_results_changed(combo)
        
        if (result.item):
            icon  = self.load_image(result.item.image_url, 32, 32)
            image = gtk.image_new_from_pixbuf(icon)
            self.builder.get_object('btn_result_item').set_image(image)
            self.builder.get_object('btn_result_item').set_label(result.item.name)
        elif (result.token):
            icon  = self.load_image(os.path.join('images','token.png'), 32, 32)
            image = gtk.image_new_from_pixbuf(icon)
            self.builder.get_object('btn_result_token').set_image(image)
            self.builder.get_object('btn_result_token').set_label(result.token.name)
        
            
    def on_cmb_results_changed(self, combo):
        self.clear_result_properties()
        
        t = combo.get_active()
        self.result.result_type = t
        if (t == rpyg_utils.RESULT_ADD_TOKEN or t == rpyg_utils.RESULT_REMOVE_TOKEN):
            self.builder.get_object('lbl_select_token').set_sensitive(True)
            self.builder.get_object('btn_result_token').set_sensitive(True)
        elif (t == rpyg_utils.RESULT_ADD_ITEM or t == rpyg_utils.RESULT_REMOVE_ITEM):
            self.builder.get_object('lbl_select_item').set_sensitive(True)
            self.builder.get_object('btn_result_item').set_sensitive(True)
            
            
            
        
        
    def init_iconview_conditions(self):
        #liststore
        iconview = self.builder.get_object('iconview_conditions')
        liststore = iconview.get_model()
        if (not liststore):
            # set basic properties
            iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

            # set columns
            iconview.set_text_column(1)
            iconview.set_pixbuf_column(0)

            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
            
            self.conditions_handler = iconview.connect('button-release-event', self.on_icon_conditions_clicked)
            
        else:
            liststore.clear()

        ignore = True #Ignore the first element
        for o in self.liststore_tokens:
            if (ignore):
                ignore = False
            else:
                liststore.append(o)

        iconview.set_model(liststore)
        
    def on_icon_conditions_clicked(self, iconview, event): 
        selected = iconview.get_selected_items()
        self.dialog.conditions = []
        if (len(selected) > 0):
            for s in selected:                
                pos = s[0]
                self.dialog.conditions.append(self.game.tokens[pos])
                
                
    def on_btn_result_item_clicked(self, button):
        self.show_window_select(self.liststore_items, self.on_btn_result_item_clicked_ok, self.on_btn_result_item_clicked_cancel)
        
    def on_btn_result_item_clicked_cancel(self, button):
        pass
    
    def on_btn_result_item_clicked_ok(self, button):
        iconview = self.builder.get_object('iconview_select')
        selected = iconview.get_selected_items()
        if len(selected)==1:
            pos = selected[0][0]
            self.result.item = self.game.items[pos]
            self.result.token = None
            #Change button image and text
            icon  = self.load_image(self.result.item.image_url, 32, 32)
            image = gtk.image_new_from_pixbuf(icon)
            self.builder.get_object('btn_result_item').set_image(image)
            self.builder.get_object('btn_result_item').set_label(self.result.item.name)
        
        
    def on_btn_result_token_clicked(self, button):
        self.show_window_select(self.liststore_tokens, self.on_btn_result_token_clicked_ok, self.on_btn_result_token_clicked_cancel)
        
    def on_btn_result_token_clicked_ok(self, button):
        iconview = self.builder.get_object('iconview_select')
        selected = iconview.get_selected_items()
        if len(selected)==1:
            pos = selected[0][0]
            self.result.token = self.game.tokens[pos]
            self.result.item = None
            #Change button image and text
            icon  = self.load_image(os.path.join('images','token.png'), 32, 32)
            image = gtk.image_new_from_pixbuf(icon)
            self.builder.get_object('btn_result_token').set_image(image)
            self.builder.get_object('btn_result_token').set_label(self.result.token.name)

            
        
    
    def on_btn_result_token_clicked_cancel(self, button):
        pass
        
        
    def on_btn_add_token_clicked(self, button):
        name = "token "+str(len(self.game.tokens)+1)
        token = self.game.add_token(name)
        liststore_icon = self.create_token_icon(token)
        self.builder.get_object('iconview_conditions').get_model().append(liststore_icon)
                

#~ 
        #~ - load a pixbuf with the image from a file using
#~ gtk.gdk.pixbuf_new_from_file()
#~ - create a pixmap of the same size using gtk.gdk.Pixmap() or
#~ gtk.gdk.Pixbuf.render_pixmap_and_mask()
#~ - draw the pixbuf image on the pixmap using
#~ gtk.gdk.Drawable.draw_pixbuf() (not needed if render_pixmap_and_mask was
#~ used)
#~ - draw your text, lines, etc. in the pixmap using either the cairo or
#~ gtk methods
#~ - transfer the pixmap to the pixbuf using gtk.gdk.Pixbuf.get_from_drawable()
#~ - write out the image using gtk.gdk.Pixbuf.save()



    ####################
    # Selects window
    ####################
    
    
    def show_window_select(self, liststore_copy, ok_callback, cancel_callback):
        iconview = self.builder.get_object('iconview_select')
        #liststore
        liststore = iconview.get_model()
        if (not liststore):
            # set basic properties

            iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

            # set columns
            iconview.set_text_column(1)
            iconview.set_pixbuf_column(0)

            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        else:
            liststore.clear()

        ignore = True #Ignore the first element
        for o in liststore_copy:
            if (ignore):
                ignore = False
            else:
                liststore.append(o)

        iconview.set_model(liststore)

        self.select_window_cancel_callback = cancel_callback
        self.select_window_ok_callback = ok_callback

        self.builder.get_object('win_select').set_visible(True)
        
        
        
        
    
    
    def on_btn_select_cancel_clicked(self, button):
        self.select_window_cancel_callback(button)
        self.select_window_ok_callback = None
        self.select_window_cancel_callback = None
        self.builder.get_object('win_select').set_visible(False)

    def on_btn_select_ok_clicked(self, button):
        self.select_window_ok_callback(button)
        self.select_window_ok_callback = None
        self.select_window_cancel_callback = None
        self.builder.get_object('win_select').set_visible(False)






    ##########################
    # Generals
    ##########################


    def exit_rpyg(self,window):
        exit()


    def clear_store(self, store):
        ignore = True
        for row in store:
            if (ignore):
                ignore = False
            else:
                store.remove(row.iter)

    def clear_current(self):
        if self.liststore_screens:
            self.clear_store(self.liststore_screens)
        if self.liststore_npcs:
            self.clear_store(self.liststore_npcs)
        if self.liststore_exits:
            self.clear_store(self.liststore_exits)

        self.builder.get_object('screen_box').set_sensitive(False)
        self.builder.get_object('screen_properties').set_sensitive(False)
        
        self.screen = None
        self.npc = None
        self.s_exit = None
        self.token = None
        self.item = None
        self.dialog = None
        self.phrase = None




    def open_game(self,button):
        self.clear_current()
        filename = self.open_file('*.rpyg')
        if (filename):
            self.open_game_file(filename)
            
    def open_game_file(self, filename):
        self.game_filename = filename
        game = rpyg_utils.open_game(filename)
        if (game):
            self.game = game[0]
            tempDir = game[1]

            self.load_screens()
            self.load_tokens()
            self.load_items()

            self.win_rpyg.set_title("RPyG Designer: "+str(os.path.basename(filename)))
            self.builder.get_object('main_area').set_sensitive(True)
        else:
            self.builder.get_object('main_area').set_sensitive(False)
            self.show_error("Error on load file")

    def load_screens(self):
        for screen in self.game.screens:
            screen_icon  = self.load_image(screen.map_file, 144, 90)
            self.liststore_screens.append([screen_icon, screen.name])

    def save_game_as(self,button):
        self.game_filename = self.save_file('*.rpyg')
        if (self.game_filename):
            if (not self.game_filename.endswith('.rpyg')):
                self.game_filename+='.rpyg'
            self.save_game(None)

    def save_game(self,button):
        #~ if (self.screen):
            #~ self.save_screen()
            #~ self.save_protagonist()
            #~ if (self.item):
                #~ self.save_item()
            #~ if (self.npc):
                #~ self.save_npc()

        if (self.game_filename):
            #Create temp dir
            tempDir = tempfile.mkdtemp(prefix = 'RPyG')


            resourcesDir = os.path.join(tempDir, "resources")
            if (not os.path.exists(resourcesDir)):
                os.makedirs(resourcesDir)

            #Copy all files
            num = 1
            for screen in self.game.screens:
                file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                num += 1
                shutil.copy2(screen.map_file, file_name)
                screen.map_file = file_name

                if screen.music_file:
                    file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                    num += 1
                    shutil.copy2(screen.music_file, file_name)
                    screen.music_file = file_name

                file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                num += 1
                shutil.copy2(screen.protagonist.img_file, file_name)
                screen.protagonist.img_file = file_name

                file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                num += 1
                shutil.copy2(screen.protagonist.img_dialog, file_name)
                screen.protagonist.img_dialog = file_name

                for npc in screen.npcs:
                    file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                    num += 1
                    shutil.copy2(npc.img_file, file_name)
                    npc.img_file = file_name

                    file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                    num += 1
                    shutil.copy2(npc.img_dialog, file_name)
                    npc.img_dialog = file_name

            for item in self.game.items:
                file_name = os.path.join(resourcesDir, 'img_'+str(num)+'.png')
                num += 1
                shutil.copy2(item.image_url, file_name)
                item.image_url = file_name



            gameFile = os.path.join(tempDir, "game")
            fileObj = open(gameFile,"w")
            pickle.dump(self.game,fileObj)
            fileObj.close()


            #Add to zip
            zfilename = self.game_filename
            zout = zipfile.ZipFile(zfilename, "w")
            zout.write(gameFile, "game")
            zout.write(resourcesDir, "resources")

            for entity in os.listdir(resourcesDir):
                f = os.path.join(resourcesDir,entity)
                name = os.path.join("resources", entity)
                zout.write(f, name)


            zout.close()

            self.win_rpyg.set_title("RPyG Designer: "+str(os.path.basename(self.game_filename)))

        else:
            self.save_game_as(None)


    def on_save_as_clicked(self,button):
        self.game_filename=self.save_dialog.get_filename()
        if (not self.game_filename.endswith('.rpyg')):
            self.game_filename+='.rpyg'
        self.win_rpyg.set_title("RPyG Designer: "+str(os.path.basename(self.game_filename)))
        self.save_game(None)
        self.builder.get_object('main_area').set_sensitive(True)



    def screen_name_change(self, field):
        if (field.get_text()):
            self.screen.name = field.get_text()
            selected = self.builder.get_object('iconview_maps').get_selected_items()
            if (len(selected) == 1):
                pos = selected[0][0]
                self.liststore_screens[pos][1]=self.screen.name


    def prot_name_change(self, field):
        if (field.get_text()):
            self.screen.protagonist.name = field.get_text()

    def npc_name_change(self, field):
        if (field.get_text()):            
            selected = self.builder.get_object('iconview_npcs').get_selected_items()
            if (len(selected) == 1):
                self.npc.name = field.get_text()
                pos = selected[0][0]
                self.liststore_npcs[pos][1]=self.npc.name

    def exit_name_change(self, field):
        if (field.get_text()):            
            selected = self.builder.get_object('iconview_exits').get_selected_items()
            if (len(selected) == 1):
                self.s_exit.name = field.get_text()
                pos = selected[0][0]
                self.liststore_exits[pos][1]=self.s_exit.name
                
    def on_token_name_changed(self, field):
        name = field.get_text()
        if (name):                        
            selected = self.builder.get_object('iconview_tokens').get_selected_items()
            if (len(selected) == 1):
                self.token.name = name
                pos = selected[0][0]
                self.liststore_tokens[pos][1]=name
                
    def on_item_name_changed(self, field):
        name = field.get_text()
        if (name):                        
            selected = self.builder.get_object('iconview_items').get_selected_items()
            if (len(selected) == 1):
                self.item.name = name
                pos = selected[0][0]
                self.liststore_items[pos][1]=name
                
    def on_dialog_name_changed(self, field):
        name = field.get_text()
        if (name):                        
            selected = self.builder.get_object('iconview_dialogs').get_selected_items()
            if (len(selected) == 1):
                self.dialog.name = name
                pos = selected[0][0]
                self.liststore_dialogs[pos][1]=name
                

    def screen_music_select(self, button):
        filename = self.open_file ("*.ogg *.mp3")
        if (filename):
            self.screen.music_file = filename
            self.builder.get_object('txt_screen_music').set_text(str(os.path.basename(self.screen.music_file)))

    ############ Maps & Music

    def on_map_screen_clicked(self,screenmap,event):
        if event.button==1:
            x=int(math.floor(event.x/16))
            y=int(math.floor(event.y/16))
            self.screen.update_path(x,y)
            screenmap.repaint()
        elif event.button==3:
            for y in range(48):
                for x in range(64):
                    self.screen.update_path(x,y)
            screenmap.repaint()

    def on_btn_edit_paths_clicked(self, button):
        filepath=self.screen.map_file
        if (filepath):
            drawing_area = gtk.DrawingArea()
            map_screen = MapScreen(filepath,self.screen)
            map_screen.show()
            map_screen.connect("button_press_event", self.on_map_screen_clicked)
            map_screen.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            win_map = self.builder.get_object('win_map')

            win_map.add(map_screen)
            win_map.set_size_request(1024, 768)
            win_map.set_visible(True)


    ##############
    #  Utils
    ##############


    def show_error(self, text):
        md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, text)
        md.run()
        md.destroy()
        
    def show_confirm(self, text):
        md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
            gtk.BUTTONS_YES_NO, text)
        response = md.run()
        md.destroy()
        return response == gtk.RESPONSE_YES

    def closeMessage(self, text):
        self.builder.get_object('dlgMessage').set_visible(False)

    def load_map_image(self, file_name):
        scaled_buf = self.load_image(file_name, 400, 250)
        self.builder.get_object('img_map').set_from_pixbuf(scaled_buf)

    def load_image(self, file_name, width=-1, height=-1):
        pixbuf = gtk.gdk.pixbuf_new_from_file(file_name)
        if (width != -1):
            if (height == -1):
                #calc height
                height = pixbuf.get_height() * width / pixbuf.get_width()
            scaled_buf = pixbuf.scale_simple(width,height,gtk.gdk.INTERP_BILINEAR)
            return scaled_buf
        else:
            return pixbuf



    def open_file(self, pattern):
        dialog = gtk.FileChooserDialog(title="RPyG: Open File",action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name(pattern)
        for p in pattern.split():
            filter.add_pattern(p)
        dialog.add_filter(filter)
        response = dialog.run()
        file_name = None
        if response == gtk.RESPONSE_OK:
            file_name = dialog.get_filename()
        dialog.destroy()
        return file_name

    def save_file(self, pattern):
        dialog = gtk.FileChooserDialog(title="RPyG: Save File",action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name(pattern)
        filter.add_pattern(pattern)

        dialog.add_filter(filter)
        response = dialog.run()
        file_name = None
        if response == gtk.RESPONSE_OK:
            file_name = dialog.get_filename()
        dialog.destroy()
        return file_name

    def debug(self, a):
        print "self.screen.protagonist.max_cols: "+str(self.screen.protagonist.max_cols)


game_file = None
if len(sys.argv)>1:
    game_file=sys.argv[1]

app = RPYG_Designer(game_file)
gtk.main()
