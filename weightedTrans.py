
import math
import numpy as np
from random import randint

class WTS(object):
	size=0
	apnumbers=0
	states=np.array
	trans=np.matrix
	weights=np.matrix
	AP=range(1,apnumbers+1)
	label=np.array
	init=0


def make_WTS(size, width, apnumbers, labels, init, init_dir):
	#labels should be given as labels={}
	#labels[x,y]=0 or 1 (1 if the ap y holds in location x)
	T=WTS()
	T.size=size
	T.apnumbers=apnumbers
	T.states=range(size*4)
	#T.init=init
	if init_dir=='L':
		k=3
	elif init_dir=='R':
		k=2
	elif init_dir=='D':
		k=1
	else:
		k=0
	T.init=(init-1)*4+k
	
	#these values should be updated according to the turtlebot
	passTime=0.01
	forwardTime=3
	turningTime=4
	T.trans=np.zeros((size*4, size*4))
	T.weights=np.zeros((size*4,size*4))
	for row in range(size*4):
		for col in range(size*4):
			if col==row: #self trans not allowed (to simplify graphsearch)
				T.trans[row,col]=0
				T.weights[row,col]=passTime
			elif row%width!=0 and col-row==4: # trans to right
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif row%width!=1 and row-col==4: #trans to left
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif col-row==width*4:#trans up
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif row-col==width*4: #trans down
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif row%4==0 and (col-row==2 or col-row==3): #turning from up
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			elif row%4==1 and (col-row==1 or col-row==2): #turning from down
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			elif row%4==2 and (col-row==-1 or col-row==-2): #turning from right
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			elif row%4==3 and (col-row==-2 or col-row==-3): #turning from left
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			else: 					#no trans
				#T.trans[row,col]=0 standard value
				T.weights[row,col]=float("inf")
	label=np.zeros((size*4,size*4+1))
	T.label=np.zeros(size*4)
	for row in range(size*4):
		for col in range(1, apnumbers+1):
			elem=int(math.floor(row/4.0))
			label[row,col]=labels[elem,col]
	for sta in range( size*4):
		vec=label[sta, :]
		index=[]
		for i, j in enumerate(vec):
			if j==1:
				index.append(i)
		T.label[sta]=sum(np.power(2, index))

	T.AP=range(1,apnumbers+1)

	return T

# lab=np.zeros((9, 6))
# for st in range(9):
# 	x=st%5
# 	if x==0:
# 		x=5
# 	lab[st, x]=1

# WTS=make_WTS(9,3,5,lab)

#print WTS.label
#print WTS.states