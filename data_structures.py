import json

class DefaultEncoder(json.JSONEncoder):
  def default(self, obj):
    return obj.__dict__
  
class Step:
  steps = set(["lid",
               "addwater",
               "addoil",
               "stir",
               "temp",
               "addcup",
               "delay",
               "done",
               "knobpos"])
  
  def __init__(self, name='', args='', json_dict=None):
    if json_dict == None:
      if name not in Step.steps:
        raise ValueError("Unrecognised step:" + step)
      self.name = name
      self.step_args = args
    else:
      self.__dict__ = json_dict
 
class Recipe:
  def __init__(self, utensil_size=0, name='', json_string=None):
    if json_string == None:
      self.name = name
      self.utensil_size = utensil_size
      self.steps = []
      self.total_time_secs = 0
    else:
      self.__dict__ = json.loads(json_string)
      tmp_steps = self.__dict__["steps"]
      del(self.__dict__["steps"])
      self.steps = []
      for s in tmp_steps:
        self.steps.append(Step(json_dict=s))

  def set_name(self, name):
    self.name = name

  def set_utensil_size(self, utensil):
    self.utensil_size = utensil
    
  def add_step(self, step):
    if not isinstance(step, Step):
      raise ValueError("step needs to be of type Step")
    self.steps.append(step)

  def set_total_time(self, time_secs):
    self.total_time_secs = time_secs

  def get_total_time(self):
    return self.total_time_secs

  def to_json(self):
    return json.dumps(self, cls=DefaultEncoder, indent = 2)

  
if __name__ == '__main__':
  r = Recipe("Beans Palya", 0)
  s = Step("lid", ["open"])
  r.add_step(Step("addcup", ['small', 4, False]))
  r.add_step(s)
  t = Recipe(json_string=r.to_json())
  print t.to_json()
  print len(t.steps)
  if t.steps[0].step_args[2]:
    print "Srikar"
