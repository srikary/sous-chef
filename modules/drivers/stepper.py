import RPi.GPIO as GPIO
import time

class StepperMotor:
  """ Wrapper interface to a stepper motor. """

  steps_per_rotation = 200
  min_delay_per_step = 0

  def __init__(self, dir_pin, step_pin, speed=60):
    GPIO.setmode(GPIO.BCM)
    self.direction_pin = dir_pin
    self.step_pin = step_pin
    GPIO.setup(self.direction_pin, GPIO.OUT)
    GPIO.setup(self.step_pin, GPIO.OUT)
    GPIO.output(self.step_pin, GPIO.LOW)
    self.delay_per_step = self.get_step_delay_from_speed(speed)

  def get_step_delay_from_speed(self, speed):
    """ Converts the speed (in rpm) to the delay between each step """

    rotations_per_second = speed / 60
    steps_per_second = rotations_per_second * StepperMotor.steps_per_rotation
    time_per_step = float(1.0)/steps_per_second
    return time_per_step - StepperMotor.min_delay_per_step

  def rotate(self, dir_is_clockwise, num_rotations):
    if dir_is_clockwise:
      GPIO.output(self.direction_pin, GPIO.HIGH)
    else:
      GPIO.output(self.direction_pin, GPIO.LOW)

    num_steps = num_rotations * StepperMotor.steps_per_rotation
    for i in range(0, num_steps):
      GPIO.output(self.step_pin, GPIO.HIGH)
      time.sleep(self.delay_per_step)
      GPIO.output(self.step_pin, GPIO.LOW)

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
  step_pins = [10]
  dir_pins = [9]
  for i in range(0, len(step_pins)):
    stepper = StepperMotor(step_pins[i], dir_pins[i], 60)
    stepper.rotate_clockwise(3)
    stepper.rotate_anticlockwise(3)
    stepper.rotate_clockwise(3)
    stepper.set_speed(120)
    stepper.rotate_clockwise(3)
    stepper.rotate_anticlockwise(3)
    stepper.rotate_clockwise(3)
