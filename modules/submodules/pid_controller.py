import modules.submodules.savitzky_golay_filter
import random
import threading
import time

def get_curr_time_in_secs():
  return time.mktime(time.localtime())

bound = lambda x, lower, upper: max(lower, min(upper, x))

class PIDController(threading.Thread):
  """ Implementation of a PID Controller to control the value of a
      manipulated variable in order to move a process_variable to a
      desired s setpoint
  """
  def __init__(self,  P, I, D,
               setpoint,
               sampling_interval_s,
               get_current_process_variable,
               set_manipulated_variable):
    """ P, I and D are the constants of a standard PID controller.
        setpoint: Desired value of the process variable
        get_current_process_variable: A parameterless function that returns
                                  a double representing the current value of
                                  the process variable.
        set_manipulated_variable: A function which takes a value between 0
                                  and 100 that is linearly interpreted by the
                                  function to set the manipulated variable.
    """
    self.P = P
    self.I = I
    self.D = D
    self.setpoint = setpoint
    self.sampling_interval_s = sampling_interval_s
    self.get_current_process_variable = get_current_process_variable
    self.set_manipulated_variable = set_manipulated_variable
    self.integral = 0.0
    self.savitzky_golay_filter = savitzky_golay_filter.SavitzkyGolayFilter(
                                     self.sampling_interval_s,
                                     self.get_error,
                                     num_points_used = 5)
    self.is_enabled = False
    self.should_stop = False

  def get_error(self):
    return (self.setpoint - self.get_current_process_variable())
  
  def run(self):
    self.is_enabled = False
    self.savitzky_golay_filter.start()
    # Randomize the start of the filter and the current thread.
    time.sleep(random.randint(0, self.sampling_interval_s/2))
    while True:
      current_time = get_curr_time_in_secs()
      # This needs to be locked. But, the consequences are not high enough to
      # justify introducing the lock.
      if self.is_enabled:
        new_manipulated_variable = self.compute_manipulated_variable()
        sef.set_manipulated_variable(new_manipulated_variable)
      elif self.should_stop:
        return # Stopping condition. Exits thread
      new_time = get_curr_time_in_secs()
      if (new_time - current_time) < self.sampling_interval_s:
        time_to_sleep = current_time + self.sampling_interval_s - new_time
        time.sleep(time_to_sleep)

  def stop(self):
    self.savitzky_golay_filter.stop()
    self.savitzky_golay_filter.join()
    self.is_enabled = False
    self.should_stop = True
    
  def compute_manipulated_variable(self):
    self.integral = self.integral + self.get_error()
    point = self.savitzky_golay_filter.get_current_smoothed_point()
    derivative = self.savitzky_golay_filter.get_current_smoothed_derivative()
    new_value = (self.P * point) + (self.I * self.integral * self.sampling_interval_s) + (self.D * derivative)
    if new_value < 0 or new_value > 100:
      new_value = max(0, min(new_value, 100))
      self.integral = (new_value -(self.P * point) - (self.D * derivative))/(selfI * self.sampling_interval_s)
    return new_value
  
  def pause(self):
    self.is_enabled = False
    self.savitzky_golay_filter.pause()
    self.integral = 0.0

  def resume(self):
    self.savitzky_golay_filter.resume()
    self.is_enabled = True
    
    
  def set_new_setpoint(self, new_setpoint):
    self.pause()
    self.setpoint = new_setpoint
    self.resume()
