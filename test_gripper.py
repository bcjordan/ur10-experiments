from urx import Robot
from libs.modded_gripper import Modded_Gripper
import os
rob = Robot("169.254.241.97")

gripper = Modded_Gripper(rob)

gripper.gripper_and_move_action(80)

robot_start_pose = rob.get_pose()
start_position = robot_start_pose.get_pos().copy()
start_orientation = robot_start_pose.get_orient().copy()
new_orientation = robot_start_pose.get_orient().copy()

# new_orientation.set_axis_angle("X")
robot_start_pose.set_pos([start_position[0], start_position[1], start_position[2] + 0.01])
robot_start_pose.set_orient(new_orientation)
rob.set_pose(robot_start_pose, 0.1, 0.1)#, True, "movej")

# robot_start_pose.set_pos(start_position)
# robot_start_pose.set_orient(new_orientation)
# rob.set_pose(robot_start_pose, 0.1, 0.1)

os.system('say "movement completed"')
