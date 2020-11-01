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
		if self.tc==0 or self.dt==0:
			return 0
		return self.tc/self.dt

print("defining main logic…")

class MainLogic():
	spd=20
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
		self.selalg=None#currently selected algorithm (for algui)
		self.algui={}#ui elements for algorithm
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
		if self.btns[5].pressed:
			self.reset()
			self.btns[5].release()
		if self.btns[2].pressed:
			self.btns[2].release()
			self.start_algorithm(Reverser)
		if self.btns[1].pressed:
			self.btns[1].release()
			self.start_algorithm(shufflers[self.btns[3].getCurval()])
		if not self.edits[0].pressed:
			self.set_speed(self.edits[0].getNum())
		self.check_itemc()
		self.process_alg_opts()
		if self.btns[0].pressed:
			if self.curalg==None:
				self.start_algorithm(algs[self.rads[0].getSelected()])
			for x in range(self.spd):
				try:
					act=next(self.gen)
				except StopIteration:
					act=(FIN,)
				except Exception as e:
					tbe.print_tb(e.__traceback__)
					print(f"{self.curalg.name}: {e}")
					act=(FIN,)
				if not self.procact(act):
					self.stop_algorithm()
					break
		elif self.curalg!=None:
			self.curalg=None
			self.gen=None
		self.labels[2].setText("Read:%02i"%self.stats[0])
		self.labels[3].setText("Swap:%02i"%self.stats[1])
		self.labels[4].setText("Insert:%02i"%self.stats[2])
		self.labels[5].setText("Bucket:%02i"%self.stats[3])
		self.labels[6].setText("Pass:%02i"%self.stats[4])
		self.check_apls()
		self.play_all()
	def stop_algorithm(self,reset_buck0=True):
		self.btns[0].release()
		self.curalg=None
		self.gen=None
		if reset_buck0:
			self.bucks[0].racts.clear()
			self.bucks[0].wacts.clear()
			self.bucks[0].rendered=False
	def start_algorithm(self,alg):
		self.curalg=alg
		self.squash_bucks()
		for name,element in self.algui.items():
			if type(element)==IntEdit:
				val=element.getNum()
			elif type(element)==ButtonSwitch:
				val=element.pressed
			elif type(element)==ButtonFlipthrough:
				val=element.getCurIndex()
			self.curalg.vals[name]=val
		self.curalg=self.curalg(BUCKLEN)
		self.avgupscc.reset()
		self.avgfpscc.reset()
		self.gen=self.curalg.gen()
		self.stats=[0,0,0,0,0]
		self.btns[0].press()
	def squash_bucks(self):
		if len(self.bucks)>1:
			for buck in range(1,len(self.bucks)):
				self.bucks[0].items.extend(self.bucks[1].items)
				del self.bucks[1]
			self.bucks[0].itemc=BUCKLEN
			self.bucks[0].render_colors()
			self.bucks[0].set_size(WIDTH2,HEIGHT)
	def reset(self):
		self.stop_algorithm(False)
		self.bucks.clear()
		self.bucks.append(Bucket(0,0,WIDTH2,HEIGHT,BUCKLEN,self.batch,maxps=self.edits[0].getNum()))
	def set_speed(self,spd):
		if spd!=self.spd:
			self.spd=spd
			for buck in self.bucks:
				buck.setmaxps(spd)
	def check_itemc(self):
		global BUCKLEN,COLORS
		itemc=self.edits[3].getNum()
		if itemc!=BUCKLEN:
			BUCKLEN=itemc
			COLORS=[color for i in range(BUCKLEN) for color in colorlamb(i/BUCKLEN)]
			self.reset()
	def process_alg_opts(self):
		selalg=self.rads[0].getSelected()
		if selalg!=self.selalg:
			self.selalg=selalg
			self.algui.clear()
			curalg=algs[selalg]
			x=0
			y=0
			for name,opt in curalg.opts.items():
				if y>10:
					if x>0:
						continue
					else:
						x+=1
						y=0
				
				if type(opt) not in (tuple,list,set):
					print(f"{curalg.name}: option {name} initialized with invalid value {opt}")
					curalg.vals[name]=None
				elif len(opt)==0:
					print(f"{curalg.name}: empty option {name} found")
					curalg.vals[name]=None
				elif opt[0]==int:
					if len(opt)!=5 or \
						type(opt[1])!=int or \
						type(opt[2]) not in (int,type(None)) or \
						type(opt[3]) not in (int,type(None)) or \
						type(opt[4])!=str:
						
						print(f"{curalg.name}: option {name} with type int doesn't match pattern (type,int,int|None,int|None,str)")
						curalg.vals[name]=None
					elif (opt[2]!=None and opt[2]>opt[1]) or (opt[3]!=None and opt[3]<=opt[1]):#if default not in input boudaries
						print(f"{curalg.name}: option {name} with type int has a default value {opt[1]} outside of its boundaries {opt[2]}:{opt[3]}")
					else:
						self.algui[name]=IntEdit(WIDTH-BTNWIDTH*(2+x),HEIGHT-BTNHEIGHT*(y+6),BTNWIDTH,BTNHEIGHT,opt[4],opt[1],batch=self.batch,anch=8,numrange=(opt[2],opt[3]))
						y+=1
				elif opt[0]==bool:
					if len(opt)!=4 or \
						type(opt[1])!=bool or \
						type(opt[2])!=str or \
						type(opt[3])!=str:
						
						print(f"{curalg.name}: option {name} with type bool doesn't match pattern (type,bool,str,str)")
						curalg.vals[name]=None
					else:
						self.algui[name]=ButtonSwitch(WIDTH-BTNWIDTH*(2+x),HEIGHT-BTNHEIGHT*(y+6),BTNWIDTH,BTNHEIGHT,opt[3],batch=self.batch,anch=8,pressedText=opt[2])
						y+=1
				elif opt[0]==list:
					if len(opt)!=4 or \
						type(opt[1])!=int or \
						type(opt[2]) not in (list,tuple,set) or \
						any(type(val)!=str for val in opt[2]) or \
						type(opt[3])!=str:
						
						print(f"{curalg.name}: option {name} with type list doesn't match pattern (type,int,(str,str,…),str)")
						curalg.vals[name]=None
					elif len(opt[2])<=opt[1]:
						print(f"{curalg.name}: option {name} with type list has a default value {opt[2]} outside of its boundaries 0:{len(opt[2])}")
						curalg.vals[name]=None
					elif len(opt[2])<2:
						print(f"{curalg.name}: option {name} with type list only has {len(opt[2])} possible values, while at least 2 are needed.")
						curalg.vals[name]=None
					elif opt[3].count("%")!=1 or opt[3].count("%s")!=1:
						print(f"{curalg.name}: option {name} with type list has an invalid format string '{opt[3]}' specified. Exactly one %s has to exist.")
					else:
						self.algui[name]=ButtonFlipthrough(WIDTH-BTNWIDTH*(2+x),HEIGHT-BTNHEIGHT*(y+6),BTNWIDTH,BTNHEIGHT,opt[3],opt[2],batch=self.batch,anch=8,default=opt[1])
						y+=1
	def check_apls(self):
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
		if VERBOSE:
			print(f"{self.curalg.name}: {act}")
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
		for item in self.algui.values():
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
				Button(WIDTH-BTNWIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Reset",logic.batch,8),
				Button(WIDTH,0,BTNWIDTH,BTNHEIGHT,"Quit",logic.batch,2,pgw.key.ESCAPE)]
logic.rads=[	RadioListPaged(WIDTH,HEIGHT-BTNHEIGHT*6,BTNWIDTH*2,BTNHEIGHT*12,[alg.name for alg in algs],11,logic.batch,8,selected=0)]
logic.edits=[	IntEdit(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"Speed",f"{logic.spd}",logic.batch,8,numrange=(1,None)),
				IntEdit(WIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"FPS/UPS","60",logic.batch,8,numrange=(1,None)),
				IntEdit(WIDTH,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Audio Concurrency","32",logic.batch,8,numrange=(0,None)),
				IntEdit(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Item count",f"{BUCKLEN}",logic.batch,8,numrange=(2,None))]
logic.bucks=[	Bucket(0,0,WIDTH2,HEIGHT,BUCKLEN,logic.batch,maxps=logic.edits[0].getNum())]

logic.btns[4].press()

try:
	print("starting main app…")
	pyglet.app.run()
finally:
	if profs:
		print(*tuple(t.get() for t in profs))
	print("goodbye")
