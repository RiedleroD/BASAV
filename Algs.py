#!/usr/bin/python3
print("  importing various libs…")
import os,sys
import random
print("  importing actions")
from Actions import *
print("  defining bases…")
class BaseAlgorithm():
	name="Base Algorithm"
	desc="This is the Base algorithm,\nit doesn't sort, but lays the foundation\nfor other algorithms."
	v=None#current value; gets set when using gen
	opts={}#algorithm options; optional (ha)
	vals={}#values that get set for the options
	def __init__(self,l):
		self.l=l#array length
	#gen yields a tuple that tells the main program what to do each iteration - it doesn't have access to the list. Read values get stored in self.v.
	#PASS()				→ does nothing
	#READ(x,i)			→ reads value of item x in bucket i and puts it into the value param next cycle
	#SWAP(x,y,i)		→ swaps item x with item y in bucket i
	#INSERT(x,y,i)		→ inserts item x at index y and pushes all items between one index to the old index
	#NEW_BUCK()			→ creates a new bucket
	#BUCKSWAP(x,i,y,j)	→ swaps item x in bucket i to index y in bucket j
	#BUCKINSERT(x,i,y,j)→inserts item x in bucket i at index y in bucket j
	#DEL_BUCK(i)		→ destroys bucket i (only empty buckets can be destroyed)
	#FIN()				→ finish (not necessary anymore, StopIteration finishes too)
	#PULL(i)			→ pulls item from bucket i into a one-item variable space
	#PUSH(i)			→ pushes item from the one-item variable space onto bucket i
	#PULSH(i,j)			→ pulls item from bucket i and pushes it onto bucket j
	gen=None
print("  defining algorithms…")
class BubbleSort(BaseAlgorithm):
	name="Bubble Sort"
	desc="Bubble Sort checks two adjacent items.\nIf the first is greater, swap them.\nThen do this for each index in the list, until the list is sorted"
	def gen(self):
		l=self.l
		i=l
		rn=True
		while rn and i>0:
			yield READ(0,0)
			v1=self.v
			rn=False
			for j in range(1,i):
				yield READ(j,0)
				v2=self.v
				if v1>v2:
					rn=True
					yield SWAP(j-1,j,0)
				else:
					v1=v2
			i-=1
class CocktailShaker(BaseAlgorithm):
	name="Cocktail Shaker"
	desc="Like Bubble Sort, but changes directions every cycle"
	def gen(self):
		l=self.l
		l2=l//2
		i=l
		rn=True
		yield READ(0,0)
		v1=self.v
		while rn and i>l2:
			rn=False
			for j in range(l-i,i):
				yield READ(j,0)
				v2=self.v
				if v1>v2:
					rn=True
					yield SWAP(j-1,j,0)
				else:
					v1=v2
			v1=v2
			for j in range(i-3,l-1-i,-1):
				yield READ(j,0)
				v2=self.v
				if v1<v2:
					rn=True
					yield SWAP(j+1,j,0)
				else:
					v1=v2
			i-=1
class NormalMergeSort(BaseAlgorithm):
	name="Merge Sort"
	desc="Merges sections until sorted"
	opts={
		"oop":(bool,False,"Out-of-Place","In-Place"),
		"conc":(bool,False,"Concurrent","Seperate")
	}
	def gen(self):
		conc=self.vals["conc"]
		oop=self.vals["oop"]
		noop=not oop
		size=1
		if oop:
			yield NEW_BUCK()
			yield NEW_BUCK()
		while size<self.l:
			merges=[self.merge(i,size,oop) for i in range(0,self.l,size*2)]
			if conc and noop:
				merge=None
				while len(merges)>0:
					if merge==None:
						merge=random.choice(merges)
					try:
						act=next(merge)
					except StopIteration:
						merges.remove(merge)
						merge=None
					else:
						if type(act)!=READ:
							merge=None
						yield act
			else:
				for merge in merges:
					for act in merge:
						yield act
			size*=2
		if oop:
			yield DEL_BUCK(1)
			yield DEL_BUCK(1)
	def merge(self,i,size,oop):
		if self.l-i<=size:#if only one block or less remains
			pass
		elif oop:
			m=i+size
			e=min(i+size*2,self.l)
			for _i in range(m,e):
				yield BUCKINSERT(m,0,0,2)
			for _i in range(i,m):
				yield BUCKINSERT(i,0,0,1)
			v=None
			_v=None
			j1=0
			j2=0
			for _i in range(i,e):
				if v==None and j1<m-i:
					yield READ(0,1)
					v=self.v
				if _v==None and j2<e-m:
					yield READ(0,2)
					_v=self.v
				if v==None:
					yield BUCKINSERT(0,2,i,0)
				elif _v==None:
					yield BUCKINSERT(0,1,i,0)
				elif v<_v:
					yield BUCKINSERT(0,2,i,0)
					j2+=1
					_v=None
				else:
					yield BUCKINSERT(0,1,i,0)
					j1+=1
					v=None
		else:
			m=i+size
			e=min(i+size*2,self.l)
			off=0
			i1=i
			yield READ(i1,0)
			v1=self.v
			i2=m
			yield READ(i2,0)
			v2=self.v
			while True:
				if v1>v2:
					yield INSERT(i2,i1+off,0)
					off+=1
					i2+=1
					if i2==e:
						break
					yield READ(i2,0)
					v2=self.v
				else:
					i1+=1
					if i1==m:
						break
					yield READ(i1+off,0)
					v1=self.v
class NaturalMergeSort(BaseAlgorithm):
	name="Natural Merge Sort"
	desc="Uses presorted sections to its advantage.\nMerges buckets until sorted."
	opts={
		"oop":(bool,False,"Out-of-Place","In-Place"),
		"conc":(bool,False,"Concurrent","Seperate")
	}
	def gen(self):
		conc=self.vals["conc"]
		oop=self.vals["oop"]
		noop=not oop
		sects=[]
		yield READ(0,0)
		v=self.v
		for i in range(1,self.l):
			yield READ(i,0)
			if self.v<v:
				sects.append(i)
			v=self.v
		sects.append(self.l)
		if oop:
			yield NEW_BUCK()
			yield NEW_BUCK()
		while len(sects)>1:
			_i=0
			merges=[]
			for j in range(0,len(sects)-1,2):
				m=sects[j]
				e=sects[j+1]
				merges.append(self.merge(_i,m,e,oop))
				_i=e
			if conc and noop:
				merge=None
				while len(merges)>0:
					if merge==None:
						merge=random.choice(merges)
					try:
						act=next(merge)
					except StopIteration:
						merges.remove(merge)
						merge=None
					else:
						if type(act)!=READ:
							merge=None
						yield act
			else:
				for merge in merges:
					for act in merge:
						yield act
			if len(sects)%2==1:
				sects=[*sects[1::2],sects[-1]]
			else:
				sects=sects[1::2]
		if oop:
			yield DEL_BUCK(1)
			yield DEL_BUCK(1)
	def merge(self,_i,m,e,oop):
		_v=None
		v=None
		j1=0
		j2=0
		if oop:
			for i in range(m,e):
				yield BUCKINSERT(m,0,0,2)
			for i in range(_i,m):
				yield BUCKINSERT(_i,0,0,1)
			for i in range(_i,e):
				if v==None and j1<m-_i:
					yield READ(0,1)
					v=self.v
				if _v==None and j2<e-m:
					yield READ(0,2)
					_v=self.v
				if v==None:
					yield BUCKINSERT(0,2,_i,0)
				elif _v==None:
					yield BUCKINSERT(0,1,_i,0)
				elif v<_v:
					yield BUCKINSERT(0,2,_i,0)
					_v=None
					j2+=1
				else:
					yield BUCKINSERT(0,1,_i,0)
					v=None
					j1+=1
		else:
			off=0
			for i in range(m,e):
				yield READ(i,0)
				v=self.v
				while True:
					if _v==None:
						yield READ(_i+off,0)
						_v=self.v
					if _v>v:
						yield INSERT(i,_i+off,0)
						off+=1
						break
					else:
						_i+=1
						_v=None
						if _i==m:
							break
				if _v==None:
					break
class MergeSortOPT(BaseAlgorithm):
	name="Merge Sort"
	desc="Merges buckets until sorted\nNote: concurrent mode only works In-Place"
	opts={
		"oop":(bool,False,"Out-of-Place","In-Place"),
		"vrs":(list,0,("Normal","Natural"),"%s"),
		"conc":(bool,False,"Concurrent","Seperate")
	}
	def __new__(cls,l):
		if cls.vals["vrs"]==0:
			alg=NormalMergeSort
		elif cls.vals["vrs"]==1:
			alg=NaturalMergeSort
		alg.vals=cls.vals
		return alg(l)
#implemented from https://en.wikipedia.org/wiki/Stooge_sort
class StoogeSort(BaseAlgorithm):
	name="Stooge Sort"
	desc="Recursively sorts the first 2/3rds, then the 2nd 2/3rds\nand then the 1st 2/3rds of a section again"
	def gen(self):
		for act in self.stooge(0,self.l-1):
			yield act
	def stooge(self,i,j):
		yield READ(i,0)
		iv=self.v
		yield READ(j,0)
		jv=self.v
		if iv>jv:
			yield SWAP(i,j,0)
		if (j-i)>1:#if there are at least 3 items in the section
			t=(j-i+1)//3
			for args in ((i,j-t),(i+t,j),(i,j-t)):
				for act in self.stooge(*args):
					yield act
class InsertionSort(BaseAlgorithm):
	name="InsertionSort"
	desc="Inserts first unsorted item into sorted subarray\nuntil no unsorted items remain"
	opts={
		"oop":[bool,False,"Out-of-Place","In-Place"]
		}
	def gen(self):
		l=self.l
		oop=self.vals["oop"]
		noop=not oop
		if oop:
			yield NEW_BUCK()
		for z in range(noop,l):
			yield READ(z*noop,0)
			v=self.v
			i=z*noop
			for j in (range(z) if oop else range(z-1,-1,-1)):
				yield READ(z-1-j if oop else j,oop)
				if v>=self.v:
					break
				i=j+oop
			if oop:
				yield BUCKINSERT(0,0,z-i,1)
			elif i!=z:
				yield INSERT(z,i,0)
		if oop:
			yield DEL_BUCK(0)
class SelectionSort(BaseAlgorithm):
	name="SelectionSort"
	desc="Swaps the smalles unsorted item with the first unsorted item\nuntil the list is sorted."
	opts={
		"oop":[bool,False,"Out-of-Place","In-Place"],
		"dp":[bool,False,"Double Pivot","Single Pivot"]
		}
	def gen(self):
		l=self.l
		oop=self.vals["oop"]
		dp=self.vals["dp"]
		if oop and dp:#double-pviot, out-of-place Selection Sort
			yield NEW_BUCK()
			yield NEW_BUCK()
			for i in range(l//2):
				bn=0
				bi=None
				sn=None
				si=None
				for j in range(l-i*2):
					yield READ(j,0)
					v=self.v
					if v>=bn:# >= makes the sort stable
						bn=v
						bi=j
					if sn==None or sn>v:
						sn=v
						si=j
				if si<bi:
					bi-=1
				yield BUCKINSERT(si,0,i,1)
				yield BUCKINSERT(bi,0,0,2)
			if l%2==1:#if odd → one item left in bucket 0
				yield BUCKINSERT(0,0,i,1)#put on top of buck 1 since it's the median
				i=1+l//2
			else:
				i=l//2
			yield DEL_BUCK(0)
			for j in range(i,l):
				yield BUCKINSERT(0,1,j,0)
			yield DEL_BUCK(1)
		elif oop:#single-pivot, out-of-place Selection Sort
			yield NEW_BUCK()
			for i in range(l):
				sn=None
				si=None
				for j in range(l-i):
					yield READ(j,0)
					v=self.v
					if sn==None or sn>v:
						sn=v
						si=j
				yield BUCKINSERT(si,0,i,1)
			yield DEL_BUCK(0)
		elif dp:#dual-pivot, in-place Selection Sort
			l1=l-1
			for i in range(l//2):
				bn=0
				bi=None
				sn=None
				si=None
				for j in range(i,l-i):
					yield READ(j,0)
					v=self.v
					if v>=bn:# >= makes the sort stable
						bn=v
						bi=j
					if sn==None or sn>v:
						sn=v
						si=j
				if si==l1-i:
					si=bi
				yield SWAP(bi,l1-i,0)
				yield SWAP(si,i,0)
		else:#single-pivot, in-place Selection Sort
			for i in range(l):
				sn=None
				si=None
				for j in range(i,l):
					yield READ(j,0)
					v=self.v
					if sn==None or sn>v:
						sn=v
						si=j
				yield SWAP(si,i,0)
class OddEvenSort(BaseAlgorithm):
	name="Odd-Even Sort"
	desc="Like bubble sort, but parallelalizable.\nToo bad that's not possible here."
	def gen(self):
		odd=False
		fin=False
		l=self.l
		while not (odd and fin):
			if not odd:
				fin=True
			#odd is a bool, but gets interpretet as an int here, 2 is the step size,
			#so if 0 is the start, it's even, if 1 is the start, it's odd.
			for i in range(odd,l-1,2):#range(start,end,step)
				yield READ(i,0)
				v1=self.v
				yield READ(i+1,0)
				v2=self.v
				if v1>v2:
					yield SWAP(i,i+1,0)
					fin=False
			odd=not odd
class RadixMSD(BaseAlgorithm):
	name="Radix MSD"
	desc="Sorts from most to least significant digit"
	opts={
		"oop":(bool,False,"Out-of-Place","In-Place"),
		"b":(int,2,2,None,"Base"),
		"hop":(list,1,("Insert","Swap"),"Hop: %s")
	}
	def gen(self):
		b=self.vals["b"]
		bless1=b-1#b less 1
		oop=self.vals["oop"]
		noop=not oop
		hop=self.vals["hop"]
		l=self.l
		maxnum=0#negative numbers hate this one weird trick
		#go through the whole list to find the largest number
		for i in range(l):
			yield READ(i,0)
			if self.v>maxnum:
				maxnum=self.v
		curbs=[1]
		curb=b
		while curb<maxnum:
			curbs.append(curb)
			curb*=b
		curbs.reverse()
		ii=[[0]*b]
		ii[0][-1]=l
		if oop:
			for i in range(b):
				yield NEW_BUCK()
		arrange_i_for_base=self.arrange_i_for_base_oop if oop else self.arrange_i_for_base_ip
		for curb in curbs:
			yield from arrange_i_for_base(curb,ii,b,hop)
			ii=[j for i in ii for j in i]
			ii.insert(0,0)#at index 0, insert 0 (because the lists beginning would be lost otherwise)
			ii=[[ii[i]]*(b-1)+[ii[i+1]] for i in range(len(ii)-1) if ii[i+1]-ii[i]>1]
		if oop:
			for i in range(b):
				yield DEL_BUCK(1)
	def arrange_i_for_base_ip(self,curb,ii,b,hop):
		for i in ii:
			bless1=b-1
			if i[-1]-i[0]<2:
				return
			for j in range(i[0],i[-1]):
				yield READ(j,0)
				digit=(self.v//curb)%b
				if digit!=bless1:
					if hop:
						yield SWAP(j,i[b-2],0)
						for z in range(b-2,digit,-1):
							yield SWAP(i[z],i[z-1],0)
					else:
						yield INSERT(j,i[digit],0)
				for x in range(digit,bless1):
					i[x]+=1
	def arrange_i_for_base_oop(self,curb,ii,b,hop):
		lii=len(ii)
		for index_ffs,i in enumerate(ii):
			bless1=b-1
			if i[-1]-i[0]<2:
				return
			_j=i[0]
			_j_=0
			j_=[0]*b
			for j in range(i[-1]-1,i[0]-1,-1):
				yield READ(j,0)
				digit=(self.v//curb)%b
				if hop:
					_j_+=1
					yield SWAP(j,ii[-1][-1]-_j_,0)
					yield PULSH(0,digit+1)
				else:
					yield BUCKINSERT(j,0,j_[digit],digit+1)
				j_[digit]+=1
				for x in range(digit,bless1):
					i[x]+=1
			for digit in range(b):
				for j in range(i[digit-1] if digit>0 else _j,i[digit]):
					if hop:
						yield PULSH(digit+1,0)
						yield SWAP(ii[-1][-1]-_j_,j,0)
						_j_-=1
					else:
						j_[digit]-=1
						yield BUCKINSERT(j_[digit],digit+1,j,0)
class RadixLSD(BaseAlgorithm):
	name="Radix LSD"
	desc="Sorts from least to most significant digit"
	opts={
		"oop":(bool,False,"Out-of-Place","In-Place"),
		"b":(int,2,2,None,"Base")
	}
	def gen(self):
		b=self.vals["b"]
		oop=self.vals["oop"]
		noop=not oop
		l=self.l
		maxb=b
		curb=1
		if oop:
			for x in range(b):
				yield NEW_BUCK()
		else:
			i=[0 for x in range(b)]
		while noop or curb<maxb:
			if oop:
				i=[0 for x in range(b)]
			elif i[0]==l:
				i=[0 for i in range(b)]
				curb*=b
			if oop:
				for j in range(l):
					yield READ(l-1-j,0)
					v=self.v
					while v>maxb:
						maxb*=b
					digit=b-(v//curb)%b
					i[digit-1]+=1
					yield PULSH(0,digit)
				for j,x in reversed(list(enumerate(i))):
					for y in range(x):
						yield PULSH(j+1,0)
				curb*=b
			else:
				if curb>=maxb:
					break
				yield READ(i[0],0)
				while self.v>maxb:
					maxb*=b
				digit=(b-1)-(self.v//curb)%b#actually the inverse of the digit, it would reverse the list otherwise
				for j in range(digit+1):
					i[j]+=1
				if digit==0:
					continue
				else:
					yield INSERT(i[0]-1,i[digit]-1,0)
		if oop:
			for x in range(b):
				yield DEL_BUCK(1)
class Quicksort(BaseAlgorithm):
	name="Quicksort"
	desc="Recursively picks a pivot and partitions all items around it\nuntil list is sorted.\nHilariously bad at sorted and reversed lists."
	p=None#needed for partitioning
	opts={
		"conc":(bool,False,"Concurrent","Separate"),
		"ps":(bool,False,"Lomuto","Hoare")
	}
	def gen(self):
		if self.vals["ps"]:
			self.partition=self.partition_lm
		else:
			self.partition=self.partition_hr
		self.conc=self.vals["conc"]
		for act in self.qs(0,self.l-1):
			yield act
	def qs(self,lo,hi):
		if lo<hi:
			for act in self.partition(lo,hi):
				yield act
			p,_p=self.p
			gens=self.qs(lo,p),self.qs(_p,hi)
			gen=0
			while True:
				try:
					act=next(gens[gen])
				except StopIteration:
					gen=gens[abs(gen-1)]
					break
				else:
					yield act
					if type(act)!=READ and self.conc:
						gen=abs(gen-1)
			for act in gen:
				yield act
	#implementation of https://en.wikipedia.org/wiki/Quicksort#Lomuto_partition_scheme
	def partition_lm(self,lo,hi):
		yield READ(hi,0)
		pivot=self.v
		i=lo
		for j in range(lo,hi):
			yield READ(j,0)
			if self.v<pivot:
				yield SWAP(i,j,0)
				i+=1
		yield SWAP(i,hi,0)
		self.p=(i-1,i+1)
	#implementation of https://en.wikipedia.org/wiki/Quicksort#Hoare_partition_scheme
	def partition_hr(self,lo,hi):
		yield READ((hi+lo)//2,0)
		pivot=self.v
		i=lo-1
		j=hi+1
		while True:
			while True:
				i+=1
				yield READ(i,0)
				if self.v>=pivot:
					break
			while True:
				j-=1
				yield READ(j,0)
				if self.v<=pivot:
					break
			if i>=j:
				self.p=(j,j+1)
				break
			yield SWAP(i,j,0)
#implementation of https://en.wikipedia.org/wiki/Heapsort#Pseudocode
class HeapSort(BaseAlgorithm):
	name="Heap Sort"
	desc="Maintains a heap and selects with its help\nefficiently the largest unsorted value\nuntil the heap is empty and the array is sorted"
	opts={
		"hc":(list,1,("Up","Down"),"Heap Construction: %s")
	}
	def gen(self):
		for act in self.heapify():
			yield act
		for end in range(self.l-1,0,-1):
			yield SWAP(end,0,0)
			for act in self.siftDown(0,end-1):
				yield act
	def heapify(self):
		if self.vals["hc"]==0:
			end=1
			while end<self.l:
				for act in self.siftUp(0,end):
					yield act
				end+=1
		elif self.vals["hc"]==1:
			for start in range((self.l-2)//2,-1,-1):
				for act in self.siftDown(start,self.l-1):
					yield act
	def siftDown(self,start,end):
		root=start
		swap=root
		yield READ(swap,0)
		vswap=vroot=self.v
		while 2*root<end:
			child=2*root+1
			yield READ(child,0)
			if vswap<self.v:
				swap=child
				vswap=self.v
			if child<end:
				yield READ(child+1,0)
				if vswap<self.v:
					swap=child+1
					vswap=self.v
			if swap==root:
				break
			else:
				yield SWAP(root,swap,0)
				vswap=vroot
				root=swap
	def siftUp(self,start,end):
		child=end
		yield READ(child,0)
		vchild=self.v#never changes
		while child>start:
			parent=(child-1)//2
			yield READ(parent,0)
			if self.v<vchild:
				yield SWAP(parent,child,0)
				child=parent
			else:
				break
#implementation of https://www.dangermouse.net/esoteric/demonsort.html with a few assumptions,
#e.g. how to check if all lower values are in the lower partition.
class DemonSort(BaseAlgorithm):
	name="Demon Sort"
	desc="Divides the array into 2 sections.\nThen gets largest item i from the first\nand lowest j from the second subarray. If j>i, apply motion,\nswap the center values or move section by 1 if necessary and repeat the check.\nthen apply this recursively if j<=i."
	opts={
		"conc":(bool,False,"Concurrent","Separate"),
		"mot":(list,0,("Rollout","Rollin","Randswap"),"Motion: %s"),
		"r":(list,0,("Inwards","Outwards"),"Checking: %s")
	}
	queue=None
	def gen(self):
		self.conc=self.vals["conc"]
		deso=self.deso(0,self.l)
		if self.conc:
			self.queue=[iter(deso)]
		else:
			yield from deso
		while self.queue:
			deso=random.choice(self.queue)
			try:
				act=next(deso)
				yield act
				while isinstance(act,READ):
					act=next(deso)
					yield act
			except StopIteration:
				self.queue.remove(deso)
	def deso(self,s,e):
		thresh=(s+e)/2
		m=round(thresh)
		while True:
			max1=None
			min2=None
			if self.vals["r"]==0:
				sm=iter(range(s,m))
				em=iter(range(e-1,m-1,-1))
			else:
				sm=iter(range(m-1,s-1,-1))
				em=iter(range(m,e))
			for _ in range(max(m-s,e-m)):
				try:
					i=next(sm)
				except StopIteration:
					pass
				else:
					yield READ(i,0)
					if max1==None or max1<self.v:
						max1=self.v
				try:
					j=next(em)
				except StopIteration:
					pass
				else:
					yield READ(j,0)
					if min2==None or min2>self.v:
						min2=self.v
				if min2<max1:
					break
			if min2<max1:
				if self.vals["mot"]==2:
					if m-s>1:
						yield SWAP(m-1,random.randrange(s,m-1),0)
					if e-m>1:
						yield SWAP(m,random.randrange(m+1,e),0)
				else:
					if self.vals["mot"]==0:
						if m-s>1:
							yield INSERT(s,m,0)
						if e-m>1:
							yield INSERT(e-1,m,0)
					else:
						if m-s>1:
							yield INSERT(m-1,s,0)
						if e-m>1:
							yield INSERT(m,e,0)
				yield READ(m-1,0)
				v1=self.v
				yield READ(m,0)
				v2=self.v
				if v1>thresh:
					if v2>thresh:
						if m-1>s:
							m-=1
						else:
							thresh+=1
					else:
						yield SWAP(m,m-1,0)
				else:
					if v2<thresh:
						if m+1<e:
							m+=1
						else:
							thresh-=1
			else:
				desosm=self.deso(s,m)
				desome=self.deso(m,e)
				if m-s>1:
					if self.conc:
						self.queue.append(iter(desosm))
					else:
						yield from desosm
				if e-m>1:
					if self.conc:
						self.queue.append(iter(desome))
					else:
						yield from desome
				break
class Reverser(BaseAlgorithm):
	name="Reverser"
	desc="reverses the set"
	def gen(self):
		for i in range(self.l//2):
			yield SWAP(i,self.l-i-1,0)
class Shuffler(BaseAlgorithm):
	name="Shuffler"
	desc="Shuffles the list"
	opts={
		"q":(int,3,0,4,"Randomness")
	}
	def gen(self):
		q=self.vals["q"]
		for i in range(self.l if q!=2 else self.l-1):
			yield (SWAP if q in (2,3) else INSERT)(i,random.randrange([i,0,i+1,0][q],self.l-1),0)
class BogoSort(BaseAlgorithm):
	name="Bogo Sort"
	desc="Shuffles the whole array, then checks if it's sorted.\nRepeat until success."
	opts=Shuffler.opts.copy()
	def gen(self):
		l=self.l
		Shuffler.vals=self.vals.copy()
		shuf=Shuffler(self.l)
		while True:
			yield READ(0,0)
			v1=self.v
			fin=True
			for i in range(1,l):
				yield READ(i,0)
				v2=self.v
				if v1>v2:
					fin=False
					break
				else:
					v1=v2
			if fin:
				break
			for act in shuf.gen():
				yield act

algs=[
	BubbleSort,
	CocktailShaker,
	OddEvenSort,
	InsertionSort,
	SelectionSort,
	Quicksort,
	HeapSort,
	RadixMSD,
	RadixLSD,
	MergeSortOPT,
	DemonSort,
	StoogeSort,
	BogoSort]
