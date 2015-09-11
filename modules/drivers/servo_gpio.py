import RPi.GPIO as GPIO
import time

def get_dutycycle_for_angle(angle):
  return float(angle) / 9 + 5 # (float(angle)/180 + 1) * 5

class Servo:
  """ Wrapper interface to a Servo."""

  def __init__(self, bcm_pin, init_pos=0, move_delay=0.01):
    """
        bcm_pin: Provide the pin (BCM numbering) that the Servo is connected to.
        init_pos: A number between 0 and 180 that specifies the initial angle
        move_delay: parameter in the constructor
    """
    self.move_delay = move_delay
    if (init_pos < 0 or init_pos > 180):
      raise ValueError("Initial position invalid:" + str(init_pos))
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm_pin, GPIO.OUT)
    self.curr_pos = init_pos
    self.pwm = GPIO.PWM(bcm_pin, 100)
    self.pwm.start(get_dutycycle_for_angle(init_pos))

  def set_angle(self, angle):
    self.curr_pos = angle
    duty = get_dutycycle_for_angle(angle)
    self.pwm.ChangeDutyCycle(duty)

  # Ensure that dest_angle is an int. Type check does not happen here.
  def move_to(self, dest_angle):
    if (dest_angle< 0 or dest_angle > 180):
      raise ValueError("Destination position invalid:" + str(dest_angle))
    direction = 1
    if (dest_angle < self.curr_pos):
      direction = -1
    for angle in range(self.curr_pos, dest_angle, direction):
      self.set_angle(angle)
      time.sleep(self.move_delay)
    self.set_angle(dest_angle)

  def get_current_pos(self):
    return self.curr_pos

if (__name__ == "__main__"):
  # Pin number, initial position
  base_servo = Servo(21, 140)
  vert_servo = Servo(20, 30)
  hor_servo = Servo(26, 0)
  tilt_servo = Servo(16, 130)
  tip_servo = Servo(19, 5)
  claw_servo = Servo(13, 55)
  while True:
    inp = raw_input("-->")
    vals = inp.split()
    if len(vals) != 2:
      print "Invalid Input:" + inp
      continue
    servo_num = int(vals[0])
    position = int(vals[1])
    if servo_num == 1:
      base_servo.move_to(position)
    elif servo_num == 2:
      vert_servo.move_to(position)
    elif servo_num == 3:
      hor_servo.move_to(position)
    elif servo_num == 4:
      tilt_servo.move_to(position)
    elif servo_num == 5:
      tip_servo.move_to(position)
    else:
      claw_servo.move_to(position)

