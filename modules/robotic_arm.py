from drivers.servo_driver import Servo
import submodules.stepper_axis as stepper_axis

from math import atan, degrees
import time

class RoboticArm:
  # Dimensions of the Arm
  vertical_offset_mm = 50
  vertical_arm_mm = 100
  horizontal_arm_mm = 100
  level_arm_len= 20
  claw_offset_to_center = 10

  small_cup_positions = [(100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30)]

  large_cup_positions = [(100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30)]

  # Positions of the cooking utensils by size.
  # Increasing index of size implies increasing diameter.
  utensil_positions_size = [(100, 180, 30, 30, 30),
                            (100, 180, 30, 30, 30),
                            (100, 180, 30, 30, 30)]
    
  # Positions of the components when the arm is at base
  base_pos = (100, 0, 30, 30, 30)
                      
  # Dimensions of the Rail
  max_rail_translation_mm = 520
  
  def __init__(self, rail_dir_pin, rail_step_pin, rail_enable_pin,
               base_servo_channel,
               vertical_servo_channel,
               horizontal_servo_channel,
               level_servo_channel,
               tipping_servo_channel,
               grasp_servo_channel):
    self.base_servo = Servo(base_servo_channel)
    self.vertical_servo = Servo(vertical_servo_channel)
    self.horizontal_servo = Servo(horizontal_servo_channel)
    self.level_servo = Servo(level_servo_channel)
    self.tipping_servo = Servo(tipping_servo_channel)
    self.grasp_servo = Servo(grasp_servo_channel)
    self.rail = stepper_axis.StepperAxis(rail_dir_pin, rail_step_pin, rail_enable_pin,
                                         RoboticArm.max_rail_translation_mm,
                                         inc_clockwise=False)
    self.move_to_base()

# Begin unfinished methods 
  def move_rail_rotate_base(self, dest_pos):
    self.at_base = False
    self.rail.move_to(max(0, min(RoboticArm.max_rail_translation_mm, dest_pos[1])))
    curr_y_pos = self.rail.get_curr_pos_mm()
    # Need to rotate base servo to point from (0,curr_pos[1]) to (dest_pos[0],dest_pos[1])
    # degrees to rotate clockwise with 0 pointing along x axis towards containers
    degrees = degrees(atan(float(curr_y_pos - dest_pos[1])
                                     /float(0 - dest_pos[0])))
    if (degrees < 0 or degrees > 180):
       raise ValueError("Invalid rotation angle:" +
                        str(degrees) + " degrees. Current position: "
                        + curr_y_pos + "Dest position: " + dest_pos)
    self.base_servo.move_to(degrees)

  def get_corrected_vertical_angle(vertical_angle):
    vertical_servo_offset = 15
    vertical_angle_corrected = vertical_angle - vertical_servo_offset
    if vertical_angle_corrected < 0:
      vertical_angle_corrected = vertical_angle_corrected - vertical_servo_offset
    return vertical_angle_corrected
  
  # All angles are in degrees. 
  def get_claw_x_from_servo_pos(base_angle, vertical_angle, horizontal_angle):
    """ Gets the position of the claw from the positions of the base, vertical
        and horizontal servos. """
    vertical_angle_corrected = get_corrected_vertical_angle(vertical_angle)

  def get_claw_y_from_servo_pos(base_angle, vertical_angle, horizontal_angle):
    None
    
# End of unfinished methods 
  
  def claw_grasp(self):
    self.grasp_servo.move_to(10)

  def claw_release(self):
    self.grasp_servo.move_to(55)

  
  def pour(self):
    """ Pours the container assuming that it is positioned over the vessel and
        waits for a few seconds before straightening it up. """
    self.tipping_servo.move_to(180)
    # Wait a few seconds for the contents to drain out.
    time.sleep(5)
    self.straighten_tipping_servo()

  def straighten_tipping_servo(self):
    self.tipping_servo.move_to(0)

  # Rail stepper and base servo have been adjusted as necessary. This function
  # Adjusts the three servos Vertical, Horizontal and Level servos to get the
  # required Z and X from to_pos.
  def execute_move_claw_xz(self, to_pos):
    from_pos = (self.vertical_servo.get_current_pos(),
                self.horizontal_servo.get_current_pos(),
                self.level_servo.get_current_pos())
    pos_delta = (to_pos[2] - from_pos[0],
                 to_pos[3] - from_pos[1],
                 to_pos[4] - from_pos[2])
    max_delta = max(abs(pos_delta[0]), abs(pos_delta[1]), abs(pos_delta[2]))
    for i in range(1, int(max_delta + 1)):
      # Update each servo proportionally
      update = [(float(i)/max_delta) * x for x in pos_delta]
      new_pos = [int(update[j] + from_pos[j]) for j in range(0, len(from_pos))]
      self.vertical_servo.move_to(new_pos[0])
      self.horizontal_servo.move_to(new_pos[1])
      self.level_servo.move_to(new_pos[2])
    self.vertical_servo.move_to(to_pos[0])
    self.horizontal_servo.move_to(to_pos[1])
    self.level_servo.move_to(to_pos[2])
    
  def move_to_cup(self, is_small_cup, cup_num):
    if is_small_cup:
      if cup_num < 0 or cup_num > 6:
        raise ValueError("Invalid small cup number:" + cup_num)
    else:
      if cup_num < 0 or cup_num > 5:
        raise ValueError("Invalid large cup number:" + cup_num)
      
    # Positions of the various servos.
    if is_small_cup:
      pos_for_cup = RoboticArm.small_cup_positions[cup_num]
    else:
      pos_for_cup = RoboticArm.large_cup_positions[cup_num]
    # Move the arm away from stirrer before moving rail.
    self.base_servo.move_to(pos_for_cup[1])
    # Arm out of collision path with stirrer. So, we can move the rail.
    self.rail.move_to(pos_for_cup[0])
    # Position claw around the cup.
    self.execute_move_claw_xz(pos_for_cup)
    self.at_base = False
    None

  def move_to_utensil(self, utensil_size):
    if utensil_size < 0 or utensil_size > 2:
      raise ValueError("Invalid utensil size:" + utensil_size)
    # Positions of the various servos.
    desired_servo_pos = RoboticArm.utensil_positions_size[utensil_size]
    self.execute_move_claw_xz(desired_servo_pos)
    self.rail.move_to(desired_servo_pos[0])
    self.base_servo.move_to(desired_servo_pos[1])
    self.at_base = False

  def move_to_base(self):
    self.execute_move_claw_xz(RoboticArm.base_pos)
    self.base_servo.move_to(RoboticArm.base_pos[1])
    self.rail.move_to(RoboticArm.base_pos[0])
    self.rail.disable()
    self.at_base = True
    None

  def is_at_base(self):
    return self.at_base

  # API method exposed by the RoboticArm
  def add_cup(self, is_small_cup, cup_num, utensil_size):
    # Init
    self.straighten_tipping_servo()
    self.claw_release()
    # Move and position around cup and grasp it
    self.move_to_cup(is_small_cup, cup_num)
    self.claw_grasp()
    self.move_to_utensil(utensil_size)
    # Pours and straightens.
    self.pour()
    self.move_to_cup(is_small_cup, cup_num)
    self.claw_release()
    self.move_to_base()
    self.rail.disable()

  def shutdown(self):
    self.move_to_base()
    
if (__name__ == "__main__"):
  arm = RoboticArm(6, 5,
                   0, # Base
                   1, # Vertical
                   2, # Horizontal
                   3, # Level/Tilt
                   4, # Tipping
                   5) # Claw
  #arm.move_to_base()
  #arm.add_cup(True, 1, 0)
  #arm.add_cup(True, 2, 0)
  #arm.add_cup(True, 3, 0)
  #arm.add_cup(True, 4, 0)
  #arm.add_cup(True, 5, 0)
