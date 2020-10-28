#!/usr/bin/python3
print("  importing constants…")
from CONSTANTS import *
print("  importing other libs…")
from random import shuffle
from collections import deque as _deque

class deque(_deque):
	def pop(self,index=None):
		if index:
			x=self[index]
			del self[index]
			return x
		else:
			if index==None:
				return super().pop()
			elif index==0:
				return super().popleft()

print("  defining entities…")

class Entity:
	vl=None
	def __init__(self,x,y,w,h,batch,anch=0,bgcolor=(255,255,255)):
		self.w=w
		self.h=h
		self.set_pos(x,y,anch)
		self.setBgColor(bgcolor)
		self.rendered=False
		self.batch=batch
	def set_pos(self,x,y,anch=0):
		self.anch=anch
		#anchor:
		#______
		#|6 7 8|
		#|3 4 5|
		#|0 1 2|
		#——————
		if not 0<=anch<=8:
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
	def setBgColor(self,color):
		self.cquad=("c3B/dynamic",color*4)
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
		self.quad=('v2f/dynamic',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
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
		if not self.vl:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,GRmp,self.quad,self.cquad)
		else:
			self.vl.vertices=self.quad[1]
			self.vl.colors=self.cquad[1]
	def __del__(self):
		if self.vl:
			self.vl.delete()

class Label(Entity):
	label=None
	def __init__(self,x,y,w,h,text,batch,anch=0,color=(255,255,255),bgcolor=(0,0,0),size=12):
		self.label=pyglet.text.Label(text,x=0,y=y-size,color=color+(255,),font_size=size,batch=batch,group=GRfg)
		self.size=size
		super().__init__(x,y,w,h,batch,anch=anch,bgcolor=bgcolor)
		self.setText(text)
		self.setColor(color)
	def setColor(self,color):
		self.color=color
		self.label.color=self.color+(255,)
	def setText(self,text):
		self.text=text
		self.label.text=text
		self.adjust_kerning()
	def adjust_kerning(self):
		if self.w:
			kern=0
			self.set_kerning(kern)
			while self.label.content_width>self.w:
				kern-=0.1
				self.set_kerning(kern)
	def set_kerning(self,kern):
		self.label.document.set_style(0,-1,{"kerning":kern})
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f/static',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			self.label.begin_update()
			self.label.x=self.cx
			self.label.y=self.cy
			self.label.anchor_x=ANCHORSx[1]
			self.label.anchor_y=ANCHORSy[1]
			self.label.end_update()
		else:
			self.label.begin_update()
			self.label.x=self.x
			self.label.y=self.y
			self.label.anchor_x=ANCHORSx[self.anch%3]
			self.label.anchor_y=ANCHORSy[self.anch//3]
			self.label.end_update()
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.w>0 and self.h>0:
			if self.vl:
				self.vl.vertices[:]=self.quad[1]
				self.vl.colors[:]=self.cquad[1]
			else:
				self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,GRmp,self.quad,self.cquad)
	def __del__(self):
		if self.label:
			self.label.delete()
		if self.vl:
			self.vl.delete()

class LabelMultiline(Label):
	def __init__(self,x,y,w,h,text,batch,anch=0,color=(255,255,255),bgcolor=(0,0,0),size=12):
		self.labels=[pyglet.text.Label(text,x=0,y=-size*1.5,color=color+(255,),font_size=size,batch=batch,group=GRfg) for line in text.split("\n")]
		super().__init__(x,y,w,h,text,batch,anch,color,bgcolor,size)
		del self.label
	def setColor(self,color):
		self.color=color
		for label in self.labels:
			label.color=self.color+(255,)
	def setText(self,text):
		self.text=text
		text=text.split("\n")
		while len(self.labels)<len(text):#make new labels if necessary
			self.labels.append(pyglet.text.Label("",x=0,y=-self.size*1.5,color=self.color,font_size=self.size,batch=self.batch,group=GRfg))
		for label in reversed(self.labels):#set all labels' text
			try:
				label.text=text.pop()
			except IndexError:
				label.text=""
		self.rendered=False
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f/static',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			for i,label in enumerate(self.labels):
				label.begin_update()
				label.x=self.cx
				label.y=self.cy+self.size*(len(self.labels)-i-1)*1.5
				label.anchor_x=ANCHORSx[1]
				label.anchor_y=ANCHORSy[1]
				label.end_update()
		else:
			for i,label in enumerate(self.labels):
				label.begin_update()
				label.x=self.x
				label.y=self.y+self.size*(len(self.labels)-i-1)*1.5
				label.anchor_x=ANCHORSx[self.anch%3]
				label.anchor_y=ANCHORSy[self.anch//3]
				label.end_update()
		self.rendered=True
	def __del__(self):
		if self.vl:
			self.vl.delete()
		for label in self.labels:
			label.delete()

class Button(Label):
	def __init__(self,x,y,w,h,text,batch,anch=0,key=None,size=12,pressedText=None):
		self.pressed=False
		self.key=key
		if pressedText:
			self.pressedText=pressedText
			self.unpressedText=text
		else:
			self.pressedText=self.unpressedText=text
		super().__init__(x,y,w,h,text,batch,anch,(0,0,0),(255,255,255),size)
	def setBgColor(self,color):
		if self.pressed:
			self.cquad=("c3B/dynamic",(*color,*color,128,128,128,128,128,128))
		else:
			self.cquad=("c3B/dynamic",(128,128,128,128,128,128,*color,*color))
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
			self.setBgColor((255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.unpressedText)
			self.setBgColor((255,255,255))
			return pyglet.event.EVENT_HANDLED

class ButtonSwitch(Button):
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			if self.pressed:
				self.release()
			else:
				self.press()

class ButtonFlipthrough(Button):
	def __init__(self,x,y,w,h,text,values,batch,anch=0,key=None,size=12,default=0):
		self.vals=values
		self.i=default
		self.text=text
		super().__init__(x,y,w,h,text%values[default],batch,anch,key,size)
	def setText(self,text):
		self.label.text=text
	def getCurval(self):
		return self.vals[self.i]
	def getCurIndex(self):
		return self.i
	def press(self):
		self.i+=1
		self.i%=len(self.vals)
		self.setText(self.text%self.getCurval())
		return pyglet.event.EVENT_HANDLED

class TextEdit(Button):#also unused
	cache=None
	def __init__(self,x,y,w,h,desc,value,batch,anch=0,key=None,size=12,allowed_chars=None):
		self.desc=desc
		self.value=self.cache=value
		self.alchrs=allowed_chars
		super().__init__(x,y,w,h,desc,batch,anch,key,size)
	def checkKey(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.cache=self.cache[:-1]
				self.setText(f"[{self.cache}]")
			elif key in (pgw.key.RETURN,pgw.key.ESCAPE):
				if self.valid_input(self.cache):
					self.release()
			else:
				try:
					char=chr(key)
				except OverflowError:#if a weird utf-8 symbol comes rolling in. Most apparent on non-english keyboards that have ß ö ä ü ect.
					return None
				if self.valid_key(char):
					self.cache+=char
					self.setText(f"[{self.cache}]")
			return pyglet.event.EVENT_HANDLED
		elif self.key!=None and key==self.key:
			return self.press()
	def valid_key(self,key):
		return self.alchrs==None or key in self.alchrs
	def valid_input(self,inpot):
		return True
	def getVal(self):
		return self.value
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText(f"[{self.cache}]")
			self.setBgColor((255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.value=self.cache
			self.pressed=False
			self.setText(self.desc)
			self.setBgColor((255,255,255))
			return pyglet.event.EVENT_HANDLED

class IntEdit(TextEdit):
	def __init__(self,x,y,w,h,desc,value,batch,anch=0,key=None,size=12,numrange=(None,None)):
		self.minnum,self.maxnum=numrange
		alchrs=tuple(str(num) for num in range(10))
		if self.minnum==None or self.minnum<0:
			alchrs+=("-",)
		super().__init__(x,y,w,h,desc,f"{value}",batch,anch,key,size,alchrs)
	def valid_input(self,inpot):
		try:
			i=int(inpot)
		except ValueError:
			return False
		else:
			return (self.minnum==None or self.minnum<=i) and (self.maxnum==None or self.maxnum>i)
	def getNum(self):
		return int(self.value)

class RadioList(Entity):
	def __init__(self,x,y,w,h,texts,batch,anch=0,keys=None,pressedTexts=None,selected=None,size=12):
		btnc=len(texts)
		if keys==None:
			keys=[None for i in range(btnc)]
		if pressedTexts==None:
			pressedTexts=[None for i in range(btnc)]
		self.btns=[Button(x,y-i*h/btnc,w,h/btnc,text,batch,anch,keys[i],size,pressedTexts[i]) for i,text in enumerate(texts)]
		self.setBgColor((192,192,192))#average color in btns
		if selected!=None:
			self.btns[selected].press()
		super().__init__(x,y,w,h,batch,anch)
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
	def draw(self):
		if not self.rendered:
			self.render()
		if not self.vl:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,GRbg,self.quad,self.cquad)
		else:
			self.vl.vertices=self.quad[1]
			self.vl.colors=self.cquad[1]
		for btn in self.btns:
			btn.draw()
	def getSelected(self):
		for i,btn in enumerate(self.btns):
			if btn.pressed:
				return i

class RadioListPaged(RadioList):
	def __init__(self,x,y,w,h,texts,pageic,batch,anch=0,keys=None,pressedTexts=None,selected=None,size=12):
		self.pageic=pageic
		self.page=0
		btnc=len(texts)
		btnh=h/(pageic+1)
		super().__init__(x,y,w,h,texts,batch,anch,keys,pressedTexts,selected,size)
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		for i,btn in enumerate(self.btns):#correct btn position and height based on pages and set label text to none
			btn.set_size(w,btnh)
			btn.set_pos(x,y-btnh*(i%self.pageic),anch)
			if btn not in onscr:
				btn.label.text=""
				if btn.vl:
					btn.vl.delete()
					btn.vl=None
		self.next=Button(x,y-btnh*pageic,w/2,btnh,"→",batch,anch,None,size)
		self.prev=Button(x-w/2,y-btnh*pageic,w/2,btnh,"←",batch,anch,None,size)
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
					if btn.vl:
						btn.vl.delete()
						btn.vl=None
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
		if self.vl:
			self.vl.vertices[:]=self.quad[1]
			self.vl.colors[:]=self.cquad[1]
		else:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,GRbg,self.quad,self.cquad)
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
	def __init__(self,x,y,w,h,itemc,batch,anch=0,maxps=None):
		super().__init__(x,y,w,h,batch,anch)
		self.maxic=abs(itemc)
		blanc=self.blanc=[0,0,0]*self.maxic*2
		if itemc<0:
			self.itemc=0
			colors=blanc.copy()
		else:
			self.itemc=itemc
			colors=COLORS.copy()
		self.items=[i for i in range(self.itemc)]
		self.racts=set()
		self.wacts=set()
		if (not maxps) or maxps>self.maxic:
			maxps=self.maxic
		self.setmaxps(maxps)#also sets ravl and wavl
		self.colors=deque(colors)
		self.vl=batch.add(
			self.maxic*2,GL_LINES,GRmp,
			('v2f/dynamic',[pos for i in range(self.maxic) for pos in self._getline(i)]),
			('c3B/stream',colors)
		)
	def setmaxps(self,maxps):
		self.maxps=maxps
		self.ravl=self.batch.add(
			maxps*2,GL_LINES,GRmp,
			('v2f/dynamic',[0,0,0,0]*maxps),
			('c3B/stream',(0,255,0,0,255,0)*maxps)
		)
		self.wavl=self.batch.add(
			maxps*2,GL_LINES,GRmp,
			('v2f/dynamic',[0,0,0,0]*maxps),
			('c3B/stream',(255,0,0,255,0,0)*maxps)
		)
	def _getyfromi(self,i):
		return self.y+self.h*(i+1)/self.maxic
	def _getline(self,i):
		y=self._getyfromi(i)
		return (self.x,y,self.x+self.w*0.9,y)
	def _getwact(self,i):
		y=self._getyfromi(i)
		return (self.x+self.w*0.9,y,self.x+self.w*0.95,y)
	def _getract(self,i):
		y=self._getyfromi(i)
		return (self.x+self.w*0.95,y,self.x+self.w,y)
	def _getvalue(self,i):
		if i>=self.itemc or i<0:
			print(f"out-of-bounds call to READ: {i} not in buck[{self.itemc}]")
			return (False,None)
		else:
			return (True,self.items[i])
	def getvalue(self,i):
		self.racts.add(i)
		return self._getvalue(i)
	def swapitems(self,x,y):
		if x>=self.itemc or x<0 or y>=self.itemc or y<0:
			print(f"out-of-bounds call to SWAP: {x},{y} not in buck[{self.itemc}]")
			return False
		else:
			self.items[x],self.items[y]=self.items[y],self.items[x]
			for j in range(6):
				self.colors[6*x+j],self.colors[6*y+j]=self.colors[6*y+j],self.colors[6*x+j]
			self.wacts.add(x)
			self.wacts.add(y)
			return True
	def insertitem(self,x,i):
		if x>=self.itemc or x<0 or i>self.itemc or i<0:
			print(f"out-of-bounds call to INSERT: {x},{i} not in buck[{self.itemc}]")
			return False
		elif i==x:
			return True
		elif i>x:
			self.items[i:i]=self.items[x],
			del self.items[x]
			for j in range(6):#this is magic
				self.colors.insert(6*i-1,self.colors.pop(6*x))
			self.wacts.add(i-1)
		else:
			self.items[i:i]=self.items.pop(x),
			for j in range(6):#also magic
				self.colors.insert(6*i+j,self.colors.pop(6*x+j))
			self.wacts.add(i)
		self.wacts.add(x)
		return True
	def swap_from(self,x,y,other):
		if x>=0 and y>=0 and other.itemc>x and self.itemc>y:
			self.items[x],other.items[y]=other.items[y],self.items[x]
			for j in range(6):
				self.colors[6*x+j],other.colors[6*y+j]=other.colors[6*y+j],self.colors[6*x+j]
			self.wacts.add(y)
			other.wacts.add(x)
			return True
		else:
			print(f"out-of-scope call to BUCKSWAP: swap {x} at buck[{other.itemc}] and {y} at buck[{self.itemc}]")
			return False
	def insert_from(self,x,y,other):
		if other.itemc>=x>=0 and self.itemc>=y>=0:
			self.items[y:y]=other.items.pop(x),
			for j in range(6):
				self.colors.insert(y*6+j,other.colors.pop(x*6))
				other.colors.append(self.colors.pop())
			self.itemc+=1
			other.itemc-=1
			self.wacts.add(y)
			other.wacts.add(x)
			return True
		else:
			print(f"out-of-scope call to BUCKINSERT: from {x} at buck[{other.itemc}] to {y} at buck[{self.itemc}]")
			return False
	def render(self):
		self.vl.vertices[:]=[pos for i in range(self.maxic) for pos in self._getline(i)]
		wvs=self._getwact(0)
		wvs=[wvs[0],0,wvs[2],0]*self.maxps
		self.wavl.vertices[:]=wvs
		rvs=self._getract(0)
		rvs=[rvs[0],0,rvs[2],0]*self.maxps
		self.ravl.vertices[:]=rvs
		self.rendered=True
	def render_colors(self):
		self.colors=[col for i in self.items for col in colorlamb(i/self.maxic)]
	def draw(self):
		if not self.rendered:
			self.render()
		if self.itemc>self.maxic:
			raise ValueError("Bucket: itemc is larger than maxic")
		self.vl.colors=self.colors
		for i,num in enumerate(self.wacts):
			if i>=self.maxps:
				break
			self.wavl.vertices[1+i*4]=self.wavl.vertices[3+i*4]=self._getyfromi(num)
		wl=len(self.wacts)
		for i in range(wl,self.maxps):
			self.wavl.vertices[1+i*4]=self.wavl.vertices[3+i*4]=-1
		for i,num in enumerate(self.racts):
			if i>=self.maxps:
				break
			self.ravl.vertices[1+i*4]=self.ravl.vertices[3+i*4]=self._getyfromi(num)
		rl=len(self.racts)
		for i in range(rl,self.maxps):
			self.ravl.vertices[1+i*4]=self.ravl.vertices[3+i*4]=-1
		if self.wacts:
			self.wacts.clear()
		if self.racts:
			self.racts.clear()
	def __del__(self):
		if self.wavl:
			self.wavl.delete()
		if self.ravl:
			self.ravl.delete()
		if self.vl:
			self.vl.delete()
