
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
	state_combos=np.matrix


def make_WTS(size, width, apnumbers, labels, init, init_dir):
	#labels should be given as labels={}
	#labels[x,y]=0 or 1 (1 if the ap y holds in location x)
	T=WTS()
	T.size=size
	T.apnumbers=apnumbers
	state_combos=np.zeros((size*4, 2))
	i=0
	for q in range(size):
		for d in range(4):
			state_combos[i,0]=q
			state_combos[i,1]=d
			i=i+1
	T.state_combos=state_combos
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
	T.init=(init)*4+k
	
	#these values should be updated according to the turtlebot
	passTime=0.01
	forwardTime=3
	turningTime=4
	T.trans=np.zeros((size*4, size*4))
	T.weights=np.zeros((size*4,size*4))
	for row in range(size*4):
		for col in range(size*4):
			if state_combos[row,0]%width!=width-1 and state_combos[col,0]-state_combos[row,0]==1: # trans to right
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif state_combos[row,0]%width!=0 and state_combos[col,0]-state_combos[row,0]==-1: #trans to left
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif state_combos[col,0]- state_combos[row,0]==width:#trans up
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif state_combos[row,0]-state_combos[col,0]==width: #trans down
				T.trans[row,col]=1
				T.weights[row,col]=forwardTime
			elif state_combos[row,1]==0 and (col-row==2 or col-row==3): #turning from up
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			elif state_combos[row,1]==1 and (col-row==1 or col-row==2): #turning from down
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			elif state_combos[row,1]==2 and (col-row==-1 or col-row==-2): #turning from right
				T.trans[row,col]=1
				T.weights[row,col]=turningTime
			elif state_combos[row,1]==3 and (col-row==-2 or col-row==-3): #turning from left
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