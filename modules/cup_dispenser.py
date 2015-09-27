from drivers.servo_driver import Servo
import time

class CupDispenser:
  cup_positions = [(175, 65), # Hold, Dispense positions
                   (130, 27),
                   (163, 45),
                   (161, 45)]

  def __init__(self,
               small_cup1_servo_channel,
               small_cup2_servo_channel,
               large_cup1_servo_channel,
               large_cup2_servo_channel):
    self.small_cup1_servo = Servo(small_cup1_servo_channel, CupDispenser.cup_positions[0][0], move_delay=0.001)
    self.small_cup2_servo = Servo(small_cup2_servo_channel, CupDispenser.cup_positions[1][0], move_delay=0.01)
    self.large_cup1_servo = Servo(large_cup1_servo_channel, CupDispenser.cup_positions[2][0], move_delay=0.01)
    self.large_cup2_servo = Servo(large_cup2_servo_channel, CupDispenser.cup_positions[3][0], move_delay=0.01)
    self.reset()
    self.all_on_hold=True

  def tip_servo(self, servo, hold_pos, dispense_pos):
    self.all_on_hold=False
    servo.move_to(hold_pos)
    servo.move_to(dispense_pos)
    time.sleep(3)
    servo.move_to(hold_pos)
    self.all_on_hold=True

  def are_all_on_hold(self):
    return self.all_on_hold

  def pour_cup(self, cup_num):
    if cup_num < 1 or cup_num > 4:
      raise ValueError("There are only four cups. Choose cup number from {0, 3}")
    cup_idx = cup_num - 1
    if cup_num == 1:
      self.tip_servo(self.small_cup1_servo,
                     CupDispenser.cup_positions[cup_idx][0],
                     CupDispenser.cup_positions[cup_idx][1])
    elif cup_num == 2:
      self.tip_servo(self.small_cup2_servo,
                     CupDispenser.cup_positions[cup_idx][0],
                     CupDispenser.cup_positions[cup_idx][1])
    elif cup_num == 3:
      self.tip_servo(self.large_cup1_servo,
                     CupDispenser.cup_positions[cup_idx][0],
                     CupDispenser.cup_positions[cup_idx][1])
    elif cup_num == 4:
      self.tip_servo(self.large_cup2_servo,
                     CupDispenser.cup_positions[cup_idx][0],
                     CupDispenser.cup_positions[cup_idx][1])
    else:
      raise ValueError("We should never get here")

  def reset(self):
    self.small_cup1_servo.move_to(CupDispenser.cup_positions[0][0])
    self.small_cup2_servo.move_to(CupDispenser.cup_positions[1][0])
    self.large_cup1_servo.move_to(CupDispenser.cup_positions[2][0])
    self.large_cup2_servo.move_to(CupDispenser.cup_positions[3][0])

  def shutdown(self):
    self.reset()

if (__name__ == "__main__"):
  dispenser = CupDispenser(
                   0, # SmallCup 1
                   1, # SmallCup 2
                   2, # LargeCup 1
                   3, # LargeCup 2
                   )
  while True:
    inp = raw_input("-->")
    cup_num = int(inp)
    if cup_num < 1 or cup_num > 4:
      print "Invalid cup number: " + str(cup_num)
    else:
      dispenser.pour_cup(cup_num)
