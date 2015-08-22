import modules.lid
import modules.pump
import modules.robotic_arm
import modules.stirrer
import modules.stove_controller
import ConfigParser

class SousChef:
  def __init__(conf_file="sous-chef.conf", utensil_index):
    self.utensil_index = utensil_index
    config = ConfigParser.RawConfigParser()
    config.read(conf_file)
    self.lid = lid.Lid(config.getint("Lid", "modules.lid.servo.bcm_pin"),
                       config.getint("Lid", "modules.lid.servo.open_pos"))

    self.water_pump = pump.Pump(config.getint("WaterPump", "modules.water_pump.relay.bcm_pin"),
                                config.getint("WaterPump", "modules.water_pump.prime_time_msec"),
                                config.getint("WaterPump", "modules.water_pump.time_per_ml_msec"))

    self.oil_pump = pump.Pump(config.getint("OilPump", "modules.oil_pump.relay.bcm_pin"),
                              config.getint("OilPump", "modules.oil_pump.prime_time_msec"),
                              config.getint("OilPump", "modules.oil_pump.time_per_ml_msec"))

    self.robotic_arm = robotic_arm.RoboticArm(config.getint("RoboticArm", "modules.arm.rail.dir_bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.rail.step_bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.base_servo.bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.vertical_servo.bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.horizontal_servo.bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.level_servo.bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.tipping_servo.bcm_pin"),
                                              config.getint("RoboticArm", "modules.arm.grasp_servo.bcm_pin"))

    self.stirrer = stirrer.Stirrer(config.getint("Stirrer", "modules.stirrer.x_rail.dir_pin"),
                                   config.getint("Stirrer", "modules.stirrer.x_rail.step_pin"),
                                   config.getint("Stirrer", "modules.stirrer.y_rail.dir_pin"),
                                   config.getint("Stirrer", "modules.stirrer.y_rail.step_pin"),
                                   config.getint("Stirrer", "modules.stirrer.z_rail.dir_pin"),
                                   config.getint("Stirrer", "modules.stirrer.z_rail.step_pin"))

    self.stove_controller = stove_controller.StoveController(config.getint("StoveController", "modules.stove_controller.servo.bcm_pin"),
                                                             config.getint("StoveController", "modules.stove_controller.switch.bcm_pin"),
                                                             config.getint("StoveController", "modules.stove_controller.sampling_interval_sec"))

  def prepare_to_move(self):
    if self.water_pump.is_open() or self.oil_pump.is_open:
      raise ValueError("Cannot move platform. One of the pumps is On")
    if not self.stirrer.is_stirrer_up():
      raise ValueError("Cannot move platform. Raise stirrer before moving the platform.")
    if not self.robotic_arm.is_at_base():
      raise ValueError("Cannot move platform. Move arm to base before moving the platform.")
    if not self.lid.is_open():
      raise ValueError("Cannot move platform. Raise lid before moving the platform.")
    self.stove_controller.hold_freeze()
    return True

  def ensure_or_position_platform_over_utensil(self):
    if not self.lid.is_open():
      raise ValueError("Cannot move platform. Raise lid before moving the platform.")
    self.stirrer.position_platform_at_utensil()

  def prepare_to_stir(self):
    if self.water_pump.is_open() or self.oil_pump.is_open:
      raise ValueError("Cannot move platform. One of the pumps is On")
    if not self.robotic_arm.is_at_base():
      raise ValueError("Cannot move platform. Move arm to base before moving the platform.")
    if not self.lid.is_open():
      raise ValueError("Cannot move platform. Raise lid before moving the platform.")
    self.ensure_or_position_platform_over_utensil()
    self.stove_controller.hold_freeze()
    
  def open_lid(self):
    self.lid.open()

  def close_lid(self):
    if not self.lid.is_open():
      return
    self.prepare_to_move()
    self.stirrer.position_platform_at_lid()
    self.lid.close()

  def add_water_in_cups(self, num_cups):
    self.ensure_or_position_platform_over_utensil()
    self.water_pump.dispense_cup(num_cups)

  def add_oil_in_tbsp(self, num_tbsp):
    self.ensure_or_position_platform_over_utensil()
    self.oil_pump.dispense_tbsp(num_tbsp)
    
  def stir(self, num_secs):
    self.prepare_to_stir()
    self.ensure_or_position_platform_over_utensil()
    self.stirrer.stir(self.utensil_index, num_secs)
    

  def set_temperature_in_celcius(self, temperature):
    self.ensure_or_position_platform_over_utensil()
    self.stove_controller.set_temperature_C(temperature)
    
  def add_cup(self, is_small_cup, cup_num):
    self.self.ensure_or_position_platform_over_utensil()
    self.robotic_arm.add_cup(is_small_cup, cup_num, self.utensil_size)

  def shutdown(self):
    self.stove_controller.shutdown()
    self.robotic_arm.shutdown()
    self.lid.shutdown()
    self.water_pump.shutdown()
    self.oil_pump.shutdown()
    self.stirrer.shutdown()
