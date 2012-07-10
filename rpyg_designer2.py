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

        filename = "rpyg_main.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)

        self.game_filename=''
        self.win_rpyg=self.builder.get_object('win_rpyg')
        self.win_add_screen = self.builder.get_object('win_add_screen')
        self.win_add_token = self.builder.get_object('win_add_token')
        self.win_add_item = self.builder.get_object('win_add_item')
        self.win_add_npc = self.builder.get_object('win_add_npc')
        self.win_dialog = self.builder.get_object('win_dialog')
        self.win_map = self.builder.get_object('win_map')
        self.load_dialog=self.builder.get_object('load_dialog')
        self.save_dialog=self.builder.get_object('save_dialog')
        self.datos_screen=self.builder.get_object('datos_screen')
        self.builder.get_object('filefilter').add_pattern("*.rpyg");
        self.builder.get_object('pngfilter').add_pattern("*.png");
        self.builder.get_object('oggfilter').add_pattern("*.ogg");
        self.screen=None
        self.item=None
        self.npc=None
        self.dialog=None
        self.game=Game()



    def exit_rpyg(self,window):
        exit()




    def on_save_as_clicked(self,button):
        self.game_filename=self.save_dialog.get_filename()
        if (not self.game_filename.endswith('.rpyg')):
            self.game_filename+='.rpyg'
        self.save_dialog.set_visible(False)
        self.save_game(None)

    def save_game(self,button):

        if (self.screen):
            self.save_screen()
            self.save_protagonist()
            if (self.item):
                self.save_item()
            if (self.npc):
                self.save_npc()

        if (self.game_filename):
            fileObj = open(self.game_filename,"w")
            pickle.dump(self.game,fileObj)
            fileObj.close()
        else:
            self.save_file_dialog(None)

    def open_file_dialog(self,button):
        self.load_dialog.set_visible(True)

    def save_file_dialog(self,button):
        self.save_dialog.set_visible(True)

    def open_file(self,dialog):
        self.load_dialog.set_visible(False)
        filename=self.load_dialog.get_filename()
        fileObj = open(filename,"r")
        self.game=pickle.load(fileObj)
        fileObj.close()
        self.load_screens()
        self.load_tokens()
        self.load_items()
        self.game_filename=filename
        self.win_rpyg.set_title("RPyG: "+str(os.path.basename(filename)))


    ##########SCREENS


    def on_btn_add_screen_clicked(self, btn):
        self.win_add_screen.set_visible(True)

    def load_screens(self):
        self.screen=None
        list_screens=self.builder.get_object('list_screens')
        list_screens.clear()
        for screen in self.game.screens:
            list_screens.append([screen.name])

        self.load_items()
        self.load_tokens()
        self.load_npcs()

    def on_win_add_screen_cancel_clicked(self,button):
        entry_new_screen = self.builder.get_object('entry_new_screen')
        entry_new_screen.set_text('')
        self.win_add_screen.set_visible(False)

    def on_win_add_screen_ok_clicked(self,button):
        entry_new_screen = self.builder.get_object('entry_new_screen')
        new_screen=entry_new_screen.get_text()
        list_screens=self.builder.get_object('list_screens')
        self.game.add_screen(new_screen)
        list_screens.append([new_screen])
        self.on_win_add_screen_cancel_clicked(None)

    def on_btn_remove_screen_clicked(self,button):
        value=get_selected_value(self.builder.get_object('view_screens'))
        if (value):
            self.game.remove_screen(value)
            self.load_screens()
            self.datos_screen.set_sensitive(False)

    def on_view_screens_cursor_changed(self,view):

        if (self.screen):
            self.save_screen()
            self.save_protagonist()
            if (self.item):
                self.save_item()
                self.item=None

            if (self.npc):
                self.save_npc()
                self.npc=None


        value=get_selected_value(view)
        if (value):
            screen=self.game.get_screen(value)
            if (screen):
                self.screen=screen
                self.datos_screen.set_sensitive(True)
                #Load screen data
                self.load_screen()

                #Load protagonist data
                self.load_protagonist()

                #Load npcs
                self.load_npcs()

                #Load exits
                self.load_exits()

            else:
                self.datos_screen.set_sensitive(False)
        else:
            self.datos_screen.set_sensitive(False)

    def load_screen(self):
        set_filename(self.builder.get_object('screen_map'),self.screen.map_file)
        set_filename(self.builder.get_object('screen_music'),self.screen.music_file)

    def save_screen(self):
        if (self.screen):
            self.screen.map_file=self.builder.get_object('screen_map').get_filename()
            self.screen.music_file=self.builder.get_object('screen_music').get_filename()


    ############ TOKENS

    def on_btn_add_token_clicked(self,button):
        self.win_add_token.set_visible(True)

    def on_win_add_token_cancel_clicked(self,button):
        entry_new_token = self.builder.get_object('entry_new_token')
        entry_new_token.set_text('')
        self.win_add_token.set_visible(False)

    def on_win_add_token_ok_clicked(self,button):
        entry_new_token = self.builder.get_object('entry_new_token')
        new_token=entry_new_token.get_text()
        list_tokens=self.builder.get_object('list_tokens')
        self.game.add_token(new_token)
        list_tokens.append([new_token])
        self.on_win_add_token_cancel_clicked(None)

    def on_btn_remove_token_clicked(self,button):
        value=get_selected_value(self.builder.get_object('view_tokens'))
        if (value):
            self.game.remove_token(value)
            self.load_tokens()

    def load_tokens(self):
        list_tokens=self.builder.get_object('list_tokens')
        list_tokens.clear()
        for token in self.game.tokens:
            list_tokens.append([token])

    ############ ITEMS

    def on_btn_add_item_clicked(self,button):
        self.win_add_item.set_visible(True)

    def on_win_add_item_cancel_clicked(self,button):
        entry_new_item = self.builder.get_object('entry_new_item')
        entry_new_item.set_text('')
        self.win_add_item.set_visible(False)

    def on_win_add_item_ok_clicked(self,button):
        entry_new_item = self.builder.get_object('entry_new_item')
        new_item_name=entry_new_item.get_text()
        list_items=self.builder.get_object('list_items')
        self.game.add_item(new_item_name)
        list_items.append([new_item_name])
        self.on_win_add_item_cancel_clicked(None)

    def on_btn_remove_item_clicked(self,button):
        value=get_selected_value(self.builder.get_object('view_items'))
        if (value):
            self.game.remove_item(value)
            self.load_items()
            self.clean_table_item()
            self.item=None

    def load_items(self):
        list_items=self.builder.get_object('list_items')
        list_items.clear()
        for item in self.game.items:
            list_items.append([item.name])
        self.clean_table_item()


    def on_view_items_cursor_changed(self,tree):
        if (self.item):
            self.save_item()
        value=get_selected_value(tree)
        if (value):
            self.item=self.game.get_item(value)
            if (self.item):
                self.builder.get_object('item_text').set_text(self.item.text)
                set_filename(self.builder.get_object('item_image_url'),self.item.image_url)
                self.load_combinations()
                self.builder.get_object('table_item').set_sensitive(True)

            else:
                 self.clean_table_item()

        else:
            self.item=None
            self.clean_table_item()

    def save_item(self):
        if (self.item):
            self.item.text=self.builder.get_object('item_text').get_text()
            self.item.image_url=self.builder.get_object('item_image_url').get_filename()

    def clean_table_item(self):
        self.builder.get_object('item_text').set_text('')
        self.builder.get_object('item_image_url').set_filename('')
        self.builder.get_object('item_image_url').set_current_folder('')
        self.builder.get_object('table_item').set_sensitive(False)




    ## Combinations (Items)
    #~ cmb_combine_item
    #~ cmb_result_ite
    #~ tree_combination_result
    #~ list_combination_result
    #~ win_add_combination


    def on_win_add_combination_cancel_clicked(self,button):
        self.builder.get_object('win_add_combination').set_visible(False)
        self.builder.get_object('cmb_combine_item').set_active(-1)
        self.builder.get_object('cmb_result_ite').set_active(-1)
        self.builder.get_object('list_combination_result').clear()

    def on_win_add_combination_ok_clicked(self,button):
        if (self.item):
            combine_item=get_active_value(self.builder.get_object('cmb_combine_item'))
            list=get_list_values(self.builder.get_object('list_combination_result'))

            remove_token=get_active_value(self.builder.get_object('cmb_comb_remove_token'))
            add_token=get_active_value(self.builder.get_object('cmb_comb_add_token'))


            self.item.add_combination(combine_item,list, add_token, remove_token)
            self.builder.get_object('list_combinations').append([combine_item,str(list)])

        self.on_win_add_combination_cancel_clicked(None)

    def on_cmb_result_item_changed(self,button):
        value=get_active_value(self.builder.get_object('cmb_result_ite'))
        if (value):
            self.builder.get_object('list_combination_result').append([value])
            self.builder.get_object('cmb_result_ite').set_active(-1)

    def on_btn_add_combination_clicked(self,button):
         self.builder.get_object('win_add_combination').set_visible(True)

    def on_btn_remove_combination_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_combinations'))
        if (value):
            self.item.remove_combination(value)
            self.load_combinations()

    def load_combinations(self):
        list_combinations=self.builder.get_object('list_combinations')
        list_combinations.clear()
        if (self.item):
            for c in self.item.combinations:
                list_combinations.append([c,str(self.item.combinations[c])])



    ############ NPC

    def on_btn_add_npc_clicked(self,button):
        self.win_add_npc.set_visible(True)

    def on_win_add_npc_cancel_clicked(self,button):
        entry_new_npc = self.builder.get_object('entry_new_npc')
        entry_new_npc.set_text('')
        self.win_add_npc.set_visible(False)

    def on_win_add_npc_ok_clicked(self,button):
        entry_new_npc = self.builder.get_object('entry_new_npc')
        new_npc_name=entry_new_npc.get_text()
        list_npcs=self.builder.get_object('list_npcs')
        self.screen.add_npc(new_npc_name)
        list_npcs.append([new_npc_name])
        self.on_win_add_npc_cancel_clicked(None)

    def on_btn_remove_npc_clicked(self,button):
        value=get_selected_value(self.builder.get_object('view_npcs'))
        if (value):
            self.screen.remove_npc(value)
            self.load_npcs()
            self.npc=None
        self.clean_table_npc()

    def load_npcs(self):
        list_npcs=self.builder.get_object('list_npcs')
        list_npcs.clear()
        if (self.screen):
            for npc in self.screen.npcs:
                list_npcs.append([npc.name])
        self.clean_table_npc()

    def on_view_npcs_cursor_changed(self,tree):
        if (self.npc):
            self.save_npc()
        if (self.screen):
            value=get_selected_value(tree)
            if (value):
                self.npc=self.screen.get_npc(value)
                if (self.npc):
                    if (self.npc.pos):
                        self.builder.get_object('npc_posx').set_text(str(self.npc.pos[0]))
                        self.builder.get_object('npc_posy').set_text(str(self.npc.pos[1]))
                    else:
                        self.builder.get_object('npc_posx').set_text('')
                        self.builder.get_object('npc_posy').set_text('')
                    self.builder.get_object('npc_max_rows').set_text(str(self.npc.max_rows))
                    self.builder.get_object('npc_max_cols').set_text(str(self.npc.max_cols))
                    set_filename(self.builder.get_object('npc_image_dialog'),self.npc.img_dialog)
                    set_filename(self.builder.get_object('npc_image_file'),self.npc.img_file)
                    self.builder.get_object('table_npc').set_sensitive(True)
                    self.load_dialogs()
                else:
                    self.clean_table_npc()
            else:
                self.clean_table_npc()



    def save_npc(self):
        if (self.npc):
            pos=[int(self.builder.get_object('npc_posx').get_text()),int(self.builder.get_object('npc_posy').get_text())]
            self.npc.pos=pos
            self.npc.img_file=self.builder.get_object('npc_image_file').get_filename()
            self.npc.img_dialog=self.builder.get_object('npc_image_dialog').get_filename()
            self.npc.max_rows=int(self.builder.get_object('npc_max_rows').get_text())
            self.npc.max_cols=int(self.builder.get_object('npc_max_cols').get_text())

    def clean_table_npc(self):
        self.builder.get_object('npc_posx').set_text('')
        self.builder.get_object('npc_posy').set_text('')
        self.builder.get_object('npc_max_rows').set_text('')
        self.builder.get_object('npc_max_cols').set_text('')
        self.builder.get_object('npc_image_file').set_filename('')
        self.builder.get_object('npc_image_file').set_current_folder('')
        self.builder.get_object('npc_image_dialog').set_filename('')
        self.builder.get_object('npc_image_dialog').set_current_folder('')
        self.builder.get_object('table_npc').set_sensitive(False)

    #### PROTAGONIST
    def save_protagonist(self):
        if (self.screen):
            prot=self.screen.protagonist
            prot.name=self.builder.get_object('prot_name').get_text()
            prot.pos=[int(self.builder.get_object('prot_posx').get_text()),int(self.builder.get_object('prot_posy').get_text())]
            prot.img_file=self.builder.get_object('prot_image_file').get_filename()
            prot.img_dialog=self.builder.get_object('prot_image_dialog').get_filename()
            prot.max_rows=int(self.builder.get_object('prot_max_rows').get_text())
            prot.max_cols=int(self.builder.get_object('prot_max_cols').get_text())


    def load_protagonist(self):
        if (self.screen):
            prot=self.screen.protagonist
            self.builder.get_object('prot_name').set_text(prot.name)
            self.builder.get_object('prot_posx').set_text(str(prot.pos[0]))
            self.builder.get_object('prot_posy').set_text(str(prot.pos[1]))
            set_filename(self.builder.get_object('prot_image_file'),prot.img_file)
            set_filename(self.builder.get_object('prot_image_dialog'),prot.img_dialog)
            self.builder.get_object('prot_max_rows').set_text(str(prot.max_rows))
            self.builder.get_object('prot_max_cols').set_text(str(prot.max_cols))







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

    def on_btn_edit_map_clicked(self, button):
        filepath=self.builder.get_object('screen_map').get_filename()
        if (filepath):
            drawing_area = gtk.DrawingArea()
            map_screen = MapScreen(filepath,self.screen)
            map_screen.show()
            map_screen.connect("button_press_event", self.on_map_screen_clicked)
            map_screen.set_events(gtk.gdk.BUTTON_PRESS_MASK)

            self.win_map.add(map_screen)
            self.win_map.set_size_request(1024, 768)
            self.win_map.set_visible(True)

    def on_btn_remove_music_clicked(self,button):
        set_filename(self.builder.get_object('screen_music'),'')


    ############# Dialogs

    def on_btn_dialogs_clicked(self,button):
        self.win_dialog.set_visible(True)

    def on_btn_close_dialogs_clicked(self,button):
        self.win_dialog.set_visible(False)

    def on_btn_add_dialog_clicked(self,button):
        self.builder.get_object('win_add_dialog').set_visible(True)

    def on_win_add_dialog_cancel_clicked(self,button):
        self.builder.get_object('win_add_dialog').set_visible(False)

    def on_win_add_dialog_ok_clicked(self,button):
        list_dialogs=self.builder.get_object('list_dialogs')
        entry_new_dialog=self.builder.get_object('entry_new_dialog')
        name=entry_new_dialog.get_text()
        list_dialogs.append([name])
        self.npc.add_dialog(name)
        self.builder.get_object('win_add_dialog').set_visible(False)
        entry_new_dialog.set_text('')



    def on_tree_dialog_cursor_changed(self,tree):
        #~ if (self.dialog):
            #~ self.save_npc_dialog()
        if (self.npc):
            value=get_selected_value(tree)
            if (value):
                self.dialog=self.npc.get_dialog(value)
                if (self.dialog):
                    self.load_phrases()
                    self.load_conditions()
                    self.load_results()
                    self.builder.get_object('phrases').set_sensitive(True)
                    self.builder.get_object('dialog_info').set_sensitive(True)


    def on_btn_remove_dialog_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_dialog'))
        if (value):
            self.npc.remove_dialog(self.dialog)
            self.load_dialogs()

    def load_dialogs(self):
        self.dialog=None
        self.builder.get_object('phrases').set_sensitive(False)
        self.builder.get_object('dialog_info').set_sensitive(False)
        self.builder.get_object('win_add_dialog').set_visible(False)

        list_dialogs=self.builder.get_object('list_dialogs')
        list_dialogs.clear()
        if (self.npc):
            for dialog in self.npc.dialogs:
                list_dialogs.append([dialog.name])

        self.clean_table_dialog()

    def clean_table_dialog(self):
        list_phrases=self.builder.get_object('list_phrases')
        list_phrases.clear()
        list_condition=self.builder.get_object('list_condition')
        list_condition.clear()
        list_result=self.builder.get_object('list_result')
        list_result.clear()


    def on_btn_add_phrase_clicked(self,button):
        self.builder.get_object('win_phrase').set_visible(True)

    def on_btn_remove_phrase_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_phrase'))
        if (value):
            self.dialog.remove_phrase(value)
            self.load_phrases()


    def on_btn_edit_phrase_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_phrase'))
        if (value):
            self.builder.get_object('entry_phrase_edit').set_text(value)
            self.builder.get_object('win_edit_phrase').set_visible(True)



    def on_win_edit_phrase_ok_clicked(self,button):
        old_value=get_selected_value(self.builder.get_object('tree_phrase'))
        value=self.builder.get_object('entry_phrase_edit').get_text()
        for dialog in self.dialog.phrases:
            if dialog.text == old_value:
                dialog.text=value
        self.builder.get_object('win_edit_phrase').set_visible(False)
        self.builder.get_object('entry_phrase_edit').set_text('')
        self.load_phrases()


    def on_win_edit_phrase_cancel_clicked(self,button):
        self.builder.get_object('win_edit_phrase').set_visible(False)
        self.builder.get_object('entry_phrase_edit').set_text('')

    def on_win_add_phrase_ok_clicked(self,button):
        if (self.dialog):
            entry_phrase=self.builder.get_object('entry_phrase')
            text=entry_phrase.get_text()
            chk_by_npc=self.builder.get_object('chk_by_npc')
            by_npc=chk_by_npc.get_active()
            self.dialog.add_phrase(text,by_npc)
            list_phrases=self.builder.get_object('list_phrases')
            list_phrases.append([text,by_npc])
            self.builder.get_object('win_phrase').set_visible(False)
            entry_phrase.set_text('')
            chk_by_npc.set_active(False)


    def on_win_add_phrase_cancel_clicked(self,button):
        self.builder.get_object('win_phrase').set_visible(False)



    def load_phrases(self):
        list_phrases=self.builder.get_object('list_phrases')
        list_phrases.clear()
        if (self.dialog):
            for phrase in self.dialog.phrases:
                list_phrases.append([phrase.text,phrase.by_npc])


    def on_cmb_condition_changed(self,cmb):
        if (self.dialog):
            value=get_active_value(cmb)
            self.dialog.add_condition(value)
            list_condition=self.builder.get_object('list_condition')
            list_condition.append([value])

    def load_conditions(self):
        list_condition=self.builder.get_object('list_condition')
        list_condition.clear()
        if (self.dialog):
            for condition in self.dialog.conditions:
                list_condition.append([condition])

    def on_btn_remove_condition_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_condition'))
        if (value):
            self.dialog.remove_condition(value)
            self.load_conditions()

    def on_btn_add_result_clicked(self,button):
        self.builder.get_object('win_add_result').set_visible(True)

    def on_win_add_result_ok_clicked(self,button):
        if self.dialog:
            name=self.builder.get_object('entry_result_name').get_text()
            result_type=get_active_value(self.builder.get_object('cmb_result_type'))
            item=get_active_value(self.builder.get_object('cmb_result_item'))
            token=get_active_value(self.builder.get_object('cmb_result_token'))
            x=self.builder.get_object('result_pos_x').get_text()
            y=self.builder.get_object('result_pos_y').get_text()

            result=Result(name,result_type)
            if (result_type=='RESULT_ADD_TOKEN'):
                result.set_token(token)
            elif (result_type=='RESULT_REMOVE_TOKEN'):
                result.set_token(token)
            elif (result_type=='RESULT_ADD_ITEM'):
                result.set_item(item)
            elif (result_type=='RESULT_REMOVE_ITEM'):
                result.set_item(item)
            elif (result_type=='RESULT_MOVE_NPC'):
                result.set_pos([x,y])

            self.dialog.add_result(result)

            list_result=self.builder.get_object('list_result')
            list_result.append([name,result_type,token,item,str([x,y])])

        self.on_win_add_result_cancel_clicked(None)

    def on_win_add_result_cancel_clicked(self,button):
        self.builder.get_object('win_add_result').set_visible(False)
        self.builder.get_object('entry_result_name').set_text('')
        self.builder.get_object('cmb_result_type').set_active(-1)
        self.builder.get_object('cmb_result_ite').set_active(-1)
        self.builder.get_object('cmb_result_token').set_active(-1)
        self.builder.get_object('result_pos_x').set_text('')
        self.builder.get_object('result_pos_y').set_text('')

    def load_results(self):
        list_result=self.builder.get_object('list_result')
        list_result.clear()
        if (self.dialog):
            for result in self.dialog.results:
                list_result.append([result.name,result.result_type,result.token,result.item,str(result.pos)])

    def on_btn_remove_result_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_result'))
        self.dialog.remove_result(value)
        self.load_results()

    ######### EXITS



    def on_win_add_exit_ok_clicked(self,button):
        if (self.screen):
            name=self.builder.get_object('entry_exit_name').get_text()
            destiny=get_active_value(self.builder.get_object('cmb_exit_destiny'))
            x=self.builder.get_object('entry_exit_x').get_text()
            y=self.builder.get_object('entry_exit_y').get_text()
            spawn_x=self.builder.get_object('entry_spawn_x').get_text()
            spawn_y=self.builder.get_object('entry_spawn_y').get_text()
            keep=self.builder.get_object('chk_keep').get_active()
            self.screen.add_exit(name,destiny,[x,y],keep,[spawn_x,spawn_y])
            list_exits=self.builder.get_object('list_exits')
            list_exits.append([name,destiny,str([x,y])])

        self.on_win_add_exit_cancel_clicked(None)

    def on_win_add_exit_cancel_clicked(self,button):
        self.builder.get_object('entry_exit_name').set_text('')
        self.builder.get_object('cmb_exit_destiny').set_active(-1)
        self.builder.get_object('entry_exit_x').set_text('')
        self.builder.get_object('entry_exit_y').set_text('')
        self.builder.get_object('win_add_exit').set_visible(False)

    def on_btn_add_exit_clicked(self,button):
        self.builder.get_object('win_add_exit').set_visible(True)

    def on_btn_remove_exit_clicked(self,button):
        value=get_selected_value(self.builder.get_object('tree_exits'))
        if (value):
            self.screen.remove_exit(value)
            self.load_exits()

    def load_exits(self):
        list_exits=self.builder.get_object('list_exits')
        list_exits.clear()
        if (self.screen):
            for e in self.screen.exits:
                list_exits.append([e.name,e.screen,str([e.pos[0],e.pos[1]])])





app = RPYG_Designer()
gtk.main()
