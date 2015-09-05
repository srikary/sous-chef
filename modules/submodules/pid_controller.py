import savitzky_golay_filter
import random
import threading
import time

def get_curr_time_in_secs():
  return time.mktime(time.localtime())

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
    threading.Thread.__init__(self)
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
                                     num_points_used_to_fit = 5)
    self.is_enabled = False
    self.should_stop = False
    self.lock = threading.Lock()

  def get_error(self):
    dest_point = self.setpoint
    return (dest_point - self.get_current_process_variable())
    
  
  def run(self):
    self.is_enabled = False
    self.savitzky_golay_filter.start()
    # Randomize the start of the filter and the current thread.
    time.sleep(random.randint(0, self.sampling_interval_s/2))
    while True:
      print "A"
      start_time = get_curr_time_in_secs()
      self.lock.acquire()
      print self.is_enabled
      if self.is_enabled:
        new_manipulated_variable = self.compute_manipulated_variable()
        print "New Dest:" + str(new_manipulated_variable)
        if new_manipulated_variable is not None:
          print "C"
          self.set_manipulated_variable(new_manipulated_variable)
      elif self.should_stop:
        self.lock.release()
        return # Stopping condition. Exits thread
      self.lock.release()
      new_time = get_curr_time_in_secs()
      if (new_time - start_time) < self.sampling_interval_s:
        time_to_sleep = start_time + self.sampling_interval_s - new_time
        time.sleep(time_to_sleep)

  def stop(self):
    self.lock.acquire()
    self.savitzky_golay_filter.stop()
    self.savitzky_golay_filter.join()
    self.is_enabled = False
    self.should_stop = True
    self.lock.release()
    
  def compute_manipulated_variable(self):
    print "P"
    point = self.savitzky_golay_filter.get_current_smoothed_point()
    print "Q"
    derivative = self.savitzky_golay_filter.get_current_smoothed_derivative()
    print "R"
    if point == None or derivative == None:
      return None
    self.integral = self.integral + point
    new_value = (self.P * point) + (self.I * self.integral * self.sampling_interval_s) + (self.D * derivative)
    if new_value < 0 or new_value > 100:
      new_value = max(0, min(new_value, 100))
      self.integral = (new_value -(self.P * point) - (self.D * derivative))/(selfI * self.sampling_interval_s)
    return new_value
  
  def pause(self):
    self.lock.acquire()
    self.is_enabled = False
    self.savitzky_golay_filter.pause()
    self.integral = 0.0
    self.lock.release()

  def resume(self):
    self.lock.acquire()
    self.savitzky_golay_filter.resume()
    self.is_enabled = True
    self.lock.release()
    
  def set_new_setpoint(self, new_setpoint):
    self.pause()
    self.setpoint = new_setpoint
    self.resume()

# Unit test helpers and methods.
class MockStove:
  def __init__(self, start_temp):
    self.deg_per_sec = 0.5
    self.curr_temp = start_temp
    self.last_update_time = get_curr_time_in_secs()
    self.dest_temp = start_temp
    
  def get_temp(self):
    time_curr = get_curr_time_in_secs()
    if self.curr_temp == self.dest_temp:
      self.last_update_time = time_curr
      return self.curr_temp
    
    degrees = self.deg_per_sec * (time_curr - self.last_update_time)
    new_temp = self.curr_temp + degrees
    if self.curr_temp > self.dest_temp:
      new_temp = self.curr_temp - degrees
    self.last_update_time = time_curr
    self.curr_tempm = new_temp
    return new_temp

  def set_temp(self, temp):
    self.dest_temp = temp
    print "Set temp to: " + str(temp)
  
if (__name__ == "__main__"):
  mock_stove = MockStove(30)
  pid = PIDController(1.0, 1.0, 0, # P, I, D
                      40,      # setpoint
                      2,       # sampling interval   
                      mock_stove.get_temp,
                      mock_stove.set_temp) 
  pid.start()
  pid.set_new_setpoint(34)
  time.sleep(10)
  pid.pause()
  time.sleep(10)
  pid.resume()
  time.sleep(10)
  pid.set_new_setpoint(37)
  time.sleep(10)
  pid.stop()
  pid.join()
