import cmd
import datetime
import os
import string
import thread
import time

from controller.sous_chef import SousChef
from data_structures import Recipe
from data_structures import Step

def get_curr_time_in_secs():
  return time.mktime(time.localtime())

class MakeRecipeCommand(cmd.Cmd):
  def __init__(self, prompt, utensil_size,
               recipe_name, recipe_storage_location):
    cmd.Cmd.__init__(self)
    self.prompt = prompt
    self.ruler = '='
    self.recipe_storage_location = recipe_storage_location
    self.recipe = Recipe(utensil_size, recipe_name.strip())
    self.sous_chef = SousChef(utensil_index=utensil_size)
    self.intro = """    You are now in the recipe maker. Type help to get all
    the available commands. Use help <command> to get help about
    a specific command. All the commands that are SUCCESSFULLY
    executed on SousChef are also logged into the recipe.
    Use the 'done' command when you're done to save the recipe
    and exit out of the recipe maker mode."""

    if not os.path.isdir(self.recipe_storage_location):
      raise ValueError("Recipe storage location needs to be a directory:" + self.recipe_storage_location)

  ## Command definitions ##
  def do_hist(self, args):
    """Print a list of commands that have been entered"""
    print self._hist

  def preloop(self):
    """Initialization before prompting user for commands.
       Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
    """
    cmd.Cmd.preloop(self)   ## sets up command completion
    self._hist    = []      ## No history yet
    self._locals  = {}      ## Initialize execution namespace for user
    self._globals = {}
    self.start_time = get_curr_time_in_secs()
    self.previous_time = get_curr_time_in_secs()

  def add_time_step_to_recipe(self):
    curr_time = get_curr_time_in_secs()
    time_delta = curr_time - self.previous_time
    self.previous_time = curr_time
    self.recipe.add_step(Step("delay", [time_delta]))

  def do_name(self, line):
    recipe_name = string.capwords(line.strip())
    self.recipe.set_name(recipe_name)

  def help_name(self):
    print """ Command to set the name of the recipe """

  def do_utensil(self, line):
    try:
      utensil_size = int(line)
      self.recipe.set_utensil_size(utensil_size)
    except Exception, e:
      print "Error:" + str(e)

  def help_utensil(self):
    print """ Command to pick the utensil used for this recipe """

  def help_lid(self):
    print """        Command to open or close the lid. Invoke only
    when this operation is possible. e.g.cup dispenser is out of the
    way, pumps are off, stirrer is up.
    Usage: lid {open,close} """

  def do_lid(self, line):
    cmd = line.strip().lower()
    try:
      if cmd == 'open':
        self.sous_chef.open_lid()
      elif cmd == 'close':
        self.sous_chef.close_lid()
      else:
        raise ValueError("options to lid must be one of {open, close}. Try help lid")
      self.add_time_step_to_recipe()
      self.recipe.add_step(Step("lid",[cmd]))
    except Exception, e:
      print "Error:" + str(e)

  def do_addwater(self, line):
    try:
      num_cups = float(line)
      self.add_time_step_to_recipe()
      self.recipe.add_step(Step("addwater",[num_cups]))
      self.sous_chef.add_water_in_cups(num_cups)
    except Exception, e:
      print "Error:" + str(e)

  def help_addwater(self):
    print """     Command to add num_cups water in cups to the
    utensil. Ensure that this move can be executed. e.g. cup dispenser is
    out of the way, lid is open
    Usage: addwater 1.5 """

  def do_addoil(self, line):
    try:
      num_tbsp = float(line)
      self.add_time_step_to_recipe()
      self.recipe.add_step(Step("addoil",[num_tbsp]))
      self.sous_chef.add_oil_in_tbsp(num_tbsp)
    except Exception, e:
      print "Error:" + str(e)

  def help_addoil(self):
    print """       Command to add num_tbsp tablespoons of oil
    to the utensil. Ensure that this move can be executed. e.g. cup
    dispenser is out of the way, lid is open
    Usage: addoil 2 """

  def do_stir(self, line):
    try:
      vals = line.split()
      stir_type = vals[0]
      num_secs = int(vals[1])
      stir_height_index=int(vals[2])

      self.add_time_step_to_recipe()
      if stir_type is "circular":
        stir_radius_index=int(vals[3])
        self.recipe.add_step(Step("stir",[stir_type, num_secs, stir_height_index, stir_radius_index]))
        self.sous_chef.stir_circular(num_secs, stir_height_index, stir_radius_index)
      elif stir_type is "linear":
        self.recipe.add_step(Step("stir",[stir_type, num_secs, stir_height_index]))
        self.sous_chef.stir_linear(num_secs, stir_height_index)
      else:
        raise ValueError(stir_type + " is invalid as stir_type") 
    except Exception, e:
      print "Error:" + str(e)

  def help_stir(self):
    print """         Command to lower the stirrer and stir the
    contents in the utensil for num_secs seconds. Ensure that this move
    can be executed. e.g. cup dispenser is out of the way, lid is open,
    pumps are off. Can stir low or high.
    Usage: stir circular 60 [1-5] [1-5]"""

  def do_temp(self, line):
    try:
      target_temp = float(line)
      self.add_time_step_to_recipe()
      self.recipe.add_step(Step("temp",[target_temp]))
      self.sous_chef.set_temperature_in_celcius(target_temp)
    except Exception, e:
      print "Error:" + str(e)

  def help_temp(self):
    print """   Command to activate the stove controller to set
    and maintain the temperature of the contents in the utensil at
    target_temperature *C. Ensure that this move can be executed.
    e.g. cup dispenser is out of the way, lid is open. This operation
    is cancelled if an operation that moves the platform is executed.
    Usage: temp 80 """

  def do_knobpos(self, line):
    try:
      target_pos = float(line)
      self.add_time_step_to_recipe()
      self.recipe.add_step(Step("knobpos",[target_pos]))
      self.sous_chef.set_knobpos(target_pos)
    except Exception, e:
      print "Error:" + str(e)

  def help_knobpos(self):
    print """   Command to activate the stove controller to disable the pid
    controller and set the position of the knob to the specified value. The
    stove is switched off if the position is 0 and is switched on for any
    other position. Position is specified as a percentage.
    Usage: knobpos 80 """

  def do_addcup(self, line):
    try:
      cup_num = int(line)
      self.add_time_step_to_recipe()
      self.recipe.add_step(Step("addcup",[cup_num]))
      self.sous_chef.add_cup(cup_num)
    except Exception, e:
      print "Error:" + str(e)

  def help_addcup(self):
    print """     Command to add the ingredients in a cup
    identified by the cup number to the utensil. Ensure that this
    move can be executed. e.g. platform is not obstructing the path
    of the arm. i.e. it is over the utensil.
    Usage: addcup 1 """

  def do_done(self, line):
    self.add_time_step_to_recipe()
    self.recipe.add_step(Step("done",[]))
    self.sous_chef.shutdown()
    curr_time = get_curr_time_in_secs()
    time_delta = curr_time - self.start_time
    self.recipe.set_total_time(time_delta)
    return True

  def help_done(self):
    print """ Command to end a recipe. Writes the recipe to file and moves back to the
    main prompt.
    Usage: done """

  def default(self, line):
    print """ Unrecognized command. Try 'help' to get the list of all available commands """

  def postloop(self):
    """Take care of any unfinished business.
       Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
    """
    cmd.Cmd.postloop(self)   ## Clean up command completion
    recipe_filename = self.recipe.name.lower().replace(" ", "_") + ".json"
    abs_recipe_filename = os.path.join(self.recipe_storage_location, recipe_filename)
    print "Saving recipe" + self.recipe.name + " to file:" + abs_recipe_filename
    f = open(abs_recipe_filename, "w")
    f.write(self.recipe.to_json())
    f.close()
    print "Exiting Recipe Maker."

  def do_exit(self, line):
    """Exits from the console"""
    return self.do_done(line)

  ## Command definitions to support Cmd object functionality ##
  def do_EOF(self, line):
    """Exit on system end of file character"""
    return self.do_done(line)

  def emptyline(self):
    """Do nothing on empty input line"""
    pass


class SousChefMain(cmd.Cmd):
  def __init__(self, recipe_directory):
    cmd.Cmd.__init__(self)
    self.prompt = "=>"
    self.ruler = '='
    self.recipe_directory = recipe_directory

  def do_hist(self, args):
    """Print a list of commands that have been entered"""
    print self._hist

  def preloop(self):
    """Initialization before prompting user for commands.
       Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
    """
    cmd.Cmd.preloop(self)   ## sets up command completion
    self._hist    = []      ## No history yet
    self._locals  = {}      ## Initialize execution namespace for user
    self._globals = {}

  def do_exit(self, args):
    """Exits from the console"""
    return True

  ## Command definitions to support Cmd object functionality ##
  def do_EOF(self, args):
    """Exit on system end of file character"""
    return self.do_exit(args)


  def do_help(self, args):
    """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
    """
    ## The only reason to define this method is for the help text in the doc string
    cmd.Cmd.do_help(self, args)

  def postloop(self):
    """Take care of any unfinished business.
       Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
    """
    cmd.Cmd.postloop(self)   ## Clean up command completion
    print "Exiting ...kthxbye"

  def default(self, line):
    print """ Unrecognized command. Try 'help' to get the list of all available commands """

  def emptyline(self):
    """Do nothing on empty input line"""
    pass

  def do_createrecipe(self, line):
    try:
      vals = line.split()
      utensil_size = int(vals[0])
      recipe_name = line[len(vals[0]):].strip()
      make_prompt = self.prompt[:-1]+':Make=>'
      create_interface = MakeRecipeCommand(make_prompt, utensil_size,
              recipe_name, self.recipe_directory)
      create_interface.cmdloop()
    except Exception, e:
      print "Error:" + str(e)

  def help_createrecipe(self):
    print """ Command to enter the recipe creating mode.
              Usage: createrecipe <utensil size> <recipe name>
                     utensil size is an integer in {0, 1, 2}
          """

  def do_playrecipe(self, line):
    try:
      if not os.path.exists(self.recipe_directory):
        raise ValueError("Recipe directory points to an invalid location")
      abs_filename = os.path.join(self.recipe_directory, line.strip().lower())
      f = open(abs_filename, "r")
      recipe = Recipe(json_string=f.read())
      f.close()
      print "This recipe will take " + str(datetime.timedelta(seconds=recipe.get_total_time())) + " secs"
      sous_chef = SousChef(utensil_index=recipe.utensil_size)
      for step in recipe.steps:
        if step.name == "lid":
          if step.step_args[0] == 'open':
            sous_chef.open_lid()
          elif step.step_args[0] == 'close':
            sous_chef.close_lid()
          else:
            raise ValueError("Invalid Recipe. Options to lid must be one of {open, close}. ")
        elif step.name == "addwater":
          sous_chef.add_water_in_cups(step.step_args[0])
        elif step.name == "addoil":
          sous_chef.add_oil_in_tbsp(step.step_args[0])
        elif step.name == "stir":
          if len(step.step_args) == 4:
            sous_chef.stir(step.step_args[0], step.step_args[1], step.step_args[2], step.step_args[3])
          else:
            sous_chef.stir(step.step_args[0], step.step_args[1], step.step_args[2])
        elif step.name == "temp":
          sous_chef.set_temperature_in_celcius(step.step_args[0])
        elif step.name == "knobpos":
          sous_chef.set_knobpos(step.step_args[0])
        elif step.name == "addcup":
          sous_chef.add_cup(step.step_args[0])
        elif step.name == "delay":
          time.sleep(step.step_args[0])
        elif step.name == "done":
          sous_chef.shutdown()
        else:
          raise ValueError("Invalid step in recipe:" + step.name)
    except Exception, e:
      print "Error:" + str(e)

  def help_playrecipe(self):
    print """ Command to load a recipe by filename and play it on Sous Chef
              Usage: playrecipe <filename>
          """

if __name__ == '__main__':
    SousChefMain("./recipe_store").cmdloop()
