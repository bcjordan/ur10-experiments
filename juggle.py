import os

from urx import Robot

# Does a quick stab upwards (+z) to test if speed would enable juggling

rob = Robot("169.254.241.97")
robot_start_pose = rob.get_pose()
start_position = robot_start_pose.get_pos().copy()
start_orientation = robot_start_pose.get_orient().copy()

robot_start_pose.set_pos([start_position[0], start_position[1], start_position[2] + 0.12])
rob.set_pose(robot_start_pose, 25, 25)#, True, "movej")
robot_start_pose.set_pos(start_position)
rob.set_pose(robot_start_pose, 0.1, 0.1)

os.system('say "movement completed"')
