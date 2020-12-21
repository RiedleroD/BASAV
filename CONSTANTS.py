#!/usr/bin/python3
print("    importing various libraries…")
import os,sys
from time import time
print("    importing pyglet…")
import pyglet
from pyglet import window as pgw
from pyglet.gl import GL_LINES, GL_QUADS
from pyglet.media import synthesis

VERBOSE=False

print("    getting parameters…")
for arg in sys.argv[1:]:
	if arg in ("-v","--verbose"):
		VERBOSE=True
		print("    Verbose mode \033[32mon\033[39m")
	else:
		print(f"    Unrecognized argument: \033[36m{arg}\033[39m")

print("    defining various constants…")

ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")

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

KP=pgw.key.KeyStateHandler()	#a dict with the key states inside
MP={pgw.mouse.LEFT:False,pgw.mouse.RIGHT:False,pgw.mouse.MIDDLE:False}

TXTCACHE={}

GRbg=pyglet.graphics.OrderedGroup(0)#background – radiolist backgrounds
GRmp=pyglet.graphics.OrderedGroup(1)#midpoint – button backgrounds & buckets
GRfg=pyglet.graphics.OrderedGroup(2)#foreground – labels

print("    defining main window…")

class MainWin(pyglet.window.Window):
	logic=None
	def __init__(self):
		config = pyglet.gl.Config(sample_buffers=1, samples=8)#because items otherwise flicker when they're over 1000
		super().__init__(fullscreen=False,style=self.WINDOW_STYLE_BORDERLESS,caption="Riedlers Sound of Sorting",config=config,vsync=True,visible=False)
		self.maximize()
		self.set_visible(True)
	def on_draw(self):
		self.clear()
		if self.logic:
			self.logic.on_draw()
	def set_logic(self,logic):
		self.logic=logic
	def on_mouse_press(self,x,y,button,modifiers):
		MP[button]=True
		if button==pgw.mouse.LEFT:
			if self.logic:
				for item in self.logic.btns+self.logic.rads+self.logic.edits+list(self.logic.algui.values()):
					ret=item.check_press(x,y)
					if ret:
						return ret
		elif button==pgw.mouse.RIGHT:
			pass
		elif button==pgw.mouse.MIDDLE:
			pass
	def on_mouse_release(self,x,y,button,modifiers):
		MP[button]=False
	def on_key_press(self,symbol,modifiers):
		if self.logic:
			for item in self.logic.edits+self.logic.btns+self.logic.rads+list(self.logic.algui.values()):
				ret=item.check_key(symbol)
				if ret:
					return ret

window=MainWin()

WIDTH,HEIGHT=window.get_size()
WIDTH2=WIDTH/2
HEIGHT2=HEIGHT/2
SIZE=(WIDTH+HEIGHT)/2#only for scaling stuff
BTNWIDTH=WIDTH/10
BTNWIDTH2=BTNWIDTH/2
BTNHEIGHT=HEIGHT/20
BTNHEIGHT2=BTNHEIGHT/2

print(f"    window size is {WIDTH}x{HEIGHT}")
print("    generating audio…")
AUDIO=pyglet.media.StaticSource(synthesis.Square(8,sample_size=8))#the longer the note, the less crackling, but the more RAM is used
