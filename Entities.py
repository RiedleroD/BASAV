#!/usr/bin/python3
from CONSTANTS import *
from random import shuffle
class Entity:
	def __init__(self,x,y,w,h,anch=0):
		self.w=w
		self.h=h
		self.set_pos(x,y,anch)
		self.rendered=False
	def set_pos(self,x,y,anch=0):
		#anchor:
		#______
		#|6 7 8|
		#|3 4 5|
		#|0 1 2|
		#——————
		if anch>8:
			raise ValueError("Entity initialized with invalid position anchor: %i"%anch)
		if anch%3==0:
			self.x=x
		elif anch%3==1:
			self.x=x-self.w/2
		else:
			self.x=x-self.w
		if anch//3==0:
			self.y=y
		elif anch//3==1:
			self.y=y-self.h/2
		else:
			self.y=y-self.h
		self.set_deriv()
	def set_size(self,w,h):
		self.w=w
		self.h=h
		self.set_deriv()
	def set_deriv(self):
		self.cx=self.x+self.w/2
		self.cy=self.y+self.h/2
		self._x=self.x+self.w
		self._y=self.y+self.h
		self.rendered=False
	def render(self):
		self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
		self.rendered=True
	def move(self,x,y):
		self.x+=x
		self.y+=y
		self.cx+=x
		self.cy+=y
		self._x+=x
		self._y+=y
		self.rendered=False
	def doesPointCollide(self,x,y):
		return x>=self.x and y>=self.y and x<=self._x and y<=self._y
	def checkPointCollision(self,x,y):
		if self.doesPointCollide(x,y):
			if x>=self.cx:
				if y>=self.cy:
					return (self._x-x,self._y-y)
				else:
					return (self._x-x,self.y-y)
			else:
				if y>=self.cy:
					return (self.x-x,self._y-y)
				else:
					return (self.x-x,self.y-y)
		else:
			return (0,0)
	def draw(self):
		if not self.rendered:
			self.render()
		pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad)

class Label(Entity):
	def __init__(self,x,y,w,h,text,anch=0,color=(255,255,255,255),bgcolor=(0,0,0,0),size=12):
		self.text=text
		self.setColor(color)
		self.setBgColor(bgcolor)
		self.anch=anch
		self.size=size
		super().__init__(x,y,w,h,anch)
	def setBgColor(self,color):
		self.cquad=("c4B",color*4)
	def setColor(self,color):
		self.color=color
	def setText(self,text):
		self.text=text
		self.rendered=False
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			self.label=pyglet.text.Label(self.text,x=self.cx,y=self.cy,anchor_x=ANCHORSx[1],anchor_y=ANCHORSy[1],color=self.color,font_size=self.size)
		else:
			self.label=pyglet.text.Label(self.text,x=self.x,y=self.y,anchor_x=ANCHORSx[self.anch%3],anchor_y=ANCHORSy[self.anch//3],color=self.color,font_size=self.size)
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.w>0 and self.h>0:
			pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		self.label.draw()

class Button(Label):
	def __init__(self,x,y,w,h,text,anch=0,key=None,size=12,pressedText=None):
		self.pressed=False
		self.key=key
		if pressedText:
			self.pressedText=pressedText
			self.unpressedText=text
		else:
			self.pressedText=self.unpressedText=text
		super().__init__(x,y,w,h,text,anch,(0,0,0,255),(255,255,255,255),size)
	def setBgColor(self,color):
		if self.pressed:
			self.cquad=("c4B",(*color,*color,128,128,128,255,128,128,128,255))
		else:
			self.cquad=("c4B",(128,128,128,255,128,128,128,255,*color,*color))
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			self.press()
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText(self.pressedText)
			self.setBgColor((255,255,255,255))
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.unpressedText)
			self.setBgColor((255,255,255,255))
	def checkKey(self,key):
		if self.key!=None and key==self.key:
			self.pressed=True
			return pyglet.event.EVENT_HANDLED
		else:
			return None

class ButtonSwitch(Button):
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			if self.pressed:
				self.release()
			else:
				self.press()

class Radio(Button):#currently unused
	def __init__(self,x,y,w,h,group,text,anch=0,key=None,size=12):
		RDG[group].append(self)
		self.group=group
		self.gindex=len(RDG[group])-1
		super().__init__(x,y,w,h,text,anch,key,size)
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			for rb in RDG[self.group]:
				rb.release()
			self.pressed=True
			self.setBgColor((255,255,255,255))
	def checkKey(self,key):
		if self.key!=None and key==self.key:
			for rb in RDG[self.group]:
				rb.release()
			self.pressed=True
			return pyglet.event.EVENT_HANDLED
		else:
			return None
	def clear(self):
		del RDG[self.group][self.gindex]
		self.group=None
		self.gindex=None

class TextEdit(Button):
	def __init__(self,x,y,w,h,desc,value="",anch=0,key=None,size=12):
		self.desc=desc
		self.value=value
		super().__init__(x,y,w,h,"%s: %s"%(desc,value),anch,key,size)
	def checkKey(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.value=value[:-1]
			elif key in (pgw.key.RETURN,pgw.key.ESCAPE):
				self.release()
				self.setText("%s"%(self.value))
			else:
				self.value+=key
				self.setText("%s: %s"%(self.desc,self.value))
		elif self.key!=None and key==self.key:
			self.pressed=True
			return pyglet.event.EVENT_HANDLED
		else:
			return None

class Bucket(Entity):
	def __init__(self,x,y,w,h,itemc,anch=0,scolor=(255,0,0),ecolor=(0,255,255)):
		self.colorlamb=lambda perc:tuple(int(self.scolor[x]*(perc)+self.ecolor[x]*(1-perc)) for x in range(len(self.scolor)))
		self.getquad=lambda perc,perc2:(self.x,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc2,self.x,self.y+self.h*perc2)
		self.getract=lambda perc,perc2:(self.x+self.w-6,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc2,self.x+self.w-6,self.y+self.h*perc2)
		self.getwact=lambda perc,perc2:(self.x+self.w-3,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc2,self.x+self.w-3,self.y+self.h*perc2)
		self.scolor=scolor
		self.ecolor=ecolor
		self.itemc=itemc
		self.items=[(i,self.colorlamb(i/itemc)) for i in range(itemc)]
		self.racts=set()
		self.wacts=set()
		super().__init__(x,y,w,h,anch)
		self.rendered=False
	def shuffle(self):
		shuffle(self.items)
		self.rendered=False
	def reverse(self):
		self.items.reverse()
		self.rendered=False
	def getvalue(self,i):
		if i>=self.itemc or i<0:
			return None
		else:
			self.racts.add(i)
			return self.items[i][0]
	def swapitems(self,x,y):
		self.items[x],self.items[y]=self.items[y],self.items[x]
		self.wacts.add(x)
		self.wacts.add(y)
		self.rendered=False
	def insertitem(self,x,i):
		if i>x:
			self.items.insert(i,self.items[x])
			del self.items[x]
		else:
			self.items.insert(i,self.items.pop(x))
		self.wacts.add(x)
		self.wacts.add(i)
		self.rendered=False
	def insert_from(self,x,y,other):
		if other.itemc>x and self.itemc>=y:
			self.items.insert(y,other.items.pop(x))
			self.itemc+=1
			other.itemc-=1
			self.wacts.add(y)
			other.wacts.add(x)
			self.rendered=other.rendered=False
		else:
			raise Exception("Bucket: out-of-scope call to insert_from")
	def render(self):
		self.batch=pyglet.graphics.Batch()
		if self.itemc>0:
			for i,item in enumerate(self.items):
				self.batch.add(4,pyglet.gl.GL_QUADS,None,('v2f',self.getquad(i/self.itemc,(i+1)/self.itemc)),('c3B',item[1]*4))
			for i,act in enumerate(self.racts):
				self.batch.add(4,pyglet.gl.GL_QUADS,None,('v2f',self.getract(act/self.itemc,(act+1)/self.itemc)),('c3B',(0,255,0,0,255,0,0,255,0,0,255,0)))
			for i,act in enumerate(self.wacts):
				self.batch.add(4,pyglet.gl.GL_QUADS,None,('v2f',self.getwact(act/self.itemc,(act+1)/self.itemc)),('c3B',(255,0,0,255,0,0,255,0,0,255,0,0)))
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		self.batch.draw()
		self.racts.clear()
		self.wacts.clear()
