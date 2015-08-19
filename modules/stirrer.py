import modules.stepper_axis as stepper_axis

import math
import time

class Stirrer:
  # Dimensions of the Rails
  max_x_rail_translation_mm = 100.0
  max_y_rail_translation_mm = 100.0
  max_z_rail_translation_mm = 100.0

  stirrer_z_up_pos = 0.0
  stirrer_z_down_pos = 120.0
  stirrer_x_utensil_pos = 100.0
  stirrer_y_utensil_pos = 100.0

  stirrer_x_home_pos = 0.0
  stirrer_y_home_pos = 0.0

  stirrer_width_mm = 50.0

  stir_start_gap = 5.0
  stir_stop_gap = 10.0

  # Diameters of the three different all-clad utensils
  utensil_diameter_mm = [270.0, 300.0, 150.0]
  
  def __init__(self,
               x_rail_dir_pin, x_rail_step_pin,
               y_rail_dir_pin, y_rail_step_pin,
               z_rail_dir_pin, z_rail_step_pin):s   
    # TODO : Fill in values to the constructor below.
    self.x_rail = stepper_axis.StepperAxis(x_rail_dir_pin, x_rail_step_pin, max_x_rail_translation_mm)
    self.y_rail = stepper_axis.StepperAxis(y_rail_dir_pin, y_rail_step_pin, max_y_rail_translation_mm)
    self.z_rail = stepper_axis.StepperAxis(z_rail_dir_pin, z_rail_step_pin, max_z_rail_translation_mm)

  def stirrer_up(self):
    self.z_rail.move_to(stirrer_z_up_pos)

  def stirrer_down(self):
    self.z_rail.move_to(stirrer_z_down_pos)

  def stirrer_position_over_utensil(self):
    self.stirrer_up()
    self.x_rail.move_to(stirrer_x_utensil_pos)
    self.y_rail.move_to(stirrer_y_utensil_pos)

  def stirrer_goto_base(self):
    self.stirrer_up()
    self.x_rail.move_to(stirrer_x_home_pos)
    self.y_rail.move_to(stirrer_y_home_pos)

  def get_cord_length_mm(dist_from_center, utensil_index):
    if utensil_index >= 3:
      raise ValueError("There are only three known utensil sizes. Invalid utensil index:" + utensil_index)

    utensil_radius = utensil_diameter_mm[utensil_index]/2
    if (dist_from_center >= utensil_radius):
      raise ValueError("Requested distance from center is invalid for specified utensil:" + dist_from_center)

    return 2 * math.sqrt((utensil_radius * utensil_radius) - (dist_from_center * dist_from_center))

  def move_to(self, dest_pos):
    start_pos = (self.x_rail.get_curr_pos_mm(), self.y_rail.get_curr_pos_mm())
    delta = ((dest_pos[0] - self.x_rail.get_curr_pos_mm()),
             (dest_pos[1] - self.y_rail.get_curr_pos_mm()))
    max_delta = max(abs(delta[0]), abs(delta[1]))
    
    for i in range(1, max_delta + 1):
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
    
  def one_stir_stroke(self, dist_from_center, utensil_index, top_to_bottom):
    cord_length = get_cord_length_mm(dist_from_center, utensil_index)
    start_x = stirrer_x_home_pos - dist_from_center
    if dist_from_center > 0:
      start_x = start_x + (stirrer_width_mm / 2)
    else:
      start_x = start_x - (stirrer_width_mm / 2)

    if top_to_bottom:
      start_y = stirrer_y_home_pos + (cord_length / 2) - stir_start_gap
      end_y = start_y - cord_length + stir_stop_gap
    else:
      start_y = stirrer_y_home_pos - (cord_length / 2) + stir_start_gap
      end_y = start_y + cord_length - stir_stop_gap

    self.execute_stir_stroke((start_x, start_y), (start_x, end_y))

  # X axis is the top rail and increases left to right (looking FROM ATX)
  # Y axis is the bottom rail and increases from ATX to front.
  def stir(self, utensil_utensil_index, stir_for_seconds):
    utensil_radius = utensil_diameter_mm[utensil_index]/2
    stir_dx = -10
    top_to_bottom = True
    start = time.get_time() # Find the right api
    while True:
      current = time.get_time()
      if (current  - start_time) > stir_for_seconds:
        break
      for dist_from_center in range((utensil_radius - stir_start_gap), -utensil_radius, stir_dx):
        self.one_stir_stroke(dist_from_center, utensil_index, top_to_bottom)
        top_to_bottom = not top_to_bottom
        current = time.get_time()
        if (current  - start_time) > stir_for_seconds:
          break
    
if (__name__ == "__main__"):
  stirrer = Stirrer(2, 3, 4, 5, 6, 7)

  stirrer.stirrer_position_over_utensil()
  stirrer.stirrer_goto_base()
  stirrer.stir(0, 100)
