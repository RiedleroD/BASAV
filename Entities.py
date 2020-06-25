#!/usr/bin/python3
from CONSTANTS import *
from random import shuffle
class Entity:
	def __init__(self,x,y,w,h,anch=0,batch=None):
		self.w=w
		self.h=h
		self.set_pos(x,y,anch)
		self.rendered=False
		self.batch=batch
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
	def __init__(self,x,y,w,h,text,anch=0,color=(255,255,255,255),bgcolor=(0,0,0,0),size=12,batch=None):
		self.label=pyglet.text.Label(text,x=0,y=0,color=color,font_size=size,batch=batch)
		self.setText(text)
		self.setColor(color)
		self.setBgColor(bgcolor)
		self.anch=anch
		self.size=size
		super().__init__(x,y,w,h,anch,batch=batch)
	def setBgColor(self,color):
		self.cquad=("c4B",color*4)
	def setColor(self,color):
		self.color=color
		self.label.color=self.color
	def setText(self,text):
		self.text=text
		self.label.text=text
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			self.label.x=self.cx
			self.label.y=self.cy
			self.label.anchor_x=ANCHORSx[1]
			self.label.anchor_y=ANCHORSy[1]
		else:
			self.label.x=self.x
			self.label.y=self.y
			self.label.anchor_x=ANCHORSx[self.anch%3]
			self.label.anchor_y=ANCHORSy[self.anch//3]
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.w>0 and self.h>0:
			pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		if self.batch==None:
			self.label.draw()

class Button(Label):
	def __init__(self,x,y,w,h,text,anch=0,key=None,size=12,pressedText=None,batch=None):
		self.pressed=False
		self.key=key
		if pressedText:
			self.pressedText=pressedText
			self.unpressedText=text
		else:
			self.pressedText=self.unpressedText=text
		super().__init__(x,y,w,h,text,anch,(0,0,0,255),(255,255,255,255),size,batch=batch)
	def setBgColor(self,color):
		if self.pressed:
			self.cquad=("c4B",(*color,*color,128,128,128,255,128,128,128,255))
		else:
			self.cquad=("c4B",(128,128,128,255,128,128,128,255,*color,*color))
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			return self.press()
	def checkKey(self,key):
		if self.key!=None and key==self.key:
			return self.press()
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText(self.pressedText)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.unpressedText)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED

class ButtonSwitch(Button):
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			if self.pressed:
				self.release()
			else:
				self.press()

class TextEdit(Button):#also unused
	def __init__(self,x,y,w,h,desc,value="",anch=0,key=None,size=12,batch=None):
		self.desc=desc
		self.value=value
		super().__init__(x,y,w,h,desc,anch,key,size,batch=batch)
	def checkKey(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.value=self.value[:-1]
				self.setText("[%s]"%self.value)
			elif key in (pgw.key.RETURN,pgw.key.ESCAPE):
				self.release()
			else:
				self.value+=chr(key)
				self.setText("[%s]"%(self.value))
			return pyglet.event.EVENT_HANDLED
		elif self.key!=None and key==self.key:
			return self.press()
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText("[%s]"%self.value)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.desc)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED

class IntEdit(TextEdit):
	nums=("0","1","2","3","4","5","6","7","8","9")
	def checkKey(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.value=self.value[:-1]
				self.setText("[%s]"%self.value)
			elif key in (pgw.key.RETURN,pgw.key.ESCAPE):
				if len(self.value)==0:
					self.value="0"
				self.release()
			else:
				char=chr(key)
				if char in self.nums:
					self.value+=chr(key)
					self.setText("[%s]"%(self.value))
			return pyglet.event.EVENT_HANDLED
		elif self.key!=None and key==self.key:
			return self.press()
	def getNum(self):
		return int(self.value)

class RadioList(Entity):
	def __init__(self,x,y,w,h,texts,anch=0,keys=None,pressedTexts=None,selected=None,size=12,batch=None):
		btnc=len(texts)
		if keys==None:
			keys=[None for i in range(btnc)]
		if pressedTexts==None:
			pressedTexts=[None for i in range(btnc)]
		self.btns=[Button(x,y-i*h/btnc,w,h/btnc,text,anch,keys[i],size,pressedTexts[i],batch=batch) for i,text in enumerate(texts)]
		self.setBgColor((192,192,192))#average color in btns
		if selected!=None:
			self.btns[selected].press()
		super().__init__(x,y,w,h,anch,batch=batch)
	def checkpress(self,x,y):
		prsd=None
		for i,btn in enumerate(self.btns):
			prsd=btn.checkpress(x,y)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd and btn.pressed:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def checkKey(self,key):
		for i,btn in enumerate(self.btns):
			prsd=btn.checkKey(key)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def render(self):
		self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
		self.rendered=True
	def setBgColor(self,color):
		self.cquad=("c3B",color*4)
	def draw(self):
		if not self.rendered:
			self.render()
		pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		for btn in self.btns:
			btn.draw()
	def getSelected(self):
		for i,btn in enumerate(self.btns):
			if btn.pressed:
				return i

class RadioListPaged(RadioList):
	def __init__(self,x,y,w,h,texts,pageic,anch=0,keys=None,pressedTexts=None,selected=None,size=12,batch=None):
		self.pageic=pageic
		self.page=0
		btnc=len(texts)
		btnh=h/(pageic+1)
		super().__init__(x,y,w,h,texts,anch,keys,pressedTexts,selected,size,batch)
		for i,btn in enumerate(self.btns):#correct btn position and height based on pages
			btn.set_pos(x,y-btnh*(i%self.pageic),anch)
			btn.set_size(w,btnh)
		self.prev=Button(x,y-btnh*pageic,w/2,btnh,"→",anch,None,size,batch=batch)
		self.next=Button(x-w/2,y-btnh*pageic,w/2,btnh,"←",anch,None,size,batch=batch)
	def checkpress(self,x,y):
		if self.prev.checkpress(x,y):
			prsd=-1
		elif self.next.checkpress(x,y):
			prsd=1
		else:
			prsd=None
		if prsd:
			self.page+=prsd
			#make sure that self.page wraps around if too big
			self.page%=-(-len(self.btns)//self.pageic)#ceiling division
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		if prsd:
			#remove text from all buttons that shouldn't be on screen (because the labels get rendered in batch)
			#re-add text from all buttons that should be on screen
			for btn in self.btns:
				if btn in onscr:
					btn.label.text=btn.text
				else:
					btn.label.text=""
			prsd=None
		for btn in onscr:
			prsd=btn.checkpress(x,y)
			if prsd:
				prsd=btn
				break
		if prsd!=None:
			for btn in self.btns:
				if btn is not prsd and btn.pressed:
					btn.release()
					if btn not in onscr:
						btn.label.text=""
			return pyglet.event.EVENT_HANDLED
	def checkKey(self,key):
		for i,btn in enumerate(self.btns):
			prsd=btn.checkKey(key)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def draw(self):
		if not self.rendered:
			self.render()
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		#draw the background plane
		pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		#draw the buttons in the current page plus prev and next
		for btn in onscr:
			btn.draw()
		self.prev.draw()
		self.next.draw()
		#releasing next & previous buttons only after drawing to show single-frame click
		if self.prev.pressed:
			self.prev.release()
		if self.next.pressed:
			self.next.release()

class Bucket(Entity):
	def __init__(self,x,y,w,h,itemc,anch=0,scolor=(255,0,0),ecolor=(0,255,255)):
		self.colorlamb=lambda perc:tuple(int(self.scolor[x]*(perc)+self.ecolor[x]*(1-perc)) for x in range(len(self.scolor)))
		self.getquad=lambda perc,perc2:(self.x,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc2,self.x,self.y+self.h*perc2)
		self.getract=lambda perc,perc2:(self.x+self.w-6,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc2,self.x+self.w-6,self.y+self.h*perc2)
		self.getwact=lambda perc,perc2:(self.x+self.w-3,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc2,self.x+self.w-3,self.y+self.h*perc2)
		self.scolor=scolor
		self.ecolor=ecolor
		self.itemc=itemc
		self.maxic=itemc
		self.items=[(i,self.colorlamb(i/itemc)) for i in range(itemc)]
		self.racts=set()
		self.wacts=set()
		super().__init__(x,y,w,h,anch,batch=pyglet.graphics.Batch())
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
			self.rendered=False
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
	def swap_from(self,x,y,other):
		if other.itemc>x and self.itemc>y:
			self.items[y],other.items[x]=self.items[x],other.items[y]
			self.wacts.add(y)
			other.wacts.add(x)
			self.rendered=other.rendered=False
		else:
			raise Exception("Bucket: out-of-scope call to swap_from")
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
		if self.itemc>self.maxic:
			self.maxic=self.itemc
		if self.itemc>0:
			self.batch.add(4*self.itemc,pyglet.gl.GL_QUADS,None,('v2f',tuple(quad for i in range(self.itemc) for quad in self.getquad(i/self.maxic,(i+1)/self.maxic))),('c3B',tuple(cquad for item in self.items for cquad in item[1]*4)))
			if len(self.racts)>0:
				self.batch.add(4*len(self.racts),pyglet.gl.GL_QUADS,None,('v2f',tuple(quad for act in self.racts for quad in self.getract(act/self.maxic,(act+1)/self.maxic))),('c3B',(0,255,0,0,255,0,0,255,0,0,255,0)*len(self.racts)))
			if len(self.wacts)>0:
				self.batch.add(4*len(self.wacts),pyglet.gl.GL_QUADS,None,('v2f',tuple(quad for act in self.wacts for quad in self.getwact(act/self.maxic,(act+1)/self.maxic))),('c3B',(255,0,0,255,0,0,255,0,0,255,0,0)*len(self.wacts)))
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		self.batch.draw()
		if len(self.racts)>0:
			self.racts.clear()
			self.rendered=False
		if len(self.wacts)>0:
			self.wacts.clear()
			self.rendered=False
