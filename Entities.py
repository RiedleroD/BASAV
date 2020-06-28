#!/usr/bin/python3
from CONSTANTS import *
from random import shuffle
import functools,operator
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
		self.label=pyglet.text.Label(text,x=0,y=-size,color=color,font_size=size,batch=batch)
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

class LabelMultiline(Label):
	def __init__(self,x,y,w,h,text,anch=0,color=(255,255,255,255),bgcolor=(0,0,0,0),size=12,batch=None):
		self.labels=[pyglet.text.Label(text,x=0,y=-size*1.5,color=color,font_size=size,batch=batch) for line in text.split("\n")]
		super().__init__(x,y,w,h,text,anch,color,bgcolor,size,batch)
		del self.label
	def setColor(self,color):
		self.color=color
		for label in self.labels:
			label.color=self.color
	def setText(self,text):
		self.text=text
		text=text.split("\n")
		while len(self.labels)<len(text):
			self.labels.append(pyglet.text.Label("",x=0,y=-self.size*1.5,color=self.color,font_size=self.size,batch=self.batch))
		self.rendered=False
		for label in reversed(self.labels):
			try:
				label.text=text.pop()
			except IndexError:
				label.text=""
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			for i,label in enumerate(self.labels):
				label.x=self.cx
				label.y=self.cy+self.size*(len(self.labels)-i-1)*1.5
				label.anchor_x=ANCHORSx[1]
				label.anchor_y=ANCHORSy[1]
		else:
			for i,label in enumerate(self.labels):
				label.x=self.x
				label.y=self.y+self.size*(len(self.labels)-i-1)*1.5
				label.anchor_x=ANCHORSx[self.anch%3]
				label.anchor_y=ANCHORSy[self.anch//3]
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.w>0 and self.h>0:
			pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		if self.batch==None:
			for label in self.labels:
				label.draw()

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

class ButtonFlipthrough(Button):
	def __init__(self,x,y,w,h,text,values,anch=0,key=None,size=12,batch=None):
		self.vals=values
		self.i=0
		self.text=text
		super().__init__(x,y,w,h,text%values[0],anch,key,size,batch=batch)
	def setText(self,text):
		self.label.text=text
	def getCurval(self):
		return self.vals[self.i]
	def press(self):
		self.i+=1
		self.i%=len(self.vals)
		self.setText(self.text%self.getCurval())
		return pyglet.event.EVENT_HANDLED

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
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		for i,btn in enumerate(self.btns):#correct btn position and height based on pages and set label text to none
			btn.set_size(w,btnh)
			btn.set_pos(x,y-btnh*(i%self.pageic),anch)
			if btn not in onscr:
				btn.label.text=""
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
	def __init__(self,x,y,w,h,itemc,anch=0):
		self.getquad=lambda perc:[self.x,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc]
		self.getquad2=lambda perc,perc2:[self.x,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc,self.x+self.w-6,self.y+self.h*perc2,self.x,self.y+self.h*perc2]
		self.getract=lambda perc:[self.x+self.w-6,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc]
		self.getract2=lambda perc,perc2:[self.x+self.w-6,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc,self.x+self.w-3,self.y+self.h*perc2,self.x+self.w-6,self.y+self.h*perc2]
		self.getwact=lambda perc:[self.x+self.w-3,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc]
		self.getwact2=lambda perc,perc2:[self.x+self.w-3,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc,self.x+self.w,self.y+self.h*perc2,self.x+self.w-3,self.y+self.h*perc2]
		super().__init__(x,y,w,h,anch,batch=pyglet.graphics.Batch())
		if itemc<0:#only sets maxic
			self.maxic=-itemc
			self.itemc=0
		else:
			self.itemc=itemc
			self.maxic=itemc
		self.items=[i for i in range(itemc)]
		self.recalc_quads()
		self.racts=set()
		self.wacts=set()
		self.grcl=[0,255,0,0,255,0,0,255,0,0,255,0]*self.maxic
		self.rdcl=[255,0,0,255,0,0,255,0,0,255,0,0]*self.maxic
	def shuffle(self):
		shuffle(self.items)
		self.rendered=False
	def reverse(self):
		self.items.reverse()
		self.rendered=False
	def recalc_quads(self):
		self.quads=[self.getquad(i/self.maxic) for i in range(self.maxic)]
		self.qwacts=[self.getwact(i/self.maxic) for i in range(self.maxic)]
		self.qracts=[self.getract(i/self.maxic) for i in range(self.maxic)]
	def getvalue(self,i):
		if i>=self.itemc or i<0:
			return None
		else:
			self.rendered=False
			self.racts.add(i)
			return self.items[i]
	def swapitems(self,x,y):
		self.items[x],self.items[y]=self.items[y],self.items[x]
		self.wacts.add(x)
		self.wacts.add(y)
		self.rendered=False
	def insertitem(self,x,i):
		#actually the fastest method I could find, see here: https://stackoverflow.com/a/62608192/10499494
		if i>x:
			self.items[i:i]=self.items[x],
			del self.items[x]
		else:
			self.items[i:i]=self.items.pop(x),
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
			self.items[y:y]=other.items.pop(x),
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
			raise ValueError("Bucket: itemc is larger than maxic")
		if self.itemc>0:
			items=self.items.copy()
			iteml=[]
			itemq=[]
			sindex=0
			bindex=0
			while len(items)>0:#group racts to not draw massive amounts of single lines, but big rects instead
				sit=items.pop(0)
				bit=sit+1
				bindex=sindex+1
				while len(items)>0 and bit==items[0]:
					bit+=1
					bindex+=1
					items.pop(0)
				if sit+1==bit:
					iteml.append(sindex)
				else:
					itemq.append((sindex,bindex))
				sindex=bindex
			if len(iteml)>0:
				self.batch.add(2*len(iteml),pyglet.gl.GL_LINES,None,('v2f',functools.reduce(operator.iconcat,[self.quads[i] for i in iteml],[])),('c3B',[cquad for i in iteml for cquad in COLORS[self.items[i]]]))
			if len(itemq)>0:
				self.batch.add(4*len(itemq),pyglet.gl.GL_QUADS,None,('v2f',functools.reduce(operator.iconcat,[self.getquad2(sit/self.maxic,bit/self.maxic) for sit,bit in itemq],[])),('c3B',[cquad for sit,bit in itemq for cquad in COLORS[self.items[sit]]+COLORS[self.items[bit-1]]]))
			
			if len(self.racts)>0:
				racts=self.racts.copy()
				ractl=[]
				ractq=[]
				while len(racts)>0:#group racts to not draw massive amounts of single lines, but big rects instead
					sact=racts.pop()
					bact=sact+1
					while sact-1 in racts:
						sact-=1
						racts.remove(sact)
					while bact in racts:
						racts.remove(bact)
						bact+=1
					if sact+1==bact:
						ractl.append(sact)
					else:
						ractq.append((sact,bact))
				if len(ractl)>0:
					self.batch.add(2*len(ractl),pyglet.gl.GL_LINES,None,('v2f',functools.reduce(operator.iconcat,[self.qracts[act] for act in ractl],[])),('c3B',self.grcl[:len(ractl)*6]))
				if len(ractq)>0:
					self.batch.add(4*len(ractq),pyglet.gl.GL_QUADS,None,('v2f',functools.reduce(operator.iconcat,[self.getract2(sact/self.maxic,bact/self.maxic) for sact,bact in ractq],[])),('c3B',self.grcl[:len(ractq)*12]))
			if len(self.wacts)>0:
				wacts=self.wacts.copy()
				wactl=[]
				wactq=[]
				while len(wacts)>0:#group wacts to not draw massive amounts of single lines, but big rects instead
					sact=wacts.pop()
					bact=sact+1
					while sact-1 in wacts:
						sact-=1
						wacts.remove(sact)
					while bact in wacts:
						wacts.remove(bact)
						bact+=1
					if sact+1==bact:
						wactl.append(sact)
					else:
						wactq.append((sact,bact))
				if len(wactl)>0:
					self.batch.add(2*len(wactl),pyglet.gl.GL_LINES,None,('v2f',functools.reduce(operator.iconcat,[self.qwacts[act] for act in wactl],[])),('c3B',self.rdcl[:len(wactl)*6]))
				if len(wactq)>0:
					self.batch.add(4*len(wactq),pyglet.gl.GL_QUADS,None,('v2f',functools.reduce(operator.iconcat,[self.getwact2(sact/self.maxic,bact/self.maxic) for sact,bact in wactq],[])),('c3B',self.rdcl[:len(wactq)*12]))
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
