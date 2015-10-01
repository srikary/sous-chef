from drivers.servo_driver import Servo

class Lid:
  """ Interface to the Lid."""
  open_pos = 180
  close_pos = 0
  def __init__(self, lid_servo_channel):
    """
        lid_servo_channel: Provide the channel (on the Servo driver) that the
                           lid Servois connected to.
        init_pos: A number between 0 and 180 that specifies the initial angle
    """
    self.lid_servo = Servo(lid_servo_channel, Lid.open_pos)
    self.is_lid_open = True

  def open(self):
    self.lid_servo.move_to(Lid.open_pos)
    self.is_lid_open = True

  def close(self):
    self.lid_servo.move_to(Lid.close_pos)
    self.is_lid_open = False

  def is_open(self):
    return self.is_lid_open

  def shutdown(self):
    self.close()

if (__name__ == "__main__"):
  lid = Lid(4)
  lid.close()
  lid.open()
