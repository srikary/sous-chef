import modules.driver.stepper as stepper

class StepperAxis:
  
  """ Represents an axis controlled by a stepper motor """
  def __init__(self, dir_pin, step_pin, max_translation_mm, speed=60, inc_clockwise=True, rotations_per_mm = 0.5):
    self.stepper = stepper.StepperMotor(dir_pin, step_pin, speed)
    self.inc_clockwise = inc_clockwise
    self.curr_pos_mm = 0
    self.max_translation_mm = max_translation_mm
    self.rotations_per_mm = rotations_per_mm  # TODO: Set this right.

  def increment_pos_by_mm(self, distance_in_mm):
    if distance_in_mm < 0:
      throw up # TODO: Throw an exception
    num_rotations = distance_in_mm * self.rotations_per_mm
    if self.inc_clockwise:
      stepper.rotate_clockwise(num_rotations)
    else:
      stepper.rotate_anticlockwise(num_rotations)

  def decrement_pos_by_mm(self, distance_in_mm):
    if distance_in_mm < 0:
      throw up # TODO: Throw an exception
    num_rotations = distance_in_mm * self.rotations_per_mm
    if self.inc_clockwise:
      stepper.rotate_anticlockwise(num_rotations)
    else:
      stepper.rotate_clockwise(num_rotations)
      
  def move_to(self, new_pos_mm):
    if new_pos_mm > max_translation_mm:
      throw up # TODO: throw an exception
    if new_pos_mm > self.curr_pos_mm:
      self.increment_pos_by_mm(new_pos_mm - self.curr_pos_mm)
    else:
      self.decrement_pos_by_mm(self.curr_pos_mm - new_pos_mm)
    self.curr_pos_mm = new_pos_mm
      
  def get_curr_pos_mm(self):
    return self.curr_pos_mm

if (__name__ == "__main__"):
  axis = StepperAxis(2, 3, 100)
  axis.move_to(70)
  axis.move_to(30)
  axis.move_to(50)
  print axis.get_curr_pos_mm()
