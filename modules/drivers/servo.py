import RPi.GPIO as GPIO
import time

class Servo:
  """ Wrapper interface to a Servo."""
  
  def __init__(self, bcm_pin, init_pos=0, move_delay_ms=0.01):
    """
        bcm_pin: Provide the pin (BCM numbering) that the Servo is connected to.
        init_pos: A number between 0 and 180 that specifies the initial angle
        move_delay: parameter in the constructor
    """
    self.move_delay = move_delay
    if (init_pos < 0 or init_pos > 180):
      raise ValueError("Initial position invalid:" + str(init_pos))

    self.curr_pos = init_pos
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm_pin, GPIO.OUT)
    self.pwm = GPIO.PWM(self.bcm_pin, 100)
    self.pwm.start(get_dutycycle_for_angle(init_pos))

  def get_dutycycle_for_angle(angle):
    return float(angle) / 36 + 5 # (float(angle)/180 + 1) * 5
  
  def set_angle(angle):
    duty = get_dutycycle_for_angle(angle)
    pwm.ChangeDutyCycle(duty)

  def move_to(self, dest_angle):
    if (dest_angle< 0 or dest_angle > 180):
      raise ValueError("Destination position invalid:" + str(dest_angle))
    direction = 1
    if (dest_angle < self.curr_pos):
      direction = -1
    for angle in range(self.curr_pos, dest_pos, direction):
      self.curr_pos = angle
      set_angle(self.curr_pos)
      time.sleep(self.move_delay)

  def get_current_pos(self):
    return self.curr_pos
          
if (__name__ == "__main__"):
  servo_pins = []
  for pin in servo_pins:
    servo = Servo(pin, 30)
    servo.move_to(50)
    servo.move_to(30)
    
