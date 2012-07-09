#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Modules
import sys, pygame, os
from pygame.locals import *
import base64
import gzip
import StringIO

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
IMG_SUITCASE=PROJECT_ROOT+'/images/suitcase.png'

WIDTH=1024
HEIGHT=768

MODE_GAME=0
MODE_INVENTORY=1
MODE_TALK=2
MODE_CUT_SCENE=3
MODE_END_GAME=4
MODE_FIRST_DIALOG=5
MODE_CUT_SCENE_REMOVE=6


FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30 # how often to check if playback has finished

# Classes
# ---------------------------------------------------------------------
 
# ---------------------------------------------------------------------
 
# Functions
# ---------------------------------------------------------------------
def load_image(filename, transparent=False):
        try: image = pygame.image.load(filename)
        except pygame.error, message:
                raise SystemExit, message
        image = image.convert()
        if transparent:
                color = image.get_at((0,0))
                image.set_colorkey(color, RLEACCEL)
        return image
        
        


def play_sound(soundfile):
    """Play sound through default mixer channel in blocking manner.
    
    This will load the whole sound into memory before playback
    """

    sound = pygame.mixer.Sound(soundfile)
    clock = pygame.time.Clock()
    sound.play()
    while pygame.mixer.get_busy():
        clock.tick(FRAMERATE)


def playmusic2(soundfile):
    """Stream music with mixer.music module using the event module to wait
       until the playback has finished.

    This method doesn't use a busy/poll loop, but has the disadvantage that 
    you neet to initialize the video module to use the event module.
    
    Also, interrupting the playback with Ctrl-C does not work :-(
    
    Change the call to 'playmusic' in the 'main' function to 'playmusic2'
    to use this method.
    """

    pygame.init()

    pygame.mixer.music.load(soundfile)
    pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
    pygame.event.set_allowed(pygame.constants.USEREVENT)
    pygame.mixer.music.play()
    pygame.event.wait()


def draw_text(screen,text, posx, posy, color=(255, 255, 255), size=24):
    font=pygame.font.SysFont("Vera", size)
    #~ font = pygame.font.Font('/home/dodger/Dropbox/proyectos/pygame/rpyg/images/DroidSans.ttf', size)
    result = pygame.font.Font.render(font, text, 1, color)
    result_rect = result.get_rect()
    result_rect.left = posx
    result_rect.top = posy
    screen.blit(result, result_rect)

    
# Corta un chara en las fil y col indicadas. Array Bidimensional.
def cut_chara(ruta, fil, col):
    image = load_image(ruta, True)
    rect = image.get_rect()
    w = rect.w / col
    h = rect.h / fil
    sprite = range(fil)
    for i in range(fil):
        sprite[i] = range(col)
 
    for f in range(fil):
        for c in range(col):
            sprite[f][c] = image.subsurface((rect.left, rect.top, w, h))
            rect.left += w
        rect.top += h
        rect.left = 0
 
    return sprite    
 
# ---------------------------------------------------------------------
 
 
def get_selected_value(treeview):
    value=None
    # Get the selection in the gtk.TreeView
    selection = treeview.get_selection()
    # Get the selection iter
    model, selection_iter = selection.get_selected()

    if (selection_iter):
        """There is a selection, so now get the the value"""
        value = treeview.get_model().get_value(selection_iter, 0)
    return value
    
def get_list_values(treelist):
    iter = treelist.get_iter_root()
    values=[]
    while (iter):
        # Get the first element
        values.append(treelist.get_value(iter, 0))
        # Get the next iter
        iter = treelist.iter_next(iter)
    return values

def get_active_value(combo):
    value=None
    selection_iter = combo.get_active_iter()
    if (selection_iter):
        value=combo.get_model().get_value(selection_iter, 0)
    return value

def set_filename(element,name):
    if (name):
            element.set_filename(name)
    else:
        element.set_filename('')
        element.set_current_folder('')
