#!/usr/bin/python3
print("  importing constants…")
from CONSTANTS import *
print("  importing other libs…")
from random import shuffle
from collections import deque as _deque

#SOME HELP IS HERE

#anchor:
#______
#|6 7 8|
#|3 4 5|
#|0 1 2|
#——————

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
	todo=32#binary representation of what has to be rerendered
	#1  - x
	#2  - y
	#4  - cx,_x
	#8  - cy,_y
	#16 - vertices
	#32 - vertexlist
	#64 - bgcolor
	w=0
	h=0
	basex=0
	basey=0
	anch=None
	bgcolor=None
	def __init__(self,x,y,w,h,batch,anch=0,bgcolor=(255,255,255),group=GRmp):
		self.group=group
		self.set_size(w,h)
		self.set_pos(x,y)
		self.set_anch(anch)
		self.set_bgcolor(bgcolor)
		self.batch=batch
	def set_pos(self,basex,basey):
		self.basex=basex
		self.basey=basey
		self.todo|=31#1+2+4+8+16
	def set_anch(self,anch):
		if not 0<=anch<=8:
			raise ValueError(f"Invalid position anchor: {anch}")
		elif anch!=self.anch:
			self.anch=anch
			self.todo|=31#1+2+4+8+16
	def set_size(self,w,h):
		if self.w!=w:
			self.w=w
			self.todo|=11#1+4+16
		if self.h!=h:
			self.h=h
			self.todo|=26#2+8+16
	def move(self,x,y):
		if x:
			self.basex+=x
			self.todo|=11#1+4+16
		if y:
			self.basey+=y
			self.todo|=26#2+8+16
	def set_bgcolor(self,color):
		if self.bgcolor!=color:
			self.bgcolor=color
			self.todo|=64
	def update_cx_x(self):
		self.cx=self.x+self.w/2
		self._x=self.x+self.w
		self.todo&=~4
	def update_cy_y(self):
		self.cy=self.y+self.h/2
		self._y=self.y+self.h
		self.todo&=~8
	def update_x(self):
		if self.anch%3==0:
			self.x=self.basex
		elif self.anch%3==1:
			self.x=self.basex-self.w/2
		else:
			self.x=self.basex-self.w
		self.todo&=~1
	def update_y(self):
		if self.anch//3==0:
			self.y=self.basey
		elif self.anch//3==1:
			self.y=self.basey-self.h/2
		else:
			self.y=self.basey-self.h
		self.todo&=~2
	def update_vl(self):
		if self.quad and self.bgcolor:#can't update if those are missing
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,('v2f',self.quad),('c3B',self.bgcolor*4))
			self.todo&=~32
	def update_vertices(self):
		self.quad=(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y)
		if self.vl:
			self.vl.vertices=self.quad
		self.todo&=~16
	def update_bgcolor(self):
		self.vl.colors=self.bgcolor*4
		self.todo&=~64
	def does_point_collide(self,x,y):
		return x>=self.x and y>=self.y and x<=self._x and y<=self._y
	def check_point_collision(self,x,y):
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
		if self.todo & 31:
			if self.todo & 1:
				self.update_x()
			if self.todo & 2:
				self.update_y()
			if self.todo & 4:
				self.update_cx_x()
			if self.todo & 8:
				self.update_cy_y()
			if self.todo & 16:
				self.update_vertices()
		if self.todo & 32:
			self.update_vl()
		if self.todo & 64:
			self.update_bgcolor()
	def __del__(self):
		if self.vl:
			self.vl.delete()

class Label(Entity):
	label=None
	todo=1312#32+1024
	#1		- x
	#2		- y
	#4		- cx,_x
	#8		- cy,_y
	#16		- quad
	#32		- bgvertexlist
	#64		- bgcolor
	#128	- text
	#256	- kerning
	#512	- textcolor
	#1024	- textanchor
	#2048	- label x
	#4096	- label y
	def __init__(self,x,y,w,h,text,batch,anch=0,color=(255,255,255),bgcolor=(0,0,0),size=12,txtgroup=GRfg,bggroup=GRmp):
		self.label=pyglet.text.Label(text,x=0,y=y-size,color=(color if len(color)==4 else color+(255,)),font_size=size,batch=batch,group=txtgroup)
		self.size=size
		self.set_text(text,False)
		self.set_color(color,False)
		super().__init__(x,y,w,h,batch,anch=anch,bgcolor=bgcolor,group=bggroup)
	def set_color(self,color,push_to_label=True):
		colorlen=len(color)
		if colorlen==4:
			pass
		elif colorlen==3:
			color=color+(255,)
		else:
			raise ValueError("Text color has to be 3 verteces long")
		self.color=color
		if push_to_label:
			self.todo|=512
	def set_text(self,text,push_to_label=True):
		self.text=text
		if push_to_label:
			self.todo|=128
	def set_anchor(self,anch):
		super().set_anchor(anch)
		self.todo|=1024
	def update_color(self):
		self.label.color=self.color
		self.todo&=~512
	def update_x(self):
		super().update_x()
		self.todo|=2048
	def update_y(self):
		super().update_y()
		self.todo|=4096
	def update_label_x(self):
		if self.w>0 and self.w>0:
			self.label.x=self.cx
		else:
			self.label.x=self.x
		self.todo&=~2048
	def update_label_y(self):
		if self.w>0 and self.w>0:
			self.label.y=self.cy
		else:
			self.label.y=self.y
		self.todo&=~4096
	def update_textanchor(self):
		if self.w>0 and self.h>0:
			self.label.anchor_x=ANCHORSx[1]
			self.label.anchor_y=ANCHORSy[1]
		else:
			self.label.anchor_x=ANCHORSx[self.anch%3]
			self.label.anchor_y=ANCHORSy[self.anch//3]
		self.todo&=~1024
	def update_text(self):
		self.label.text=self.text
		self.todo&=~128
		self.todo|=256
	def update_kerning(self):
		self.todo&=~256
		if self.w in TXTCACHE:
			if self.text in TXTCACHE[self.w]:
				self.label.document.set_style(0,-1,TXTCACHE[self.w][len(self.text)])
				return
		else:
			TXTCACHE[self.w]={}
		kern=0
		self.label.document.set_style(0,-1,{"kerning":kern})
		self.label.end_update()#instant updates are needed from here
		while self.label.content_width>self.w:
			kern-=0.1
			if kern<-1.5:
				self.size-=0.1
				kern=0
			self.label.document.set_style(0,-1,{"kerning":kern,"font_size":self.size})
		TXTCACHE[self.w][len(self.text)]={"kerning":kern,"font_size":self.size}
	def draw(self):#32% of time
		if self.todo:
			if self.todo & 63:#1+2+4+8+16+32
				if self.todo & 1:
					self.update_x()
				if self.todo & 2:
					self.update_y()
				if self.todo & 4:
					self.update_cx_x()
				if self.todo & 8:
					self.update_cy_y()
				if self.todo & 16:
					self.update_vertices()
			if self.todo & 32:
				self.update_vl()
			if self.todo & 64:
				self.update_bgcolor()
			if self.todo & 8064:#128+256+512+1024+2048+4096:
				self.label.begin_update()
				if self.todo & 128:
					self.update_text()
				if self.todo & 512:
					self.update_color()#text color
				if self.todo & 1024:
					self.update_textanchor()
				if self.todo & 2048:
					self.update_label_x()
				if self.todo & 4096:
					self.update_label_y()
				#has to be done outside of label update function since it depends on instantaneous label content width updates
				if self.w and self.todo & 256:
					self.update_kerning()
				self.label.end_update()
	def __del__(self):
		if self.label:
			self.label.delete()
		if self.vl:
			self.vl.delete()

class LabelMultiline(Entity):
	#1  - x
	#2  - y
	#4  - cx,_x
	#8  - cy,_y
	#16 - vertices
	#32 - vertexlist
	#64 - bgcolor
	#128- text
	text=None
	def __init__(self,x,y,w,h,text,batch,anch=0,color=(255,255,255),size=12):
		texts=text.split("\n")
		self.labels=[Label(x,y-size*1.5*(i-len(texts)),0,0,line,anch=anch,size=size,batch=batch) for i,line in enumerate(texts)]
		self.size=size
		self.set_color(color)
		super().__init__(x,y,w,h,batch,anch)
		self.set_color(color)
	def set_color(self,color):
		self.color=color
		for label in self.labels:
			label.set_color(color)
	def set_text(self,text):
		if text!=self.text:
			self.text=text
			self.todo|=128
	def update_text(self):
		text=self.text.split("\n")
		labels=self.labels.copy()
		y=self.y
		for txt in reversed(text):
			if labels:
				label=labels.pop()
				label.set_text(txt)
			else:
				label=Label(self.x,y,0,0,text=txt,anch=self.anch,color=self.color,size=self.size,batch=self.batch)
				self.labels.append(label)
			y-=self.size*1.5
		for remaining in labels:
			remaining.text=""
		self.todo&=~128
	def draw(self):#14.2% of time (contributes to Label.draw())
		super().draw()
		if self.todo & 128:
			self.update_text()
		for label in self.labels:
			label.draw()
	def __del__(self):
		if self.vl:
			self.vl.delete()

class Button(Label):
	def __init__(self,x,y,w,h,text,batch,anch=0,key=None,size=12,pressed_text=None,txtgroup=GRfg,bggroup=GRmp):
		self.pressed=False
		self.key=key
		if pressed_text:
			self.pressed_text=pressed_text
			self.unpressed_text=text
		else:
			self.pressed_text=self.unpressed_text=text
		super().__init__(x,y,w,h,text,batch,anch,(0,0,0),(255,255,255),size,txtgroup,bggroup)
	def update_bgcolor(self):
		if self.pressed:
			self.vl.colors=(*self.bgcolor,*self.bgcolor,128,128,128,128,128,128)
		else:
			self.vl.colors=(128,128,128,128,128,128,*self.bgcolor,*self.bgcolor)
		self.todo&=~64
	def check_press(self,x,y):
		if self.does_point_collide(x,y):
			return self.press()
	def check_key(self,key):
		if self.key!=None and key==self.key:
			return self.press()
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.set_text(self.pressed_text)
			self.todo|=64
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.set_text(self.unpressed_text)
			self.todo|=64
			return pyglet.event.EVENT_HANDLED

class ButtonSwitch(Button):
	def check_press(self,x,y):
		if self.does_point_collide(x,y):
			if self.pressed:
				self.release()
			else:
				self.press()

class ButtonFlipthrough(Button):
	def __init__(self,x,y,w,h,text,values,batch,anch=0,key=None,size=12,default=0):
		self.vals=values
		self.i=default
		self._text=text
		super().__init__(x,y,w,h,text%values[default],batch,anch,key,size)
	def get_curval(self):
		return self.vals[self.i]
	def get_curindex(self):
		return self.i
	def press(self):
		self.i=(self.i+1)%len(self.vals)
		self.set_text(self._text%self.get_curval())
		return pyglet.event.EVENT_HANDLED

class TextEdit(Button):#also unused
	cache=None
	def __init__(self,x,y,w,h,desc,value,batch,anch=0,key=None,size=12,allowed_chars=None):
		self.desc=desc
		self.value=self.cache=value
		self.alchrs=allowed_chars
		super().__init__(x,y,w,h,desc,batch,anch,key,size)
	def check_key(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.cache=self.cache[:-1]
				self.set_text(f"[{self.cache}]")
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
					self.set_text(f"[{self.cache}]")
			return pyglet.event.EVENT_HANDLED
		elif self.key!=None and key==self.key:
			return self.press()
	def valid_key(self,key):
		return self.alchrs==None or key in self.alchrs
	def valid_input(self,inpot):
		return True
	def get_val(self):
		return self.value
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.set_text(f"[{self.cache}]")
			self.todo|=64
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.value=self.cache
			self.pressed=False
			self.set_text(self.desc)
			self.todo|=64
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
	def get_num(self):
		return int(self.value)

class RadioList(Entity):
	def __init__(self,x,y,w,h,texts,batch,anch=0,keys=None,pressed_texts=None,selected=None,size=12):
		btnc=len(texts)
		if self.btns==None:
			if keys==None:
				keys=[None for i in range(btnc)]
			if pressed_texts==None:
				pressed_texts=[None for i in range(btnc)]
			self.btns=[Button(x,y-i*h/btnc,w,h/btnc,text,batch,anch,keys[i],size,pressed_texts[i]) for i,text in enumerate(texts)]
		if selected!=None:
			self.btns[selected].press()
		super().__init__(x,y,w,h,batch,anch,bgcolor=(192,192,192),group=GRbg)
	def check_press(self,x,y):
		prsd=None
		for i,btn in enumerate(self.btns):
			prsd=btn.check_press(x,y)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd and btn.pressed:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def check_key(self,key):
		for i,btn in enumerate(self.btns):
			prsd=btn.check_key(key)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def draw(self):
		super().draw()
		for btn in self.btns:
			btn.draw()
	def get_selected(self):
		for i,btn in enumerate(self.btns):
			if btn.pressed:
				return i

class RadioListPaged(RadioList):
	def __init__(self,x,y,w,h,texts,pageic,batch,anch=0,keys=None,selected=None,size=12):
		self.pageic=pageic
		self.page=0
		btnc=len(texts)
		btnh=h/(pageic+1)
		self.groups=[]
		self.btns=[]
		for page in range(-(-btnc//pageic)):
			groupfg=pyglet.graphics.Group(GRfg)
			groupbg=pyglet.graphics.Group(GRmp)
			self.groups.append((groupfg,groupbg))
			if page!=0:
				groupfg.visible=groupbg.visible=False
			for i in range(pageic):
				j=page*pageic+i
				if j>=len(texts):
					break
				self.btns.append(Button(x,y-i*btnh,w,btnh,texts[j],batch,anch,size=size,txtgroup=groupfg,bggroup=groupbg))
		super().__init__(x,y,w,h,texts,batch,anch,keys,None,selected,size)
		self.next=Button(x,y-btnh*pageic,w/2,btnh,"→",batch,anch,size=size)
		self.prev=Button(x-w/2,y-btnh*pageic,w/2,btnh,"←",batch,anch,size=size)
	def check_press(self,x,y):
		if self.prev.check_press(x,y):
			prsd=-1
		elif self.next.check_press(x,y):
			prsd=1
		else:
			prsd=None
		if prsd:
			#hide old page
			for group in self.groups[self.page]:
				group.visible=False
			#next/previous page
			self.page+=prsd
			#make sure that self.page wraps around if too big
			self.page%=-(-len(self.btns)//self.pageic)#ceiling division
			#unhide new page
			for group in self.groups[self.page]:
				group.visible=True
			return pyglet.event.EVENT_HANDLED
		else:
			for btn in self.btns[self.page*self.pageic:(self.page+1)*self.pageic]:#checking buttons that are on screen
				prsd=btn.check_press(x,y)
				if prsd:
					prsd=btn
					break
			if prsd!=None:#releasing all other buttons (because this is a *radio* list)
				for btn in self.btns:
					if btn is not prsd and btn.pressed:
						btn.release()
				return pyglet.event.EVENT_HANDLED
	def check_key(self,key):
		for i,btn in enumerate(self.btns):#checking all buttons, not just the ones on screen
			prsd=btn.check_key(key)
			if prsd:
				prsd=i
				break
		if prsd!=None:#unchecking all other buttons
			for i,btn in enumerate(self.btns):
				if i!=prsd:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def draw(self):
		super().draw()
		#draw buttons plus prev and next
		for btn in self.btns:
			btn.draw()
		self.prev.draw()
		self.next.draw()
		#releasing next & previous buttons only after drawing to show single-frame click
		if self.prev.pressed:
			self.prev.release()
		if self.next.pressed:
			self.next.release()

class Bucket(Entity):
	ravl=None
	wavl=None
	todo=32
	#1		- x
	#2		- y
	#4		- cx,_x
	#8		- cy,_y
	#16		- vertices
	#32		- vertexlist
	#64		- colors
	#128	- ravl verteces
	#256	- wavl verteces
	#512	- colors (regenerate)
	def __init__(self,x,y,w,h,itemc,batch,anch=0,maxps=None):
		super().__init__(x,y,w,h,batch,anch)
		self.maxic=abs(itemc)
		blanc=self.blanc=[0,0,0]*self.maxic*2
		if itemc<0:#don't fill, just set maxic
			self.itemc=0
			colors=blanc.copy()
		else:#fill and set maxic
			self.itemc=itemc
			colors=self.generate_colors()
		self.items=[i for i in range(self.itemc)]
		self.racts=set()
		self.wacts=set()
		self.prevracts=set()
		self.prevwacts=set()
		if (not maxps) or maxps>self.maxic:
			maxps=self.maxic
		self.setmaxps(maxps)#also sets ravl and wavl
		self.colors=colors
	def setmaxps(self,maxps):#happens too rarely to add to todo
		self.maxps=maxps
		if self.ravl:
			self.ravl.delete()
		self.ravl=self.batch.add(
			maxps*2,GL_LINES,GRmp,
			('v2f/stream',[-1,-1,-1,-1]*maxps),
			('c3B/static',(0,255,0,0,255,0)*maxps)
		)
		if self.wavl:
			self.wavl.delete()
		self.wavl=self.batch.add(
			maxps*2,GL_LINES,GRmp,
			('v2f/stream',[-1,-1,-1,-1]*maxps),
			('c3B/static',(255,0,0,255,0,0)*maxps)
		)
		self.todo|=384#128+256
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
	def pull_item(self):
		if self.itemc==0:
			print(f"out-of-bounds call to PULL: Bucket empty")
			return False,None
		else:
			self.itemc-=1
			#shit code bc slicing doesn't work with deques
			self.colors[6*self.itemc]=10
			for i in range(6*self.itemc+1,6*self.itemc+6):
				self.colors[i]=0
			#it's just this→ self.colors[6*self.itemc,6*self.itemc+6]=10,0,0,0,0,0
			self.wacts.add(self.itemc)
			self.todo|=64
			return True,self.items.pop()
	def push_item(self,item):
		if self.itemc==self.maxic:
			print(f"out-of-bounds call to PUSH: Bucket full")
			return False
		else:
			self.itemc+=1
			#again fuck deques
			cl=colorlamb(item/self.maxic)
			for i in range(0,6):
				self.colors[6*self.itemc+i-6]=cl[i]
			#self.colors[6*self.itemc-6:6*self.itemc]=colorlamb(item/self.maxic)
			self.wacts.add(self.itemc-1)
			self.items.append(item)
			self.todo|=64
			return True
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
			self.todo|=64
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
		self.todo|=64
		return True
	def swap_from(self,x,y,other):
		if x>=0 and y>=0 and other.itemc>x and self.itemc>y:
			self.todo|=64
			other.todo|=64
			self.items[x],other.items[y]=other.items[y],self.items[x]
			for j in range(6):
				self.colors[6*x+j],other.colors[6*y+j]=other.colors[6*y+j],self.colors[6*x+j]
			self.wacts.add(y)
			other.wacts.add(x)
			return True
		else:
			print(f"out-of-bounds call to BUCKSWAP: swap {x} at buck[{other.itemc}] and {y} at buck[{self.itemc}]")
			return False
	def insert_from(self,x,y,other):
		if other.itemc>x>=0 and self.itemc>=y>=0:
			self.todo|=64
			other.todo|=64
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
			print(f"out-of-bounds call to BUCKINSERT: from {x} at buck[{other.itemc}] to {y} at buck[{self.itemc}]")
			return False
	def generate_vl(self,j):
		colors=self.colors[6*j*PARTLEN:min(6*(j+1)*PARTLEN,6*BUCKLEN)]
		if sum(colors)==0:#lazily create vertexlists if items are at a high enough index
			return None
		else:
			amount=min(PARTLEN,BUCKLEN//(j+1))*2
			verteces=[pos for i in range(j*PARTLEN,min((j+1)*PARTLEN,BUCKLEN)) for pos in self._getline(i)]
			return self.batch.add(amount,GL_LINES,GRmp,('v2f/dynamic',verteces),('c3B/stream',colors))
	def update_vl(self):
		self.vls=[self.generate_vl(j) for j in range(-(-self.maxic//PARTLEN))]
		self.todo&=~32
	def update_vertices(self):
		if self.vls:
			for j,vl in enumerate(self.vls):
				if vl:
					vl.vertices=[pos for i in range(len(vl.vertices)//4) for pos in self._getline(i+PARTLEN*j)]
			self.todo&=~16
	def update_wavl(self):
		wvs=self._getwact(0)
		wvs=[wvs[0],-1,wvs[2],-1]*self.maxps
		self.wavl.vertices[:]=wvs
		self.todo&=~256
	def update_ravl(self):
		rvs=self._getract(0)
		rvs=[rvs[0],-1,rvs[2],-1]*self.maxps
		self.ravl.vertices[:]=rvs
		self.todo&=~128
	def update_acts(self):
		if self.racts:
			for i,num in enumerate(self.racts):
				if i>=self.maxps:
					break
				self.ravl.vertices[1+i*4]=self.ravl.vertices[3+i*4]=self._getyfromi(num)
			rl=len(self.racts)
			for i in range(rl,self.maxps):
				self.ravl.vertices[1+i*4]=self.ravl.vertices[3+i*4]=-1
			self.prevracts,self.racts=self.racts,self.prevracts
			self.racts.clear()
		elif self.prevracts:
			for i in range(min(len(self.prevracts),self.maxps)):
				self.ravl.vertices[1+i*4]=self.ravl.vertices[3+i*4]=-1
		if self.wacts:
			for i,num in enumerate(self.wacts):
				if i>=self.maxps:
					break
				self.wavl.vertices[1+i*4]=self.wavl.vertices[3+i*4]=self._getyfromi(num)
			wl=len(self.wacts)
			for i in range(wl,self.maxps):
				self.wavl.vertices[1+i*4]=self.wavl.vertices[3+i*4]=-1
			self.prevwacts,self.wacts=self.wacts,self.prevwacts
			self.wacts.clear()
		elif self.prevwacts:
			for i in range(min(len(self.prevwacts),self.maxps)):
				self.wavl.vertices[1+i*4]=self.wavl.vertices[3+i*4]=-1
	def render_colors(self):
		self.colors=[col for i in self.items for col in colorlamb(i/self.maxic)]
		self.todo&=~64
	def generate_colors(self):
		return [col for i in range(self.maxic) for col in colorlamb(i/self.maxic)]
	def draw(self):#9.1% of time
		if self.todo & 63:
			if self.todo & 1:
				self.update_x()
			if self.todo & 2:
				self.update_y()
			if self.todo & 4:
				self.update_cx_x()
			if self.todo & 8:
				self.update_cy_y()
			if self.todo & 32:
				self.update_vl()
			if self.todo & 16:
				self.update_vertices()
				self.todo|=384#128+256
		if self.todo & 64:
			for j,vl in enumerate(self.vls):
				colorpart=self.colors[6*j*PARTLEN:6*(j+1)*PARTLEN]
				if not vl:
					self.vls[j]=vl=self.generate_vl(j)#gets assigned to 0 if only black again
					if vl:
						vl.colors=colorpart
				else:
					vl.colors=colorpart
			self.todo&=~64
		if self.todo & 128:
			self.update_ravl()
		if self.todo & 256:
			self.update_wavl()
		self.update_acts()
		if self.itemc>self.maxic:
			raise ValueError("Bucket: itemc is larger than maxic")
	def __del__(self):
		if self.wavl:
			self.wavl.delete()
		if self.ravl:
			self.ravl.delete()
		if self.vls:
			for vl in self.vls:
				if vl:
					vl.delete()
