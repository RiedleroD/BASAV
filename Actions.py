#!/usr/bin/python3
class BaseAction:
	def __init__(self):
		pass
	def validate(self):
		return True
	def act(self):
		return True
	def __str__(self):
		return "BaseAction()"
	def __repr__(self):
		return self.__str__()
#PASS()					→ does nothing for a cycle
class PASS(BaseAction):
	def __str__(self):
		return "PASS()"
#READ(x,b)				→ reads value of item x in bucket i and puts it into the value param next cycle
class READ(BaseAction):
	def __init__(self,x,b):
		self.x=x
		self.b=b
	def validate(self):
		if not 0<=self.b<len(logic.bucks):
			print(f"{logic.curalg.name}: READ: b={self.b} is out of range(0,{len(logic.bucks)})")
			return False
		elif not 0<=self.x<logic.bucks[self.b].itemc:
			print(f"{logic.curalg.name}: READ: x={self.x} is out of range(0,{logic.bucks[self.b].itemc}) in bucket {self.b}")
			return False
		else:
			return True
	def act(self):
		rv,logic.curval=logic.bucks[self.b].getvalue(self.x)
		logic.stats[0]+=1
		logic.curalg.v=logic.curval
		logic.play(logic.curval)
		return rv
	def __str__(self):
		return f"READ(x={self.x},b={self.b})"
#SWAP(x,y,b)			→ swaps item x with item y in bucket b
class SWAP(BaseAction):
	def __init__(self,x,y,b):
		self.x=x
		self.y=y
		self.b=b
	def validate(self):
		if not 0<=self.b<len(logic.bucks):
			print(f"{logic.curalg.name}: SWAP: b={self.b} is out of range(0,{len(logic.bucks)})")
			return False
		elif not 0<=self.x<logic.bucks[self.b].itemc:
			print(f"{logic.curalg.name}: SWAP: x={self.x} is out of range(0,{logic.bucks[self.b].itemc}) in bucket {self.b}")
			return False
		elif not logic.bucks[self.b].itemc>self.y>=0:
			print(f"{logic.curalg.name}: SWAP: y={self.y} is out of range(0,{logic.bucks[self.b].itemc}) in bucket {self.b}")
			return False
		else:
			return True
	def act(self):
		logic.stats[1]+=1
		logic.play_index(self.b,self.x)
		logic.play_index(self.b,self.y)
		return logic.bucks[self.b].swapitems(self.x,self.y)
	def __str__(self):
		return f"SWAP(x={self.x},y={self.y},b={self.b})"
#INSERT(x,y,b)			→ inserts item x at index y and pushes all items between one index to the old index
class INSERT(BaseAction):
	def __init__(self,x,y,b):
		self.x=x
		self.y=y
		self.b=b
	def validate(self):
		if not 0<=self.b<len(logic.bucks):
			print(f"{logic.curalg.name}: INSERT: b={self.b} is out of range(0,{len(logic.bucks)})")
			return False
		elif not 0<=self.x<logic.bucks[self.b].itemc:
			print(f"{logic.curalg.name}: INSERT: x={self.x} is out of range(0,{logic.bucks[self.b].itemc}) in bucket {self.b}")
			return False
		elif not logic.bucks[self.b].itemc>=self.y>=0:
			print(f"{logic.curalg.name}: INSERT: y={self.y} is out of range(0,{logic.bucks[self.b].itemc}) in bucket {self.b}")
			return False
		else:
			return True
	def act(self):
		logic.stats[2]+=1
		logic.play_index(self.b,self.x)
		return logic.bucks[self.b].insertitem(self.x,self.y)
	def insertless(self):
		if self.x<self.y:
			for i in range(self.x,self.y):
				yield SWAP(i,i+1,self.b)
		else:
			for i in range(self.x,self.y,-1):
				yield SWAP(i-1,i,self.b)
	def __str__(self):
		return f"INSERT(x={self.x},y={self.y},b={self.b})"
#NEW_BUCK()				→ creates a new bucket
class NEW_BUCK(BaseAction):
	def act(self):
		chunksize=logic.window.width/((len(logic.bucks)+1)*2)
		for i,buck in enumerate(logic.bucks):
			buck.set_pos(chunksize*i,0)
			buck.set_size(chunksize,logic.window.height)
		logic.bucks.append(Bucket(logic.window.width/2-chunksize,0,chunksize,logic.window.height,-logic.bucks[0].maxic,logic.batch,maxps=logic.edits[0].getNum()))
		logic.stats[3]+=1
		return True
	def __str__(self):
		return "NEW_BUCK()"
#BUCKSWAP(x,bx,y,by)	→ swaps item x in bucket bx to index y in bucket by
class BUCKSWAP(BaseAction):
	def __init__(self,x,bx,y,by):
		self.x=x
		self.bx=bx
		self.y=y
		self.by=by
	def validate(self):
		if not 0<=self.bx<len(logic.bucks):
			print(f"{logic.curalg.name}: BUCKSWAP: bx={self.bx} is out of range(0,{len(logic.bucks)})")
			return False
		elif not len(logic.bucks)>self.by>=0:
			print(f"{logic.curalg.name}: BUCKSWAP: by={self.by} is out of range(0,{len(logic.bucks)})")
			return False
		elif not 0<=self.x<logic.bucks[self.bx].itemc:
			print(f"{logic.curalg.name}: BUCKSWAP: x={self.x} is out of range(0,{logic.bucks[self.bx].itemc}) in bucket {self.bx}")
			return False
		elif not logic.bucks[self.by].itemc>self.y>=0:
			print(f"{logic.curalg.name}: BUCKSWAP: y={self.y} is out of range(0,{logic.bucks[self.by].itemc}) in bucket {self.by}")
			return False
		else:
			return True
	def act(self):
		logic.stats[1]+=1
		logic.play_index(self.bx,self.x)
		logic.play_index(self.by,self.y)
		return logic.bucks[self.by].swap_from(self.x,self.y,logic.bucks[self.bx])
	def __str__(self):
		return f"BUCKSWAP(x={self.x},bx={self.bx},y={self.y},by={self.by})"
#BUCKINSERT(x,bx,y,by)	→ inserts item x in bucket bx at index y in bucket by
class BUCKINSERT(BaseAction):
	def __init__(self,x,bx,y,by):
		self.x=x
		self.bx=bx
		self.y=y
		self.by=by
	def validate(self):
		if not 0<=self.bx<len(logic.bucks):
			print(f"{logic.curalg.name}: BUCKINSERT: bx={self.bx} is out of range(0,{len(logic.bucks)})")
			return False
		elif not len(logic.bucks)>self.by>=0:
			print(f"{logic.curalg.name}: BUCKINSERT: by={self.by} is out of range(0,{len(logic.bucks)})")
			return False
		elif not 0<=self.x<=logic.bucks[self.bx].itemc:
			print(f"{logic.curalg.name}: BUCKINSERT: x={self.x} is out of range(0,{logic.bucks[self.bx].itemc+1}) in bucket {self.bx}")
			return False
		elif not logic.bucks[self.by].itemc>=self.y>=0:
			print(f"{logic.curalg.name}: BUCKINSERT: y={self.y} is out of range(0,{logic.bucks[self.by].itemc+1}) in bucket {self.by}")
			return False
		else:
			return True
	def act(self):
		logic.stats[2]+=1
		logic.play_index(self.bx,self.x)
		return logic.bucks[self.by].insert_from(self.x,self.y,logic.bucks[self.bx])
	def insertless(self):
		if self.bx==self.by:
			for a in INSERT(self.x,self.y,self.bx).insertless():
				yield a
		else:
			for a in INSERT(self.x,logic.bucks[self.bx].itemc-1,self.bx).insertless():
				yield a
			yield PULSH(self.bx,self.by)
			for a in INSERT(logic.bucks[self.by].itemc-1,self.y,self.by).insertless():
				yield a
	def __str__(self):
		return f"BUCKINSERT(x={self.x},bx={self.bx},y={self.y},by={self.by})"
#DEL_BUCK(b)			→ destroys bucket b (only empty buckets can be destroyed)
class DEL_BUCK(BaseAction):
	def __init__(self,b):
		self.b=b
	def validate(self):
		if not 0<=self.b<len(logic.bucks):
			print(f"{logic.curalg.name}: DEL_BUCK: b={self.b} is out of range(0,{len(logic.bucks)})")
			return False
		elif logic.bucks[self.b].itemc:
			print(f"{logic.curalg.name}: DEL_BUCK: b={self.b} targets a non-empty bucket with {logic.bucks[self.b].itemc} items left")
			return False
		else:
			return True
	def act(self):
		del logic.bucks[self.b]
		chunksize=logic.window.width/(len(logic.bucks)*2)
		for i,buck in enumerate(logic.bucks):
			buck.set_size(chunksize,logic.window.height)
			buck.set_pos(chunksize*i,0)
		logic.stats[3]+=1
		return True
	def __str__(self):
		return f"DEL_BUCK(b={self.b})"
#FIN()					→ finish (not necessary anymore, StopIteration finishes too)
class FIN(BaseAction):
	def act(self):
		return False
	def __str__(self):
		return "FIN()"
#PULL(b)				→ pulls item from bucket b into a one-item variable space
class PULL(BaseAction):
	def __init__(self,b):
		self.b=b
	def validate(self):
		if not 0<=self.b<len(logic.bucks):
			print(f"{logic.curalg.name}: PULL: b={self.b} is out of range(0,{len(logic.bucks)})")
			return False
		elif logic.varspace!=None:
			print(f"{logic.curalg.name}: PULL: varspace isn't empty")
			return False
		elif not logic.bucks[self.b].itemc:
			print(f"{logic.curalg.name}: PULL: b={self.b} targets a non-empty bucket with {logic.bucks[self.b].itemc} items left")
			return False
		else:
			return True
	def act(self):
		rv,var=logic.bucks[self.b].pull_item()
		logic.play(var)
		logic.stats[5]+=1
		if rv:
			logic.varspace=var
		return rv
	def __str__(self):
		return f"PULL(b={self.b})"
#PUSH(b)				→ pushes item from the one-item variable space onto bucket b
class PUSH(BaseAction):
	def __init__(self,b):
		self.b=b
	def validate(self):
		if not 0<=self.b<len(logic.bucks):
			print(f"{logic.curalg.name}: PUSH: b={self.b} is out of range(0,{len(logic.bucks)})")
			return False
		elif logic.varspace==None:
			print(f"{logic.curalg.name}: PUSH: varspace is empty")
			return False
		else:
			return True
	def act(self):
		rv=logic.bucks[self.b].push_item(logic.varspace)
		logic.play(logic.varspace)
		logic.stats[6]+=1
		if rv:
			logic.varspace=None
		return rv
	def __str__(self):
		return f"PUSH(b={self.b})"
#PULSH(bx,by)			→ pulls item from bucket bx and pushes it onto bucket by
class PULSH(BaseAction):
	def __init__(self,bx,by):
		self.bx=bx
		self.by=by
	def validate(self):
		if not 0<=self.bx<len(logic.bucks):
			print(f"{logic.curalg.name}: PULSH: bx={self.bx} is out of range(0,{len(logic.bucks)})")
			return False
		elif not len(logic.bucks)>self.by>=0:
			print(f"{logic.curalg.name}: PULSH: by={self.by} is out of range(0,{len(logic.bucks)})")
			return False
		elif logic.varspace!=None:
			print(f"{logic.curalg.name}: PULSH: varspace isn't empty")
			return False
		elif not logic.bucks[self.bx].itemc:
			print(f"{logic.curalg.name}: PULL: bx={self.bx} targets a non-empty bucket with {logic.bucks[self.b].itemc} items left")
			return False
		else:
			return True
	def act(self):
		rv,var=logic.bucks[self.bx].pull_item()
		logic.play(var)
		logic.stats[5]+=1
		logic.stats[6]+=1
		if rv:
			return logic.bucks[self.by].push_item(var)
		else:
			return rv
	def __str__(self):
		return f"PULSH(bx={self.bx},by={self.by})"
