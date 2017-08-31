#Synthesis
import math
import numpy as np 
import hybridAuto as ha
import weightedTrans as wt
import product as p
import graphSearch as gs

#ROS
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped

#---------------------------------------------------------------
#GOTO
class GoToPose():
    def __init__(self):
    	self.goal_sent = False

	# What to do if shut down (e.g. Ctrl-C or failure)
	rospy.on_shutdown(self.shutdown)
	
	# Tell the action client that we want to spin a thread by default
	self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
	rospy.loginfo("Wait for the action server to come up")

	# Allow up to 5 seconds for the action server to come up
	self.move_base.wait_for_server(rospy.Duration(5))

    def goto(self, pos, quat):

        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
                                     Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))
        # Start moving
        self.move_base.send_goal(goal)
        # Allow TurtleBot up to 60 seconds to complete task
        success = self.move_base.wait_for_result(rospy.Duration(60)) 
        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)

#---------------------------------------------------------------
#synthesis

#make a TAhd
dead=10 #deadline
A=ha.make_manual_TAhd(dead)

# waypoints
#list of lists, each inner list contains x, y coord 
#number of lists equals number of states in env 
#update coord after mapping!
WP=[[3.2,4.0],[3.01,3.08], [2.4,4.92], [2.05,2.08], [2.07,3.15], [1.94,4.11],[1.02,2.03],[0.953,2.98],[1.03,4.57]]

#make a WTS
lab=np.zeros((9, 3))
k=1
count=1
for st in range(9):
	x=(st+k)%3
	lab[st, x]=1
	if k==1 and count==3:
		k=0
	elif k==0 and count==6:
		k=2
	count=count+1
init=2
init_dir='U'
TS=wt.make_WTS(9,3,2,lab, init, init_dir)

print TS.label[16]
#make a product
P=p.makeProduct(A,TS)
for q2 in range(len(P.states)):
	if P.trans[P.init,q2]!=float("inf"):
		print P.trans[P.init,q2], P.init,'-->',  q2

#initial graphsearch 
c=0.5
inc=0.1 #how much c is changed
#[path, dc, dd, dh]=graphsearch
string, path, finalTime, finalDC, finalDD, finalHD=gs.findPath(P,c)

#feedback to terminal
if finalHD!=float("inf"):
	#path found
	#convert path to path_WTS
	print path
	path_WTS=[]
	path_env=[]
	for q in path:
		path_WTS.append(P.states_combos[q,1]) #here WTS states-> env and direction
	print path_WTS
	for pi in path_WTS:
		path_env.append(TS.state_combos[pi, 0]) #env
	print path_env[0]
	print string, '\n The suggested path is: ', path_env, '\n The resulting distances are: \n dH: ',finalHD, '    dc: ', finalDC, '    dd: ', finalDD 
else:
	print string
#ask for input while it doesn't match one of the given 
input=raw_input("\n Indicate if you approve the suggestion or if you want to resynthesize or abort as:\n OK - I am happy run the bot!, stop - The distances are too big, abort!,\n c+ - I wish to find a path which better meets deadlines, c- - I wish to find a path which performs better w.r.t. the non-temporally bounded tasks\n\n")
feedback=['OK', 'stop', 'c+', 'c-']
while input not in feedback:
	input=raw_input("\n You inserted an unapproved feedback. Please use OK, stop, c+ or c-\n")

while input!='OK' and input!='stop':
	#feedback was c+ or c-
	oldPath=path
	if input=='c+':
		while path==oldPath and c<=1:
			c=c+inc
			string, path, finalTime, finalDC, finalDD, finalHD=gs.findPath(P,c)
	elif input=='c-':
		while path==oldPath and c>=0:
			c=c-inc
			string, path, finalTime, finalDC, finalDD, finalHD=gs.findPath(P,c)
	#feedback to terminal
	if finalHD!=float("inf") and (c<=1 and c>=0):
		#path found
		#convert path to path_WTS
		path_WTS=[] 
		path_env=[]
		for q in path:
			path_WTS.append(P.states_combos[q,1]) #here WTS states-> env and direction
		for pi in path_WTS:
			path_env.append(int(math.floor(pi/4.0))) #env
		print string, '\n The suggested path is: ', path_env, '\n The resulting distances are: \n dH: ',finalHD, '    dc: ', finalDC, '    dd: ', finalDD 
	elif c>1 or c<0:
		print 'No path that matches your wish could be found.\n'
	else:
		print string
	#ask for input while it doesn't match one of the given 4
	input=raw_input("\n Indicate if you approve the suggestion or if you want to resynthesize or abort as:\n OK - I am happy run the bot!, stop - The distances are too big, abort!,\n c+ - I wish to find a path which better meets deadlines, c- - I wish to find a path which performs better w.r.t. the non-temporally bounded tasks\n\n")
	feedback=['OK', 'stop', 'c+', 'c-']
	while input not in feedback:
		input=raw_input("\n You inserted an unapproved feedback. Please use OK, stop, c+ or c-\n")
#---------------------------------------------------------------
#send bot

#ok or stop was given as input
if input=='OK':
	#send waypoints to turtlebot
	rospy.init_node('nav_test', anonymous=False)
	navigator = GoToPose()
	pub=rospy.Publisher('move_base_simple/goal', PoseStamped, queue_size=10)
	timeStart=rospy.get_time()
	for pi in path_env:
		pi=int(pi)
		x=WP[pi][0]
		y=WP[pi][1]
		position = {'x': x, 'y' : y}
		quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
		rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
		succ = navigator.goto(position, quaternion)
		if succ==False:
			#something went wrong
			print 'An error occurred and the bot failed to reach waypoint: ', pi 
			break
		else:
			newTime=rospy.get_time()
			passedTime=newTime-timeStart
			#reached waypoint - continue
			print 'Bot reached: ', pi, ' at time', passedTime
	if succ==True:
		print 'Task completed! \n ----------------------------\n'
else:
	#inform terminal that it is aborted
	print 'You decided to abort the synthesis, no commands will be sent to the bot.\n ---------------------------------------------\n'
