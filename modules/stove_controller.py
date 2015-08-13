import modules.driver.servo as servo
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
  high_pos = 0
  low_pos = 180
  def __init__(self, servo_bcm_pin, switch_bcm_pin):
    """
        servo_bcm_pin: Provide the pin (BCM numbering) that the lid Servo
        is connected to.
        init_pos: A number between 0 and 180 that specifies the initial angle
    """
    self.servo = servo.Servo(servo_bcm_pin, low_pos)
    self.switch_bcm_pin = switch_bcm_pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.switch_bcm_pin, GPIO.OUT)
    self.off()
    temp_sensor = TMP006.TMP006()
    temp_sensor.begin()
    
  def on(self):
    GPIO.output(self.switch_bcm_pin, GPIO.HIGH)
    self.is_on = True

  def off(self):
    GPIO.output(self.switch_bcm_pin, GPIO.LOW)
    self.is_on = False
    
  def is_on(self):
    return self.is_on

  def set_temperature_C(self, temperature):
    self.on()
    # TODO: implement a pid controller after the temperature sensor is coded up.

  def get_temperature_C(self):
    return temp_sensor.readObjTempC()
  
if (__name__ == "__main__"):
  controller = StoveConroller(2, 3)
  print "Before" controller.get_temperature()
  controller.set_temperature_C(60)
  print "After" controller.get_temperature_C()
  controller.off()
