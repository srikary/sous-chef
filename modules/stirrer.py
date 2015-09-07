import submodules.stepper_axis as stepper_axis
import math
import time

class PlatformPosition:
  BASE = 1
  UTENSIL = 2
  LID = 3

def get_curr_time_in_secs():
  return time.mktime(time.localtime())

class Stirrer:
  # Dimensions of the Rails
  max_x_rail_translation_mm = 380.0
  max_y_rail_translation_mm = 325.0
  max_z_rail_translation_mm = 300.0

  z_up_pos = 0.0
  z_down_pos = 120.0
  x_utensil_pos = 190.0
  y_utensil_pos = 162.0

  x_lid_utensil_pos = 190.0
  y_lid_utensil_pos = 192.0

  x_home_pos = 5.0
  y_home_pos = 5.0

  stirrer_x_offset = 45
  stirrer_y_offset = 45

  stirrer_width_mm = 50.0

  stir_start_gap = 5.0 # Distance from utensil wall where the stirrer starts a stroke.
  stir_stop_gap = 20.0 # Distance from utensil wall where the stirrer stops during a stroke.

  # Diameters of the three different all-clad utensils
  utensil_diameter_mm = [270.0, 300.0, 150.0]

  def __init__(self,
               x_rail_dir_pin, x_rail_step_pin,
               y_rail_dir_pin, y_rail_step_pin,
               z_rail_dir_pin, z_rail_step_pin):
    # TODO : Fill in values to the constructor below.
    self.x_rail = stepper_axis.StepperAxis(x_rail_dir_pin, x_rail_step_pin, Stirrer.max_x_rail_translation_mm)
    self.y_rail = stepper_axis.StepperAxis(y_rail_dir_pin, y_rail_step_pin, Stirrer.max_y_rail_translation_mm)
    self.z_rail = stepper_axis.StepperAxis(z_rail_dir_pin, z_rail_step_pin, Stirrer.max_z_rail_translation_mm)
    self.platform_position = PlatformPosition.BASE

  def move_to(self, dest_pos):
    start_pos = (self.x_rail.get_curr_pos_mm(), self.y_rail.get_curr_pos_mm())
    delta = ((dest_pos[0] - self.x_rail.get_curr_pos_mm()),
             (dest_pos[1] - self.y_rail.get_curr_pos_mm()))
    max_delta = max(abs(delta[0]), abs(delta[1]))

    for i in range(1, int(max_delta + 1)):
      next_x = start_pos[0] + ((float(i) / max_delta) * delta[0])
      next_y = start_pos[1] + ((float(i) / max_delta) * delta[1])
      self.x_rail.move_to(next_x)
      self.y_rail.move_to(next_y)

  def execute_stir_stroke(self, start_pos, end_pos):
    self.stirrer_up()
    self.move_to(start_pos)
    self.stirrer_down()
    self.move_to(end_pos)
    self.stirrer_up()

  def get_cord_length_mm(self, dist_from_center, utensil_index):
    if utensil_index >= 3:
      raise ValueError("There are only three known utensil sizes. Invalid utensil index:" + utensil_index)

    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    if (dist_from_center >= utensil_radius):
      raise ValueError("Requested distance from center is invalid for specified utensil:" + dist_from_center)

    return 2 * math.sqrt((utensil_radius * utensil_radius) - (dist_from_center * dist_from_center))

  def one_stir_stroke(self, dist_from_center, utensil_index, top_to_bottom):
    print "Stroke:" + str(dist_from_center)+ ", " + str(top_to_bottom)
    stirrer_width_half = (Stirrer.stirrer_width_mm/ 2)
    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    # Compute the max height that the stirrer can stir on this stroke
    edge_dist_from_center = dist_from_center + stirrer_width_half
    if dist_from_center < 0:
      edge_dist_from_center = dist_from_center - stirrer_width_half
    # This stroke will keep the edge out of bounds. Return without doing anything.
    if abs(edge_dist_from_center) >= utensil_radius:
        return
    cord_length = self.get_cord_length_mm(edge_dist_from_center, utensil_index)

    # Coordinates for the center of the platform for which the stirrer is at the
    # center of the utensil
    stirrer_x_center = Stirrer.x_utensil_pos + Stirrer.stirrer_x_offset
    stirrer_y_center = Stirrer.y_utensil_pos + Stirrer.stirrer_y_offset

    x_delta = stirrer_x_center + dist_from_center

    if top_to_bottom:
      start_y = stirrer_y_center + (cord_length / 2) - Stirrer.stir_start_gap
      end_y = start_y - cord_length + Stirrer.stir_stop_gap + Stirrer.stir_start_gap
    else:
      start_y = stirrer_y_center - (cord_length / 2) + Stirrer.stir_start_gap
      end_y = start_y + cord_length - Stirrer.stir_stop_gap - Stirrer.stir_start_gap
    print "Executing stroke: " + repr(x_delta) + ", " + repr(start_y) + ", " + repr(end_y)
    self.execute_stir_stroke((x_delta, start_y), (x_delta, end_y))

  ################  Public methods. #################

  def stirrer_up(self):
    self.z_rail.move_to(Stirrer.z_up_pos)

  def stirrer_down(self):
    self.z_rail.move_to(Stirrer.z_down_pos)

  def is_stirrer_up(self):
    return self.z_rail.get_curr_pos_mm == Stirrer.z_up_pos

  def position_platform_at_utensil(self):
    self.stirrer_up()
    self.x_rail.move_to(Stirrer.x_utensil_pos)
    self.y_rail.move_to(Stirrer.y_utensil_pos)
    self.platform_position = PlatformPosition.UTENSIL

  def position_platform_at_base(self):
    self.stirrer_up()
    self.x_rail.move_to(Stirrer.x_home_pos)
    self.y_rail.move_to(Stirrer.y_home_pos)
    self.platform_position = PlatformPosition.UTENSIL

  def position_platform_at_lid(self):
    self.stirrer_up()
    self.x_rail.move_to(Stirrer.x_lid_utensil_pos)
    self.y_rail.move_to(Stirrer.y_lid_utensil_pos)
    self.platform_position = PlatformPosition.LID

  def is_platform_at_base(self):
    return self.platform_position == PlatformPosition.BASE

  def is_platform_at_utensil(self):
    return self.platform_position == PlatformPosition.UTENSIL

  def is_platform_at_lid(self):
    return self.platform_position == PlatformPosition.LID

  # X axis is the top rail and increases left to right (looking FROM ATX)
  # Y axis is the bottom rail and increases from ATX to front.
  def stir(self, utensil_index, stir_for_seconds):
    self.position_platform_at_utensil()
    self.stirrer_down()
    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    stir_dx = -10
    top_to_bottom = True
    start_time = get_curr_time_in_secs()
    while True:
      current = get_curr_time_in_secs()
      if (current  - start_time) > stir_for_seconds:
        break
      for dist_from_center in range(int(utensil_radius), int(-utensil_radius), stir_dx):
        self.one_stir_stroke(dist_from_center, utensil_index, top_to_bottom)
        top_to_bottom = not top_to_bottom
        current = get_curr_time_in_secs()
        if (current  - start_time) > stir_for_seconds:
          break

  def shutdown(self):
    self.position_platform_at_base()

if (__name__ == "__main__"):
  stirrer = Stirrer(7, 8,  # X Dir, Step
                   11, 25, # Y Dir, Step
                   9, 10)  # Z Dir, Step
  stirrer.position_platform_at_utensil()
  print "At Utensil"
  time.sleep(10)
  stirrer.position_platform_at_lid()
  print "At Lid"
  time.sleep(10)
  stirrer.stir(0, 20)
  print "Done stirring"
  time.sleep(10)
  stirrer.position_platform_at_base()
  print "At Base"
  time.sleep(10)
