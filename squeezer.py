from tkinter import *
from magenta.models.sketch_rnn.sketch_rnn_train import *
from magenta.models.sketch_rnn.model import *
from magenta.models.sketch_rnn.utils import *
from magenta.models.sketch_rnn.rnn import *
from six.moves import xrange
from dataclasses import dataclass
from typing import List
from PIL import Image, ImageTk

import os
import random
import subprocess

@dataclass
class ArmDoodleCommand:
    pen_down: bool
    dx: float
    dy: float


def draw_strokes(data, canvas, factor=0.2):
    doodle_commands = []
    min_x, max_x, min_y, max_y = get_bounds(data, factor)
    # dwg = svgwrite.Drawing(svg_filename, size=dims)
    # dwg.add(dwg.rect(insert=(0, 0), size=dims,fill='white'))
    lift_pen = 1
    last_x, last_y = (250, 250)
    command = "m"
    for i in xrange(len(data)):
        x = float(data[i,0])/factor
        y = float(data[i,1])/factor
        if (lift_pen == 1):
          command = "m"
          doodle_commands.append(ArmDoodleCommand(False, x, y))
          canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes", fill="#00ff00")
        elif (command != "l"):
          command = "l"
          doodle_commands.append(ArmDoodleCommand(True, x, y))
          canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes")
        else:
          command = ""
          doodle_commands.append(ArmDoodleCommand(True, x, y))
          canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes")
        lift_pen = data[i, 2]
        last_x = last_x + x
        last_y = last_y + y
    return doodle_commands
    # stroke_width = 1
    # dwg.add(dwg.path(p).stroke(the_color,stroke_width).fill("none"))
    # dwg.save()
    # display(SVG(dwg.tostring()))


def simulate_draw(doodle_commands: List[ArmDoodleCommand], doodle_canvas, multiple, robot_multiple):
    last_x, last_y = (0, 0)
    last_robot_x, last_robot_y = (0, 0)
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    min_robot_x, min_robot_y, max_robot_x, max_robot_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    for d in doodle_commands:
        x, y = d.dx * multiple, d.dy * multiple
        robot_x, robot_y = d.dx * robot_multiple, d.dy * robot_multiple
        if not d.pen_down:
          doodle_canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes", fill="#00ff00", )
        else:
          doodle_canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes")
        last_x, last_y = last_x + x, last_y + y
        last_robot_x, last_robot_y = last_robot_x + robot_x, last_robot_y + robot_y
        min_x, min_y, max_x, max_y = min(last_x, min_x), min(last_y, min_y), max(last_x, max_x), max(last_y, max_y),
        min_robot_x, min_robot_y, max_robot_x, max_robot_y = min(last_robot_x, min_robot_x), \
                                                             min(last_robot_y, min_robot_y), max(last_robot_x, max_robot_x), max(last_robot_y, max_robot_y),
    doodle_canvas.create_text(.5 * WINDOW, .2 * WINDOW, text="Min: {0:5.2f},{1:5.2f}  Max: {2:5.2f},{3:5.2f}".format(min_x, min_y, max_x, max_y), font=("Helvetica", 18), tags="doodle_text", fill="#7CA2C3")
    doodle_canvas.create_text(.5 * WINDOW, .25 * WINDOW, text="Robot Min: {0:5.2f},{1:5.2f}  Max: {2:5.2f},{3:5.2f}".format(min_robot_x, min_robot_y, max_robot_x, max_robot_y), font=("Helvetica", 18), tags="doodle_text", fill="#7CA2C3")

# def load_env_compatible(data_dir, model_dir):
#   """Loads environment for inference mode, used in jupyter notebook."""
#   # modified https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/sketch_rnn_train.py
#   # to work with depreciated tf.HParams functionality
#   model_params = sketch_rnn_model.get_default_hparams()
#   with tf.gfile.Open(os.path.join(model_dir, 'model_config.json'), 'r') as f:
#     data = json.load(f)
#   fix_list = ['conditional', 'is_training', 'use_input_dropout', 'use_output_dropout', 'use_recurrent_dropout']
#   for fix in fix_list:
#     data[fix] = (data[fix] == 1)
#   model_params.parse_json(json.dumps(data))
#   return load_dataset(data_dir, model_params, inference_mode=True)
#
# def load_model_compatible(model_dir):
#   """Loads model for inference mode, used in jupyter notebook."""
#   # modified https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/sketch_rnn_train.py
#   # to work with depreciated tf.HParams functionality
#   model_params = sketch_rnn_model.get_default_hparams()
#   with tf.gfile.Open(os.path.join(model_dir, 'model_config.json'), 'r') as f:
#     data = json.load(f)
#   fix_list = ['conditional', 'is_training', 'use_input_dropout', 'use_output_dropout', 'use_recurrent_dropout']
#   for fix in fix_list:
#     data[fix] = (data[fix] == 1)
#   model_params.parse_json(json.dumps(data))
#
#   model_params.batch_size = 1  # only sample one at a time
#   eval_model_params = sketch_rnn_model.copy_hparams(model_params)
#   eval_model_params.use_input_dropout = 0
#   eval_model_params.use_recurrent_dropout = 0
#   eval_model_params.use_output_dropout = 0
#   eval_model_params.is_training = 0
#   sample_model_params = sketch_rnn_model.copy_hparams(eval_model_params)
#   sample_model_params.max_seq_len = 1  # sample one point at a time
#   return [model_params, eval_model_params, sample_model_params]

def load_env_compatible(data_dir, model_dir):
  """Loads environment for inference mode, used in jupyter notebook."""
  # modified https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/sketch_rnn_train.py
  # to work with depreciated tf.HParams functionality
  model_params = sketch_rnn_model.get_default_hparams()
  with tf.gfile.Open(os.path.join(model_dir, 'model_config.json'), 'r') as f:
    data = json.load(f)
  fix_list = ['conditional', 'is_training', 'use_input_dropout', 'use_output_dropout', 'use_recurrent_dropout']
  for fix in fix_list:
    data[fix] = (data[fix] == 1)
  model_params.parse_json(json.dumps(data))
  return load_dataset(data_dir, model_params, inference_mode=True)

def load_model_compatible(model_dir):
  """Loads model for inference mode, used in jupyter notebook."""
  # modified https://github.com/tensorflow/magenta/blob/master/magenta/models/sketch_rnn/sketch_rnn_train.py
  # to work with depreciated tf.HParams functionality
  model_params = sketch_rnn_model.get_default_hparams()
  with tf.gfile.Open(os.path.join(model_dir, 'model_config.json'), 'r') as f:
    data = json.load(f)
  fix_list = ['conditional', 'is_training', 'use_input_dropout', 'use_output_dropout', 'use_recurrent_dropout']
  for fix in fix_list:
    data[fix] = (data[fix] == 1)
  model_params.parse_json(json.dumps(data))

  model_params.batch_size = 1  # only sample one at a time
  eval_model_params = sketch_rnn_model.copy_hparams(model_params)
  eval_model_params.use_input_dropout = 0
  eval_model_params.use_recurrent_dropout = 0
  eval_model_params.use_output_dropout = 0
  eval_model_params.is_training = 0
  sample_model_params = sketch_rnn_model.copy_hparams(eval_model_params)
  sample_model_params.max_seq_len = 1  # sample one point at a time
  return [model_params, eval_model_params, sample_model_params]

def decode(z_input=None, draw_mode=True, temperature=0.1, factor=0.2):
  z = None
  if z_input is not None:
    z = [z_input]
  sample_strokes, m = sample(sess, sample_model, seq_len=eval_model.hps.max_seq_len, temperature=temperature, z=z)
  strokes = to_normal_strokes(sample_strokes)
  if draw_mode:
    print("Drawing")
    # draw_strokes(strokes, factor)
  return strokes

models_root_dir = '/tmp/sketch_rnn/models'
model_dir = '/tmp/sketch_rnn/models/flamingo/lstm_uncond'
download_pretrained_models()
[hps_model, eval_hps_model, sample_hps_model] = load_model_compatible(model_dir)
# construct the sketch-rnn model here:
reset_graph()
reset_graph()
model = Model(hps_model)
eval_model = Model(eval_hps_model, reuse=True)
sample_model = Model(sample_hps_model, reuse=True)

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())
load_checkpoint(sess, model_dir)
N = 10
reconstructions = []


def idle(parent, canvas):
    canvas.update()
    parent.after_idle(idle, parent, canvas)


WINDOW = 600  # window size
DOODLE_MULTIPLE = 3
ROBOT_MULTIPLE = .005
root = Tk()
root.title('UR10 Doodle UI (q to exit)')
root.bind('q', 'exit')
root.bind('<Escape>', 'exit')
canvas = Canvas(root, width=WINDOW, height=.75 * WINDOW, background='white')
image = Image.open("ur10.jpg")
photo = ImageTk.PhotoImage(image)
img2 = canvas.create_image(-10, -3, image=photo, anchor="nw")
canvas.create_text(.5 * WINDOW, .125 * WINDOW, text="Press R to generate a new doodle!", font=("Helvetica", 24), tags="text1", fill="#949494")
canvas.create_text(.5 * WINDOW, .7 * WINDOW, text="Robot Draw Multiple: {}".format(ROBOT_MULTIPLE), font=("Helvetica", 12), tags="text1", fill="#949494")

target_doodle = []

def say_from_phrases(phrases):
    subprocess.Popen(['say', "{}".format(random.choice(phrases))])

say_from_phrases(['Welcome, I am a robot arm. Here is a drawing I just came up with.'])

def do_draw_random():
    global target_doodle # lol

    canvas.delete("doodle_text")
    canvas.delete("doodle_strokes")
    drawing = decode(temperature=0.5, draw_mode=False)
    strokes = draw_strokes(drawing, canvas)
    canvas.delete("doodle_text")
    canvas.delete("doodle_strokes")
    simulate_draw(strokes, canvas, DOODLE_MULTIPLE, ROBOT_MULTIPLE)
    canvas.move('doodle_strokes', 250, 250)
    target_doodle = strokes
    say_from_phrases(['This is one I just thought of.',
                      "Wouldn't this look great?",
                      "Let me draw this.",
                      "Come on let me draw this.",
                      'Please let me draw this, it is my favorite.',
                      "It's not my best idea but it could be good."])


def do_arm_draw(doodle_commands: List[ArmDoodleCommand], robot_multiple):
    os.system('say "I will now commence drawing. Humans, please stand back."')
    from urx import Robot
    from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper
    rob = Robot("169.254.241.97")
    robot_pose = rob.get_pose()
    start_position = robot_pose.get_pos().copy()
    start_orientation = robot_pose.get_orient().copy()

    last_robot_x, last_robot_y = start_position[0], start_position[1]

    pen_was_down = False

    for d in doodle_commands:
        robot_dx, robot_dy = d.dx * robot_multiple, d.dy * robot_multiple

        increased_x, increased_y = last_robot_x + robot_dx, last_robot_y + robot_dy

        if not d.pen_down:
            if pen_was_down:
                say_from_phrases(['Yes! Very nice.',
                                   'This is coming along well.',
                                   'This may be my best creation yet.',
                                   'This will be great.'])
            robot_pose.set_pos([increased_x, increased_y, start_position[2] + 0.01])
            rob.set_pose(robot_pose, 0.1, 0.1)
        else:
            robot_pose.set_pos([increased_x, increased_y, start_position[2]])
            rob.set_pose(robot_pose, 0.1, 0.1)

        # Increment position, update cross-step state
        last_robot_x, last_robot_y = increased_x, increased_y
        pen_was_down = d.pen_down

    # Go back to home
    robot_pose.set_pos([start_position[0], start_position[1], start_position[2] + 0.01])
    robot_pose.set_pos([start_position[0], start_position[1], start_position[2]])
    rob.set_pose(robot_pose, 0.1, 0.1)
    say_from_phrases(["Human! How do you like my doodle?"])

root.bind('r', func=lambda e: do_draw_random())
root.bind('d', func=lambda e: do_arm_draw(target_doodle, ROBOT_MULTIPLE))

canvas.pack()


#
# start idle loop
#
root.after(100, idle, root, canvas)
root.mainloop()
