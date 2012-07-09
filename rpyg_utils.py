#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Modules
import sys, pygame
from pygame.locals import *
import base64
import gzip
import StringIO



# Constants
WIDTH = 1024
HEIGHT = 768
 
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
 
