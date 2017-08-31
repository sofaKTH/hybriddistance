import math
import numpy as np 
import hybridAuto as ha
import weightedTrans as wt
import product as p

def findPath(product, c):
	init=product.init
	final=product.final
	states=product.states
	state_combos=product.states_combos
	trans=product.trans
	Ix=product.Ix
	Ih=product.Ih
	X=product.X
	Xv=product.Xv

	Nq=len(states)

	time=np.zeros(Nq) #time passed since init
	hd=np.zeros(Nq) #hybrid distance from init
	dc=np.zeros(Nq)
	dd=np.zeros(Nq)
	for q in states:
		if q!=init:
			time[q]=float("inf")
			hd[q]=float("inf")
			dc[q]=float("inf")
			dd[q]=float("inf")
	Spool=[init] # Search pool
	pathFound=False

	parent=np.ones(Nq)*(Nq+10) # parent of each state initially a dummy value


	while pathFound==False and len(Spool)!=0:
		#choose q1 as the state in Spool closest to init wrt hd
		q1=Spool[0]
		for q in Spool:
			if hd[q]<hd[q1]:
				q1=q
		#check if q1 is final
		if q1 in final:
			pathFound=True
		else:
			#find succ of q1
			succ=[]
			for q2 in states:
				if trans[q1, q2]!=float("inf"):
					succ.append(q2)
			#check if succ is valid time wise
			for q2 in succ:
				violation=False
				for x in X:
					if Ix[q2]==x:
						currTime=time[q1]+trans[q1,q2]
						if currTime>=Xv[x-1]:
							#time is violated
							violation=True
				if violation==False:
					#time is ok, check if a better path has been found
					currDC=c*(Ih[q1,1]+Ih[q2,1])
					currDD=(1-c)*(Ih[q1,2]+Ih[q2,2])
					currHD=hd[q1]+currDC+currDD
					if currHD< hd[q2]: #if better: update and add to Spool
						hd[q2]=currHD
						dc[q2]=currDC
						dd[q2]=currDD
						parent[q2]=q1
						time[q2]=time[q1]+trans[q1,q2]
						Spool.append(q2)
			#remove q1 from Spool
			Spool.remove(q1)

	#either spool went empty or a path was found!
	if pathFound==False:
		path=[]
		finalTime=float("inf")
		finalDC=float("inf")
		finalDD=float("inf")
		finalHD=float("inf")
		return 'No path found', path, finalTime, finalDC, finalDD, finalHD
	else:
		path=[q1]
		finalTime=time[q1]
		finalDC=dc[q1]
		finalDD=dd[q1]
		finalHD=hd[q1]
		while parent[q1]!=Nq+10:
			path.insert(0, parent[q1])
			q1=parent[q1]
		return 'path found', path, finalTime, finalDC, finalDD, finalHD
