import modules.driver.servo as servo
import modules.stepper_axis as stepper_axis

import math
import time

class RoboticArm:
  # Dimensions of the Arm
  vertical_offset_mm = 50
  vertical_arm_mm = 100
  horizontal_arm_mm = 100
  level_arm_len= 20
  claw_offset_to_center = 10

  small_cup_positions = [(100, 0, 30, 30, 30), (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30), (100, 0, 30, 30, 30),
                         (100, 0, 30, 30, 30), (100, 0, 30, 30, 30)]

  large_cup_positions = [(100, 0, 30, 30, 30), (100, 0, 30, 30, 30),
                        (100, 0, 30, 30, 30), (100, 0, 30, 30, 30),
                        (100, 0, 30, 30, 30), (100, 0, 30, 30, 30)]

  # Positions of the cooking utensils by size.
  # Increasing index of size implies increasing diameter.
  utensil_positions_size = [(100, 180, 30, 30, 30),
                           (100, 180, 30, 30, 30),
                           (100, 180, 30, 30, 30)]
    

  servo_base_pos = (100, 0, 30, 30, 30)
                      
  # Dimensions of the Rail
  max_rail_translation_mm = 100
  def __init__(self, rail_dir_pin, rail_step_pin,
               base_servo_pin,
               vertical_servo_pin,
               horizontal_servo_pin,
               level_servo_pin,
               tipping_servo_pin,
               grasp_servo_pin):
    self.base_servo = servo.Servo(base_servo_pin)
    self.vertical_servo = servo.Servo(vertical_servo_pin)
    self.horizontal_servo = servo.Servo(horizontal_servo_pin)
    self.level_servo = servo.Servo(level_servo_pin)
    self.tipping_servo = servo.Servo(tipping_servo_pin)
    self.grasp_servo = servo.Servo(grasp_servo_pin)
    self.move_to_base()
    
    # TODO : Fill in values to the constructor below.
    self.rail = stepper_axis.StepperAxis(rail_dir_pin, rail_step_pin, max_rail_translation_mm)

  def claw_grasp():
    self.grasp_servo.move_to(10)

  def claw_release():
    self.grasp_servo.move_to(55)

  
  def pour():
    """ Pours the container assuming that it is positioned over the vessel and
        waits for a few seconds before straightening it up. """
    self.tipping_servo.move_to(180)
    # Wait a few seconds for the contents to drain out.
    time.sleep(5)
    self.tipping_servo.move_to(0)

  def straighten_tipping_servo():
    self.tipping_servo.move_to(0)

# Begin unfinished methods 
  def move_rail_rotate_base(self, dest_pos):
    self.at_base = False
    self.rail.move_to(max(0, min(max_rail_translation_mm, dest_pos[1])))
    curr_y_pos = self.rail.get_curr_pos_mm()
    # Need to rotate base servo to point from (0,curr_pos[1]) to (dest_pos[0],dest_pos[1])
    # degrees to rotate clockwise with 0 pointing along x axis towards containers
    degrees = math.degrees(math.atan(float(curr_y_pos - dest_pos[1])
                                     /float(0 - dest_pos[0])))
    if (degrees < 0 or degrees > 180):
       raise ValueError("Invalid rotation angle:" +
                        str(degrees) + " degrees. Current position: "
                        + curr_y_pos + "Dest position: " + dest_pos)
    base_servo.move_to(degrees)

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
    
  # Rail stepper and base servo have been adjusted as necessary. This function
  # Adjusts the three servos Vertical, Horizontal and Level servos to get the
  # required Z and X from to_pos.
  def execute_move_claw_xz(self, to_pos):
    from_pos = (self.vertical_servo.get_current_pos(),
                self.horizontal_servo.get_current_pos(),
                self.level_servo.get_current_pos())
    pos_delta = (to_pos[2] - self.vertical_servo.get_current_pos(),
                 to_pos[3] - self.horizontal_servo.get_current_pos(),
                 to_pos[4] - self.level_servo.get_current_pos())
    max_delta = max(abs(pos_delta[0]), abs(pos_delta[1]), abs(pos_delta[2]))
    for i in range(1, max_delta + 1):
      # Update each servo proportionally
      update = [(float(i)/max_delta) * x for x in pos_delta]
      new_pos = [int(update[j] + from_pos[j]) for j in range(0, len(from_pos))]
      self.vertical_servo.move_to(new_pos[0])
      self.horizontal_servo.move_to(new_pos[1])
      self.level_servo.move_to(new_pos[2])
    self.at_base = False
    None
    
  def move_to(self, dest_pos):
    self.move_rail_rotate_base(dest_pos)
    self.execute_move_claw_xz(dest_pos)
# End of unfinished methods 
    
  def move_to_cup(self, is_small_cup, cup_num):
    if is_small_cup:
      if cup_num < 0 or cup_num > 6:
        raise ValueError("Invalid small cup number:" + cup_num)
    else:
      if cup_num < 0 or cup_num > 5:
        raise ValueError("Invalid large cup number:" + cup_num)
      
    # Positions of the various servos.
    if is_small_cup:
      pos_for_cup = small_cup_positions[cup_num]
    else:
      pos_for_cup = large_cup_positions[cup_num]

    self.rail.move_to(pos_for_cup[0])
    self.base_servo.move_to(pos_for_cup[1])
    self.execute_move_claw_xz(pos_for_cup)
    self.at_base = False
    None

  def move_to_utensil(self, utensil_size):
    if utensil_size < 0 or utensil_size > 2:
      raise ValueError("Invalid utensil size:" + utensil_size)

    self.at_base = False
    # Positions of the various servos.
    desired_servo_pos = utensil_positions_size[utensil_size]
    self.execute_move_claw_xz(desired_servo_pos)
    self.rail.move_to(desired_servo_pos[0])
    self.base_servo.move_to(desired_servo_pos[1])
    None

  def move_to_base(self):  
    self.base_servo.move_to(servo_base_pos[1])
    self.execute_move_claw_xz(servo_base_pos)
    self.rail.move_to(servo_base_pos[0])
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
    self.pour()
    self.move_to_base()

  def shutdown(self):
    self.move_to_base()
    
if (__name__ == "__main__"):
  arm = RoboticArm(2, 3, 4, 5, 6, 7, 8, 9)
  arm.move_to_base()
  arm.add_cup(True, 1, 0)
  arm.add_cup(True, 2, 0)
  arm.add_cup(True, 3, 0)
  arm.add_cup(True, 4, 0)
  arm.add_cup(True, 5, 0)
