from Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import time

# A Servo PWM has the following encoding,
#  0.6millisecond pulse length is position 0
#  1.5millisecond pulse length is position 90
#  2.3millisecond pulse length is position 180

def get_pulse_lengths(freq, resolution):
  pw_pos0 = 0.6
  pw_pos180 = 2.3
  # Period of the waveform in milliseconds
  T_ms = float(1000)/freq
  # Period per quantile (due to the resolution)
  T_quantile = T_ms/resolution
  angle_to_quantile = range(181)
  pw_range = pw_pos180 - pw_pos0
  for angle in range(0, 181):
    time_ms_required = pw_pos0 + float(angle * pw_range)/180
    quantile_required = time_ms_required/T_quantile
    angle_to_quantile[angle] = int(quantile_required)
  return angle_to_quantile

class Servo:
  """ Wrapper interface to a Servo."""
  driver_address = 0x40
  pwm_freq = 60
  # The servo driver takes a 4byte number which divides the 1/F time into
  # 4096 quantiles. The start of the signal and the end of the signal are
  # expressed as the indices of these quantiles.
  driver_resolution = 4096

  def __init__(self, driver_channel, init_pos=0, move_delay=0.01):
    """
        driver_channel: Provide the channel number (on the driver) of the Servo that this object represents.
        init_pos: A number between 0 and 180 that specifies the initial angle
        move_delay: parameter in the constructor
    """
    self.move_delay = move_delay
    if (init_pos < 0 or init_pos > 180):
      raise ValueError("Initial position invalid:" + str(init_pos))
    self.driver_channel = driver_channel
    self.pwm = PWM(Servo.driver_address)
    self.pwm.setPWMFreq(Servo.pwm_freq)
    self.angle_to_quantile = get_pulse_lengths(Servo.pwm_freq, Servo.driver_resolution)
    self.set_angle(init_pos)

  def set_angle(self, angle):
    if (angle < 0 or angle > 180):
      raise ValueError("Destination position invalid:" + str(angle))
    self.curr_pos = angle
    print self.angle_to_quantile[angle]
    self.pwm.setPWM(self.driver_channel, 0, self.angle_to_quantile[angle])

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
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(13, GPIO.OUT)
  GPIO.output(13, GPIO.LOW)
  # Pin number, initial position
  base_servo = Servo(0, 140, move_delay=0.005)
  vert_servo = Servo(1, 30)
  hor_servo = Servo(2, 0)
  tilt_servo = Servo(4, 130)
  tip_servo = Servo(3, 5)
  claw_servo = Servo(5, 55)
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

