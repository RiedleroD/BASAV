#!/usr/bin/python3
from Entities import *
from Algs import *

class GameWin(pyglet.window.Window):
	def __init__(self,*args,**kwargs):
		self.push_handlers(KP)
		self.ft=0
		self.set_ft(1/60)
		self.curalg=None
		self.curval=None
		self.stats=[0,0,0,0,0]
		self.labels=[]
		self.btns=[]
		self.rads=[]
		self.edits=[]
		self.bucks=[]
		self.batch=pyglet.graphics.Batch()
		super().__init__(*args,**kwargs)
	def set_ft(self,ft):
		if ft!=self.ft:
			self.ft=ft
			pyglet.clock.unschedule(self.update)
			pyglet.clock.schedule_interval(self.update,ft)
	def update(self,dt):
		self.labels[1].setText("UPS:%02i/%02i"%(round(1/(dt)),1/self.ft))
		if not self.edits[1].pressed:
			self.set_ft(1/self.edits[1].getNum())
		if self.btns[-1].pressed:
			self.btns[3].release()
			sys.exit(0)
		if self.btns[2].pressed:
			self.btns[2].release()
			self.curalg=Reverser(self.bucks[0].itemc)
			self.stats=[0,0,0,0,0]
			self.btns[0].press()
		if self.btns[1].pressed:
			self.btns[1].release()
			self.curalg=Randomizer(self.bucks[0].itemc)
			self.stats=[0,0,0,0,0]
			self.btns[0].press()
		if self.btns[0].pressed:
			if self.curalg==None:
				self.curalg=algs[self.rads[0].getSelected()](self.bucks[0].itemc)
				self.stats=[0,0,0,0,0]
			for x in range(self.edits[0].getNum()):
				act=self.curalg.cycle(self.curval)
				if act==PASS:#pass
					self.stats[4]+=1
				elif act[0]==READ:#read value
					self.curval=self.bucks[act[2]].getvalue(act[1])
					self.stats[0]+=1
				elif act[0]==SWAP:#swap items
					self.bucks[act[3]].swapitems(act[1],act[2])
					self.stats[1]+=1
				elif act[0]==INSERT:#insert item to index
					self.bucks[act[3]].insertitem(act[1],act[2])
					self.stats[2]+=1
				elif act[0]==NEW_BUCK:#create new bucket
					self.bucks.append(Bucket(0,0,0,0,0))
					chunksize=WIDTH2/len(self.bucks)
					for i,buck in enumerate(self.bucks):
						buck.set_size(chunksize,HEIGHT)
						buck.set_pos(chunksize*i,0)
					if len(act)>1:
						self.bucks[-1].insert_from(act[1],0,self.bucks[act[2]])
					self.bucks[-1].maxic=self.bucks[0].maxic
					self.stats[3]+=1
				elif act[0]==BUCKSWAP:#swap from bucket into another
					#(BUCKSWAP,x_i,x_buck,y_i,y_buck)
					#(0       ,1   ,2    ,3  ,4     )
					self.bucks[act[4]].swap_from(act[1],act[3],self.bucks[act[2]])
					self.stats[1]+=1
				elif act[0]==BUCKINSERT:#insert from bucket into another
					#(BUCKINSERT,src_i,src_buck,dst_i,dst_buck)
					#(0         ,1    ,2       ,3    ,4       )
					self.bucks[act[4]].insert_from(act[1],act[3],self.bucks[act[2]])
					self.stats[2]+=1
				elif act[0]==DEL_BUCK:#delete bucket
					if self.bucks[act[1]].itemc==0:
						del self.bucks[act[1]]
						chunksize=WIDTH2/len(self.bucks)
						for i,buck in enumerate(self.bucks):
							buck.set_size(chunksize,HEIGHT)
							buck.set_pos(chunksize*i,0)
					else:
						raise Exception("Unexpected call to DEL_BUCK for non-empty bucket")
					self.stats[3]+=1
				elif act[0]==FIN:#finished
					self.btns[0].release()
					self.curalg=None
					self.bucks[0].racts.clear()
					self.bucks[0].wacts.clear()
					self.bucks[0].rendered=False
					break
		elif self.curalg!=None:
			self.curalg=None
			del self.bucks[:]
			self.bucks.append(Bucket(0,0,WIDTH2,HEIGHT,256))
		self.labels[2].setText("Read:%02i"%self.stats[0])
		self.labels[3].setText("Swap:%02i"%self.stats[1])
		self.labels[4].setText("Insert:%02i"%self.stats[2])
		self.labels[5].setText("Bucket:%02i"%self.stats[3])
		self.labels[6].setText("Pass:%02i"%self.stats[4])
	def on_draw(self):
		global TIME
		t=time()
		self.labels[0].setText("FPS:%02i"%(round(1/(t-TIME))))#for some reason, pyglet.clock.tick() doesn't return the correct time, so I had to calculate it manually
		TIME=t
		del t
		self.clear()
		for item in self.labels+self.btns+self.rads+self.edits+self.bucks:
			item.draw()
		self.batch.draw()
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

window=GameWin(fullscreen=False,style=GameWin.WINDOW_STYLE_BORDERLESS,caption="Riedler Sound of Sorting",vsync=True,visible=False)
screen=window.display.get_default_screen()
window.set_size(screen.width,screen.height)
window.set_visible(True)

WIDTH,HEIGHT=window.get_size()
WIDTH2=WIDTH/2
HEIGHT2=HEIGHT/2
SIZE=(WIDTH+HEIGHT)/2#only for scaling stuff
BTNWIDTH=WIDTH/10
BTNWIDTH2=BTNWIDTH/2
BTNHEIGHT=HEIGHT/20
BTNHEIGHT2=BTNHEIGHT/2

window.labels=[	Label(WIDTH2,HEIGHT,0,0,"FPS:00",6,batch=window.batch),
				Label(WIDTH2,HEIGHT-15,0,0,"UPS:00/60",6,batch=window.batch),
				Label(WIDTH2,HEIGHT-45,0,0,"Read:00",6,batch=window.batch),
				Label(WIDTH2,HEIGHT-60,0,0,"Swap:00",6,batch=window.batch),
				Label(WIDTH2,HEIGHT-75,0,0,"Insert:00",6,batch=window.batch),
				Label(WIDTH2,HEIGHT-90,0,0,"Bucket:00",6,batch=window.batch),
				Label(WIDTH2,HEIGHT-105,0,0,"Pass:00",6,batch=window.batch)]
window.btns=[	ButtonSwitch(WIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Sort",8,pressedText="Stop",batch=window.batch),
			 	Button(WIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Shuffle",8,batch=window.batch),
			 	Button(WIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Reverse",8,batch=window.batch),
			 	Button(WIDTH,0,BTNWIDTH,BTNHEIGHT,"Quit",2,pgw.key.ESCAPE,batch=window.batch)]
window.rads=[	RadioList(WIDTH,HEIGHT-BTNHEIGHT*6,BTNWIDTH,BTNHEIGHT*len(algs),[alg.name for alg in algs],8,selected=0,batch=window.batch)]#radiolists
window.edits=[	IntEdit(WIDTH,HEIGHT-BTNHEIGHT*3,BTNWIDTH,BTNHEIGHT,"Speed","100",8,batch=window.batch),#Edits
			  	IntEdit(WIDTH,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"FPS","60",8,batch=window.batch)]
window.bucks=[	Bucket(0,0,WIDTH2,HEIGHT,256)]#buckets

pyglet.app.run()
