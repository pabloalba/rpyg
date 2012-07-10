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


        #~ self.item=None
        #~ self.npc=None
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

        icon  = self.load_image("./images/pos_map.png", 16, 16)
        image = gtk.image_new_from_pixbuf(icon)
        self.builder.get_object('btn_prot_map').set_image(image)




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
        self.screen = self.game.screens[pos]
        self.load_map_image(self.screen.map_file)
        self.builder.get_object('screen_box').set_sensitive(True)
        self.builder.get_object('screen_properties').set_sensitive(True)
        self.builder.get_object('txt_screen_name').set_text(self.screen.name)
        self.builder.get_object('txt_screen_music').set_text(str(os.path.basename(self.screen.music_file)))


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

    def btn_prot_image_dialogs_clicked(self, button):
        filename = self.open_file('*.png')
        if (filename):
            self.screen.protagonist.img_file = filename
            icon  = self.load_image(filename, 90)
            image = gtk.image_new_from_pixbuf(icon)
            button.set_image(image)



    def btn_prot_image_chara_clicked(self, button):
        filename = self.open_file('*.png')
        if (filename):

            pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
            #Get size
            width = pixbuf.get_width()
            height = pixbuf.get_height()
            self.screen.protagonist.max_rows = width / 32
            self.screen.protagonist.max_cols = height / 48


            self.screen.protagonist.img_dialog = filename

            image = gtk.image_new_from_pixbuf(pixbuf.subpixbuf(0, 0, 32, 48))
            button.set_image(image)



    def btn_prot_map_clicked(self, button):
        filepath=self.screen.map_file
        if (filepath):
            drawing_area = gtk.DrawingArea()
            map_screen = MapScreen(filepath,self.screen)
            map_screen.show()
            map_screen.connect("button_press_event", self.on_prot_map_clicked)
            map_screen.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            win_map = self.builder.get_object('win_map')

            try:
                x = int(self.builder.get_object('prot_x').get_text())
                y = int(self.builder.get_object('prot_y').get_text())

                map_screen.mark_x = x
                map_screen.mark_y = y
            except:
                pass

            win_map.add(map_screen)
            win_map.set_size_request(1024, 768)
            win_map.set_visible(True)

    def on_prot_map_clicked(self,screenmap,event):
        if event.button==1:
            x=int(math.floor(event.x/32))
            y=int(math.floor(event.y/32))
            self.builder.get_object('prot_x').set_text(str(x))
            self.builder.get_object('prot_y').set_text(str(y))
            self.builder.get_object('win_map').destroy()
            pos = [x, y]
            self.screen.protagonist.pos = pos

    def update_prot_coordinates(self, fiels):
        try:
            x = int(self.builder.get_object('prot_x').get_text())
            y = int(self.builder.get_object('prot_y').get_text())
            pos = [x, y]
            self.screen.protagonist.pos = pos
        except:
            pass



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



    def screen_name_change(self, field):
        self.screen.name = field.get_text()

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



app = RPYG_Designer()
gtk.main()
