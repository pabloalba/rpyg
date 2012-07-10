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
        self.game_dir=''

        self.win_rpyg=self.builder.get_object('win_rpyg')


        #~ self.win_add_screen = self.builder.get_object('win_add_screen')
        #~ self.win_add_token = self.builder.get_object('win_add_token')
        #~ self.win_add_item = self.builder.get_object('win_add_item')
        #~ self.win_add_npc = self.builder.get_object('win_add_npc')
        #~ self.win_dialog = self.builder.get_object('win_dialog')
        #~ self.win_map = self.builder.get_object('win_map')



        #~ self.datos_screen=self.builder.get_object('datos_screen')
        #~

        #~ self.item=None
        #~ self.npc=None
        #~ self.dialog=None



        self.liststore_maps = None
        self.screen = None
        self.game = Game()
        self.init_iconview()

    def init_iconview(self):


        # creo el iconview
        iconview = self.builder.get_object('iconview_maps')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # le indico qué columna del liststore tiene el texto, y cuál el icono
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)

        # pongo un scrolledwindow, para que quede más bonito
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)

        # defino los tipos a representar
        liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)



        add_icon = self.load_image("images/add_map.png", 144, 90)

        liststore.append([add_icon, "Add map"])

        iconview.set_model(liststore)
        self.liststore_maps = liststore

        iconview.connect('selection_changed', self.on_icon_map_clicked)


        #self.builder.get_object('maps_scroll').add(iconview)

        self.win_rpyg.show_all()

    def on_icon_map_clicked(self, iconview):
        self.win_rpyg.show_all()
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, open add dialog
            if (pos == 0):
                self.open_map_dialog(None)
            else:
                self.load_screen(pos-1)

    def load_screen(self, pos):
        screen = self.game.screens[pos]
        self.load_map_image("samples/forest/resources/maps/forest.png")

    def open_map_dialog(self,button):
        filename = self.open_file('*.png')
        if (filename):
            #Create new screen
            screen_name = str(os.path.basename(filename))
            self.game.add_screen(screen_name)
            screen_icon  = self.load_image(filename, 144, 90)
            self.liststore_maps.append([screen_icon, screen_name])
            self.win_rpyg.show_all()


    def exit_rpyg(self,window):
        exit()


    def open_game(self,button):
        filename = self.open_file('*.rpyg')
        if (filename):

            #Extract zip to temp dir
            tempDir = tempfile.mkdtemp(prefix = 'RPyG')
            zf = zipfile.ZipFile(filename)


            # extract files to directory structure
            for i, name in enumerate(zf.namelist()):
                if not name.endswith('/'):
                    outfile = open(os.path.join(tempDir, name), 'wb')
                    outfile.write(zf.read(name))
                    outfile.flush()
                    outfile.close()



            game_file = os.path.join(tempDir, "game")
            fileObj = open(game_file,"r")
            try:
                self.game=pickle.load(fileObj)

                #~ self.load_screens()
                #~ self.load_tokens()
                #~ self.load_items()
                self.game_filename=game_file
                self.game_dir=tempDir
                self.win_rpyg.set_title("RPyG Designer: "+str(os.path.basename(filename)))
                self.builder.get_object('main_area').set_sensitive(True)
            except:
                self.builder.get_object('main_area').set_sensitive(False)
                self.showMessage("Error on load file")


            fileObj.close()



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
            if (self.game_dir):
                tempDir = self.game_dir
            else:
                tempDir = tempfile.mkdtemp(prefix = 'RPyG')
                self.game_dir = tempDir
            gameFile = os.path.join(tempDir, "game")
            fileObj = open(gameFile,"w")
            pickle.dump(self.game,fileObj)
            fileObj.close()

            resourcesDir = os.path.join(tempDir, "resources")
            if (not os.path.exists(resourcesDir)):
                os.makedirs(resourcesDir)



            #Add to zip
            zfilename = self.game_filename
            zout = zipfile.ZipFile(zfilename, "w")
            zout.write(gameFile, "game")
            zout.write(resourcesDir, "resources")
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


    def showMessage(self, text):
        self.builder.get_object('lblMessage').set_text(text)
        self.builder.get_object('dlgMessage').set_visible(True)

    def closeMessage(self, text):
        self.builder.get_object('dlgMessage').set_visible(False)

    def load_map_image(self, file_name):
        scaled_buf = self.load_image(file_name, 400, 250)
        self.builder.get_object('img_map').set_from_pixbuf(scaled_buf)

    def load_image(self, file_name, width=-1, height=-1):
        pixbuf = gtk.gdk.pixbuf_new_from_file(file_name)
        if (width != -1):
            scaled_buf = pixbuf.scale_simple(width,height,gtk.gdk.INTERP_BILINEAR)
            return scaled_buf
        else:
            return pixbuf


    def open_file(self, pattern):
        dialog = gtk.FileChooserDialog(title="RPyG: Open File",action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
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



app = RPYG_Designer()
gtk.main()
