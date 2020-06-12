#!/usr/bin/python3
import pyglet
from pyglet import window as pgw
from Entities import *
from Algs import *

Es= [
	 [Label(WIDTH2,HEIGHT,0,0,"FPS:00",6),
	  Label(WIDTH2,HEIGHT-15,0,0,"UPS:00",6)],
	 [ButtonSwitch(WIDTH,HEIGHT,BTNWIDTH,BTNHEIGHT,"Sort",8,pressedText="Stop"),
	  Button(WIDTH,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Shuffle",8),
	  Button(WIDTH,HEIGHT-BTNHEIGHT*2,BTNWIDTH,BTNHEIGHT,"Reverse",8),
	  Button(WIDTH,0,BTNWIDTH,BTNHEIGHT,"Quit",2,pgw.key.ESCAPE)],
	 [],#radios
	 [],#Textedits
	 [Bucket(0,0,WIDTH2,HEIGHT,256)]#buckets
	]

curalg=None
curval=None

def on_cycle(dt):
	global Es,curalg,curval
	Es[0][1].setText("UPS:%02i"%(round(1/(dt))))
	btns=Es[1]
	if btns[-1].pressed:
		btns[3].release()
		sys.exit(0)
	if btns[2].pressed:
		btns[2].release()
		Es[4][0].reverse()
		curalg=None
	if btns[1].pressed:
		Es[4][0].shuffle()
		btns[1].release()
		curalg=None
	if btns[0].pressed:
		bucks=Es[4]
		if curalg==None:
			curalg=MergeSort(bucks[0].itemc)
		for x in range(100):
			act=curalg.cycle(curval)
			if act==None:#pass
				pass
			elif act[0]==READ:#read value
				curval=bucks[act[2]].getvalue(act[1])
			elif act[0]==SWAP:#swap items
				bucks[act[3]].swapitems(act[1],act[2])
			elif act[0]==INSERT:#insert item to index
				bucks[act[3]].insertitem(act[1],act[2])
			elif act[0]==NEW_BUCK:#create new bucket
				bucks.append(Bucket(0,0,0,0,0))
				chunksize=WIDTH2/len(Es[4])
				for i,buck in enumerate(Es[4]):
					buck.set_size(chunksize,HEIGHT)
					buck.set_pos(chunksize*i,0)
				bucks[-1].insert_from(act[1],0,bucks[act[2]])
			elif act[0]==BUCKINSERT:#insert from bucket into another
				#(BUCKINSERT,src_i,src_buck,dst_i,dst_buck)
				#(0         ,1    ,2       ,3    ,4       )
				bucks[act[4]].insert_from(act[1],act[3],bucks[act[2]])
			elif act[0]==DEL_BUCK:#delete bucket
				if bucks[act[1]].itemc==0:
					del bucks[act[1]]
					chunksize=WIDTH2/len(Es[4])
					for i,buck in enumerate(Es[4]):
						buck.set_size(chunksize,HEIGHT)
						buck.set_pos(chunksize*i,0)
				else:
					raise Exception("Unexpected call to DEL_BUCK for non-empty bucket")
			elif act[0]==FIN:#finished
				btns[0].release()
				curalg=None
				bucks[0].racts.clear()
				bucks[0].wacts.clear()
				bucks[0].rendered=False
				break

@window.event
def on_draw():
	global Es,TIME
	t=time()
	Es[0][0].setText("FPS:%02i"%(round(1/(t-TIME))))
	TIME=t
	del t
	window.clear()
	for div in Es:	#for btns, guys, stageparts, ect. in Es
		for item in div:
			item.draw()		#draw the darn thing

@window.event
def on_mouse_press(x,y,button,modifiers):
	MP[button]=True
	if button==pgw.mouse.LEFT:
		for btn in Es[1]:
			btn.checkpress(x,y)
		for rad in Es[2]:
			rad.checkpress(x,y)
	elif button==pgw.mouse.RIGHT:
		pass
	elif button==pgw.mouse.MIDDLE:
		pass

@window.event
def on_mouse_release(x,y,button,modifiers):
	MP[button]=False

@window.event
def on_key_press(symbol,modifiers):
	res=None
	for btn in Es[1]:
		ret=btn.checkKey(symbol)
		if ret:
			res=ret
	return res

#event_logger = pgw.event.WindowEventLogger()
#window.push_handlers(event_logger)
window.push_handlers(KP)
pyglet.clock.schedule_interval(on_cycle,1/60)

pyglet.app.run()
