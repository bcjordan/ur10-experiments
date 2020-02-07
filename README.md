# ur10-experiments
Experiments with a UR10 Robot Arm!



### The Dream: Juggling final project balls

* [juggle.py](https://github.com/bcjordan/ur10-experiments/blob/master/juggle.py) - python code for acceleration/velocity control experiments.

One of my initial project ideas was to build robot arms that could juggle and pass balls. So I thought using a robot arm to test my final project (smart color-LED juggling balls) would be fun to try.

I started by characterizing the upward velocity of the arm, since that would be the ultimate pinch-point for a juggling arm. If it couldn't get a ball into the air, it wouldn't work.

At speed 100 in the UR-10 GUI, the arm moved so slow that something on it would not get any air time.

Once I hooked up to the ethernet and controlled the arm commands directly through the python API, I found that much higher velocities were possible.

I very slowly ratcheted up the velocities with very confined small upward `+z` movements.

I placed a small ball of tape on the arm to see if the velocity was high enough to constitute a throw.

![juggling](uploads/c82bc27d937e9e9e3b33b7fea2f371f6/juggling.mp4)

It got a few inches of height!

By the time it got there, the arm's movement slow-down seemed so extreme I didn't want to continue pushing the limits of the arm without some more research that it would be OK for the machine. So I decided to pivot to a different project for the week!

If I were to continue on this, I would explore:

* Rotating the wrist of the arm simultaneous with the upward movement (similar to how we move our wrists when throwing a ball upwards)
* Incorporating a LONG catch/throw end-effector that provides leverage — since juggling balls (even clubs) are much lighter than most UR-10 payloads, this should be fine.

### The Fall-back Plan: sketch-rnn model + squeezing bottles = ketchup art

* [gui.py](https://github.com/bcjordan/ur10-experiments/blob/master/gui.py) - imports a sketch-rnn model (flamingos), generates a random series of drawing steps from the latent space, and sends robot arm commands to doodle
* [squeezer.py](https://github.com/bcjordan/ur10-experiments/blob/master/squeezer.py) - version that additionally tightens the gripper to slowly squeeze a bottle (initially Ketchup, but intended to work for other bottles as well)

I thought it was interesting how the robot arm had both a gripper and very fine 2-axis control, so I wanted to combine the two. I decided to try to make a system that would draw stuff with squeezable bottles.

I also figured sketch-rnn model would be an interesting way to get individual strokes for a variety of drawings. And that way the art is completely the robot's!

#### Making a Drawing UI (that talks to you)

![ui-shot-bad](uploads/7921c9dc502a6ee21c6f7958d5bff786/ui-shot-bad.png)

I wanted to have a GUI to be able to see what the arm was about to draw. I initially wanted to explore using JS, but found that there weren't any great node/JS libraries out there for controlling the UR-10 (YET!). There is one node-RED module, but I had trouble getting that connected up to the UR-10.

I decided to build off of my python experiments and use this as an opportunity to play with tkinter, which I was pleasantly surprised how nice it was to work with.

The GUI app process:

1. Downloads a pre-trained sketch-rnn model (in my case, `flamingo`s and loads a checkpoint) — looking back, I would have chosen a model with better drawings. People are bad at drawing flamingos, and so is the model!
    `from magenta.models.sketch_rnn.model import *`
2. Draws the model to a tkinter `canvas` with a tag so it can later be cleared
    `canvas.create_line(last_x, last_y, last_x + x, last_y + y, tags="doodle_strokes", fill="#00ff00")`
3. Listens to `r` keystroke to trigger grabbing a new drawing, and `d` keystroke to commence the robot arm drawing the creation.
    `root.bind('d', func=lambda e: do_arm_draw(target_doodle, ROBOT_MULTIPLE))`

When simulating on a canvas, it also collects ArmDoodleCommand moves into an array:

```
@dataclass
class ArmDoodleCommand:
    pen_down: bool
    dx: float
    dy: float
```

It then uses that same set of commands (with a different scale multiplier) to draw with the robot arm.

When drawing with the arm, it:

1. Connects to the robot `from urx import Robot; robot = Robot(ARM_IP)`
2. Gets the current pose / rotation `robot.get_pose()`
3. Moves to the next point. If the pen is up, include a `z` axis increase when moving in order to not draw.

I additionally made it use `espeak` / `speak` (on OS X) to say stuff out loud while it draws and when it is complete. This was sometimes useful in debugging when I had to keep my eye on the robot arm in order to man the stop button while also debugging the code.

Initially the speech was blocking, using `os.system`, so I changed it to: `subprocess.Popen(['say', "{}".format(random.choice(phrases))])`, where phrases is an array of goofy things the robot could say.

```
    say_from_phrases(['This is one I just thought of.',
                      "Wouldn't this look great?",
                      "Let me draw this.",
                      "Come on let me draw this.",
                      'Please let me draw this, it is my favorite.',
                      "It's not my best idea but it could be good."])

    say_from_phrases(["Human! How do you like my doodle?"])
```

#### Testing with Drawing

I initially brought down a pencil to try drawing with. As I was zeroing the robot arm, I realized a pencil would be one of the worst possible drawing implements, since it would have very little give and would change its required zero over time.

![pencil-bad-idea](uploads/6cb3ee878bdcc05ea98bfa19010c1455/pencil-bad-idea.jpg)

I then tried a standard sharpie marker, which worked OK! After a while, though, on strokes that went perpendicular to the gripper, the marker would slip and go diagonal, losing firm contact.

![manual-grip-marker](uploads/d0685a60cb8a2d9826ec3803d9a78ea9/manual-grip-marker.jpg)

![robot-drawing-2](uploads/f1d48d91f7072dac52350b9a5ab662d6/robot-drawing-2.jpg)

A kindly CBA student then pointed us towards paint-y-markers with spring-y tips. Those worked really well.

![robot-drawing](uploads/16af50835f3a4c3f019d3be2013253d0/robot-drawing.jpg)

![robot-drawing-3](uploads/3ec6f4b2e613f28e5436edaa7dedce2b/robot-drawing-3.jpg)

My code had a bug where it would return home after drawing, but not lift the pen up. I eventually fixed it but haven't run it with a pen since then!

#### Ketchup Time

The dream here was to create a system that could work with any squeezable bottle. Since I had some in my refrigerator, I started with ketchup.

To control the gripper, within the drawing code, `if step.pen_down`:

```
if squeeze_count % SQUEEZE_EACH_STEPS == 0:
    current_squeeze += 1
    gripper.gripper_action(current_squeeze) # really gripper_position
squeeze_count += 1
```

This way it increases the integer gripper position once every N doodle steps.

Precautions I followed, since I wanted to make sure I didn't get any anywhere:

* Mount ketchup with a cup underneath the gripper. Ketchup drips for ~30 seconds after being initially gripped.

![ketchup-setup](uploads/41e7449b6f9bbaecfe2aff2348857402/ketchup-setup.jpg)

* To avoid requiring a tighter grip, I added rubber bands to the gripper fingers.
* Made sure not to let the bottle drop. This partially informed the approach of continually increasing grip pressure, rather than periodically gripping and un-gripping the bottle.
* Have a layer of plastic underneath the paper for no leakage

![multiple-layers-arm-shot](uploads/44cee5d1051867174df3a1f1eb87683e/multiple-layers-arm-shot.png)

I found that tipping the ketchup to the side at a 45 degree angle would allow for a better grip and flow of the ketchup.

![Zeroing the Ketchup](uploads/6410c3932fb8a5fab704dbae8f1b8c01/output_video_small_2.mp4)

![First Attempt: Gripping Too Fast](uploads/b37837fec5176ee8bf83e76d428d2ce8/output_video_small.mp4)

Final creation:

![Beautiful Final Drawing](uploads/200235f9d72403c3c89bcf764a7f65cd/final_drawing.mp4)

The drawing it ultimately produced was underwhelming, but if you squint at it, you can sort of see a flamingo:

![drawing-terrible](uploads/e50506d659e4e07204af8b9a840c79cb/drawing-terrible.jpg)

The robot tried its best!

As I walked home the night of ketchup drawing, despite not having gotten any ketchup on me or any equipment, my brain was still smelling ketchup. Looking back, I would have chosen paint, or glue.


