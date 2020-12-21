#!/usr/bin/python3
print("importing entities…")
from Entities import *
print("importing actions")
import Actions
from Actions import *
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
	varspace=None
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
		self.stats=[0,0,0,0,0,0,0]
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
			self.labels[1].set_text("UPS:%02i/%02i"%(round(self.upscc.getHz()),self.fps))
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
			self.labels[9].set_text("Randomness:%02i"%randomness)
			self.upscc.reset()
		if not self.edits[1].pressed:
			self.set_fps(self.edits[1].get_num())
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
			Shuffler.vals["q"]=self.btns[3].get_curval()
			self.start_algorithm(Shuffler,False)
		if not self.edits[0].pressed:
			self.set_speed(self.edits[0].get_num())
		self.check_itemc()
		self.process_alg_opts()
		if self.btns[0].pressed:
			if self.curalg==None:
				self.start_algorithm(algs[self.rads[0].get_selected()])
			for x in range(self.spd):
				try:
					act=next(self.gen)
				except StopIteration:
					act=FIN()
				except Exception as e:
					tbe.print_tb(e.__traceback__)
					print(f"{self.curalg.name}: {e}")
					act=FIN()
				if not self.procact(act):
					self.stop_algorithm()
					break
		elif self.curalg!=None:
			self.stop_algorithm()
		self.labels[2].set_text("Read:%02i"%self.stats[0])
		self.labels[3].set_text("Swap:%02i"%self.stats[1])
		self.labels[4].set_text("Insert:%02i"%self.stats[2])
		self.labels[5].set_text("Bucket:%02i"%self.stats[3])
		self.labels[6].set_text("Pass:%02i"%self.stats[4])
		self.labels[7].set_text("Pull:%02i"%self.stats[5])
		self.labels[8].set_text("Push:%02i"%self.stats[6])
		self.check_apls()
		self.play_all()
	def stop_algorithm(self,reset_buck0=True):
		self.btns[0].release()
		self.curalg=None
		self.gen=None
		if reset_buck0:
			self.squash_bucks()
			self.bucks[0].racts.clear()
			self.bucks[0].wacts.clear()
	def start_algorithm(self,alg,procopts=True):
		self.curalg=alg
		if procopts:
			for name,element in self.algui.items():
				if type(element)==IntEdit:
					val=element.get_num()
				elif type(element)==ButtonSwitch:
					val=element.pressed
				elif type(element)==ButtonFlipthrough:
					val=element.get_curindex()
				self.curalg.vals[name]=val
		self.curalg=self.curalg(BUCKLEN)
		self.avgupscc.reset()
		self.avgfpscc.reset()
		self.gen=self.wrap_around_gen(self.curalg.gen())
		self.stats=[0,0,0,0,0,0,0]
		self.btns[0].press()
	def wrap_around_gen(self,gen):
		for act in gen:
			if self.btns[6].pressed:
				if type(act)==INSERT:
					for a in act.insertless():
						yield a
					continue
				elif type(act)==BUCKINSERT:
					for a in act.insertless():
						yield a
					continue
			yield act
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
		self.bucks.append(Bucket(0,0,WIDTH2,HEIGHT,BUCKLEN,self.batch,maxps=self.edits[0].get_num()))
	def set_speed(self,spd):
		if spd!=self.spd:
			self.spd=spd
			for buck in self.bucks:
				buck.setmaxps(spd)
	def check_itemc(self):
		global BUCKLEN,COLORS
		itemc=self.edits[3].get_num()
		if itemc!=BUCKLEN:
			BUCKLEN=itemc
			COLORS=[color for i in range(BUCKLEN) for color in colorlamb(i/BUCKLEN)]
			self.reset()
	def process_alg_opts(self):
		selalg=self.rads[0].get_selected()
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
						self.algui[name]=ButtonSwitch(WIDTH-BTNWIDTH*(2+x),HEIGHT-BTNHEIGHT*(y+6),BTNWIDTH,BTNHEIGHT,opt[3],batch=self.batch,anch=8,pressed_text=opt[2])
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
		aconcur=self.edits[2].get_num()-self.aconcur
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
					if item==None:
						item=-BUCKLEN
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
	def procact(self,act):
		if not isinstance(act,BaseAction):
			print(f"{self.curalg.name}: Invalid act type: {type(act)}, only children of BaseAction are allowed")
			return False
		if not act.validate():
			return False
		if VERBOSE:
			print(f"{self.curalg.name}: {act}")
		return act.act()
	def on_draw(self):
		self.fpscc.checkpoint()#updates dt and tc and waits for next checkpoint
		self.avgfpscc.checkpoint()
		if self.fpscc.dt>=0.1:
			self.labels[0].set_text("FPS:%02i/%02i"%(round(self.fpscc.getHz()),self.fps))
			self.fpscc.reset()
		for item in self.labels:
			item.draw()
		for item in self.btns:
			item.draw()
		for item in self.rads:
			item.draw()
		self.labels[-1].set_text(algs[self.rads[0].get_selected()].desc)
		for item in self.edits:
			item.draw()
		for item in self.algui.values():
			item.draw()
		for item in self.bucks:#!!!!almost half of the total time is spent in this function!!!
			item.draw()
		self.batch.draw()
		pyglet.clock.tick()

logic=MainLogic(window)

logic.labels=[	Label(WIDTH2,HEIGHT,0,0,"FPS:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-15,0,0,"UPS:00/60",logic.batch,6),
				Label(WIDTH2,HEIGHT-45,0,0,"Read:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-60,0,0,"Swap:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-75,0,0,"Insert:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-90,0,0,"Bucket:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-105,0,0,"Pass:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-120,0,0,"Pull:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-135,0,0,"Push:00",logic.batch,6),
				Label(WIDTH2,HEIGHT-150,0,0,"Randomness:00",logic.batch,6),
				LabelMultiline(WIDTH2,0,0,0,"Sorting\nalgorithm\nDescription",logic.batch,0)]
logic.btns=[	ButtonSwitch(WIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Sort",logic.batch,8,pressed_text="Stop"),
				Button(WIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Shuffle",logic.batch,8),
				Button(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Reverse",logic.batch,8),
				ButtonFlipthrough(WIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Randomness: %i",[3,0,1,2],logic.batch,8),
				ButtonSwitch(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Audio: OFF",logic.batch,8,pressed_text="Audio: ON"),
				Button(WIDTH-BTNWIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Reset",logic.batch,8),
				ButtonSwitch(WIDTH-BTNWIDTH*2,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"No-Inserts: OFF",logic.batch,8,pressed_text="No-Inserts: ON"),
				Button(WIDTH,0,BTNWIDTH,BTNHEIGHT,"Quit",logic.batch,2,pgw.key.ESCAPE)]
logic.rads=[	RadioListPaged(WIDTH,HEIGHT-BTNHEIGHT*6,BTNWIDTH*2,BTNHEIGHT*12,[alg.name for alg in algs],11,logic.batch,8,selected=0)]
logic.edits=[	IntEdit(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"Speed",f"{logic.spd}",logic.batch,8,numrange=(1,None)),
				IntEdit(WIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"FPS/UPS","60",logic.batch,8,numrange=(1,None)),
				IntEdit(WIDTH,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Audio Concurrency","32",logic.batch,8,numrange=(0,None)),
				IntEdit(WIDTH-BTNWIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Item count",f"{BUCKLEN}",logic.batch,8,numrange=(2,None))]
logic.bucks=[	Bucket(0,0,WIDTH2,HEIGHT,BUCKLEN,logic.batch,maxps=logic.edits[0].get_num())]

logic.btns[4].press()

print("exposing logic to actions…")
Actions.logic=logic
Actions.Bucket=Bucket#because of one specific action needing that
print("starting main app…")
try:
	pyglet.app.run()
finally:
	if profs:
		print(*tuple(t.get() for t in profs))
print("goodbye")
