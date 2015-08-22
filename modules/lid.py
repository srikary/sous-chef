import modules.driver.servo as servo

class Lid:
  """ Interface to the Lid."""
  open_pos = 0
  close_pos = 180
  def __init__(self, lid_servo_bcm_pin):
    """
        lid_servo_bcm_pin: Provide the pin (BCM numbering) that the lid Servo
        is connected to.
        init_pos: A number between 0 and 180 that specifies the initial angle
    """
    self.lid_servo = servo.Servo(lid_servo_bcm_pin, open_pos)
    self.is_open = True
    
  def open(self):
    self.lid_servo.move_to(open_pos)
    self.is_open = True
    
  def close(self):
    self.lid_servo.move_to(close_pos)
    self.is_open = False

  def is_open(self):
    return self.is_open

  def shutdown(self):
    self.open()
    
if (__name__ == "__main__"):
  lid = Lid(2)
  lid.close()
  lid.open()
