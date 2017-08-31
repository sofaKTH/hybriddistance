import math
import numpy as np 
import hybridAuto as ha
import weightedTrans as wt

class Product(object):
	states_combos=np.matrix
	states=[]
	trans=np.matrix
	final=[]
	Ix=np.array
	Ih=np.array
	init=0
	X=[]
	Xv=[]


def makeProduct(A, T):
	P=Product()
	i=0
	states_combos=np.zeros((len(A.locations)*len(T.states),3))
	for loc in A.locations:
		for sta in T.states:
			states_combos[i, 1]=int(sta)
			states_combos[i, 2]=int(loc)
			i=i+1

	P.states_combos=states_combos
	P.states=range(i)
	#print states_combos

	#trans
	trans=np.zeros((i,i))
	for q1 in P.states:
		for q2 in P.states:
			sta1=states_combos[q1, 1]
			sta2=states_combos[q2, 1]
			loc1=states_combos[q1, 2]
			loc2=states_combos[q2, 2]
			if T.trans[sta1,sta2]==1: #if the transition exists in WTS
				for ind in range(len(A.X)+1):
					if A.E[loc1, T.label[sta2], ind]==loc2: #if the label of the next location matches the act on the edge
						trans[q1,q2]=T.weights[sta1,sta2]
					else:
						trans[q1,q2]=float("inf")
			else:
				trans[q1,q2]=float("inf")
			if sta1==8 and sta2==16:
				print trans[q1,q2], q1, q2
	P.trans=trans
	# final, Ix, Ih, init
	final=[]
	Ix=np.zeros(len(P.states))
	Ih=np.zeros((len(P.states), 3))
	init=0
	for q in P.states:
		loc=states_combos[q,2]
		sta=states_combos[q,1]
		if loc==A.final:
			final.append(q)
		Ix[q]=A.Ix[loc]
		Ih[q,1]=A.Ih[1,loc]
		Ih[q,2]=A.Ih[2,loc]
		if loc==A.init and sta==T.init:
			init=q
	P.final=final
	P.Ix=Ix
	P.Ih=Ih
	P.init=init
	P.X=A.X
	P.Xv=A.Xv
	return P

