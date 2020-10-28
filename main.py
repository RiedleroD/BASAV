#!/usr/bin/python3
print("importing entities…")
from Entities import *
print("importing algorithms…")
from Algs import *
print("importing various other libraries…")
import traceback as tbe
from collections import deque

class ClockCounter():
	def __init__(self):
		self.reset()
	def cycle(self,dt):
		self.dt+=dt
		self.tc+=1
	def start(self):
		self.st=time()
	def checkpoint(self):
		t=time()
		self.dt+=t-self.st
		self.tc+=1
		self.st=t
	def end(self):
		self.dt+=time()-self.st
		self.tc+=1
	def reset(self):
		self.dt=0
		self.tc=0
	def getHz(self):
		return self.tc/self.dt

print("defining main logic…")

class MainLogic():
	def __init__(self,win):
		self.window=win
		self.window.push_handlers(KP)
		self.window.set_logic(self)
		self.upscc=ClockCounter()
		self.fpscc=ClockCounter()
		self.fpscc.start()
		self.avgupscc=ClockCounter()
		self.avgfpscc=ClockCounter()
		self.avgfpscc.start()
		self.fps=0
		self.set_fps(60)#set_fps needs self.fps to exist & sets more than that, so I have to do both here.
		self.curalg=None
		self.curval=None
		self.gen=None
		self.aconcur=0
		self.playing=True
		self.stats=[0,0,0,0,0]
		self.labels=[]
		self.btns=[]
		self.rads=[]
		self.edits=[]
		self.bucks=[]
		self.toplay=deque()
		self.apls=[]#audio players
		self.batch=pyglet.graphics.Batch()
	def set_fps(self,fps):
		if fps!=self.fps and fps>0:
			self.fps=fps
			pyglet.clock.unschedule(self.update)
			pyglet.clock.schedule_interval(self.update,1/fps)
	def update(self,dt):
		self.upscc.cycle(dt)
		self.avgupscc.cycle(dt)
		if self.upscc.dt>=0.1:
			#update ups counter
			self.labels[1].setText("UPS:%02i/%02i"%(round(self.upscc.getHz()),self.fps))
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
			self.upscc.reset()
		if not self.edits[1].pressed:
			self.set_fps(self.edits[1].getNum())
		if self.btns[-1].pressed:
			self.btns[3].release()
			sys.exit(0)
		if self.btns[2].pressed:
			self.btns[2].release()
			self.curalg=Reverser(self.bucks[0].itemc)
			self.avgupscc.reset()
			self.avgfpscc.reset()
			self.gen=self.curalg.gen()
			self.stats=[0,0,0,0,0]
			self.btns[0].press()
		if self.btns[1].pressed:
			self.btns[1].release()
			self.curalg=shufflers[self.btns[3].getCurval()](self.bucks[0].itemc)
			self.avgupscc.reset()
			self.avgfpscc.reset()
			self.gen=self.curalg.gen()
			self.stats=[0,0,0,0,0]
			self.btns[0].press()
		aconcur=self.edits[2].getNum()-self.aconcur
		self.aconcur+=aconcur
		if aconcur>0:
			for i in range(aconcur):
				apl=pyglet.media.Player()
				apl.queue(AUDIO)
				apl.volume=0
				apl.loop=True
				apl.play()
				self.apls.append(apl)
		elif aconcur<0:
			for apl in self.apls[aconcur:]:
				apl.next_source()
				apl.delete()
				self.apls.remove(apl)
		if self.btns[0].pressed:
			if self.curalg==None:
				self.curalg=algs[self.rads[0].getSelected()](self.bucks[0].itemc)
				self.avgupscc.reset()
				self.avgfpscc.reset()
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
		if self.btns[4].pressed and self.toplay:
			for apl in self.apls:
				if not self.toplay:
					apl.volume=0
				else:
					item=self.toplay.pop()
					apl.volume=1/self.aconcur
					apl.pitch=1+item/BUCKLEN
				if not self.playing:
					apl.play()
			self.playing=True
		elif self.playing:
			for apl in self.apls:
				apl.pause()
			self.playing=False
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
			print(f"{self.curalg.name}: finished with average fps {self.avgfpscc.getHz():.0f} and ups {self.avgupscc.getHz():.0f}")
			return False
		else:
			print(f"{self.curalg.name}: Invalid act: {act}")
			return False
	def on_draw(self):
		self.fpscc.checkpoint()#updates dt and tc and waits for next checkpoint
		self.avgfpscc.checkpoint()
		if self.fpscc.dt>=0.1:
			self.labels[0].setText("FPS:%02i/%02i"%(round(self.fpscc.getHz()),self.fps))
			self.fpscc.reset()
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

logic=MainLogic(window)

logic.labels=[	Label(WIDTH2,HEIGHT,0,0,"FPS:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-15,0,0,"UPS:00/60",logic.batch,6),
				Label(WIDTH2,HEIGHT-45,0,0,"Read:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-60,0,0,"Swap:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-75,0,0,"Insert:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-90,0,0,"Bucket:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-105,0,0,"Pass:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-120,0,0,"Randomness:00",logic.batch,6),
				LabelMultiline(WIDTH2,0,0,0,"Sorting\nalgorithm\nDescription",logic.batch,0)]
logic.btns=[	ButtonSwitch(WIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Sort",logic.batch,8,pressedText="Stop"),
				Button(WIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Shuffle",logic.batch,8),
				Button(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Reverse",logic.batch,8),
				ButtonFlipthrough(WIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Randomness: %i",[3,0,1,2],logic.batch,8),
				ButtonSwitch(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Audio: OFF",logic.batch,8,pressedText="Audio: ON"),
				Button(WIDTH,0,BTNWIDTH,BTNHEIGHT,"Quit",logic.batch,2,pgw.key.ESCAPE)]
logic.rads=[	RadioListPaged(WIDTH,HEIGHT-BTNHEIGHT*6,BTNWIDTH*2,BTNHEIGHT*12,[alg.name for alg in algs],11,logic.batch,8,selected=0)]
logic.edits=[	IntEdit(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"Speed","20",logic.batch,8),
				IntEdit(WIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"FPS/UPS","60",logic.batch,8),
				IntEdit(WIDTH,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Audio Concurrency",f"{32}",logic.batch,8)]
logic.bucks=[	Bucket(0,0,WIDTH2,HEIGHT,BUCKLEN,logic.batch,maxps=logic.edits[0].getNum())]

logic.btns[4].press()

try:
	print("starting main app…")
	pyglet.app.run()
finally:
	if profs:
		print(*tuple(t.get() for t in profs))
	print("goodbye")
