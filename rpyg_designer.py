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



        #Marked Path
        cr.set_source_rgba(0, 0, 1, 0.5)
        for x in range(64):
            for y in range(48):
                if self.screen.valid_path[y][x]==1:
                    cr.rectangle(x*16, y*16, 16, 16)
                    cr.fill()

        #mark
        if (self.mark_x > -1) and (self.mark_y > -1):
            cr.set_source_rgba(1, 1, 0, 0.5)
            cr.rectangle(self.mark_x*32, self.mark_y*32, 32, 32)
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


        self.npc = None
        self.s_exit = None

        #~ self.item=None

        #~ self.dialog=None

        self.win_rpyg.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("lightgray"))

        self.builder.get_object('box_prot_title').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('label_prot').modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#ffffff'))
        self.builder.get_object('box_prot').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#A0A0A0"))

        self.builder.get_object('box_npcs_title').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('label_npcs').modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#ffffff'))
        self.builder.get_object('box_npcs').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#A0A0A0"))

        self.builder.get_object('box_exits_title').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color('#606060'))
        self.builder.get_object('label_exits').modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color('#ffffff'))
        self.builder.get_object('box_exits').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#A0A0A0"))






        self.builder.get_object('box_npcs').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('box_exits').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('main_area').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('other_properties').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))
        self.builder.get_object('viewport2').modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#D3D3D3"))

        icon  = self.load_image(os.path.join('images','pos_map.png'), 16, 16)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_prot_map').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_npc_map').set_image(image)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_exit_map').set_image(image)

        icon  = self.load_image(os.path.join('images','dialogs.png'), 90)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_npc_dialogs').set_image(image)


        self.liststore_maps = None
        self.liststore_npcs = None
        self.liststore_exits = None
        self.screen = None
        self.game = Game()
        self.init_iconview_maps()

    def init_iconview_maps(self):
        # set basic properties
        iconview = self.builder.get_object('iconview_maps')
        iconview.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        iconview.set_item_orientation(gtk.ORIENTATION_VERTICAL)

        # set columns
        iconview.set_text_column(1)
        iconview.set_pixbuf_column(0)


        # set liststore
        if (self.liststore_npcs):
            liststore = self.liststore_maps
            liststore.clear()
        else:
            liststore = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)


        #Add icon for 'add screen'
        add_icon = self.load_image("images/add_map.png", 144, 90)
        liststore.append([add_icon, "Add screen"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_maps = liststore

        #assign event
        iconview.connect('selection_changed', self.on_icon_map_clicked)

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



        #Add icon for 'add npc'
        add_icon = self.load_image("images/add_npc.png", 32, 48)
        liststore.append([add_icon, "Add npc"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_npcs = liststore

        #assign event
        iconview.connect('selection_changed', self.on_icon_npc_clicked)

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



        #Add icon for 'add exit'
        add_icon = self.load_image(os.path.join("images","add_exit.png"), 32, 32)
        liststore.append([add_icon, "Add exit"])

        #set liststore
        iconview.set_model(liststore)
        self.liststore_exits = liststore

        #assign event
        iconview.connect('selection_changed', self.on_icon_exit_clicked)

        self.win_rpyg.show_all()



    def on_icon_map_clicked(self, iconview):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, open add dialog
            if (pos == 0):
                self.open_map_dialog(None)
            else:
                self.load_screen(pos-1)

    def on_icon_npc_clicked(self, iconview):
        selected = iconview.get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            #if it is the first icon, open add dialog
            if (pos == 0):
                self.open_npc_dialog(None)
            else:
                self.npc = self.screen.npcs[pos-1]
                self.load_npc_properties(self.screen.npcs[pos-1])

    def on_icon_exit_clicked(self, iconview):
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
                pass

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


    def open_map_dialog(self,button):
        filename = self.open_file('*.png')
        if (filename):
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
            self.liststore_maps.append([screen_icon, screen_name])

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
            self.set_actor_chara(npc, filename)

            #Load and select npc
            pos = len(self.screen.npcs)
            self.npc = self.screen.npcs[pos-1]
            self.add_npc_icon(self.npc)
            self.load_npc_properties(self.npc)
            self.builder.get_object('iconview_npcs').select_path((pos,))
            self.builder.get_object('npc_area').set_sensitive(True)

    def load_exits(self):
        self.init_iconview_exits()


    def load_npcs(self):
        self.init_iconview_npcs()
        if (len(self.screen.npcs) == 0 ):
            self.builder.get_object('npc_name').set_text('')
            self.builder.get_object('npc_x').set_text('')
            self.builder.get_object('npc_y').set_text('')
            self.builder.get_object('npc_area').set_sensitive(False)
        else:
            self.builder.get_object('npc_area').set_sensitive(True)
            #Load npcs
            i = 0
            for npc in self.screen.npcs:
                self.add_npc_icon(npc)

            #Load and select npc
            pos = len(self.screen.npcs)
            self.npc = self.screen.npcs[pos-1]
            self.load_npc_properties(self.npc)
            self.builder.get_object('iconview_npcs').select_path((pos,))


    def add_npc_icon(self, npc):
        #Add npc icon
        pixbuf = gtk.gdk.pixbuf_new_from_file(npc.img_file)
        subpixbuf = pixbuf.subpixbuf(0, 0, 32, 48)
        self.liststore_npcs.append([subpixbuf, npc.name])
        self.win_rpyg.show_all()

    def load_npc_properties(self, npc):
        #Write npc properties
        self.builder.get_object('npc_name').set_text(npc.name)
        self.builder.get_object('npc_x').set_text(str(npc.pos[0]))
        self.builder.get_object('npc_y').set_text(str(npc.pos[1]))
        self.actor_load_image_dialog(self.builder.get_object('btn_npc_image_dialogs'), self.npc.img_dialog)

    def load_exit_properties(self, s_exit):
        #Write exit properties
        self.builder.get_object('exit_name').set_text(s_exit.name)
        self.builder.get_object('exit_x').set_text(str(s_exit.pos[0]))
        self.builder.get_object('exit_y').set_text(str(s_exit.pos[1]))


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
    # Actors
    ###################################################



    #Protagonist
    def btn_prot_image_dialogs_clicked(self, button):
        self.btn_image_dialogs_clicked(button, self.screen.protagonist)

    def btn_prot_image_chara_clicked(self, button):
        filename = self.open_file('*.png')
        self.set_actor_chara(self.screen.protagonist, filename)
        self.load_prot_chara(button, filename)

    def load_prot_chara(self, button, filename):
        if not filename:
            filename = os.path.join('images','default_dialog_img')
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        image = gtk.image_new_from_pixbuf(pixbuf.subpixbuf(0, 0, 32, 48))
        button.set_image(image)

    def btn_prot_map_clicked(self, button):
        self.btn_map_clicked(button, self.on_prot_map_clicked, self.screen.protagonist.pos[0], self.screen.protagonist.pos[1])


    def on_prot_map_clicked(self,screenmap,event):
        field_x = self.builder.get_object('prot_x')
        field_y = self.builder.get_object('prot_y')
        self.on_map_clicked(screenmap,event, self.screen.protagonist, field_x, field_y)

    def update_prot_coordinates(self, field):
        try:
            x = int(self.builder.get_object('prot_x').get_text())
            y = int(self.builder.get_object('prot_y').get_text())
            pos = [x, y]
            self.screen.protagonist.pos = pos
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
        self.on_map_clicked(screenmap, event, self.npc, field_x, field_y)

    def update_npc_coordinates(self, a, b):
        try:
            x = int(self.builder.get_object('npc_x').get_text())
            y = int(self.builder.get_object('npc_y').get_text())
            pos = [x, y]
            self.npc.pos = pos
        except:
            pass

    #exit
    def btn_exit_map_clicked(self, button):
        self.btn_map_clicked(button, self.on_exit_map_clicked, self.s_exit.pos[0], self.s_exit.pos[1])

    def on_exit_map_clicked(self,screenmap,event):
        field_x = self.builder.get_object('exit_x')
        field_y = self.builder.get_object('exit_y')
        self.on_map_clicked(screenmap,event, self.s_exit, field_x, field_y)


    #actors
    def set_actor_chara(self, actor, filename):
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        #Get size
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        actor.max_rows = width / 32
        actor.max_cols = height / 48
        actor.img_file = filename
        return pixbuf

    def btn_image_dialogs_clicked(self, button, actor):
        filename = self.open_file('*.png')
        self.actor_load_image_dialog(button, filename)
        actor.img_dialog = filename


    def actor_load_image_dialog(self, button, filename):
        if not filename:
            filename = os.path.join('images','default_dialog_img')
        icon  = self.load_image(filename, 90)
        image = gtk.image_new_from_pixbuf(icon)
        button.set_image(image)


    def btn_map_clicked(self, button, callback, x, y):
        filepath=self.screen.map_file
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

    def on_map_clicked(self, screenmap, event, actor, field_x, field_y):
        if event.button==1:
            x=int(math.floor(event.x/32))
            y=int(math.floor(event.y/32))
            field_x.set_text(str(x))
            field_y.set_text(str(y))
            self.builder.get_object('win_map').destroy()
            pos = [x, y]
            actor.pos = pos




    ##########################
    # Generals
    ##########################


    def exit_rpyg(self,window):
        exit()


    def clear_current():
        self.builder.get_object('screen_box').set_sensitive(False)
        self.builder.get_object('screen_properties').set_sensitive(False)

    def open_game(self,button):
        clear_current()
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



    def screen_name_change(self, field, event):
        self.screen.name = field.get_text()
        selected = self.builder.get_object('iconview_maps').get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            self.liststore_maps[pos][1]=self.screen.name


    def prot_name_change(self, field, event):
        self.screen.protagonist.name = field.get_text()

    def npc_name_change(self, field, event):
        self.npc.name = field.get_text()
        selected = self.builder.get_object('iconview_npcs').get_selected_items()
        if (len(selected) == 1):
            pos = selected[0][0]
            self.liststore_npcs[pos][1]=self.npc.name

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
        print "self.npc: "+str(self.npc)
        print "self.npc.img_dialog: "+str(self.npc.img_dialog)




app = RPYG_Designer()
gtk.main()
