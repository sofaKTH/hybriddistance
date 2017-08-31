import math
import numpy as np
import itertools

#operators=["Always", "Eventually", "And", "Or", "Until", "Not"]

class TAhd(object):
	apnumbers=0
	locations=np.array
	init=0
	final=0
	AP=range(1,apnumbers+1)
	X=np.array
	#H=["dc", "dd"]
	Ix=np.array
	Ih=np.matrix
	E=np.matrix
	L=np.array
	Xv=[]


def make_manual_TAhd(dead):
	#MITL=A not 1 and E (below 5) 2
	A=TAhd()
	A.apnumbers=2
	A.locations=range(6)
	A.init=0
	A.final=4
	A.AP=range(1,A.apnumbers+1)
	A.X=[1]
	A.Xv=[dead]
	A.Ix=np.zeros(6)
	for x in [0,1]:
		A.Ix[x]=1
	A.Ih=np.zeros((3,6))
	for x in [0,1,4,5]:
		A.Ih[1,x]=0
	for x in [2,3]:
		A.Ih[1,x]=1
	for x in [0,3,4]:
		A.Ih[2,x]=0
	for x in [1,2,5]:
		A.Ih[2,x]=1
	
	sep_act=np.power(2,range(1,A.apnumbers+1))
	act=[]
	for elem in range(len(sep_act)+1):
		for sub in itertools.combinations(sep_act,elem):
			act.append(sum(sub))
	
	#E: (sta1,act,index) if multiple
	A.E=np.ones((6,act[len(act)-1]+1,len(A.X)*2))*10
	
	#from 0
	A.E[0,act[1],0]=1
	A.E[0,act[0],0]=0
	A.E[0,act[1],1]=2
	A.E[0,act[0],1]=3
	for i in [2]:
		A.E[0,act[i],0]=4
	for i in [3]:
		A.E[0,act[i],0]=5
	#from 1
	A.E[1,act[0],0]=0
	A.E[1,act[1],0]=1
	A.E[1,act[1],1]=2
	A.E[1,act[0],1]=3
	for i in [2]:
		A.E[1,act[i],0]=4	
	for i in [3]:
		A.E[1,act[i],0]=5
	#from 2
	for i in [1]:
		A.E[2,act[i],0]=2
	for i in [0]:
		A.E[2,act[i],0]=3
	for i in [2]:
		A.E[2,act[i],0]=4
	for i in [3]:
		A.E[2,act[i],0]=5
	#from 3
	for i in [1]:
		A.E[3,act[i],0]=2
	for i in [0]:
		A.E[3,act[i],0]=3
	for i in [2]:
		A.E[3,act[i],0]=4
	for i in [3]:
		A.E[3,act[i],0]=5
	#from 4
	for i in [0,2]:
		A.E[4,act[i],0]=4
	for i in [1,3]:
		A.E[4,act[i],0]=5
	#from 5
	for i in [0,2]:
		A.E[5,act[i],0]=4
	for i in [1,3]:
		A.E[5,act[i],0]=5

	L0=[0]
	L1=[1]
	L2=[1,5]
	L3=[0,3]
	L4=[0,2,3,6]
	L5=[1,4,5,7]
	L=[L0,L2,L3,L4,L5]
	A.L=L
	return A


#A=make_manual_TAhd()
#print 'Locations: ', A.locations,"\n initial: ", A.init,"\n AP: ", A.AP, "\n Final: ", A.final, "\n Clocks: ",A.X, "\n Mapping of clocks: ",A.Ix, "\n mapping of hybrid dist", A.Ih, "\n Edges: ", A.E, "\n Labels: ",A.L




# class MITLsub(object):
# 	apnumbers=0
# 	operator=""
# 	ap1={}
# 	ap2={}
# 	deadline=float("inf")
# 	subType=0

# def constructMITLsub(string):
# 	phiI=MITLsub()
# 	info=string.split("_")
# 	if info[0] in operators:
# 		phiI.operator=info[0]
# 	aps=info[2].split(",")
# 	for elem in aps:
# 		aps[elem]=int(aps[elem])
# 	phiI.ap1=aps
# 	if info[1]!=""
# 		phiI.deadline=int(info[1])
# 	else:
# 		phiI.deadline=float("inf")
# 	if len(info)=5:
# 		aps=info[3].split(",")
# 		for elem in aps:
# 			aps[elem]=int(aps[elem])
# 		phiI.ap2=aps
# 		phiI.subType=int(info[4])
# 	else:
# 		phiI.ap2=0
# 		phiI.subType=int(info[3])


# def constructTAhd(MITL,apnumbers):
# 	#MITL is given as an array of subformulas 
# 	#s.t. the complete formula is the conjunction 
# 	#of the subformulas
# 	#the subformulas are on the form [[ap1 ap2 ...],Op,dead]
# 	A=TAhd()
# 	Nsub=len(MITL)
# 	varphi={}
# 	varphiNumb=[]
# 	X=0
# 	Ix={}
# 	for sub in range(Nsub):
# 		varphi[sub,0]=1
# 		if MITL[sub].deadline!=float("inf"): #temp bounded
# 			varphi[sub,1]=1
# 			varphi[sub,2]=1
# 			varphiNumb.append(3)
# 			X=X+1
# 			Ix{sub}
# 		elif MITL[sub].subType==1:
# 			varphi[sub,1]=1
# 			varphi[sub,2]=0
# 			varphiNumb.append(2)
# 		elif MITL[sub].subType==2:
# 			varphi[sub,1]=0
# 			varphi[sub,2]=1
# 			varphiNumb.append(2)
# 	Nloc=np.prod(varphiNumb)
# 	A.locations=range(Nloc)
# 	A.init=0
# 	A.F=Nloc
# 	A.apnumbers=apnumbers
# 	A.AP=range(1,apnumbers+1)
# 	A.X=range(1,X+1)
# 	A.Ix=