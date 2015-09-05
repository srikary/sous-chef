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
    threading.Thread.__init__(self)
    self.points = deque([])
    self.sampling_interval = sampling_interval
    self.get_next_point = get_next_point
    self.lock = threading.Lock()
    self.num_points_used_to_fit = num_points_used_to_fit 
    if sampling_interval <= 1:
      raise ValueError("Sampling interval has to be > 1:" + sampling_interval)
    self.is_enabled = True
    self.should_stop = False
    
  def run(self):
    """ Adds a point every sampling_interval secs. """
    while True:
      start_time = get_curr_time_in_secs()
      self.lock.acquire()
      if self.is_enabled:
        point = self.get_next_point()
        self.points.append(point)
        if len(self.points) > self.num_points_used_to_fit:
          self.points.popleft()
        # print self.points
      elif self.should_stop:
        self.lock.release()
        return # Stopping condition. Exits thread
      self.lock.release()
      new_time = get_curr_time_in_secs()
      if (new_time - start_time) < self.sampling_interval:
        time_to_sleep = start_time + self.sampling_interval - new_time
        time.sleep(time_to_sleep)

  def stop(self):
    self.lock.acquire()
    self.is_enabled = False
    self.should_stop = True
    self.lock.release()

  def pause(self):
    self.lock.acquire()
    self.is_enabled = False
    self.points.clear()
    self.lock.release()

  def resume(self):
    self.lock.acquire()
    self.is_enabled = True
    self.lock.release()
    
  def get_last_raw_point(self):
    self.lock.acquire()
    if len(self.points) == 0:
      val = None
    else:
      val = self.points[len(self.points) - 1]
    self.lock.release()
    return val
  
  def get_current_smoothed_point(self):
    """ Will only smooth if there are more than num_points_used_to_fit points
      sampled already.
    """
    self.lock.acquire()
    smoothed_value = 0.0
    if len(self.points) >= self.num_points_used_to_fit:
      convolution_filter = SavitzkyGolayFilter.function_convolution_tables[
        self.num_points_used_to_fit][1]
      normalization_factor = SavitzkyGolayFilter.function_convolution_tables[
        self.num_points_used_to_fit][0]
     
      for i in range(0, self.num_points_used_to_fit):
        smoothed_value = smoothed_value + convolution_filter[i]*self.points[i]
      smoothed_value = float(smoothed_value)/float(normalization_factor)
      self.lock.release()
    else:
      self.lock.release()
      smoothed_value = self.get_last_raw_point()

    return smoothed_value

  def get_current_smoothed_derivative(self):
    """ Will only smooth if there are more than num_points_used_to_fit points
        sampled already.
    """
    self.lock.acquire()
    smoothed_value = 0.0
    if len(self.points) >= self.num_points_used_to_fit:
      convolution_filter = SavitzkyGolayFilter.derivative_convolution_tables[
        self.num_points_used_to_fit][1]
      normalization_factor = SavitzkyGolayFilter.derivative_convolution_tables[
        self.num_points_used_to_fit][0]
     
      for i in range(0, self.num_points_used_to_fit):
        smoothed_value = smoothed_value + convolution_filter[i]*self.points[i]
      smoothed_value = float(smoothed_value)/float(normalization_factor * self.sampling_interval)
      self.lock.release()
    else:
      self.lock.release()
      smoothed_value = 0.0
    return smoothed_value


def get_pt():
  time_start = (get_curr_time_in_secs() - 1441473133)/2
  return 4 + time_start * time_start

if (__name__ == "__main__"):
  filter = SavitzkyGolayFilter(2, get_pt, 5)
  filter.start()
  for i in range(0, 10):
    print "" + str(i) + " " + str(filter.get_current_smoothed_derivative()) +  " k "
    time.sleep(2)
  filter.pause()
  for i in range(0, 5):
    print "" + str(i) + " " + str(filter.get_current_smoothed_point()) +  " k "
    time.sleep(2)
  filter.resume()
  for i in range(0, 10):
    print "" + str(i) + " " + str(filter.get_current_smoothed_point()) +  " k "
    time.sleep(2)
  filter.stop()
  filter.join()
