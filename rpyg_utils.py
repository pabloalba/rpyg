#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modules
import sys, pygame
from pygame.locals import *
import base64
import gzip
import StringIO
import tempfile
import os
import zipfile
import pickle



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

def play_background_music(soundfile):
    pygame.mixer.init()
    pygame.mixer.music.load(soundfile)
    pygame.mixer.music.play(-1)


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



def __load_resource__(tempDir, file_name):
    base_name = os.path.basename(file_name)
    return os.path.join(tempDir, "resources", base_name)


def __load_resources__(tempDir, game):
    #Load all files
    for screen in game.screens:
        screen.map_file = __load_resource__(tempDir, screen.map_file)

        if screen.music_file:
            screen.music_file = __load_resource__(tempDir, screen.music_file)

        screen.protagonist.img_file = __load_resource__(tempDir, screen.protagonist.img_file)
        screen.protagonist.img_dialog = __load_resource__(tempDir, screen.protagonist.img_dialog)

        for npc in screen.npcs:
            npc.img_file = __load_resource__(tempDir, npc.img_file)
            npc.img_dialog = __load_resource__(tempDir, npc.img_dialog)


    for item in game.items:
        item.image_url = __load_resource__(tempDir, item.image_url)

def open_game(filename):
        try:
            #Extract zip to temp dir
            tempDir = tempfile.mkdtemp(prefix = 'RPyG')

            resourcesDir = os.path.join(tempDir, "resources")
            os.makedirs(resourcesDir)

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

            game = pickle.load(fileObj)

            __load_resources__(tempDir, game)

            fileObj.close()
            return [game, tempDir]
        except:
            return None
