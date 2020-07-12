#!/usr/bin/python3
import os,sys
import random

PASS=None
READ=0
SWAP=1
INSERT=2
NEW_BUCK=3
BUCKSWAP=4
BUCKINSERT=5
DEL_BUCK=6
FIN=7

class BaseAlgorithm():
	name="Base Algorithm"
	desc="This is the Base algorithm,\nit doesn't sort, but lays the foundation\nfor other algorithms."
	v=None#current value; gets set when using gen
	def __init__(self,l):
		self.l=l#array length
	#gen yields a tuple that tells the main program what to do each iteration - it doesn't have access to the list. Read values get stored in self.v.
	#None		→ does nothing
	#(READ,x,i)	→ reads value of item x in bucket i and puts it into the value param next cycle; None means there is no item at this index
	#(SWAP,x,y,i)	→ swaps item x with item y in bucket i
	#(INSERT,x,y,i)	→ inserts item x at index y and pushes all items between one index to the old index
	#(NEW_BUCK,)	→ creates a new bucket
	#(BUCKSWAP,x,i,y,j)→ swaps item x in bucket i to index y in bucket j
	#(BUCKINSERT,x,i,y,j)→inserts item x in bucket i at index y in bucket j
	#(DEL_BUCK,i)		→ destroys bucket i (only empty buckets can be destroyed)
	#(FIN,)		→ finish (not necessary anymore, StopIteration finishes too)
	gen=None

class BubbleSort(BaseAlgorithm):
	name="Bubble Sort"
	desc="Bubble Sort checks two adjacent items.\nIf the first is greater, swap them.\nThen do this for each index in the list, until the list is sorted"
	def gen(self):
		l=self.l
		i=l
		rn=True
		while rn and i>0:
			yield (READ,0,0)
			v1=self.v
			rn=False
			for j in range(1,i):
				yield (READ,j,0)
				v2=self.v
				if v1>v2:
					rn=True
					yield (SWAP,j-1,j,0)
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
		yield (READ,0,0)
		v1=self.v
		while rn and i>l2:
			rn=False
			for j in range(l-i,i):
				yield (READ,j,0)
				v2=self.v
				if v1>v2:
					rn=True
					yield (SWAP,j-1,j,0)
				else:
					v1=v2
			v1=v2
			for j in range(i-3,l-1-i,-1):
				yield (READ,j,0)
				v2=self.v
				if v1<v2:
					rn=True
					yield (SWAP,j+1,j,0)
				else:
					v1=v2
			i-=1

class MergeSort(BaseAlgorithm):
	name="Merge Sort"
	desc="Merges buckets until sorted"
	def gen(self):
		yield (NEW_BUCK,)
		yield (NEW_BUCK,)
		s=1#merge block size
		i=0#main bucket index
		i1=0#left bucket index
		i2=0#right bucket index
		l=self.l
		while s+1<l:
			while i+s<l:
				for i1 in range(s):
					yield (BUCKINSERT,i,0,i1,1)
				for i2 in range(s):
					if i+i1+i2+1==l:
						i2-=1
						break
					yield (BUCKINSERT,i,0,i2,2)
				self.a=1.6
				i1+=1
				i2+=1
				v1=None
				v2=None
				while i1>0 and i2>0:
					if v1==None:
						yield (READ,0,1)
						v1=self.v
					if v2==None:
						yield (READ,0,2)
						v2=self.v
					if v2<v1:#this implementation ensures stable mergesort, v1<v2 and reversed actions wouldn't be stable.
						i2-=1
						v2=None
						yield (BUCKINSERT,0,2,i,0)
					else:
						i1-=1
						v1=None
						yield (BUCKINSERT,0,1,i,0)
					i+=1
				while i1>0:
					i1-=1
					yield (BUCKINSERT,0,1,i,0)
					i+=1
				while i2>0:
					i2-=1
					yield (BUCKINSERT,0,2,i,0)
					i+=1
			i=0
			s*=2
		yield (DEL_BUCK,1)
		yield (DEL_BUCK,1)

class BogoSort(BaseAlgorithm):
	name="Bogo Sort"
	desc="Randomizes the whole set, then checks if it's sorted"
	def gen(self):
		l=self.l
		while True:
			yield (READ,0,0)
			v1=self.v
			fin=True
			for i in range(1,l):
				yield (READ,i,0)
				v2=self.v
				if v1>v2:
					fin=False
					break
				else:
					v1=v2
			if fin:
				break
			for i in range(l):
				yield (SWAP,i,random.randrange(l),0)

class InsertionSort(BaseAlgorithm):
	name="InsertionSort"
	desc="Inserts first unsorted item into sorted subarray\nuntil no unsorted items remain"
	def gen(self):
		l=self.l
		for z in range(1,l):
			yield (READ,z,0)
			v=self.v
			i=z
			for j in range(z-1,-1,-1):
				yield (READ,j,0)
				if v>self.v:
					break
				i=j
			if i!=z:
				yield (INSERT,z,i,0)

class InsertionSortOOP(BaseAlgorithm):
	name="InsertionSort OOP"
	desc="Inserts first unsorted item into sorted bucket\nuntil no unsorted items remain"
	def gen(self):
		l=self.l
		yield (NEW_BUCK,)
		for z in range(l):
			yield (READ,0,0)
			v1=self.v
			i=0
			for j in range(z):
				yield (READ,z-1-j,1)
				v2=self.v
				if v2<v1:
					break
				i=j+1
			yield (BUCKINSERT,0,0,z-i,1)
		yield (DEL_BUCK,0)

class SelectionSort(BaseAlgorithm):
	name="SelectionSort"
	desc="Swaps the smalles unsorted item with the first unsorted item\nuntil the list is sorted."
	def gen(self):
		l=self.l
		for i in range(l):
			sn=None
			si=None
			for j in range(i,l):
				yield (READ,j,0)
				v=self.v
				if sn==None or sn>v:
					sn=v
					si=j
			yield (SWAP,si,i,0)

class DoubleSelectionSort(BaseAlgorithm):
	name="Double Selection Sort"
	desc="Swaps the smalles unsorted item with the first unsorted item\nand the biggest unsorted item with the last unsorted item\nuntil the list is sorted."
	def gen(self):
		l=self.l
		l1=l-1
		for i in range(l//2):
			bn=0
			bi=None
			sn=None
			si=None
			for j in range(i,l-i):
				yield (READ,j,0)
				v=self.v
				if v>=bn:# >= makes the sort stable
					bn=v
					bi=j
				if sn==None or sn>v:
					sn=v
					si=j
			if si==l1-i:
				si=bi
			yield (SWAP,bi,l1-i,0)
			yield (SWAP,si,i,0)

class SelectionSortOOP(BaseAlgorithm):
	name="Selectionsort OOP"
	desc="Puts the smallest item in bucket 0 to the end of bucket 1\nuntil bucket 0 is empty."
	def gen(self):
		l=self.l
		yield (NEW_BUCK,)
		for i in range(l):
			sn=None
			si=None
			for j in range(l-i):
				yield (READ,j,0)
				v=self.v
				if sn==None or sn>v:
					sn=v
					si=j
			yield (BUCKINSERT,si,0,i,1)
		yield (DEL_BUCK,0)

class DoubleSelectionSortOOP(BaseAlgorithm):
	name="Double Selectionsort OOP"
	desc="Puts the smalles unsorted item in the first bucket\nand the biggest unsorted item in the second bucket,\nthen dumps the buckets in the main one."
	def gen(self):
		l=self.l
		yield (NEW_BUCK,)
		yield (NEW_BUCK,)
		for i in range(l//2):
			bn=0
			bi=None
			sn=None
			si=None
			for j in range(l-i*2):
				yield (READ,j,0)
				v=self.v
				if v>=bn:# >= makes the sort stable
					bn=v
					bi=j
				if sn==None or sn>v:
					sn=v
					si=j
			if si<bi:
				bi-=1
			yield (BUCKINSERT,si,0,i,1)
			yield (BUCKINSERT,bi,0,0,2)
		if l%2==1:#if odd → one item left in bucket 0
			yield (BUCKINSERT,0,0,i,1)#put on top of buck 1 since it's the median
			i=1+l//2
		else:
			i=l//2
		yield (DEL_BUCK,0)
		for j in range(i,l):
			yield (BUCKINSERT,0,1,j,0)
		yield (DEL_BUCK,1)

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
				yield (READ,i,0)
				v1=self.v
				yield (READ,i+1,0)
				v2=self.v
				if v1>v2:
					yield (SWAP,i,i+1,0)
					fin=False
			odd=not odd

class RadixLSDBASE(BaseAlgorithm):
	name="Radix LSD BASE"
	desc="Base for all Radix LSD non-OOP Sorts."
	def gen(self):
		b=self.b
		l=self.l
		maxb=b
		curb=1
		i=[0 for x in range(b)]
		while True:
			if i[0]==l:
				i=[0 for i in range(b)]
				curb*=b
			if curb>=maxb:
				break
			yield (READ,i[0],0)
			while self.v>maxb:
				maxb*=b
			digit=(b-1)-(self.v//curb)%b#actually the inverse of the digit, it would reverse the list otherwise
			for j in range(digit+1):
				i[j]+=1
			if digit==0:
				continue
			else:
				yield (INSERT,i[0]-1,i[digit]-1,0)

class RadixLSDBASEOOP(BaseAlgorithm):
	name="Radix LSD BASE OOP"
	desc="Base for all Radix LSD OOP Sorts."
	def gen(self):
		b=self.b
		l=self.l
		maxb=b
		curb=1
		for x in range(b):
			yield (NEW_BUCK,)
		while curb<maxb:
			i=[0 for x in range(b)]
			for j in range(l):
				yield (READ,0,0)
				v=self.v
				while v>maxb:
					maxb*=b
				digit=b-(v//curb)%b
				i[digit-1]+=1
				yield (BUCKINSERT,0,0,0,digit)
			for j,x in enumerate(i):
				for y in range(x):
					yield (BUCKINSERT,0,j+1,0,0)
			curb*=b
		for x in range(b):
			yield (DEL_BUCK,1)

class RadixLSDB2(RadixLSDBASE):
	name="Radix LSD 2"
	desc="Sorts by least significant digit in base 2."
	b=2

class RadixLSDB2OOP(RadixLSDBASEOOP):
	name="Radix LSD 2 OOP"
	desc="Sorts by least significant digit in base 2 out of place."
	b=2

class RadixLSDB4(RadixLSDBASE):
	name="Radix LSD 4"
	desc="Sorts by least significant digit in base 4."
	b=4

class RadixLSDB4OOP(RadixLSDBASEOOP):
	name="Radix LSD 4 OOP"
	desc="Sorts by least significant digit in base 4 out-of-place."
	b=4

class RadixLSDB10(RadixLSDBASE):
	name="Radix LSD 10"
	desc="Sorts by least significant digit in base 10."
	b=10

class RadixLSDB10OOP(RadixLSDBASEOOP):
	name="Radix LSD 10 OOP"
	desc="Sorts by least significant digit in base 10 out-of-place."
	b=10

#implementation of https://en.wikipedia.org/wiki/Quicksort#Lomuto_partition_scheme with pseudo-recursion.
class Quicksort(BaseAlgorithm):
	name="Quicksort"
	desc="Recursively picks a pivot and partitions all items around it\nuntil list is sorted.\nHilariously bad at sorted and reversed lists."
	def gen(self):#TODO: this is badly transitioned from the days of the cycle API, rewrite needed
		lv=[[0,self.l-1,0]]
		while True:
			cv=lv[-1]
			a=cv[2]
			v=self.v
			if a==0:
				if cv[0]<cv[1]:#if lo<hi:
					cv[2]=1
					lv.append([cv[0],cv[1],4])
				else:
					del lv[-1],cv
					if len(lv)==0:
						break
			elif a==1:
				cv[2]=2
				lv.append([cv[0],cv[3]-1,0])
			elif a==2:
				cv[2]=3
				lv.append([cv[3]+1,cv[1],0])
			elif a==3:
				del lv[-1],cv
				if len(lv)==0:
					break
			elif a==4:
				cv[2]=5
				yield (READ,cv[1],0)
			elif a==5:
				cv.append(v)#3 - pivot
				cv.append(cv[0])#4 - i
				cv.append(cv[0])#5 - j
				cv[2]=6#a=6
			elif a==6:
				if cv[5]>cv[1]:#if j>hi
					cv[2]=8	#a=8
					yield (SWAP,cv[4],cv[1],0)#SWAP i,hi,0
				else:
					cv[2]=7#a=7
					yield (READ,cv[5],0)#READ j,0
			elif a==7:
				cv[5]+=1#j++
				cv[2]=6
				if v<cv[3]:	#if A[j]<pivot:
					cv[4]+=1	#i++
					yield (SWAP,cv[4]-1,cv[5]-1,0)#SWAP i,j,0
			elif a==8:
				lv[-2].append(cv[4])#return i
				del lv[-1],cv

class Reverser(BaseAlgorithm):
	name="Reverser"
	desc="reverses the set"
	def gen(self):
		for i in range(self.l//2):
			yield (SWAP,i,self.l-i-1,0)

class Shuffler(BaseAlgorithm):
	name="Shuffler"
	desc="Shuffles the list"
	def gen(self):
		for i in range(self.l):
			yield (SWAP,i,random.randrange(self.l),0)

class ShufflerOneSide(BaseAlgorithm):
	name="One-Sided Shuffler"
	desc="Shuffles the list one-sided\n(not 100% random)"
	def gen(self):
		for i in range(self.l):
			yield (SWAP,i,random.randrange(i+1,self.l),0)

class ShufflerInsert(BaseAlgorithm):
	name="Shuffler"
	desc="Shuffles the list by inserting\n(pretty bad)"
	def gen(self):
		for i in range(self.l):
			yield (INSERT,i,random.randrange(self.l),0)

class ShufflerOneSideInsert(BaseAlgorithm):
	name="Shuffler"
	desc="Shuffles the list one-sided by inserting\n(very,very bad)"
	def gen(self):
		for i in range(self.l):
			yield (INSERT,i-1,random.randrange(i+1,self.l),0)

shufflers=[ShufflerOneSideInsert,ShufflerInsert,ShufflerOneSide,Shuffler]#shufflers from worst to best
algs=[
	BubbleSort,
	CocktailShaker,
	OddEvenSort,
	InsertionSort,InsertionSortOOP,
	SelectionSort,SelectionSortOOP,
	DoubleSelectionSort,DoubleSelectionSortOOP,
	Quicksort,
	RadixLSDB2,RadixLSDB2OOP,
	RadixLSDB4,RadixLSDB4OOP,
	RadixLSDB10,RadixLSDB10OOP,
	MergeSort,
	BogoSort]
