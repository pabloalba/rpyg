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


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

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


#result types
RESULT_REMOVE_NPC = 0
RESULT_ADD_TOKEN = 1 
RESULT_REMOVE_TOKEN = 2
RESULT_ADD_ITEM = 3
RESULT_REMOVE_ITEM = 4
RESULT_MOVE_NPC = 5
RESULT_END_GAME = 5



# Functions
# ---------------------------------------------------------------------
def load_image(filename, transparent=False, width=-1, height=-1):
    try:
        image = pygame.image.load(filename)
        if (width!=-1):
            if (height==-1):
                #calc height
                height = image.get_height() * width / image.get_width()
            image = pygame.transform.scale(image, (width, height))

    except pygame.error, message:
        raise SystemExit, message
    image = image.convert()
    if transparent:
        color = image.get_at((0,0))
        image.set_colorkey(color, RLEACCEL)
    return image
        

def play_background_music(soundfile):
    pygame.mixer.quit()
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



def draw_text(screen,text, posx, posy, color=(255, 255, 255), size=24):
    font=pygame.font.SysFont("Vera", size)
    #~ font = pygame.font.Font('/home/dodger/Dropbox/proyectos/pygame/rpyg/images/DroidSans.ttf', size)
    result = pygame.font.Font.render(font, text, 1, color)
    result_rect = result.get_rect()
    result_rect.left = posx
    result_rect.top = posy
    screen.blit(result, result_rect)
