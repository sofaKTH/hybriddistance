#Synthesis
import math
import numpy as np 
import hybridAuto as ha
import weightedTrans as wt
import product as p
import graphSearch as gs

#ROS
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseActionGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped

#---------------------------------------------------------------
#GOTO <-- is something wrong here?
class GoToPose():
    def __init__(self):
    	self.goal_sent = False
    	rospy.on_shutdown(self.shutdown)
    	self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    	rospy.loginfo("Wait for the action server to come up")
    	self.move_base.wait_for_server(rospy.Duration(5))

    def goto(self, pos, quat):
        # Construct a movebasegoal
        goal_sent = True
        goal=MoveBaseGoal()
        goal.target_pose.header.frame_id='/map'
        goal.target_pose.header.stamp=rospy.Time.now()
        goal.target_pose.pose.position.x=pos['x']
        goal.target_pose.pose.position.y=pos['y']
        goal.target_pose.pose.position.z=0.0
        goal.target_pose.pose.orientation.x=quat['r1']
        goal.target_pose.pose.orientation.y=quat['r2']
        goal.target_pose.pose.orientation.z=quat['r3']
        goal.target_pose.pose.orientation.w=quat['r4']
        # Send goal
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
	#Reset goal_sent status
        self.goal_sent = False
        return result
    # When TurtleBot couldn't reach the goal in time
    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)

#---------------------------------------------------------------
#Synthesis

# Construct a TAhd (specific formula defined)
dead=10 #deadline
A=ha.make_manual_TAhd(dead)

# Construct a WTS
# 1. List of Waypoints
#list of lists, each inner list contains x, y coordinates 
#number of lists equals number of states
#update coordinates after mapping!
WP=[[3.2,4.0],[3.01,3.08], [2.4,4.92], [2.05,2.08], [2.07,3.15], [1.94,4.11],[1.02,2.03],[0.953,2.98],[1.03,4.57]]
#2. labelling construction
# consider 3x3 environment with 4 possible orientations (up, down, left, right)
# 3 ap's considered (value of x)
# the below create one specific labelling, can be changed in accordance with desire
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
# 3. set initial state and initial orientation
init=2
init_dir='U'
#4. Build the WTS
TS=wt.make_WTS(9,3,2,lab, init, init_dir)

#Construct a product
P=p.makeProduct(A,TS)

#First graphsearch 
c=0.5 #initial value of weight
inc=0.1 #how much c is changed when feedback is given later
string, path, finalTime, finalDC, finalDD, finalHD=gs.findPath(P,c) # find path

#Send feedback to terminal
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
	#no path found - environment doesn't match task
	print string
#Ask for feedback from terminal
if finalHD!=float("inf"):
	#ask for input while it doesn't match one of the given 
	input=raw_input("\n Indicate if you approve the suggestion or if you want to resynthesize or abort as:\n OK - I am happy run the bot!, stop - The distances are too big, abort!,\n c+ - I wish to find a path which better meets deadlines, c- - I wish to find a path which performs better w.r.t. the non-temporally bounded tasks\n\n")
	feedback=['OK', 'stop', 'c+', 'c-']
	while input not in feedback:
		input=raw_input("\n You inserted an unapproved feedback. Please use OK, stop, c+ or c-\n")
	# correct feedback has been given
	
	# Check if c should be changed 
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
		#Send new feedback to terminal
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
			# human preference can't be reached
			print 'No path that matches your wish could be found.\n'
		else:
			#error - this should not happen
			print string
		#ask for input while it doesn't match one of the given 4
		input=raw_input("\n Indicate if you approve the suggestion or if you want to resynthesize or abort as:\n OK - I am happy run the bot!, stop - The distances are too big, abort!,\n c+ - I wish to find a path which better meets deadlines, c- - I wish to find a path which performs better w.r.t. the non-temporally bounded tasks\n\n")
		feedback=['OK', 'stop', 'c+', 'c-']
		while input not in feedback:
			input=raw_input("\n You inserted an unapproved feedback. Please use OK, stop, c+ or c-\n")
	#---------------------------------------------------------------
	#Send path to TurtleBot

	#ok or stop was given as input
	if input=='OK':
		#send waypoints to turtlebot
		rospy.init_node('nav_test', anonymous=False)
		navigator = GoToPose()
		#pub=rospy.Publisher('move_base_simple/goal', PoseStamped, queue_size=10)
		timeStart=rospy.get_time()
		# For every goal-state in the path
		for pi in path_env:
			# get and set corresponding coordinates
			pi=int(pi)
			x=WP[pi][0]
			y=WP[pi][1]
			position = {'x': x, 'y' : y}
			quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}
			rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
			#send goal to bot through GOTO class above
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
