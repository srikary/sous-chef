from drivers.servo_driver import Servo
import submodules.pid_controller as pid_controller
import RPi.GPIO as GPIO
import time

# Ensure that you have installed the TMP006 library from AdaFruit
# https://learn.adafruit.com/tmp006-temperature-sensor-python-library/software
# sudo apt-get update
# sudo apt-get install build-essential python-dev python-pip python-smbus git
# sudo pip install RPi.GPIO
# git clone https://github.com/adafruit/Adafruit_Python_TMP.git
# cd Adafruit_Python_TMP
# sudo python setup.py install
# sudo python examples/simpletest.py
import Adafruit_TMP.TMP006 as TMP006

class StoveController:
  """ Interface to the Stove/HotPlate."""
  high_pos = 180
  low_pos = 0
  kP = 0.3 # Set these values appropriately.
  kI = 0.001
  kD = 0.0

  def __init__(self, servo_channel, switch_bcm_pin, sampling_interval_s = 5):
    """
        servo_channel: Provide the channel (on the Servo driver) that the lid
                       Servo is connected to.
        init_pos: A number between 0 and 180 that specifies the initial angle
    """
    self.servo = Servo(servo_channel, StoveController.low_pos)
    self.switch_bcm_pin = switch_bcm_pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.switch_bcm_pin, GPIO.OUT)
    self.off()
    self.temp_sensor = TMP006.TMP006(address=0x41)
    self.temp_sensor.begin()
    self.temp_pid_controller = pid_controller.PIDController(StoveController.kP,
                                                            StoveController.kI,
                                                            StoveController.kD,
                                                            20, # setpoint
                                                            sampling_interval_s,
                                                            self.get_temperature_C,
                                                            self.set_knobpos_from_percentage)
    self.temp_pid_controller.start()

  def on(self):
    GPIO.output(self.switch_bcm_pin, GPIO.HIGH)
    self.is_on = True

  def off(self):
    GPIO.output(self.switch_bcm_pin, GPIO.LOW)
    self.is_on = False

  # Shutdown for good. Cannot use stove without restarting.
  def shutdown(self):
    self.off()
    self.temp_pid_controller.stop()
    self.temp_pid_controller.join()

  # Hold the stove at the current setting and pause temperature control.
  def hold_freeze(self):
    self.temp_pid_controller.pause()

  def is_on(self):
    return self.is_on

  def set_knobpos_from_percentage(self, percentage):
    if percentage < 0 or percentage > 100:
      raise ValueError("KnobPos is set through percentage. Needs to be in [0, 100]")
    print "Dest %: " + str(percentage)
    target_value = int((float(abs(StoveController.low_pos - StoveController.high_pos)) * percentage)/ 100)
    self.servo.move_to(int(StoveController.low_pos + target_value))

  # Public methods
  def set_temperature_C(self, temperature):
    self.on()
    self.temp_pid_controller.set_new_setpoint(temperature)

  def get_temperature_C(self):
    temp = self.temp_sensor.readObjTempC()
    print "Current Temp: " + str(temp) + "*C"
    return temp

  def set_knobpos(self, pos):
    self.hold_freeze()
    self.set_knobpos_from_percentage(pos)

if (__name__ == "__main__"):
  controller = StoveController(5, 12)
  print "Before" + str(controller.get_temperature_C())

  #controller.set_temperature_C(60)
  #for i in range(0, 100):
  #  time.sleep(5)
  controller.set_knobpos(5)
  time.sleep(10)
  controller.shutdown()
