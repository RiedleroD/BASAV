#!/usr/bin/python3
import os,sys,pyglet
from pyglet import window as pgw
from time import time

window=pgw.Window(fullscreen=False,style=pgw.Window.WINDOW_STYLE_BORDERLESS,caption="Riedler Sound of Sorting",vsync=False,visible=False)
screen=window.display.get_default_screen()
window.set_size(screen.width,screen.height)
window.set_visible(True)

running=True
RDG=([],[],[],[])#Radio groups

WIDTH,HEIGHT=window.get_size()
WIDTH2=WIDTH/2
HEIGHT2=HEIGHT/2
SIZE=(WIDTH+HEIGHT)/2#only for scaling stuff
BTNWIDTH=WIDTH/20
BTNWIDTH2=BTNWIDTH/2
BTNHEIGHT=HEIGHT/20
BTNHEIGHT2=BTNHEIGHT/2

ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")

TIME=time()

KP=pgw.key.KeyStateHandler()	#a dict with the key states inside
MP={pgw.mouse.LEFT:False,pgw.mouse.RIGHT:False,pgw.mouse.MIDDLE:False}
