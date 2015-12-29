import modules.lid as lid
import modules.pump as pump
import modules.cup_dispenser as cup_dispenser
import modules.stirrer as stirrer
import modules.stove_controller as stove_controller
import ConfigParser
import RPi.GPIO as GPIO
import time

class SousChef:
  def __init__(self, utensil_index, conf_file="./config/sous-chef.conf"):
    self.utensil_index = utensil_index
    config = ConfigParser.RawConfigParser()
    config.read(conf_file)
    GPIO.setmode(GPIO.BCM)
    self.servo_driver_enable_pin = config.getint("CupDispenser", "modules.servo.enable_bcm_pin")

    self.water_pump = pump.Pump(config.getint("WaterPump", "modules.water_pump.relay.bcm_pin"),
                                config.getint("WaterPump", "modules.water_pump.prime_time_msec"),
                                config.getint("WaterPump", "modules.water_pump.time_per_ml_msec"))

    self.oil_pump = pump.Pump(config.getint("OilPump", "modules.oil_pump.relay.bcm_pin"),
                              config.getint("OilPump", "modules.oil_pump.prime_time_msec"),
                              config.getint("OilPump", "modules.oil_pump.time_per_ml_msec"))

    #GPIO.setup(self.servo_driver_enable_pin, GPIO.OUT)
    #GPIO.output(self.servo_driver_enable_pin, GPIO.LOW)
    self.lid = lid.Lid(config.getint("Lid", "modules.lid.servo.channel"))
    self.cup_dispenser = cup_dispenser.CupDispenser(config.getint("CupDispenser", "modules.dispenser.small_cup1.channel"),
                                                    config.getint("CupDispenser", "modules.dispenser.small_cup2.channel"),
                                                    config.getint("CupDispenser", "modules.dispenser.large_cup1.channel"),
                                                    config.getint("CupDispenser", "modules.dispenser.large_cup2.channel"))
    self.stirrer = stirrer.Stirrer(config.getint("Stirrer", "modules.stirrer.x_rail.dir_pin"),
                                   config.getint("Stirrer", "modules.stirrer.x_rail.step_pin"),
                                   config.getint("Stirrer", "modules.stirrer.x_rail.enable_pin"),
                                   config.getint("Stirrer", "modules.stirrer.y_rail.dir_pin"),
                                   config.getint("Stirrer", "modules.stirrer.y_rail.step_pin"),
                                   config.getint("Stirrer", "modules.stirrer.y_rail.enable_pin"),
                                   config.getint("Stirrer", "modules.stirrer.z_rail.dir_pin"),
                                   config.getint("Stirrer", "modules.stirrer.z_rail.step_pin"),
                                   config.getint("Stirrer", "modules.stirrer.z_rail.enable_pin"),)

    self.stove_controller = stove_controller.StoveController(config.getint("StoveController", "modules.stove_controller.servo.channel"),
                                                             config.getint("StoveController", "modules.stove_controller.switch.bcm_pin"),
                                                             config.getint("StoveController", "modules.stove_controller.sampling_interval_sec"))
    self.cup_dispenser.reset()
    self.lid.open()

  def prepare_to_move(self):
    if self.water_pump.is_open() or self.oil_pump.is_open():
      raise ValueError("Cannot move platform. One of the pumps is On")
    if not self.stirrer.is_stirrer_up():
      raise ValueError("Cannot move platform. Raise stirrer before moving the platform.")
    if not self.cup_dispenser.are_all_on_hold():
      raise ValueError("Cannot move platform. Let the cup dispenser finish dispensing.")
    if not self.lid.is_open():
      raise ValueError("Cannot move platform. Raise lid before moving the platform.")
    self.stove_controller.hold_freeze()
    return True

  def ensure_or_position_platform_over_utensil(self):
    if not self.lid.is_open():
      raise ValueError("Cannot move platform. Raise lid before moving the platform.")
    self.stirrer.position_platform_at_utensil()

  def ensure_or_position_platform_at_base(self):
    if not self.lid.is_open():
      raise ValueError("Cannot move platform. Raise lid before moving the platform.")
    self.stirrer.stirrer_up()
    self.stirrer.position_platform_at_base()

  def prepare_to_stir(self):
    if self.water_pump.is_open() or self.oil_pump.is_open():
      raise ValueError("Cannot move platform. One of the pumps is On")
    if not self.cup_dispenser.are_all_on_hold():
      raise ValueError("Cannot move platform. Let the cup dispenser finish dispensing.")
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
    self.ensure_or_position_platform_at_base()
    self.water_pump.dispense_cup(num_cups)

  def add_oil_in_tbsp(self, num_tbsp):
    self.ensure_or_position_platform_at_base()
    self.oil_pump.dispense_tbsp(num_tbsp)

  def stir_linear(self, num_secs, stir_height_index):
    self.prepare_to_stir()
    self.ensure_or_position_platform_over_utensil()
    self.stirrer.stir_linear(self.utensil_index, num_secs, stir_height_index)

  def stir_circular(self, num_secs, stir_height_index, stir_radius_index):
    self.prepare_to_stir()
    self.ensure_or_position_platform_over_utensil()
    self.stirrer.stir_circular(self.utensil_index, num_secs, stir_height_index, stir_radius_index)
    
  def set_temperature_in_celcius(self, temperature):
    self.ensure_or_position_platform_at_base()
    self.stove_controller.set_temperature_C(temperature)

  def set_knobpos(self, pos):
    self.stove_controller.set_knobpos(pos)
    if pos == 0:
      self.stove_controller.off()
    else:
      self.stove_controller.on()

  def add_cup(self, cup_num):
    self.prepare_to_move()
    self.stirrer.position_platform_for_cup(cup_num)
    self.cup_dispenser.pour_cup(cup_num)

  def shutdown(self):
    self.stove_controller.shutdown()
    self.lid.shutdown()
    self.water_pump.shutdown()
    self.oil_pump.shutdown()
    self.cup_dispenser.shutdown()
    self.stirrer.shutdown()

if (__name__ == "__main__"):
  sous_chef = SousChef(0, conf_file="./config/sous-chef.conf")
  inp = raw_input("-->")
  sous_chef.set_knobpos(50)
  #sous_chef.add_cup(1)
  #sous_chef.close_lid()
  #time.sleep(2)
  sous_chef.open_lid()
  #sous_chef.stir(30, stir_height_index=4)
  sous_chef.shutdown()
