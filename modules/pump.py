import RPi.GPIO as GPIO
import time

class Pump:
  """ Interface to a Pump."""
  ml_per_cup_ = 236.58
  ml_per_tbsp_ = 14.78

  def __init__(self, switch_bcm_pin, prime_time_msec, time_per_ml_msec):
    """
        relay_bcm_pin: Provide the pin (BCM numbering) that the Pump's relay
        is connected to.
        is_open: A boolean value to specify  the start state of the relay.
        prime_time_msec: Time required to prime the pump.
        time_per_ml_msec: Time required to prime one ml AFTER priming.
    """
    self.switch_bcm_pin = switch_bcm_pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.switch_bcm_pin, GPIO.OUT)
    GPIO.output(self.switch_bcm_pin, GPIO.HIGH)
    self.is_open = False
    self.prime_time_msec = prime_time_msec
    self.time_per_ml_msec = time_per_ml_msec
    self.prime()

  def open(self):
    GPIO.output(self.switch_bcm_pin, GPIO.LOW)
    self.is_open = True

  def is_open(self):
    return self.is_open

  def close(self):
    GPIO.output(self.switch_bcm_pin, GPIO.HIGH)
    self.is_open = False

  def run_pump_for_msec(self, msec):
    secs = float(msec)/1000;
    self.open()
    time.sleep(secs)
    self.close()

  def prime(self):
    self.run_pump_for_msec(self.prime_time_msec)

  def dispense_ml(self, volume_ml):
    # volume to time
    time_msec = volume_ml * self.time_per_ml_msec
    self.run_pump_for_msec(time_msec)

  def dispense_cup(self, num_cups):
    volume_ml = num_cups * Pump.ml_per_cup_
    self.dispense_ml(volume_ml)

  def dispense_tbsp(self, num_tbsps):
    volume_ml = num_tbsps * Pump.ml_per_tbsp_
    self.dispense_ml(volume_ml)

  def shutdown(self):
    self.close()

if (__name__ == "__main__"):
  pump = Pump(12, 5000, 20)
  print "Primed"
  pump.dispense_tbsp(1)
  print "First Part done"
  pump.dispense_cup(0.25)
  print "Second Part done"
