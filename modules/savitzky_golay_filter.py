from collections import deque
import threading
import time

def get_curr_time_in_secs():
    return time.mktime(time.localtime())
  
class SavitzkyGolayFilter(threading.Thread):
  """ Savitzky Golay filter which smoothens by fitting a quadratic over 5
      points.
      get_next_point : A parameterless functional which returns a double
                       representing the value of the point when it was invoked
      sampling_interval: The interval between two successive calls of
                        get_next_point.
  """
  
  # Convolution tables to obtain the smoothed function (using a cubic function
  # for smoothing). The map is keyed by the number of points used in the
  # convolution and the value is a tuple of (normalization factor for each
  # coefficient, an array of size 'key containing the coefficients. 
  function_convolution_tables = {5 : (35, [-3, 12, 17, 12, -3]),
                        7 : (21, [-2, 3, 6, 7, 6, 3, -2]),
                        9 : (231, [-21, 14, 39, 54, 59, 54, 39, 14, -21])}

  # Convolution tables to obtain the smoothed derivative of the function
  # (using a cubic function for smoothing). The map is keyed by the number
  # of points used in the convolution and the value is a tuple of (normalization
  # factor for each coefficient, an array of size 'key containing the coefficients).
  # Multiply the normalization factor by sampling_interval to get the final
  # normalization factor
  derivative_convolution_tables = {5 : (12, [-1, 8, 0, 8, 1]),
                        7 : (252, [-22, 67, 58, 0, -58, -67, 22]),
                        9 : (1188, [-86, 142, 193, 126, 0, -126, -193, -142, 86])}
  
  def __init__(self, sampling_interval, get_next_point, num_points_used_to_fit = 5):
    self.points = deque([])
    self.sampling_interval = sampling_interval
    self.get_next_point = get_next_point
    self.lock = threading.Lock()
    self.num_points_used_to_fit = num_points_used_to_fit 
    if sampling_interval <= 1:
      raise ValueError("Sampling interval has to be > 1:" + sampling_interval)
    self.is_enabled = False
    self.should_stop = False
    
  def run(self):
    """ Adds a point every sampling_interval secs. """
    self.is_enabled = False
    while True:
      current_time = get_curr_time_in_secs()
      lock.acquire()
      if self.is_enabled:
        point = self.get_next_point()
        self.points.append(point)
        if len(self.points) > self.num_points_used_to_fit:
          self.points.popleft()
        lock.release()
      elif self.should_stop:
        lock.release()
        return # Stopping condition. Exits thread
      new_time = get_curr_time_in_secs()
      if (new_time - current_time) < self.sampling_interval:
        time_to_sleep = current_time + self.sampling_interval - new_time
        time.sleep(time_to_sleep)

  def stop(self):
    lock.acquire()
    self.is_enabled = False
    self.should_stop = True
    lock.release()

  def pause(self):
    lock.acquire()
    self.is_enabled = False
    self.points.clear()
    lock.release()

  def resume(self):
    lock.acquire()
    self.is_enabled = True
    lock.release()
    
  def get_last_raw_point(self):
    lock.acquire()
    if len(self.points) == 0:
      val = None
    else:
      val = self.points[len(self.points) - 1]
    lock.release()
    return val
  
  def get_current_smoothed_point(self):
  """ Will only smooth if there are more than num_points_used_to_fit points
      sampled already.
  """
    lock.acquire()
    smoothed_value = 0.0
    if len(self.points) >= self.num_points_used_to_fit:
      convolution_filter = function_convolution_tables[self.num_points_used_to_fit][1]
      normalization_factor = function_convolution_tables[self.num_points_used_to_fit][0]
     
      for i in range(0, self.num_points_used_to_fit):
        smoothed_value = smoothed_value + convolution_filter[i]*self.points[i]
      smoothed_value = float(smoothed_value)/float(normalization_factor)
      lock.release()
    else:
      lock.release()
      smoothed_value = get_last_raw_point()

    return smoothed_value

  def get_current_smoothed_derivative(self):
  """ Will only smooth if there are more than num_points_used_to_fit points
      sampled already.
  """
    lock.acquire()
    smoothed_value = 0.0
    if len(self.points) >= self.num_points_used_to_fit:
      convolution_filter = derivative_convolution_tables[self.num_points_used_to_fit][1]
      normalization_factor = derivative_convolution_tables[self.num_points_used_to_fit][0]
     
      for i in range(0, self.num_points_used_to_fit):
        smoothed_value = smoothed_value + convolution_filter[i]*self.points[i]
      smoothed_value = float(smoothed_value)/float(normalization_factor * self.sampling_interval)
      lock.release()
    else:
      lock.release()
      smoothed_value = 0.0
    return smoothed_value
