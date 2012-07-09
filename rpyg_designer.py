#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import pickle
from game import *
from gtk import *
import os, math
import gobject, cairo





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



    # Handle the expose-event by drawing
    def do_expose_event(self, event):

        # Create the cairo context
        cr = self.window.cairo_create()

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
    def __init__(self):

        filename = "rpyg_designer.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)

        self.game_filename=''
        
        self.win_rpyg=self.builder.get_object('win_rpyg')
        #~ self.win_add_screen = self.builder.get_object('win_add_screen')
        #~ self.win_add_token = self.builder.get_object('win_add_token')
        #~ self.win_add_item = self.builder.get_object('win_add_item')
        #~ self.win_add_npc = self.builder.get_object('win_add_npc')
        #~ self.win_dialog = self.builder.get_object('win_dialog')
        #~ self.win_map = self.builder.get_object('win_map')
        self.load_dialog=self.builder.get_object('load_dialog')
        self.save_dialog=self.builder.get_object('save_dialog')
        self.builder.get_object('filefilter').add_pattern("*.rpyg");
        self.builder.get_object('pngfilter').add_pattern("*.png");
        self.builder.get_object('oggfilter').add_pattern("*.ogg");
        
        
        #~ self.datos_screen=self.builder.get_object('datos_screen')
        #~ 
        #~ self.screen=None
        #~ self.item=None
        #~ self.npc=None
        #~ self.dialog=None
        self.game=Game()



    def exit_rpyg(self,window):
        exit()


    def open_file_dialog(self,button):
        self.load_dialog.set_visible(True)
        
    def open_file(self,dialog):
        self.load_dialog.set_visible(False)
        filename=self.load_dialog.get_filename()
        fileObj = open(filename,"r")
        self.game=pickle.load(fileObj)
        fileObj.close()
        #~ self.load_screens()
        #~ self.load_tokens()
        #~ self.load_items()
        self.game_filename=filename
        self.win_rpyg.set_title("RPyG: "+str(os.path.basename(filename)))
        self.builder.get_object('lblGameName').set_text(str(os.path.basename(filename)))
        
        

    def save_file_dialog(self,button):
        self.save_dialog.set_visible(True)
        
    def save_file(self,button):
        #~ if (self.screen):
            #~ self.save_screen()
            #~ self.save_protagonist()
            #~ if (self.item):
                #~ self.save_item()
            #~ if (self.npc):
                #~ self.save_npc()

        if (self.game_filename):
            fileObj = open(self.game_filename,"w")
            pickle.dump(self.game,fileObj)
            fileObj.close()
        else:
            self.save_file_dialog(None)
    

    def on_save_as_clicked(self,button):
        self.game_filename=self.save_dialog.get_filename()
        if (not self.game_filename.endswith('.rpyg')):
            self.game_filename+='.rpyg'
        self.win_rpyg.set_title("RPyG: "+str(os.path.basename(self.game_filename)))
        self.builder.get_object('lblGameName').set_text(str(os.path.basename(self.game_filename)))
        self.save_dialog.set_visible(False)
        self.save_file(None)

app = RPYG_Designer()
gtk.main()
