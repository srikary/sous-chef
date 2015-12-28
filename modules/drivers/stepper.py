import RPi.GPIO as GPIO
import time

def get_curr_time_in_secs():
  return time.time()

class StepperMotor:
  """ Wrapper interface to a stepper motor. """

  steps_per_rotation = 200
  min_delay_per_step = 0.001
  acceleration = 0.9 # revolutions/s^2
  innitial_velocity = 0.1

  def __init__(self, dir_pin, step_pin, enable_pin, speed=90):
    GPIO.setmode(GPIO.BCM)
    self.direction_pin = dir_pin
    self.step_pin = step_pin
    self.enable_pin = enable_pin
    GPIO.setup(self.direction_pin, GPIO.OUT)
    GPIO.output(self.direction_pin, GPIO.LOW)
    GPIO.setup(self.step_pin, GPIO.OUT)
    GPIO.output(self.step_pin, GPIO.LOW)
    GPIO.setup(self.enable_pin, GPIO.OUT)
    self.disable()
    self.set_speed(speed)

  def enable(self):
    GPIO.output(self.enable_pin, GPIO.LOW)

  def disable(self):
    GPIO.output(self.enable_pin, GPIO.HIGH)

  def get_step_delay_from_speed(self, rotations_per_second):
    """ Converts the speed (in rps) to the delay between each step """
    steps_per_second = rotations_per_second * StepperMotor.steps_per_rotation
    time_per_step = float(1.0)/steps_per_second
    return (time_per_step - StepperMotor.min_delay_per_step)

  def rotate(self, dir_is_clockwise, num_rotations):
    self.enable()
    if dir_is_clockwise:
      GPIO.output(self.direction_pin, GPIO.HIGH)
    else:
      GPIO.output(self.direction_pin, GPIO.LOW)

    num_steps = int(num_rotations * StepperMotor.steps_per_rotation)
    velocity = StepperMotor.initial_velocity
    acc = StepperMotor.acceleration
    prev_time = get_curr_time_in_secs()
    half_way = num_steps / 2
    deceleration_point = num_steps
    for i in range(0, num_steps):
      GPIO.output(self.step_pin, GPIO.HIGH)
      time.sleep(0.001)
      GPIO.output(self.step_pin, GPIO.LOW)
      curr_time = get_curr_time_in_secs()
      dt = curr_time - prev_time
      prev_time = curr_time
      velocity += acc * dt
      step_delay = self.get_step_delay_from_speed(velocity)
      time.sleep(step_delay)
      # Once we've hit max velocity or accelerated upto halfway we
      # set acceleration to 0.
      if acc > 0 and (i >= num_steps or velocity >= self.speed_rps):
        acc = 0
        deceleration_point = num_steps - i
      if acc > 0 and i >= deceleration_point:
        acc = -StepperMotor.acceleration
    return float(num_steps)/ StepperMotor.steps_per_rotation

  def set_speed(self, speed):
    self.speed_rps = float(speed)/60
    self.delay_per_step = self.get_step_delay_from_speed(self.speed_rps)

  def rotate_at_speed(self, speed, dir_is_clockwise, num_rotations):
    self.set_speed(speed)
    return self.rotate(dir_is_clockwise, num_rotations)

  def rotate_clockwise_at_speed(self, speed, num_rotations):
    return self.rotate_at_speed(speed, True, num_rotations)

  def rotate_anticlockwise_at_speed(self, speed, num_rotations):
    return self.rotate_at_speed(speed, False, num_rotations)

  def rotate_clockwise(self, num_rotations):
    return self.rotate(True, num_rotations)

  def rotate_anticlockwise(self, num_rotations):
    return self.rotate(False, num_rotations)

if (__name__ == "__main__"):
  y_stepper = StepperMotor(11, 25, 20, 60)
  x_stepper = StepperMotor(7, 8, 19, 60)
  z_stepper = StepperMotor(9, 10, 21, 60)
  r_stepper = StepperMotor(6, 5, 26, 60)
  while True:
    inp = raw_input("-->")
    vals = inp.split()
    if len(vals)!=2:
      raise ValueError("invalid number of arguments")
    motor_num = int(vals[0])
    rotations = int(vals[1])
    direction = True
    if rotations < 0:
      direction = False
      rotations = abs(rotations)
    if motor_num == 1:
      y_stepper.rotate_at_speed(60, direction, rotations)
    elif motor_num == 2:
      x_stepper.rotate_at_speed(60, direction, rotations)
    elif motor_num == 3:
      z_stepper.rotate_at_speed(120, direction, rotations)
    else:
      r_stepper.rotate_at_speed(60, direction, rotations)
