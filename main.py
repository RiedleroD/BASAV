#!/usr/bin/python3
from Entities import *
from Algs import *
import traceback as tbe
from collections import deque

class GameWin(pyglet.window.Window):
	def __init__(self,*args,**kwargs):
		self.push_handlers(KP)
		self.tc=0
		self.dt=0
		self.fps=0
		self.set_fps(60)#set_fps needs self.fps to exist & sets more than that, so I have to do both here.
		self.curalg=None
		self.curval=None
		self.gen=None
		self.stats=[0,0,0,0,0]
		self.labels=[]
		self.btns=[]
		self.rads=[]
		self.edits=[]
		self.bucks=[]
		self.toplay=deque()
		self.apls=[pyglet.media.Player() for i in range(10)]#audio players
		for apl in self.apls:
			apl.volume=0.1
		self.batch=pyglet.graphics.Batch()
		super().__init__(*args,**kwargs)
	def set_fps(self,fps):
		if fps!=self.fps and fps>0:
			self.fps=fps
			pyglet.clock.unschedule(self.update)
			pyglet.clock.schedule_interval(self.update,1/fps)
	def update(self,dt):
		self.tc+=1
		self.dt+=dt
		if self.dt>=0.1:
			#update ups counter
			self.labels[1].setText("UPS:%02i/%02i"%(round(self.tc/self.dt),self.fps))
			#update randomness counter
			randomness=0
			for buck in self.bucks:
				previ=None
				for i in buck.items:
					if previ==None:
						previ=i
					else:
						if previ>i:
							randomness+=previ-i
						previ=i
			self.labels[7].setText("Randomness:%02i"%randomness)
			#set tc and dt to 0
			self.tc=0
			self.dt=0
		if not self.edits[1].pressed:
			self.set_fps(self.edits[1].getNum())
		if self.btns[-1].pressed:
			self.btns[3].release()
			sys.exit(0)
		if self.btns[2].pressed:
			self.btns[2].release()
			self.curalg=Reverser(self.bucks[0].itemc)
			self.gen=self.curalg.gen()
			self.stats=[0,0,0,0,0]
			self.btns[0].press()
		if self.btns[1].pressed:
			self.btns[1].release()
			self.curalg=shufflers[self.btns[3].getCurval()](self.bucks[0].itemc)
			self.gen=self.curalg.gen()
			self.stats=[0,0,0,0,0]
			self.btns[0].press()
		if self.btns[0].pressed:
			if self.curalg==None:
				self.curalg=algs[self.rads[0].getSelected()](self.bucks[0].itemc)
				self.gen=self.curalg.gen()
				self.stats=[0,0,0,0,0]
			for x in range(self.edits[0].getNum()):
				try:
					act=next(self.gen)
				except StopIteration:
					act=(FIN,)
				except Exception as e:
					tbe.print_tb(e.__traceback__)
					print(f"{self.curalg.name}: {e}")
					act=(FIN,)
				if not self.procact(act):
					self.btns[0].release()
					self.curalg=None
					self.gen=None
					self.bucks[0].racts.clear()
					self.bucks[0].wacts.clear()
					self.bucks[0].rendered=False
					break
		elif self.curalg!=None:
			self.curalg=None
			self.gen=None
			if len(self.bucks)>1:
				for buck in range(1,len(self.bucks)):
					self.bucks[0].items.extend(self.bucks[1].items)
					del self.bucks[1]
				self.bucks[0].itemc=BUCKLEN
				self.bucks[0].render_colors()
				self.bucks[0].set_size(WIDTH2,HEIGHT)
		self.labels[2].setText("Read:%02i"%self.stats[0])
		self.labels[3].setText("Swap:%02i"%self.stats[1])
		self.labels[4].setText("Insert:%02i"%self.stats[2])
		self.labels[5].setText("Bucket:%02i"%self.stats[3])
		self.labels[6].setText("Pass:%02i"%self.stats[4])
		self.play_all()
	def play_all(self):
		for i,apl in enumerate(self.apls):
			if self.toplay:
				item=self.toplay.pop()
			else:
				return
			if apl.playing:
				apl.next_source()
			apl.queue(AUDIOS[item])
			if not apl.playing:
				apl.play()
		self.toplay.clear()
	def play(self,item):
		self.toplay.append(item)
	def play_index(self,b,i):
		return self.play(self.bucks[b]._getvalue(i)[1])
	def act_read(self,act):
		if len(act)!=3:
			print(f"{self.curalg.name}: READ: incorrect act length {len(act)}: only length of 3 is allowed")
			return False
		elif act[2]>=len(self.bucks) or act[2]<0:
			print(f"{self.curalg.name}: READ: Bucket {act[2]} does not exist, max is {len(self.bucks)-1}")
			return False
		else:
			rv,self.curval=self.bucks[act[2]].getvalue(act[1])
			self.stats[0]+=1
			if self.curalg.gen:
				self.curalg.v=self.curval
			self.play(self.curval)
			return rv
	def act_swap(self,act):
		if len(act)!=4:
			print(f"{self.curalg.name}: SWAP: incorrect act length {len(act)}: only length of 4 is allowed")
			return False
		elif act[3]>=len(self.bucks) or act[3]<0:
			print(f"{self.curalg.name}: SWAP: Bucket {act[3]} does not exist, max is {len(self.bucks)-1}")
			return False
		else:
			self.stats[1]+=1
			self.play_index(act[3],act[1])
			self.play_index(act[3],act[2])
			return self.bucks[act[3]].swapitems(act[1],act[2])
	def act_insert(self,act):
		if len(act)!=4:
			print(f"{self.curalg.name}: INSERT: incorrect act length {len(act)}: only length of 4 is allowed")
			return False
		elif act[3]>=len(self.bucks) or act[3]<0:
			print(f"{self.curalg.name}: INSERT: Bucket {act[3]} does not exist, max is {len(self.bucks)-1}")
			return False
		else:
			self.stats[2]+=1
			self.play_index(act[3],act[1])
			return self.bucks[act[3]].insertitem(act[1],act[2])
	def act_new_buck(self,act):
		if len(act) not in (1,3):
			print(f"{self.curalg.name}: NEW_BUCK: incorrect act length {len(act)}: only length of 1 or 3 is allowed")
			return False
		else:
			chunksize=WIDTH2/(len(self.bucks)+1)
			for i,buck in enumerate(self.bucks):
				buck.set_pos(chunksize*i,0)
				buck.set_size(chunksize,HEIGHT)
			self.bucks.append(Bucket(WIDTH2-chunksize,0,chunksize,HEIGHT,-BUCKLEN,self.batch,maxps=self.edits[0].getNum()))
			self.stats[3]+=1
			return True
	def act_buckswap(self,act):
		if len(act)!=5:
			print(f"{self.curalg.name}: BUCKSWAP: incorrect act length {len(act)}: only length of 5 is allowed")
			return False
		elif act[2]>=len(self.bucks) or act[2]<0:
			print(f"{self.curalg.name}: BUCKSWAP: Bucket {act[2]} does not exist, max is {len(self.bucks)-1}")
			return False
		elif act[4]>=len(self.bucks) or act[4]<0:
			print(f"{self.curalg.name}: BUCKSWAP: Bucket {act[4]} does not exist, max is {len(self.bucks)-1}")
			return False
		else:
			self.stats[1]+=1
			self.play_index(act[2],act[1])
			self.play_index(act[4],act[3])
			return self.bucks[act[4]].swap_from(act[1],act[3],self.bucks[act[2]])
	def act_buckinsert(self,act):
		if len(act)!=5:
			print(f"{self.curalg.name}: BUCKINSERT: incorrect act length {len(act)}: only length of 5 is allowed")
			return False
		elif act[2]>=len(self.bucks) or act[2]<0:
			print(f"{self.curalg.name}: BUCKINSERT: Bucket {act[2]} does not exist, max is {len(self.bucks)-1}")
			return False
		elif act[4]>=len(self.bucks) or act[4]<0:
			print(f"{self.curalg.name}: BUCKINSERT: Bucket {act[4]} does not exist, max is {len(self.bucks)-1}")
			return False
		else:
			self.stats[2]+=1
			self.play_index(act[2],act[1])
			return self.bucks[act[4]].insert_from(act[1],act[3],self.bucks[act[2]])
	def act_del_buck(self,act):
		if len(act)!=2:
			print(f"{self.curalg.name}: DEL_BUCK: incorrect act length {len(act)}: only length of 2 is allowed")
			return False
		elif self.bucks[act[1]].itemc!=0:
			print(f"{self.curalg.name}: DEL_BUCK on non-empty bucket {act[1]} with {self.bucks[act[1]].itemc} items")
			return False
		else:
			del self.bucks[act[1]]
			chunksize=WIDTH2/len(self.bucks)
			for i,buck in enumerate(self.bucks):
				buck.set_size(chunksize,HEIGHT)
				buck.set_pos(chunksize*i,0)
			self.stats[3]+=1
			return True
	def procact(self,act):
		if act!=PASS and type(act)!=tuple:
			print(f"{self.curalg.name}: Invalid act type: {type(act)}, only tuples and PASS are allowed")
			return False
		if act==PASS or act[0]==PASS:#pass
			self.stats[4]+=1
			return True
		elif act[0]==READ:#read value
			return self.act_read(act)
		elif act[0]==SWAP:#swap items
			return self.act_swap(act)
		elif act[0]==INSERT:#insert item to index
			return self.act_insert(act)
		elif act[0]==NEW_BUCK:#create new empty bucket
			return self.act_new_buck(act)
		elif act[0]==BUCKSWAP:#swap from bucket into another
			return self.act_buckswap(act)
		elif act[0]==BUCKINSERT:#insert from bucket into another
			return self.act_buckinsert(act)
		elif act[0]==DEL_BUCK:#delete bucket
			return self.act_del_buck(act)
		elif act[0]==FIN:#finished
			print(f"{self.curalg.name}: finished")
			return False
		else:
			print(f"{self.curalg.name}: Invalid act: {act}")
			return False
	def on_draw(self):
		global TIME,DTIME,TIMEC
		t=time()
		DTIME+=t-TIME
		TIMEC+=1
		if DTIME>=0.1:
			self.labels[0].setText("FPS:%02i/%02i"%(round(TIMEC/DTIME),self.fps))
			TIMEC=0
			DTIME=0
		TIME=t
		del t
		self.clear()
		for item in self.labels:#2000µs–5000µs
			item.draw()
		for item in self.btns:	#100µs
			item.draw()
		for item in self.rads:	#300µs
			item.draw()
		self.labels[-1].setText(algs[self.rads[0].getSelected()].desc)
		for item in self.edits:	#40µs
			item.draw()
		for item in self.bucks:	#1000µs–1500µs depending on how much inserting (heavy) vs swapping (light) vs reading (ultra light) is done and how many buckets are present
			item.draw()
		self.batch.draw()		#1500µs–2000µs
		pyglet.clock.tick()
	def on_mouse_press(self,x,y,button,modifiers):
		MP[button]=True
		if button==pgw.mouse.LEFT:
			for item in self.btns+self.rads+self.edits:
				ret=item.checkpress(x,y)
				if ret:
					return ret
		elif button==pgw.mouse.RIGHT:
			pass
		elif button==pgw.mouse.MIDDLE:
			pass
	def on_mouse_release(self,x,y,button,modifiers):
		MP[button]=False
	def on_key_press(self,symbol,modifiers):
		for item in self.edits+self.btns+self.rads:
			ret=item.checkKey(symbol)
			if ret:
				return ret
config = pyglet.gl.Config(sample_buffers=1, samples=8)#because items otherwise flicker when they're over 1000
window=GameWin(fullscreen=False,style=GameWin.WINDOW_STYLE_BORDERLESS,caption="Riedler Sound of Sorting",config=config,vsync=True,visible=False)
window.maximize()
window.set_visible(True)

WIDTH,HEIGHT=window.get_size()
WIDTH2=WIDTH/2
HEIGHT2=HEIGHT/2
SIZE=(WIDTH+HEIGHT)/2#only for scaling stuff
BTNWIDTH=WIDTH/10
BTNWIDTH2=BTNWIDTH/2
BTNHEIGHT=HEIGHT/20
BTNHEIGHT2=BTNHEIGHT/2

window.labels=[	Label(WIDTH2,HEIGHT,0,0,"FPS:00",window.batch,6),
				Label(WIDTH2,HEIGHT-15,0,0,"UPS:00/60",window.batch,6),
				Label(WIDTH2,HEIGHT-45,0,0,"Read:00",window.batch,6),
				Label(WIDTH2,HEIGHT-60,0,0,"Swap:00",window.batch,6),
				Label(WIDTH2,HEIGHT-75,0,0,"Insert:00",window.batch,6),
				Label(WIDTH2,HEIGHT-90,0,0,"Bucket:00",window.batch,6),
				Label(WIDTH2,HEIGHT-105,0,0,"Pass:00",window.batch,6),
				Label(WIDTH2,HEIGHT-120,0,0,"Randomness:00",window.batch,6),
				LabelMultiline(WIDTH2,0,0,0,"Sorting\nalgorithm\nDescription",window.batch,0)]
window.btns=[	ButtonSwitch(WIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Sort",window.batch,8,pressedText="Stop"),
			 	Button(WIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Shuffle",window.batch,8),
			 	Button(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Reverse",window.batch,8),
			 	ButtonFlipthrough(WIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Randomness: %i",[3,0,1,2],window.batch,8),
			 	Button(WIDTH,0,BTNWIDTH,BTNHEIGHT,"Quit",window.batch,2,pgw.key.ESCAPE)]
window.rads=[	RadioListPaged(WIDTH,HEIGHT-BTNHEIGHT*5,BTNWIDTH*2,BTNHEIGHT*13,[alg.name for alg in algs],12,window.batch,8,selected=0)]#radiolists
window.edits=[	IntEdit(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"Speed","100",window.batch,8),#Edits
			  	IntEdit(WIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"FPS/UPS","60",window.batch,8)]
window.bucks=[	Bucket(0,0,WIDTH2,HEIGHT,BUCKLEN,window.batch,maxps=window.edits[0].getNum())]#buckets
try:
	pyglet.app.run()
finally:
	print(*tuple(t.get() for t in profs))
