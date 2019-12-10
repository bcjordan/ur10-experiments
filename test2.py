import os
def interact():
    import code
    code.InteractiveConsole(locals=globals()).interact()

from urx import Robot
rob = Robot("169.254.241.97")
robot_start_pose = rob.get_pose()
start_position = robot_start_pose.get_pos().copy()
start_orientation = robot_start_pose.get_orient().copy()
new_orientation = robot_start_pose.get_orient().copy()

#
unit_quaternion = new_orientation.get_unit_quaternion()
print(unit_quaternion)
interact()

# new_orientation.set_axis_angle("X")
robot_start_pose.set_pos([start_position[0], start_position[1], start_position[2]])
robot_start_pose.set_orient(new_orientation)
rob.set_pose(robot_start_pose, 0.1, 0.1)#, True, "movej")
robot_start_pose.set_pos(start_position)
robot_start_pose.set_orient(new_orientation)
rob.set_pose(robot_start_pose, 0.1, 0.1)

# rob.rx -= 0.1  # rotate tool around X axis
# rob.z_t += 0.01  # move robot in tool z axis for +1cm

os.system('say "movement completed"')
