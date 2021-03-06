from ..drivers import stepper

class StepperAxis:

  """ Represents an axis controlled by a stepper motor """
  def __init__(self, dir_pin, step_pin, enable_pin, max_translation_mm, speed=60,
               inc_clockwise=True, rotations_per_mm = (float(8)/256.5)):
    self.stepper = stepper.StepperMotor(dir_pin, step_pin, enable_pin, speed)
    self.inc_clockwise = inc_clockwise
    self.curr_pos_mm = 0
    self.max_translation_mm = max_translation_mm
    self.rotations_per_mm = rotations_per_mm  # 35mm per rotation.

  def enable(self):
    self.stepper.enable()

  def disable(self):
    self.stepper.disable()

  def get_speed(self):
    return self.stepper.get_speed()

  def set_speed(self, speed):
    self.stepper.set_speed(speed)

  # Private methods
  def increment_pos_by_mm(self, distance_in_mm):
    if distance_in_mm < 0:
      raise ValueError("Invalid increment. Has to be positive:" + str(distance_in_mm))
    num_rotations = distance_in_mm * self.rotations_per_mm
    if self.inc_clockwise:
      actual_rotations = self.stepper.rotate_clockwise(num_rotations)
    else:
      actual_rotations = self.stepper.rotate_anticlockwise(num_rotations)
    return float(actual_rotations)/self.rotations_per_mm

  def decrement_pos_by_mm(self, distance_in_mm):
    if distance_in_mm < 0:
      raise ValueError("Invalid decrement. Has to be positive:" + str(distance_in_mm))
    num_rotations = distance_in_mm * self.rotations_per_mm
    if self.inc_clockwise:
      actual_rotations = self.stepper.rotate_anticlockwise(num_rotations)
    else:
      actual_rotations = self.stepper.rotate_clockwise(num_rotations)
    return float(actual_rotations)/self.rotations_per_mm

  # End private methods

  def move_to(self, new_pos_mm):
    if new_pos_mm > self.max_translation_mm or new_pos_mm < 0:
        raise ValueError("Invalid value:" + str(new_pos_mm) + " for new_pos_mm. Has to be within " +
                       " range(0," +str(self.max_translation_mm) + ")")
    if new_pos_mm > self.curr_pos_mm:
      self.curr_pos_mm += self.increment_pos_by_mm(new_pos_mm - self.curr_pos_mm)
    else:
      self.curr_pos_mm -= self.decrement_pos_by_mm(self.curr_pos_mm - new_pos_mm)

  def get_curr_pos_mm(self):
    return self.curr_pos_mm

if (__name__ == "__main__"):
  y_stepper = StepperAxis(11, 25, 20, 6000, speed=150)
  x_stepper = StepperAxis(7, 8, 19, 6000, inc_clockwise=False, speed=150)
  z_stepper = StepperAxis(9, 10, 21,
          max_translation_mm=6000, inc_clockwise=True, speed=180, rotations_per_mm=0.79)
  #z_stepper.curr_pos_mm = 55
  r_stepper = StepperAxis(6, 5, 26, 6000, inc_clockwise=False)
  while True:
    inp = raw_input("-->")
    vals = inp.split()
    if len(vals)!=2:
      raise ValueError("invalid number of arguments")
    motor_num = int(vals[0])
    position = int(vals[1])
    if motor_num == 1:
      y_stepper.move_to(position)
      print "Y Currently at: " + str(y_stepper.get_curr_pos_mm())
    elif motor_num == 2:
      x_stepper.move_to(position)
      print "X Currently at: " + str(x_stepper.get_curr_pos_mm())
    elif motor_num == 3:
      z_stepper.move_to(position)
      print "Z Currently at: " + str(z_stepper.get_curr_pos_mm())
    else:
      r_stepper.move_to(position)
      print "R Currently at: " + str(r_stepper.get_curr_pos_mm())
