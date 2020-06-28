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
SCOLOR=(255,0,0)
ECOLOR=(0,255,255)

class Timer():
	def __init__(self):
		self.t=0
		self.c=0
	def start(self):
		self.T=time()
	def end(self):
		self.t+=time()-self.T
		self.T=None
		self.c+=1
	def get(self):
		if self.c==0:
			return None
		else:
			return self.t/self.c

profs=[Timer() for i in range(0)]
colorlamb=lambda perc:[int(SCOLOR[x]*(perc)+ECOLOR[x]*(1-perc)) for x in range(len(SCOLOR))]*2

COLORS=[colorlamb(i/BUCKLEN) for i in range(BUCKLEN)]

KP=pgw.key.KeyStateHandler()	#a dict with the key states inside
MP={pgw.mouse.LEFT:False,pgw.mouse.RIGHT:False,pgw.mouse.MIDDLE:False}
