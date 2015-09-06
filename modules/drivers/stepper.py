import RPi.GPIO as GPIO
import time

class StepperMotor:
  """ Wrapper interface to a stepper motor. """

  steps_per_rotation = 200
  min_delay_per_step = 0.001

  def __init__(self, dir_pin, step_pin, speed=30):
    GPIO.setmode(GPIO.BCM)
    self.direction_pin = dir_pin
    self.step_pin = step_pin
    GPIO.setup(self.direction_pin, GPIO.OUT)
    GPIO.output(self.direction_pin, GPIO.LOW)
    GPIO.setup(self.step_pin, GPIO.OUT)
    GPIO.output(self.step_pin, GPIO.LOW)
    self.delay_per_step = self.get_step_delay_from_speed(speed)

  def get_step_delay_from_speed(self, speed):
    """ Converts the speed (in rpm) to the delay between each step """

    rotations_per_second = float(speed) / 60
    steps_per_second = rotations_per_second * StepperMotor.steps_per_rotation
    time_per_step = float(1.0)/steps_per_second
    return (time_per_step - StepperMotor.min_delay_per_step)

  def rotate(self, dir_is_clockwise, num_rotations):
    if dir_is_clockwise:
      GPIO.output(self.direction_pin, GPIO.HIGH)
    else:
      GPIO.output(self.direction_pin, GPIO.LOW)

    num_steps = int(num_rotations * StepperMotor.steps_per_rotation)
    for i in range(0, num_steps):
      GPIO.output(self.step_pin, GPIO.HIGH)
      time.sleep(0.001)
      GPIO.output(self.step_pin, GPIO.LOW)
      time.sleep(self.delay_per_step)

  def set_speed(self, speed):
    self.delay_per_step = self.get_step_delay_from_speed(speed)

  def rotate_at_speed(self, speed, dir_is_clockwise, num_rotations):
    self.set_speed(speed)
    self.rotate(dir_is_clockwise, num_rotations)

  def rotate_clockwise_at_speed(self, speed, num_rotations):
    self.rotate_at_speed(speed, True, num_rotations)

  def rotate_anticlockwise_at_speed(self, speed, num_rotations):
    self.rotate_at_speed(speed, False, num_rotations)

  def rotate_clockwise(self, num_rotations):
    self.rotate(True, num_rotations)

  def rotate_anticlockwise(self, num_rotations):
    self.rotate(False, num_rotations)

if (__name__ == "__main__"):
  y_stepper = StepperMotor(6, 5, 60)
  x_stepper = StepperMotor(9, 10, 60)
  z_stepper = StepperMotor(7, 8, 60)
  r_stepper = StepperMotor(11, 25, 60)
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
      y_stepper.rotate_at_speed(20, direction, rotations)
    elif motor_num == 2:
      x_stepper.rotate_at_speed(30, direction, rotations)
    elif motor_num == 3:
      z_stepper.rotate_at_speed(30, direction, rotations)
    else:
      r_stepper.rotate_at_speed(30, direction, rotations)
