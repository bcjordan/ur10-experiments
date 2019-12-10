from tkinter import *
from magenta.models.sketch_rnn.sketch_rnn_train import *
from magenta.models.sketch_rnn.model import *
from magenta.models.sketch_rnn.utils import *
from magenta.models.sketch_rnn.rnn import *
from six.moves import xrange
from dataclasses import dataclass
from typing import List


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
          doodle_canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes", fill="#00ff00")
        else:
          doodle_canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes")
        last_x, last_y = last_x + x, last_y + y
        last_robot_x, last_robot_y = last_robot_x + robot_x, last_robot_y + robot_y
        min_x, min_y, max_x, max_y = min(last_x, min_x), min(last_y, min_y), max(last_x, max_x), max(last_y, max_y),
        min_robot_x, min_robot_y, max_robot_x, max_robot_y = min(last_robot_x, min_robot_x), \
                                                             min(last_robot_y, min_robot_y), max(last_robot_x, max_robot_x), max(last_robot_y, max_robot_y),
    doodle_canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes")
    doodle_canvas.create_text(.5 * WINDOW, .2 * WINDOW, text="Min: {0:7.2f},{1:7.2f}   Max: {2:7.2f},{3:7.2f}".format(min_x, min_y, max_x, max_y), font=("Helvetica", 18), tags="doodle_text", fill="#0000b0")
    doodle_canvas.create_text(.5 * WINDOW, .25 * WINDOW, text="Robot Min: {0:7.2f},{1:7.2f}   Max: {2:7.2f},{3:7.2f}".format(min_robot_x, min_robot_y, max_robot_x, max_robot_y), font=("Helvetica", 18), tags="doodle_text", fill="#0000b0")


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
ROBOT_MULTIPLE = .01
root = Tk()
root.title('UR10 Doodle UI (q to exit)')
root.bind('q', 'exit')
root.bind('<Escape>', 'exit')
canvas = Canvas(root, width=WINDOW, height=.75 * WINDOW, background='white')
canvas.create_text(.5 * WINDOW, .125 * WINDOW, text="Press R to generate a new doodle!", font=("Helvetica", 24), tags="text1", fill="#0000b0")
canvas.create_text(.5 * WINDOW, .7 * WINDOW, text="Robot Draw Multiple: {}".format(ROBOT_MULTIPLE), font=("Helvetica", 12), tags="text1", fill="#0000b0")

def do_draw_random():
    canvas.delete("doodle_text")
    canvas.delete("doodle_strokes")
    drawing = decode(temperature=0.5, draw_mode=False)
    strokes = draw_strokes(drawing, canvas)
    canvas.delete("doodle_text")
    canvas.delete("doodle_strokes")
    simulate_draw(strokes, canvas, DOODLE_MULTIPLE, ROBOT_MULTIPLE)
    canvas.move('doodle_strokes', 250, 250)


root.bind('r', func=lambda e: do_draw_random())

canvas.pack()


#
# start idle loop
#
root.after(100, idle, root, canvas)
root.mainloop()
