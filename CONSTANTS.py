#!/usr/bin/python3
import os,sys,pyglet
from pyglet import window as pgw
from pyglet.gl import GL_LINES, GL_QUADS
from pyglet.media import synthesis
from time import time

ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")

TIME=time()
DTIME=0
TIMEC=0
BUCKLEN=2000
SCOLOR=(0,255,255)
ECOLOR=(255,0,0)

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

profs=[Timer() for i in range(0)]#for speed debugging purposes
colorlamb=lambda perc:[int(SCOLOR[x]*(1-perc)+ECOLOR[x]*perc) for x in range(len(SCOLOR))]*2
audiolamb=lambda perc:pyglet.media.StaticSource(synthesis.Square(1/80,440+440*perc,sample_size=8))#less than 1/60 because that reduces cpu load apparently, but doesn't sound too bad

COLORS=[color for i in range(BUCKLEN) for color in colorlamb(i/BUCKLEN)]
AUDIOS=[audiolamb(i/BUCKLEN) for i in range(BUCKLEN)]

KP=pgw.key.KeyStateHandler()	#a dict with the key states inside
MP={pgw.mouse.LEFT:False,pgw.mouse.RIGHT:False,pgw.mouse.MIDDLE:False}

GRbg=pyglet.graphics.OrderedGroup(0)#background – radiolist backgrounds
GRmp=pyglet.graphics.OrderedGroup(1)#midpoint – button backgrounds & buckets
GRfg=pyglet.graphics.OrderedGroup(2)#foreground – labels
