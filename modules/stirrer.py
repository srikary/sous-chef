import submodules.stepper_axis as stepper_axis
import math
import random
import time

class PlatformPosition:
  BASE = 1
  UTENSIL = 2
  LID = 3
  IN_BETWEEN = 4

def get_curr_time_in_secs():
  return time.mktime(time.localtime())

class Stirrer:
  # Dimensions of the Rails
  max_x_rail_translation_mm = 345.0
  max_y_rail_translation_mm = 290.0
  max_z_rail_translation_mm = 100.0
  z_rotations_per_mm = 0.79


  z_up_pos = 0
  z_mid_pos = 55.0
  z_down_pos = max_z_rail_translation_mm
  x_utensil_pos = 171.0
  y_utensil_pos = 122.0

  x_lid_utensil_pos = 171.0
  y_lid_utensil_pos = 287.0

  x_home_pos = 0.0
  y_home_pos = 0.0

  stirrer_x_offset = 53
  stirrer_y_offset = 46

  stirrer_width_mm = 60.0

  stirring_height = [3.0, 10.0, 20.0, 35.0, 60.0]
  stir_start_gap = 5.0 # Distance from utensil wall where the stirrer starts a stroke.
  stir_stop_gap = 45.0 # Distance from utensil wall where the stirrer stops during a stroke.

  # Diameters of the three different all-clad utensils
  utensil_diameter_mm = [200.0, 205.0, 150.0]

  platform_pos_for_cup = [( 310,  45), # SmallCup1
                          (  35,  52), # SmallCup2
                          ( 171,   0), # LargeCup1
                          ( 171,   0)] # LargeCup2

  def __init__(self,
               x_rail_dir_pin, x_rail_step_pin, x_rail_enable_pin,
               y_rail_dir_pin, y_rail_step_pin, y_rail_enable_pin,
               z_rail_dir_pin, z_rail_step_pin, z_rail_enable_pin):
    # TODO : Fill in values to the constructor below.
    self.x_rail = stepper_axis.StepperAxis(x_rail_dir_pin, x_rail_step_pin, x_rail_enable_pin,
            Stirrer.max_x_rail_translation_mm, inc_clockwise=False, speed=150)
    self.y_rail = stepper_axis.StepperAxis(y_rail_dir_pin, y_rail_step_pin, y_rail_enable_pin,
            Stirrer.max_y_rail_translation_mm, speed=150)
    self.z_rail = stepper_axis.StepperAxis(z_rail_dir_pin, z_rail_step_pin, z_rail_enable_pin,
            max_translation_mm=Stirrer.max_z_rail_translation_mm,
            inc_clockwise=True, speed=220, rotations_per_mm=Stirrer.z_rotations_per_mm)
    self.platform_position = PlatformPosition.BASE

  def disable(self):
    self.x_rail.disable()
    self.y_rail.disable()
    self.z_rail.disable()

  def move_to2(self, dest_pos):
    start_pos = (self.x_rail.get_curr_pos_mm(), self.y_rail.get_curr_pos_mm(), self.z_rail.get_curr_pos_mm())
    delta = ((dest_pos[0] - self.x_rail.get_curr_pos_mm()),
             (dest_pos[1] - self.y_rail.get_curr_pos_mm()),
             (dest_pos[2] - self.z_rail.get_curr_pos_mm()))
    max_delta = max(abs(delta[0]), abs(delta[1]), abs(delta[2]))

    for i in range(1, int(max_delta + 1), 5):
      next_x = start_pos[0] + ((float(i) / max_delta) * delta[0])
      next_y = start_pos[1] + ((float(i) / max_delta) * delta[1])
      next_z = start_pos[2] + ((float(i) / max_delta) * delta[2])
      self.x_rail.move_to(next_x)
      self.y_rail.move_to(next_y)
      self.z_rail.move_to(next_z)
    self.x_rail.move_to(dest_pos[0])
    self.y_rail.move_to(dest_pos[1])
    self.z_rail.move_to(dest_pos[2])

  def move_to(self, dest_pos):
    self.z_rail.move_to(dest_pos[2])
    self.x_rail.move_to(dest_pos[0])
    self.y_rail.move_to(dest_pos[1])

  def execute_stir_stroke(self, start_pos, end_pos):
    self.move_to((start_pos[0], start_pos[1], start_pos[2]))
    self.stirrer_down()
    self.move_to((end_pos[0], end_pos[1], end_pos[2]))

  def get_cord_length_mm(self, dist_from_center, utensil_index):
    if utensil_index >= 3:
      raise ValueError("There are only three known utensil sizes. Invalid utensil index:" + utensil_index)

    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    if (dist_from_center >= utensil_radius):
      raise ValueError("Requested distance from center is invalid for specified utensil:" + dist_from_center)

    return 2 * math.sqrt((utensil_radius * utensil_radius) - (dist_from_center * dist_from_center))

  def get_dist(self, dx, dy):
    return math.sqrt((dx * dx) + (dy * dy))

  def get_pos_for_angle(self, angle, utensil_radius):
    stirrer_width_half = (Stirrer.stirrer_width_mm/ 2)
    dx = math.cos(angle) * utensil_radius
    dy = math.sin(angle) * utensil_radius
    if dx > 0:
      dx = dx - stirrer_width_half
      dx_p = dx - Stirrer.stirrer_width_mm
    else:
      dx = dx + stirrer_width_half
      dx_p = dx + Stirrer.stirrer_width_mm

    stirrer_edge_pos = self.get_dist(dx_p, dy)
    if  stirrer_edge_pos > utensil_radius:
      raise ValueError("Stirrer cannot be positioned at this angle:" + str(angle))
    return (dx, dy)

  def position_along_radius_at_angle(self, utensil_radius, angle):
    z_pos = self.z_rail.get_curr_pos_mm()
    stirrer_x_center = Stirrer.x_utensil_pos + Stirrer.stirrer_x_offset
    stirrer_y_center = Stirrer.y_utensil_pos + Stirrer.stirrer_y_offset
    (dx, dy) = self.get_pos_for_angle(angle, utensil_radius)
    dest = (stirrer_x_center + dx, stirrer_y_center + dy, z_pos)
    self.move_to(dest)

  def one_circular_stir_stroke(self, utensil_radius, rotate_clockwise):
    old_x_speed = self.x_rail.get_speed()
    old_y_speed = self.y_rail.get_speed()
    twopiby360 = (2 * math.pi) / 360
    start = 0
    end = 360
    increment = 1
    if not rotate_clockwise:
      start = 360
      end = 0
      increment = -1
    for i in range(start, end, increment):
      try:
        self.position_along_radius_at_angle(utensil_radius, i * twopiby360)
        self.x_rail.set_speed(270)
        self.y_rail.set_speed(270)
      except ValueError:
        continue
    self.x_rail.set_speed(old_x_speed)
    self.y_rail.set_speed(old_y_speed)

  def one_linear_stir_stroke(self, stirrer_dist_from_center, utensil_index, top_to_bottom, stir_height_index):
    #print "Stroke:" + str(dist_from_center)+ ", " + str(top_to_bottom)
    stirrer_width_half = (Stirrer.stirrer_width_mm/ 2)
    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    # Compute the max height that the stirrer can stir on this stroke
    edge_dist_from_center = stirrer_dist_from_center + stirrer_width_half
    if stirrer_dist_from_center < 0:
      edge_dist_from_center = stirrer_dist_from_center - stirrer_width_half
    # This stroke will keep the edge out of bounds. Return without doing anything.
    if abs(edge_dist_from_center) >= utensil_radius:
      return
    cord_length = self.get_cord_length_mm(edge_dist_from_center, utensil_index)

    # Coordinates for the center of the platform for which the stirrer is at the
    # center of the utensil
    stirrer_x_center = Stirrer.x_utensil_pos + Stirrer.stirrer_x_offset
    stirrer_y_center = Stirrer.y_utensil_pos + Stirrer.stirrer_y_offset

    x_delta = stirrer_x_center + stirrer_dist_from_center

    if top_to_bottom:
      start_y = stirrer_y_center + (cord_length / 2) - Stirrer.stir_start_gap
      end_y = start_y - cord_length + Stirrer.stir_stop_gap + Stirrer.stir_start_gap
    else:
      start_y = stirrer_y_center - (cord_length / 2) + Stirrer.stir_start_gap
      end_y = start_y + cord_length - Stirrer.stir_stop_gap - Stirrer.stir_start_gap
    #print "Executing stroke: " + repr(x_delta) + ", " + repr(start_y) + ", " + repr(end_y)
    if stir_height_index < 4:
      this_stroke_up_pos = Stirrer.z_down_pos - Stirrer.stirring_height[stir_height_index]
    else:
      full_stroke_length = Stirrer.stirring_height[stir_height_index]
      this_stroke_length = (float(utensil_radius - abs(edge_dist_from_center))/utensil_radius)* full_stroke_length
      this_stroke_up_pos = Stirrer.z_down_pos - this_stroke_length

    self.execute_stir_stroke((x_delta, start_y, this_stroke_up_pos), (x_delta, end_y, Stirrer.z_down_pos))

  ################  Public methods. #################

  def stirrer_up(self):
    self.z_rail.move_to(Stirrer.z_up_pos)

  def stirrer_mid(self):
    self.z_rail.move_to(Stirrer.z_mid_pos)

  def stirrer_down(self):
    self.z_rail.move_to(Stirrer.z_down_pos)

  def is_stirrer_up(self):
    return abs(self.z_rail.get_curr_pos_mm() - Stirrer.z_up_pos) <= 2

  def position_platform_at_utensil(self):
    if not self.is_platform_at_utensil():
      self.stirrer_up()
      self.x_rail.move_to(Stirrer.x_utensil_pos)
      self.y_rail.move_to(Stirrer.y_utensil_pos)
      self.platform_position = PlatformPosition.UTENSIL

  def position_platform_at_base(self):
    if not self.is_platform_at_base():
      self.stirrer_up()
      self.x_rail.move_to(Stirrer.x_home_pos)
      self.y_rail.move_to(Stirrer.y_home_pos)
      self.platform_position = PlatformPosition.BASE
      self.disable()

  def position_platform_at_lid(self):
    if not self.is_platform_at_lid():
      self.stirrer_up()
      self.x_rail.move_to(Stirrer.x_lid_utensil_pos)
      self.y_rail.move_to(Stirrer.y_lid_utensil_pos)
      self.platform_position = PlatformPosition.LID
      self.disable()

  def is_platform_at_base(self):
    return self.platform_position == PlatformPosition.BASE

  def is_platform_at_utensil(self):
    return self.platform_position == PlatformPosition.UTENSIL

  def is_platform_at_lid(self):
    return self.platform_position == PlatformPosition.LID

  def get_random_distance(self, radius):
    angle = random.uniform(0, 2 * math.pi)
    return radius * math.cos(angle)

  # X axis is the top rail and increases left to right (looking FROM ATX)
  # Y axis is the bottom rail and increases from ATX to front.
  def stir_linear(self, utensil_index, stir_for_seconds, stir_height_index):
    self.position_platform_at_utensil()
    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    stirrer_width_half = (Stirrer.stirrer_width_mm/ 2)
    top_to_bottom = True
    start_time = get_curr_time_in_secs()
    distances = [0 , 60, -60, -20, 20, 80, -80, -40, 40]
    index = 0
    while True:
      current = get_curr_time_in_secs()
      if (current  - start_time) > stir_for_seconds:
        break
      dist_from_center = distances[index]
      # print "Stirring at distance " + str(dist_from_center)
      index += 1
      index %= len(distances)
      self.one_linear_stir_stroke(dist_from_center, utensil_index, top_to_bottom, stir_height_index)
      top_to_bottom = not top_to_bottom
    # self.stirrer_up()
    # self.position_platform_at_base()

  def stir_circular(self, utensil_index, stir_for_seconds, stir_height_index, stir_radius_index):
    self.position_platform_at_utensil()
    # self.stirrer_mid()
    utensil_radius = Stirrer.utensil_diameter_mm[utensil_index]/2
    this_stroke_down_pos = Stirrer.z_down_pos - Stirrer.stirring_height[stir_height_index]
    this_stroke_radius = (float(stir_radius_index)/5)* utensil_radius
    self.position_along_radius_at_angle(this_stroke_radius, 0)
    self.z_rail.move_to(this_stroke_down_pos)
    start_time = get_curr_time_in_secs()
    rotate_clockwise = True
    while True:
      current = get_curr_time_in_secs()
      if (current  - start_time) > stir_for_seconds:
        break
      self.one_circular_stir_stroke(this_stroke_radius, rotate_clockwise)
      rotate_clockwise = not rotate_clockwise
    # self.stirrer_up()
    # self.position_platform_at_base()

  def position_platform_for_cup(self, cup_num):
    self.stirrer_up()
    if cup_num < 1 or cup_num > 4:
      raise ValueError("Cup number has to be one of {1, 2, 3, 4}")
    cup_idx = cup_num - 1
    self.x_rail.move_to(Stirrer.platform_pos_for_cup[cup_idx][0])
    self.y_rail.move_to(Stirrer.platform_pos_for_cup[cup_idx][1])
    self.platform_position = PlatformPosition.IN_BETWEEN

  def shutdown(self):
    self.position_platform_at_base()

if (__name__ == "__main__"):
  stirrer = Stirrer(7, 8, 19,  # X Dir, Step, Enable
                   11, 25, 20, # Y Dir, Step, Enable
                   9, 10, 21)  # Z Dir, Step, Enable

  #stirrer.position_platform_at_utensil()
  print "At Utensil"
  #time.sleep(2)
  #stirrer.position_platform_at_lid()
  print "At Lid"
  #time.sleep(2)
  #stirrer.stir(0, 50, stir_height_index=3)
  stirrer.stir_linear(0, 100, stir_height_index=4)
  #stirrer.stir_circular(0, 20, stir_height_index=3, stir_radius_index=3)
  #stirrer.position_along_radius_at_angle(100, math.pi/2)
  #stirrer.one_circular_stir_stroke(100, True)
  time.sleep(2)
  print "Done stirring"
  #time.sleep(10)
  stirrer.position_platform_at_base()
  print "At Base"
