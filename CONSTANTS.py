#!/usr/bin/python3
import os,sys,pyglet
from pyglet import window as pgw
from time import time

ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")

TIME=time()
DTIME=0
TIMEC=0
BUCKLEN=2048

KP=pgw.key.KeyStateHandler()	#a dict with the key states inside
MP={pgw.mouse.LEFT:False,pgw.mouse.RIGHT:False,pgw.mouse.MIDDLE:False}
